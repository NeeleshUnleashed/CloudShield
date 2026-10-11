# CloudShield: Autonomous Disaster Response & Supply Optimization

> **OPERATING MODE**: `AWS_MODE=mock` (Strict Zero-Charge Local Mode)  
> **AWS ACCOUNT**: `206238482111` (assumed-role/AccountFullAccessRole)  
> **STATUS**: Complete, Tested & Demonstrable End-to-End

---

## 1. Quickstart — Running the Application Locally

### Step 1: Run All Automated Tests
Verify all 28 automated test checkpoints across DPRI, Demand Prediction, Inventory, Allocation, Human-in-the-Loop Approval, Demo RBAC, and Multi-Region Prioritization:
```powershell
python -m pytest -v
```

### Step 2: Start the Local Dashboard Server
Launch the local FastAPI server:
```powershell
python run_server.py
```

### Step 3: Open in Browser
- 🖥️ **Interactive Dashboard UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📖 **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 🩺 **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 2. Human-in-the-Loop Approval Pipeline & Demo RBAC

CloudShield enforces an explicit two-stage authorization gate to ensure zero unauthorized inventory dispatches:

```
[1. Incident Ingestion] ── Submitted by EMERGENCY_OFFICER
          │
          ▼
[2. DPRI & Demand Prediction] ── Calibrated Sphere Humanitarian Model
          │
          ▼
[3. Allocation Recommendation] ── Multi-Depot Greedy Optimization
          │
          ▼
[4. Proposal State: PENDING_APPROVAL] ── Zero Inventory Deducted • Zero Dispatches Sent
          │
          ├── (Reject) ──► Status: REJECTED (Zero Stock Deducted)
          ▼ (Approve)
[5. Director Authorization Gate] ── Authorized by LOGISTICS_DIRECTOR (RBAC Enforced)
          │
          ├──► [6. Atomic Inventory Decrement] ── SQLite Transactional Commit
          └──► [7. Simulated SNS Broadcast] ── CloudWatch & SNS Audit Event
```

### Demo RBAC Permissions Matrix:
- `EMERGENCY_OFFICER`: Ingests disaster parameters, calculates DPRI, creates proposals (`PENDING_APPROVAL`).
- `LOGISTICS_DIRECTOR`: Reviews proposals, authorizes inventory deduction, or rejects proposals.
- `AUDITOR`: Read-only observer across incidents, inventory matrices, and persistent audit logs (Write attempts rejected with 403 Forbidden).

> **Academic Note**: Demo role selection is designed for presentation and evaluation; it is not a production-grade cryptographic identity provider.

---

## 3. AWS Services: Simulated vs. Integrated Breakdown

To guarantee **\$0.00 unexpected charges** on Free Tier, CloudShield explicitly isolates live AWS calls:

| AWS Service | Operating Status | Implementation Mechanism | Cloud Charges Incurred |
| :--- | :--- | :--- | :---: |
| **AWS CLI / STS** | **Genuinely Integrated** | Read-only identity verification (`aws sts get-caller-identity`) | **$0.00** |
| **Amazon SNS** | **Simulated (Mock Mode)** | In-memory & SQLite event broadcaster (`app/core/notification_engine.py`) | **$0.00** |
| **Amazon DynamoDB / RDS** | **Simulated (Mock Mode)** | Local SQLite ACID transactional database (`data/cloudshield.db`) | **$0.00** |
| **Amazon S3** | **Simulated (Mock Mode)** | Local filesystem storage repository (`data/local_storage/s3/`) | **$0.00** |
| **AWS Lambda & API Gateway** | **Simulated (Mock Mode)** | Local high-performance FastAPI server (`app/main.py`) | **$0.00** |
| **Amazon CloudWatch** | **Simulated (Mock Mode)** | Structured local log streams (`logs/sns_simulated_alerts.log`) | **$0.00** |
| **Amazon VPC & NAT Gateway** | **Architecture Blueprint** | Documented zero-charge VPC design; **Zero NAT Gateways created** | **$0.00** |

---

## 4. Project Documentation Structure

- 📋 **[Testing Checkpoints Ledger](TESTING_CHECKPOINTS.md)**: Real executed test commands, timestamps, and captured outputs.
- 🎓 **[Viva & Defense Guide](docs/VIVA_PREPARATION.md)**: Comprehensive Q&A covering DPRI mathematics, algorithm choices, and system design.
- ☁️ **[Target AWS Architecture Spec](deployment/aws/ARCHITECTURE_SPEC.md)**: IAM roles, VPC subnets, Security Groups, Lambda, DynamoDB/RDS, S3, SNS, and CloudWatch mapping.
- 🔒 **[AWS Cost Safety Policy](docs/AWS_COST_SAFETY.md)**: Zero unexpected charges policy, banned resource list (NAT Gateways, Public IPv4, ALBs).
- 💰 **[Deployment Cost Estimate](deployment/aws/DEPLOYMENT_COST_ESTIMATE.md)**: $0.00 local vs. Free-Tier cloud cost models.
- 📦 **[Live Resource Inventory](deployment/aws/RESOURCE_INVENTORY.md)**: AWS account resource tracking (0 live resources provisioned).
- 🗺️ **[Revised 3–4 Day Roadmap](docs/ARCHITECTURE_AND_ROADMAP.md)**: Milestone breakdown and delivery timeline.

---

## 4. Key Architectural Safeguards

1. **Strict Mock Mode (`AWS_MODE=mock`)**: Drop-in SQLite and file-based adapters ensure zero mutating network requests are sent to AWS.
2. **Zero Live Charges Incurred**: Current AWS expenditure is **$0.00**.
3. **No External Microservice Overhead**: Self-contained, production-clean implementation utilizing installed dependencies (`FastAPI`, `Pydantic`, `SQLite3`, `NumPy`, `Scikit-learn`).
