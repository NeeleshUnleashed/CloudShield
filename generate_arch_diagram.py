import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Publication-grade system architecture diagram
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

# Palette
c_ingest = '#DBEAFE' # Blue light
c_engine = '#FEF3C7' # Amber light
c_state  = '#FEE2E2' # Red light
c_cloud  = '#DCFCE7' # Green light
c_border = '#1E293B'

# Boxes
# Layer 1: Ingestion
b1 = patches.FancyBboxPatch((0.5, 4.2), 2.2, 1.4, boxstyle="round,pad=0.1", fc=c_ingest, ec=c_border, lw=1.2)
ax.add_patch(b1)
ax.text(1.6, 5.2, "1. INGESTION TIER", ha='center', va='center', fontsize=9, fontweight='bold', color='#1E3A8A')
ax.text(1.6, 4.7, "• Flood Depth (m)\n• Isolation Index (%)\n• Displaced Population\n• Vulnerability Ratio", ha='center', va='center', fontsize=7.5, color='#1F2937')

# Layer 2: Decision & Prediction
b2 = patches.FancyBboxPatch((3.8, 4.2), 2.4, 1.4, boxstyle="round,pad=0.1", fc=c_engine, ec=c_border, lw=1.2)
ax.add_patch(b2)
ax.text(5.0, 5.2, "2. ANALYTICAL ENGINES", ha='center', va='center', fontsize=9, fontweight='bold', color='#B45309')
ax.text(5.0, 4.7, "• DPRI Urgency Evaluator\n• Sphere Demand Forecaster\n• Multi-Depot Knapsack\n• Distance Decay Penalty", ha='center', va='center', fontsize=7.5, color='#1F2937')

# Layer 3: Governance State Machine
b3 = patches.FancyBboxPatch((7.3, 4.2), 2.2, 1.4, boxstyle="round,pad=0.1", fc=c_state, ec=c_border, lw=1.2)
ax.add_patch(b3)
ax.text(8.4, 5.2, "3. GOVERNANCE GATE", ha='center', va='center', fontsize=9, fontweight='bold', color='#B91C1C')
ax.text(8.4, 4.7, "• PENDING_APPROVAL\n• Zero Stock Deduction\n• Director Action ID\n• Idempotency Check", ha='center', va='center', fontsize=7.5, color='#1F2937')

# Layer 4: AWS Infrastructure Tier (Bottom)
b4 = patches.FancyBboxPatch((0.5, 0.6), 9.0, 2.8, boxstyle="round,pad=0.15", fc=c_cloud, ec=c_border, lw=1.5)
ax.add_patch(b4)
ax.text(5.0, 3.1, "4. PRODUCTION AWS INFRASTRUCTURE (Sydney: ap-southeast-2)", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#15803D')

# Sub-services inside AWS
services = [
    ("Amazon EC2\n(t3.micro, AL2023)\nFastAPI + Uvicorn ASGI\nsystemd daemonized", 1.5, 1.8),
    ("Amazon EBS\n(8GB gp3 SSD)\nPersistent SQLite WAL\nACID crash durability", 3.8, 1.8),
    ("Amazon S3\n(Private Bucket)\nHourly hot backup (.db)\n7-Day Lifecycle Rule", 6.2, 1.8),
    ("Amazon SNS & CloudWatch\nAlert Fanout (DPRI ≥ 0.75)\nUnified stdout/stderr\nIMDSv2 Least-Privilege IAM", 8.4, 1.8),
]

for title, sx, sy in services:
    s_box = patches.FancyBboxPatch((sx - 0.95, sy - 0.8), 1.9, 1.6, boxstyle="round,pad=0.08", fc='white', ec='#15803D', lw=1)
    ax.add_patch(s_box)
    ax.text(sx, sy, title, ha='center', va='center', fontsize=7.5, color='#1F2937')

# Arrows
arrowprops = dict(facecolor='#0F2B5C', edgecolor='#0F2B5C', width=1.5, headwidth=6, shrink=0.08)
ax.annotate('', xy=(3.8, 4.9), xytext=(2.7, 4.9), arrowprops=arrowprops)
ax.annotate('', xy=(7.3, 4.9), xytext=(6.2, 4.9), arrowprops=arrowprops)
ax.annotate('', xy=(8.4, 3.4), xytext=(8.4, 4.2), arrowprops=dict(facecolor='#B91C1C', edgecolor='#B91C1C', width=1.5, headwidth=6, shrink=0.08))
ax.annotate('', xy=(1.6, 3.4), xytext=(1.6, 4.2), arrowprops=dict(facecolor='#1E3A8A', edgecolor='#1E3A8A', width=1.5, headwidth=6, shrink=0.08))

plt.tight_layout()
out_path = r'e:\cloud\docs\screenshots\graph_8_system_architecture.png'
plt.savefig(out_path, dpi=300)
plt.close()
print('Generated:', out_path)
