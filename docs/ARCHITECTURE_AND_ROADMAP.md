# CloudShield: Revised 3–4 Day Accelerated Architecture & Roadmap

> **DEADLINE**: 3–4 Days  
> **OPERATING PRINCIPLE**: Working end-to-end demo first, reliable simple architecture, zero AWS charges (`AWS_MODE=mock`).

---

## 1. 3–4 Day Milestone Breakdown

| Milestone | Target Timeline | Focus Area | Status |
| :--- | :--- | :--- | :--- |
| **Milestone 1** | **Day 1 (Immediate)** | **Core Workflow Backend & Automated Tests**<br>• DPRI Calculation Engine<br>• Resource Demand Predictor<br>• Shortage Calculator & Allocation Optimizer<br>• Local SQLite Database & Seed Inventory<br>• Simulated SNS Alert Dispatcher<br>• Full Automated Test Suite & Checkpoint Verification | **IN PROGRESS** |
| **Milestone 2** | **Day 2** | **FastAPI Endpoints & Integration**<br>• REST API routes for disaster intake, DPRI, inventory, and allocation<br>• End-to-end integration tests (`disaster → DPRI → demand → shortage → allocation → alert → inventory`)<br>• Swagger / OpenAPI validation | Planned |
| **Milestone 3** | **Day 3** | **Interactive Frontend Dashboard**<br>• Disaster simulation control panel<br>• Live DPRI gauge & risk breakdown<br>• Real-time warehouse inventory table<br>• Allocation recommendation visualizer & dispatch execution button<br>• Live SNS alert feed | Planned |
| **Milestone 4** | **Day 4** | **Documentation, Viva Prep & AWS Integration Blueprint**<br>• Complete Viva & defense guide (`docs/VIVA_PREPARATION.md`)<br>• Target AWS Cloud Architecture specification (IAM, EC2, S3, RDS, SNS, CloudWatch, VPC)<br>• Setup & run instructions for non-technical evaluation | Planned |

---

## 2. The Core 7-Step Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Disaster Officer
    participant API as FastAPI Backend
    participant DPRI as DPRI Engine
    participant ML as Demand Prediction Engine
    participant Inv as SQLite Inventory Store
    participant Alloc as Allocation Optimizer
    participant SNS as Simulated SNS Service

    User->>API: 1. Submit Disaster Report (Type, Severity, Pop, Region)
    API->>DPRI: 2. Compute DPRI (Hazard x Vuln / Capacity)
    DPRI-->>API: DPRI Score (0.0 - 1.0) & Risk Level
    API->>ML: 3. Predict Resource Demands (Water, Food, Medical, Shelter, Power)
    ML-->>API: Predicted Units Required
    API->>Inv: 4. Check Current Regional Stock Levels
    Inv-->>API: Available Inventory
    API->>Alloc: 5. Calculate Shortages & Optimal Depot Allocation
    Alloc-->>API: Dispatch Recommendations
    API->>SNS: 6. Publish Dispatch Alert & Deficiency Notice (Simulated SNS)
    SNS-->>API: Alert Confirmed (MessageID)
    API->>Inv: 7. Commit Stock Allocations (Deplete Dispatched Stock)
    Inv-->>API: Updated Inventory Levels
    API-->>User: Complete Incident Summary & Allocation Manifest
```

---

## 3. Scope Controls for Deadline Protection

To guarantee delivery within 3–4 days:
1. **No External Microservices**: Single unified Python service serving both the REST API and the Frontend.
2. **Standard Installed Libraries**: Pydantic, FastAPI, SQLite3, NumPy, Pandas, Scikit-learn.
3. **Local Storage / SQLite**: In-memory and local SQLite database for instant zero-config launch.
4. **Local Mock AWS Adapters**: S3 (local file system), DynamoDB/RDS (SQLite), SNS (in-memory logger and event dispatcher).
5. **Zero Paid Cloud Deployments**: All cloud interactions remain in mock mode.
