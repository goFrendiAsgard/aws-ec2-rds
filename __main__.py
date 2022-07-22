import pulumi
import pulumi_aws as aws


config = pulumi.Config()
public_key_path = config.require('publicKeyPath')
private_key_path = config.require('privateKeyPath')
db_instance_size = config.get('dbInstanceSize') or 'db.t3.small'
db_name = config.get('dbName') or 'appdb'
db_username = config.get('dbUsername') or 'admin'
db_password = config.require_secret('dbPassword')
ec2_instance_size = config.get('ec2InstanceSize') or 't3.small'


# Dynamically fetch AZs so we can spread across them.
availability_zones = aws.get_availability_zones()
# Dynamically query for the AMI in this region.
ami = aws.ec2.get_ami(
    # owners=['amazon'],
    owners=['099720109477'],
    filters=[
            aws.ec2.GetAmiFilterArgs(
            name='name',
            # https://ap-southeast-1.console.aws.amazon.com/ec2/home?region=ap-southeast-1#LaunchInstances:ami=ami-0888eeebde2cb99f7
            values=['ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*']
        )
    ],
    most_recent=True
)


# Read in the public key for easy use below.
public_key = open(public_key_path).read()
# Read in the private key for easy use below (and to ensure it's marked a secret!)
private_key = pulumi.Output.secret(open(private_key_path).read())


# Set up a Virtual Private Cloud to deploy our EC2 instance and RDS datbase into.
prod_vpc = aws.ec2.Vpc(
    'prod-vpc',
    cidr_block='10.192.0.0/16',
    enable_dns_support=True, # gives you an internal domain name
    enable_dns_hostnames=True, # gives yoiu an internal host name
    enable_classiclink=False,
    instance_tenancy='default'
)

# Create public subnets for the EC2 instance.
prod_subnet_public1 = aws.ec2.Subnet(
    'prod-subnet-public-1',
    vpc_id=prod_vpc.id,
    cidr_block='10.192.0.0/24',
    map_public_ip_on_launch=True,
    availability_zone=availability_zones.names[0]
)

# Create private subnets for RDS:
prod_subnet_private1 = aws.ec2.Subnet(
    'prod-subnet-private-1',
    vpc_id=prod_vpc.id,
    cidr_block='10.192.20.0/24',
    map_public_ip_on_launch=False,
    availability_zone=availability_zones.names[1]
)
prod_subnet_private2 = aws.ec2.Subnet(
    'prod-subnet-private-2',
    vpc_id=prod_vpc.id,
    cidr_block='10.192.21.0/24',
    map_public_ip_on_launch=False,
    availability_zone=availability_zones.names[2]
)

# Create a gateway for internet connectivity:
prod_igw = aws.ec2.InternetGateway('prod-igw', vpc_id=prod_vpc.id)

# Create a route table:
prod_public_rt = aws.ec2.RouteTable('prod-public-rt',
    vpc_id=prod_vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            # associated subnets can reach anywhere:
            cidr_block='0.0.0.0/0',
            # use this IGW to reach the internet:
            gateway_id=prod_igw.id,
        )
    ]
)
prod_rta_public_subnet1 = aws.ec2.RouteTableAssociation(
    'prod-rta-public-subnet-1',
    subnet_id=prod_subnet_public1.id,
    route_table_id=prod_public_rt.id
)

# Security group for EC2:
ec2_allow_rule = aws.ec2.SecurityGroup(
    'ec2-allow-rule',
    vpc_id=prod_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description='HTTPS',
            from_port=443,
            to_port=443,
            protocol='tcp',
            cidr_blocks=['0.0.0.0/0'],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            description='HTTP',
            from_port=80,
            to_port=80,
            protocol='tcp',
            cidr_blocks=['0.0.0.0/0'],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            description='SSH',
            from_port=22,
            to_port=22,
            protocol='tcp',
            cidr_blocks=['0.0.0.0/0'],
        ),
    ],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol='-1',
        cidr_blocks=['0.0.0.0/0'],
    )],
    tags={
        'Name': 'allow ssh,http,https',
    }
)

# Security group for RDS:
rds_allow_rule = aws.ec2.SecurityGroup(
    'rds-allow-rule',
    vpc_id=prod_vpc.id,
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        description='MySQL',
        from_port=3306,
        to_port=3306,
        protocol='tcp',
        security_groups=[ec2_allow_rule.id],
    )],
    # allow all outbound traffic.
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol='-1',
        cidr_blocks=['0.0.0.0/0'],
    )],
    tags={
        'Name': 'allow ec2',
    }
)

# Place the RDS instance into private subnets:
rds_subnet_grp = aws.rds.SubnetGroup(
    'rds-subnet-grp',
    subnet_ids=[
        prod_subnet_private1.id,
        prod_subnet_private2.id,
    ]
)

# Create the RDS instance:
app_rds = aws.rds.Instance(
    'app-rds',
    allocated_storage=10,
    engine='mysql',
    engine_version='5.7',
    instance_class=db_instance_size,
    db_subnet_group_name=rds_subnet_grp.id,
    vpc_security_group_ids=[rds_allow_rule.id],
    db_name=db_name,
    username=db_username,
    password=db_password,
    skip_final_snapshot=True,
)

# Create a keypair to access the EC2 instance:
app_keypair = aws.ec2.KeyPair('app-keypair', public_key=public_key)

app_ec2_user_data = '''
#!/bin/bash
echo "Hello, World!" > index.html
nohup python -m SimpleHTTPServer 80 &
'''

# Create an EC2 instance to run app (after RDS is ready).
app_ec2 = aws.ec2.Instance(
    'app-instance',
    ami=ami.id,
    instance_type=ec2_instance_size,
    subnet_id=prod_subnet_public1.id,
    vpc_security_group_ids=[ec2_allow_rule.id],
    key_name=app_keypair.id,
    tags={
        'Name': 'app.web',
    },
    # Only create after RDS is provisioned.
    opts=pulumi.ResourceOptions(depends_on=[app_rds]),
    # Define what to do once created
    user_data=app_ec2_user_data,
    user_data_replace_on_change=True
)

# Give our EC2 instance an elastic IP address.
app_eip = aws.ec2.Eip('app-eip', instance=app_ec2.id)

pulumi.export('app-ec2-public-dns', app_ec2.public_dns)
pulumi.export('app-eip-public-dns', app_eip.public_dns)
pulumi.export('app-rds-address', app_rds.address)
