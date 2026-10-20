# CloudShield: Live AWS Resource Inventory

> **ACCOUNT**: `206238482111`  
> **ASSUMED ROLE**: `AccountFullAccessRole`  
> **PRIMARY REGION**: `ap-southeast-2` (Sydney)  
> **LAST AUDITED**: Live Deployment Verification  
> **TOTAL LIVE CLOUD RESOURCES**: **6** (All active and operational)

---

## 1. CloudShield Component Inventory

| Component / Subsystem | AWS Service | Current State | Live Cloud Resource Name / ARN | Hourly Cost | Monthly Cost | Cost Approval Date |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Compute & Host** | EC2 (`t3.micro`) | **LIVE ACTIVE** | `i-0f5a671d1b8a31d23` (IP: `32.236.173.240`) | $0.00 *(Free Tier)* | $0.00 *(Free Tier)* | 2026-10-20 |
| **Public IPv4 Allocation**| EC2 IPv4 | **LIVE ACTIVE** | `32.236.173.240` | $0.005 | $3.60 | 2026-10-20 |
| **Firewall / Ingress** | Security Group | **LIVE ACTIVE** | `sg-08249050614cb6db9` (`cloudshield-app-sg`) | $0.00 | $0.00 | 2026-10-20 |
| **IAM Instance Role** | IAM Profile & Role | **LIVE ACTIVE** | `arn:aws:iam::206238482111:role/CloudShieldEC2AppRole` | $0.00 | $0.00 | 2026-10-20 |
| **Storage & Backups** | Amazon S3 | **LIVE ACTIVE** | `arn:aws:s3:::cloudshield-artifacts-206238482111-ap-southeast-2` | $0.00 *(Free Tier)* | <$0.01 | 2026-10-20 |
| **Emergency Alerts** | Amazon SNS | **LIVE ACTIVE** | `arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts` | $0.00 *(Free Tier)* | $0.00 | 2026-10-20 |
| **Logging & Audit** | CloudWatch Logs | **LIVE ACTIVE** | `arn:aws:logs:ap-southeast-2:206238482111:log-group:/cloudshield/application` | $0.00 *(Free Tier)* | $0.00 | 2026-10-20 |

---

## 2. Live Cloud Resource Tracking Table

| Service | Resource Name / ID | Exact ARN | Created Date | Approved Duration | Max Cost Cap | Teardown Command | Verification Command |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EC2** | `i-0f5a671d1b8a31d23` | `arn:aws:ec2:ap-southeast-2:206238482111:instance/i-0f5a671d1b8a31d23` | 2026-10-20 | Demo Session | $0.05 | `aws ec2 terminate-instances --instance-ids i-0f5a671d1b8a31d23 --region ap-southeast-2` | `aws ec2 describe-instances --instance-ids i-0f5a671d1b8a31d23 --region ap-southeast-2` |
| **Security Group** | `cloudshield-app-sg` | `arn:aws:ec2:ap-southeast-2:206238482111:security-group/sg-08249050614cb6db9` | 2026-10-20 | Demo Session | $0.00 | `aws ec2 delete-security-group --group-id sg-08249050614cb6db9 --region ap-southeast-2` | `aws ec2 describe-security-groups --group-ids sg-08249050614cb6db9 --region ap-southeast-2` |
| **S3** | `cloudshield-artifacts-206238482111-ap-southeast-2` | `arn:aws:s3:::cloudshield-artifacts-206238482111-ap-southeast-2` | 2026-10-20 | 7-day lifecycle | $0.01 | `aws s3 rm s3://cloudshield-artifacts-206238482111-ap-southeast-2 --recursive && aws s3api delete-bucket --bucket cloudshield-artifacts-206238482111-ap-southeast-2 --region ap-southeast-2` | `aws s3api head-bucket --bucket cloudshield-artifacts-206238482111-ap-southeast-2` |
| **SNS** | `CloudShield-Disaster-Alerts` | `arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts` | 2026-10-20 | Demo Session | $0.00 | `aws sns delete-topic --topic-arn arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts --region ap-southeast-2` | `aws sns get-topic-attributes --topic-arn arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts --region ap-southeast-2` |
| **CloudWatch** | `/cloudshield/application` | `arn:aws:logs:ap-southeast-2:206238482111:log-group:/cloudshield/application` | 2026-10-20 | 1-day retention | $0.00 | `aws logs delete-log-group --log-group-name /cloudshield/application --region ap-southeast-2` | `aws logs describe-log-groups --log-group-name-prefix /cloudshield/application --region ap-southeast-2` |
| **IAM Profile** | `CloudShieldEC2Profile` | `arn:aws:iam::206238482111:instance-profile/CloudShieldEC2Profile` | 2026-10-20 | Demo Session | $0.00 | `aws iam remove-role-from-instance-profile --instance-profile-name CloudShieldEC2Profile --role-name CloudShieldEC2AppRole && aws iam delete-instance-profile --instance-profile-name CloudShieldEC2Profile` | `aws iam get-instance-profile --instance-profile-name CloudShieldEC2Profile` |
| **IAM Role** | `CloudShieldEC2AppRole` | `arn:aws:iam::206238482111:role/CloudShieldEC2AppRole` | 2026-10-20 | Demo Session | $0.00 | `aws iam delete-role-policy --role-name CloudShieldEC2AppRole --policy-name CloudShieldAppPolicy && aws iam delete-role --role-name CloudShieldEC2AppRole` | `aws iam get-role --role-name CloudShieldEC2AppRole` |

---

## 3. Resource Change Audit Log

| Timestamp (UTC) | Event Type | Resource Type | Target ARN | Verification Result |
| :--- | :--- | :--- | :--- | :--- |
| 2026-10-20 17:41 | Create Role | IAM Role | `arn:aws:iam::206238482111:role/CloudShieldEC2AppRole` | Verified via `get-role` |
| 2026-10-20 17:51 | Create Profile | IAM Profile | `arn:aws:iam::206238482111:instance-profile/CloudShieldEC2Profile` | Role bound & verified |
| 2026-10-20 17:51 | Create Bucket | S3 Bucket | `arn:aws:s3:::cloudshield-artifacts-206238482111-ap-southeast-2` | Private + 7d lifecycle active |
| 2026-10-20 17:56 | Create Topic | SNS Topic | `arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts` | Active in `ap-southeast-2` |
| 2026-10-20 18:01 | Create LogGroup | CloudWatch | `arn:aws:logs:ap-southeast-2:206238482111:log-group:/cloudshield/application` | 1-day retention set |
| 2026-10-20 18:12 | Create SG | Security Group | `arn:aws:ec2:ap-southeast-2:206238482111:security-group/sg-08249050614cb6db9` | Port 8000 locked to `182.66.218.113/32` |
| 2026-10-20 18:40 | Launch Instance | EC2 (`t3.micro`) | `arn:aws:ec2:ap-southeast-2:206238482111:instance/i-0f5a671d1b8a31d23` | Running, Public IP: `32.236.173.240` |
| 2026-10-20 18:44 | E2E Verification | Automated Test | Full 12-step test suite (`tests/test_remote_ec2.py`) | 100% Passed (12/12 steps verified) |
