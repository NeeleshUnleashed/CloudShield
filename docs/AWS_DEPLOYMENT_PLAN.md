# CloudShield: AWS Pre-Deployment Execution Plan & Cost Guardrails

> **STATUS**: PRE-DEPLOYMENT SPECIFICATION (LOCAL GATES PASSED)  
> **POLICY**: ZERO RESOURCES CREATED WITHOUT EXPLICIT APPROVAL  
> **ACCOUNT**: `206238482111`  
> **TARGET REGION**: `ap-southeast-2` (Sydney)  
> **CURRENT MODE**: `AWS_MODE=mock` (Zero Charges Incurred)

---

## 1. Pre-Deployment Verification Status

Before any live AWS resource provisioning can be proposed, all local verification gates must be satisfied:

| Local Verification Gate | Target Requirement | Status | Evidence |
| :--- | :--- | :---: | :--- |
| **Local Automated Tests** | 100% passing test suite | **PASSED** | 33 passed in 1.48s (`python -m pytest -v`) |
| **Workflow Pipeline** | Intake → DPRI → Demand → Shortage → Proposal → Director Approval → Dispatch | **PASSED** | Verified via live test runner |
| **Zero Inventory Bleed** | Proposals and rejections never deduct inventory | **PASSED** | Verified via `test_approval_and_rbac.py` |
| **RBAC Security Boundaries** | Unauthorized operations blocked with HTTP 403 | **PASSED** | 403 Forbidden verified for all role violations |
| **Zero Secrets Policy** | No credentials or access keys committed | **PASSED** | Scanned workspace: 0 exposed secrets |
| **Cost Gate Verification** | Banned charge traps avoided (NAT GW, Public IPv4, ALB) | **PASSED** | Documented in `docs/AWS_COST_SAFETY.md` |

---

## 2. Step-by-Step Pre-Deployment Plan (Only When Approved)

> [!IMPORTANT]
> The following steps are documented for pre-deployment planning and academic defense. **DO NOT execute these commands without explicit written user authorization.**

### Stage 1: IAM Least-Privilege Execution Role
Create the IAM execution role and policy without storing credentials on instances:
```powershell
# 1. Create IAM Role with EC2 trust relationship
aws iam create-role --role-name CloudShieldEC2AppRole --assume-role-policy-document file://deployment/aws/trust_policy.json

# 2. Attach least-privilege policy (S3, SNS, CloudWatch Logs)
aws iam put-role-policy --role-name CloudShieldEC2AppRole --policy-name CloudShieldAppPolicy --policy-document file://deployment/aws/app_policy.json

# 3. Create instance profile
aws iam create-instance-profile --instance-profile-name CloudShieldEC2Profile
aws iam add-role-to-instance-profile --instance-profile-name CloudShieldEC2Profile --role-name CloudShieldEC2AppRole
```

### Stage 2: Networking & Security Groups (Zero NAT Gateway Design)
```powershell
# 1. Create VPC
$VPC_ID = (aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query "Vpc.VpcId" --output text)

# 2. Create Internet Gateway & attach
$IGW_ID = (aws ec2 create-internet-gateway --query "InternetGateway.InternetGatewayId" --output text)
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# 3. Create Public Subnet for EC2 (ap-southeast-2a)
$PUB_SUBNET = (aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ap-southeast-2a --query "Subnet.SubnetId" --output text)

# 4. Create Security Groups
$SG_APP = (aws ec2 create-security-group --group-name sg-cloudshield-app --description "CloudShield App SG" --vpc-id $VPC_ID --query "GroupId" --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_APP --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_APP --protocol tcp --port 443 --cidr 0.0.0.0/0
```

### Stage 3: Amazon SNS Topic & Subscriptions
```powershell
# Create standard topic for disaster alerts (Free tier: 1M publishes free)
$TOPIC_ARN = (aws sns create-topic --name CloudShield-Disaster-Alerts --query "TopicArn" --output text)

# Subscribe email endpoint (Requires manual confirmation link click)
aws sns subscribe --topic-arn $TOPIC_ARN --protocol email --notification-endpoint "officer@example.com"
```

### Stage 4: Amazon S3 Artifact Bucket with Lifecycle Expiration
```powershell
# Create private S3 bucket
aws s3api create-bucket --bucket cloudshield-artifacts-206238482111-ap-southeast-2 --create-bucket-configuration LocationConstraint=ap-southeast-2

# Enable 7-day expiration lifecycle rule to prevent storage charges
aws s3api put-bucket-lifecycle-configuration --bucket cloudshield-artifacts-206238482111-ap-southeast-2 --lifecycle-configuration file://deployment/aws/s3_lifecycle.json
```

### Stage 5: Amazon CloudWatch Log Group
```powershell
# Create log group
aws logs create-log-group --log-group-name /cloudshield/application

# Set 1-day retention limit (STRICT Free Tier guardrail)
aws logs put-retention-policy --log-group-name /cloudshield/application --retention-in-days 1
```

### Stage 6: EC2 Instance Launch (Free Tier t4g.micro / t2.micro)
```powershell
aws ec2 run-instances `
    --image-id ami-04f77a83fa42a3e5d `
    --instance-type t4g.micro `
    --iam-instance-profile Name=CloudShieldEC2Profile `
    --security-group-ids $SG_APP `
    --subnet-id $PUB_SUBNET `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Project,Value=CloudShield},{Key=Environment,Value=Test}]"
```

---

## 3. Teardown & Immediate Decommissioning Protocol

To guarantee zero residual charges after testing, execute this teardown sequence:

```powershell
# 1. Terminate EC2 instance
aws ec2 terminate-instances --instance-ids <INSTANCE_ID>

# 2. Delete SNS topic
aws sns delete-topic --topic-arn $TOPIC_ARN

# 3. Empty and delete S3 bucket
aws s3 rm s3://cloudshield-artifacts-206238482111-ap-southeast-2 --recursive
aws s3api delete-bucket --bucket cloudshield-artifacts-206238482111-ap-southeast-2

# 4. Delete CloudWatch Log Group
aws logs delete-log-group --log-group-name /cloudshield/application

# 5. Delete Security Groups & VPC
aws ec2 delete-security-group --group-id $SG_APP
aws ec2 detach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID
aws ec2 delete-subnet --subnet-id $PUB_SUBNET
aws ec2 delete-vpc --vpc-id $VPC_ID
```

---

## 4. Free Tier Monthly Cost Projection

| Service | Allocated Capacity | Free Tier Limit | Expected Monthly Cost |
| :--- | :--- | :--- | :---: |
| **EC2 (`t4g.micro`)** | 1 instance (750 hours) | 750 hours/month free | **$0.00** |
| **RDS (`db.t4g.micro`)** | 1 single-AZ (750 hours, 20GB) | 750 hours/month free | **$0.00** |
| **S3 Storage** | < 100 MB | 5 GB standard free | **$0.00** |
| **SNS Alerts** | < 500 publishes | 1,000,000 requests free | **$0.00** |
| **CloudWatch Logs** | < 50 MB (1-day retention) | 5 GB ingestion free | **$0.00** |
| **VPC & Data Egress** | Direct internet gateway | 100 GB egress free | **$0.00** |
| **TOTAL** | — | — | **$0.00 / month** |
