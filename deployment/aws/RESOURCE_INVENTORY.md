# CloudShield: Live AWS Resource Inventory

> **ACCOUNT**: `206238482111`  
> **ASSUMED ROLE**: `AccountFullAccessRole`  
> **PRIMARY REGION**: `ap-southeast-2`  
> **LAST AUDITED**: Phase 0 Baseline  
> **TOTAL LIVE CLOUD RESOURCES**: **0** (All components running locally via mock adapters)

---

## 1. CloudShield Component Inventory

| Component / Subsystem | Intended AWS Service | Current State | Live Cloud Resource Name / ARN | Hourly Cost | Monthly Cost | Cost Approval Date |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Frontend UI** | S3 / CloudFront | **LOCAL MOCK** | None (Local SPA / FastAPI Static) | $0.00 | $0.00 | N/A (Mocked) |
| **Backend REST API** | Lambda + API Gateway | **LOCAL MOCK** | None (Local FastAPI Server) | $0.00 | $0.00 | N/A (Mocked) |
| **Prediction Engine** | Lambda / SageMaker Serverless | **LOCAL MOCK** | None (Local Scikit-learn / XGBoost) | $0.00 | $0.00 | N/A (Mocked) |
| **DPRI Calculator** | Lambda / Step Functions | **LOCAL MOCK** | None (Local Python Engine) | $0.00 | $0.00 | N/A (Mocked) |
| **Inventory Store** | DynamoDB | **LOCAL MOCK** | None (Local SQLite / JSON adapter) | $0.00 | $0.00 | N/A (Mocked) |
| **Event Pipeline** | SQS / EventBridge | **LOCAL MOCK** | None (In-memory Python Queue) | $0.00 | $0.00 | N/A (Mocked) |
| **System Logging** | CloudWatch Logs | **LOCAL MOCK** | None (Local File Logger in `logs/`) | $0.00 | $0.00 | N/A (Mocked) |

---

## 2. Live Cloud Resource Tracking Table

This table is maintained strictly before and after any approved cloud deployment:

| Service | Resource Name / ID | Exact ARN | Created Date | Approved Duration | Max Cost Cap | Teardown Command | Verification Command |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| *(None)* | *(None)* | *(None)* | *(None)* | *(None)* | *(None)* | *(None)* | *(None)* |

---

## 3. Read-Only Verification Audit Commands

To verify that zero resources exist in the account without mutating anything, run these read-only inspection commands:

```powershell
# 1. Check for any EC2 instances
aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]" --output table

# 2. Check for any S3 buckets associated with CloudShield
aws s3 ls

# 3. Check for any DynamoDB tables
aws dynamodb list-tables --output table

# 4. Check for any Lambda functions
aws lambda list-functions --query "Functions[*].[FunctionName,Runtime]" --output table

# 5. Check for any CloudFormation stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query "StackSummaries[*].[StackName,StackStatus]" --output table
```

---

## 4. Resource Change Audit Log

| Timestamp | Event Type | Resource Type | Target ARN | Approved By | Verification Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-10-11 | Phase 0 Baseline | System Audit | N/A | System Initialization | 0 live resources verified |
