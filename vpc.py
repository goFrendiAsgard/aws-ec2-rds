import pulumi_aws as aws

# Dynamically fetch AZs so we can spread across them.
availability_zones = aws.get_availability_zones()

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
    map_public_ip_on_launch=True, # False for private subnet
    availability_zone=availability_zones.names[0]
)

# Create public subnets for the EC2 instance.
prod_subnet_public2 = aws.ec2.Subnet(
    'prod-subnet-public-2',
    vpc_id=prod_vpc.id,
    cidr_block='10.192.1.0/24',
    map_public_ip_on_launch=True, # False for private subnet
    availability_zone=availability_zones.names[1]
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
prod_rta_public_subnet2 = aws.ec2.RouteTableAssociation(
    'prod-rta-public-subnet-2',
    subnet_id=prod_subnet_public2.id,
    route_table_id=prod_public_rt.id
)


# Security group for glue:
all_allow_rule = aws.ec2.SecurityGroup(
    'all-allow-rule',
    vpc_id=prod_vpc.id,
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        from_port=0,
        to_port=0,
        protocol='-1',
        cidr_blocks=['0.0.0.0/0'],
    )],
    # allow all outbound traffic.
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol='-1',
        cidr_blocks=['0.0.0.0/0'],
    )],
    tags={
        'Name': 'all-allowed-rule',
    }
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
        'Name': 'ec2-allow-rule',
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
        security_groups=[ec2_allow_rule.id, all_allow_rule.id],
    )],
    # allow all outbound traffic.
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol='-1',
        cidr_blocks=['0.0.0.0/0'],
    )],
    tags={
        'Name': 'rds-allow-rule',
    }
)

# Place the RDS instance into private subnets:
rds_subnet_grp = aws.rds.SubnetGroup(
    'rds-subnet-grp',
    subnet_ids=[
        prod_subnet_public1.id,
        prod_subnet_public2.id
        # prod_subnet_private1.id,
        # prod_subnet_private2.id,
    ]
)

# You need this so that your VPC can access s3
s3_vpc_endpoint = aws.ec2.VpcEndpoint(
    "s3-vpc-endpoint",
    vpc_id=prod_vpc.id,
    vpc_endpoint_type='Gateway',
    service_name="com.amazonaws.ap-southeast-1.s3",
    route_table_ids=[prod_public_rt.id],
    tags={
        'Name': 's3-endpoint',
    }
)

# You need this so that your VPC can access glue
glue_vpc_endpoint = aws.ec2.VpcEndpoint(
    "glue-vpc-endpoint",
    vpc_id=prod_vpc.id,
    vpc_endpoint_type='Interface',
    service_name='com.amazonaws.ap-southeast-1.glue',
    subnet_ids=[prod_subnet_public1.id, prod_subnet_public2.id],
    security_group_ids=[ec2_allow_rule.id, rds_allow_rule.id],
    private_dns_enabled=True,
    tags={
        'Name': 'glue-endpoint',
    }
)