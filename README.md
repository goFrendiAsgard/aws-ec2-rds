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

```bash
pulumi config set aws:region us-east-1
pulumi config set publicKeyPath app-keypair.pub
pulumi config set privateKeyPath app-keypair
pulumi config set dbPassword Alch3mist --secret
```

```bash
pulumi login --local
pulumi up
```

# Remote SSH to EC2

```bash
ssh -i app-keypair ec2-user@18.143.39.223
```
