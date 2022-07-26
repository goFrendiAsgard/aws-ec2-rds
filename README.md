# Setup AWS CLI

Follow this [guide](https://www.pulumi.com/registry/packages/aws/installation-configuration/)

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

## Create Access Key

Follow this [guide](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)

TL;DR:

- Click the right top menu of your AWS console
- Choose `security credentials`
- Create access key
- Download/write down your access + secret key

## Configure AWS

Type `aws configure`, put the `access key` and `secret key` you've seen earlier.

# Create ssh key

```bash
ssh-keygen -f app-keypair
```

# Create EC2 + RDS instances

Follow this [guide](https://www.pulumi.com/blog/deploy-wordpress-aws-pulumi-ansible/)

Set configurations:

```bash
pulumi config set aws:region ap-southeast-1
pulumi config set publicKeyPath app-keypair.pub
pulumi config set privateKeyPath app-keypair
pulumi config set dbPassword Alch3mist --secret
```

Set passphrase (we don't use any):

```bash
mkdir -p ./pulumiLock
export PULUMI_BACKEND_URL="file://./pulumiLock"
export PULUMI_CONFIG_PASSPHRASE=
```

Create EC2 and RDS

```bash
# pulumi login --local
pulumi up
```

Show EC2 and RDS address

```bash
pulumi stack output
```

# Remote SSH to EC2

```bash
ssh -i app-keypair ubuntu@$(pulumi stack output app-eip-public-dns)
```

# Populate RDS

```bash
mysql -u admin -pAlch3mist --host <app-rds-address>
# Paste from ./sql
```

# Architecture

![](images/architecture.png)

# Demo

[video](https://drive.google.com/file/d/1dw-1pw-_yW8-UtbfgXF7HeSb59aONnxx/view?usp=sharing)

# References

[Glue tutorial](https://aws.amazon.com/blogs/big-data/data-preparation-using-an-amazon-rds-for-mysql-database-with-aws-glue-databrew/)

[Athena troubleshooting: insufficient permission](https://docs.aws.amazon.com/quicksight/latest/user/troubleshoot-athena-insufficient-permissions.html)