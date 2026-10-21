import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (on pages after cover/page 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "BCSE355L: Cloud Architecture Design — CloudShield Project Report")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "AWS Account: 206238482111 | Sydney (ap-southeast-2)")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_text)
        self.drawString(54, 32, "Confidential — Prepared for B.Tech Cloud Architecture Examination (BCSE355L v2.0)")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 44, letter[0] - 54, 44)
        
        self.restoreState()

def build_pdf(filename="BCSE355L_CloudShield_AWS_Architecture_Defense.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1A365D")    # Dark Navy
    c_secondary = colors.HexColor("#2B6CB0")  # Royal Blue
    c_accent = colors.HexColor("#C05621")     # Warm Amber/Orange
    c_dark = colors.HexColor("#2D3748")       # Body text dark
    c_light_bg = colors.HexColor("#F7FAFC")   # Light gray
    c_code_bg = colors.HexColor("#EDF2F7")    # Code block background
    c_border = colors.HexColor("#E2E8F0")     # Border color

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2C5282")
    )

    code_style = ParagraphStyle(
        'CodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#2D3748")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_dark
    )

    story = []

    # ==========================================
    # COVER / HEADER BANNER
    # ==========================================
    story.append(Paragraph("BCSE355L: Cloud Architecture Design", title_style))
    story.append(Paragraph("Final Project Comprehensive AWS Architecture & Engineering Defense Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_secondary, spaceBefore=0, spaceAfter=8))

    meta_table_data = [
        [
            Paragraph("<b>Project:</b> CloudShield (Predictive Disaster Logistics)", table_cell_style),
            Paragraph("<b>AWS Account ID:</b> 206238482111", table_cell_style)
        ],
        [
            Paragraph("<b>AWS Region:</b> ap-southeast-2 (Sydney)", table_cell_style),
            Paragraph("<b>Target Host:</b> http://32.236.173.240:8000", table_cell_style)
        ],
        [
            Paragraph("<b>Syllabus Version:</b> 2.0 (8 Specialized Modules)", table_cell_style),
            Paragraph("<b>Live Mode:</b> AWS_MODE=live (IMDSv2 Enforced)", table_cell_style)
        ],
        [
            Paragraph("<b>GitHub Repository:</b> https://github.com/NeeleshUnleashed/CloudShield", table_cell_style),
            Paragraph("<b>Status:</b> 100% Deployed & E2E Verified (12/12 Tests)", table_cell_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[260, 244])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # SECTION 1: EXECUTIVE SUMMARY & CURRICULUM MAPPING
    # ==========================================
    story.append(Paragraph("1. Executive Summary & Curriculum Alignment", h1_style))
    story.append(Paragraph(
        "This project was engineered to directly satisfy the requirements of <b>BCSE355L (Cloud Architecture Design)</b>. "
        "CloudShield is an autonomous, explainable disaster response resource allocation platform combining deterministic multi-criteria risk scoring (DPRI), "
        "Sphere Humanitarian Standards demand forecasting, and multi-depot optimization with a two-stage human-in-the-loop approval gate. "
        "The application is fully operational in the Sydney AWS region (<code>ap-southeast-2</code>) adhering strictly to the AWS Well-Architected Framework.",
        body_style
    ))

    # ==========================================
    # SECTION 2: MODULE-BY-MODULE AWS SERVICES BREAKDOWN
    # ==========================================
    story.append(Paragraph("2. Comprehensive AWS Services Breakdown (What, How & Why)", h1_style))
    story.append(Paragraph(
        "Each AWS service deployed in CloudShield directly corresponds to a specific unit of the BCSE355L syllabus:",
        body_style
    ))

    services_data = [
        [
            Paragraph("Syllabus Module", table_header_style),
            Paragraph("AWS Service Used", table_header_style),
            Paragraph("Implementation (HOW it is used)", table_header_style),
            Paragraph("Architectural Rationale (WHY needed)", table_header_style)
        ],
        [
            Paragraph("<b>Module 1</b><br/>Cloud Foundations & IAM", table_cell_style),
            Paragraph("<b>AWS IAM</b><br/>Role & Profile", table_cell_style),
            Paragraph("<code>CloudShieldEC2AppRole</code> attached via <code>CloudShieldEC2Profile</code>. Enforces least-privilege inline policy for SNS, S3, and CloudWatch. Uses IMDSv2 for ephemeral credential rotation.", table_cell_style),
            Paragraph("Eliminates static hardcoded API keys. Prevents credential leakage in GitHub/disk. Limits blast radius if the instance is compromised.", table_cell_style)
        ],
        [
            Paragraph("<b>Module 2</b><br/>Compute & Storage", table_cell_style),
            Paragraph("<b>Amazon EC2</b><br/>(Compute)", table_cell_style),
            Paragraph("<code>t3.micro</code> (2 vCPUs, 1GB RAM) running Amazon Linux 2023. Managed as a systemd background daemon (<code>cloudshield.service</code>) running FastAPI on port 8000.", table_cell_style),
            Paragraph("Eliminates cold-start latency for real-time disaster triage. In <code>ap-southeast-2</code>, <code>t3.micro</code> is Free Tier eligible (750 hrs/mo free) while t2.micro is not.", table_cell_style)
        ],
        [
            Paragraph("<b>Module 2</b><br/>Compute & Storage", table_cell_style),
            Paragraph("<b>Amazon EBS</b><br/>(Block Store)", table_cell_style),
            Paragraph("8 GB <code>gp3</code> General Purpose SSD root volume (/dev/xvda). Baseline 3,000 IOPS, 125 MB/s throughput. Hosts OS and active SQLite transactional database.", table_cell_style),
            Paragraph("Provides persistent, low-latency POSIX file locks necessary for ACID database transactions. Configured with <code>DeleteOnTermination: true</code> to avoid orphaned charges.", table_cell_style)
        ],
        [
            Paragraph("<b>Module 2</b><br/>Compute & Storage", table_cell_style),
            Paragraph("<b>Amazon S3</b><br/>(Object Store)", table_cell_style),
            Paragraph("<code>cloudshield-artifacts-206238482111-ap-southeast-2</code>. Stores automated atomic SQLite database snapshots. Enforces 7-day expiration lifecycle & Block Public Access.", table_cell_style),
            Paragraph("Guarantees 11 9's durability (99.999999999%) for disaster records. The 7-day lifecycle prevents backup accumulation and guarantees zero cost overages.", table_cell_style)
        ],
        [
            Paragraph("<b>Module 3</b><br/>Networking & Content Delivery", table_cell_style),
            Paragraph("<b>Amazon VPC & Security Groups</b>", table_cell_style),
            Paragraph("VPC <code>vpc-02a4493bff64cb2c9</code>, public subnet in <code>ap-southeast-2a</code>. Security group <code>cloudshield-app-sg</code> restricts TCP port 8000 exclusively to <code>182.66.218.113/32</code>.", table_cell_style),
            Paragraph("Hardware-level stateful perimeter filtering. Protects lightweight demo RBAC from public internet scrapers and bots. Avoided $32.85/mo NAT Gateway charge trap.", table_cell_style)
        ],
        [
            Paragraph("<b>Module 4</b><br/>Database Services", table_cell_style),
            Paragraph("<b>Database Architecture</b> (EBS/RDS/DynamoDB)", table_cell_style),
            Paragraph("Deployed with ACID SQLite on EBS + S3 sync. Documented migration path to <b>Amazon Aurora PostgreSQL Multi-AZ</b> and <b>Amazon DynamoDB</b>.", table_cell_style),
            Paragraph("SQLite eliminates $15+/mo RDS idle instance charges for college demo while guaranteeing full ACID serializability. Enterprise blueprint details Multi-AZ failover.", table_cell_style)
        ],
        [
            Paragraph("<b>Module 5</b><br/>Management & Cost Optimization", table_cell_style),
            Paragraph("<b>Amazon CloudWatch Logs</b>", table_cell_style),
            Paragraph("Log Group <code>/cloudshield/application</code> with streams <code>app-stdout</code> and <code>app-stderr</code> shipped by CloudWatch Agent. Enforces strict 1-day retention.", table_cell_style),
            Paragraph("Centralized forensic log streaming outside the host. 1-day retention guarantees log volume remains well beneath the 5 GB Free Tier monthly ceiling.", table_cell_style)
        ],
        [
            Paragraph("<b>Module 6</b><br/>Security & Compliance", table_cell_style),
            Paragraph("<b>Security & IMDSv2</b>", table_cell_style),
            Paragraph("Enforced <code>HttpTokens=required</code> and <code>HttpPutResponseHopLimit=2</code> on EC2. Implements the AWS Shared Responsibility Model.", table_cell_style),
            Paragraph("Neutralizes SSRF (Server-Side Request Forgery) attacks by requiring a session token header, preventing credential theft from internal metadata services.", table_cell_style)
        ],
        [
            Paragraph("<b>Module 7</b><br/>Application Integration", table_cell_style),
            Paragraph("<b>Amazon SNS</b><br/>(Pub/Sub)", table_cell_style),
            Paragraph("Standard topic <code>CloudShield-Disaster-Alerts</code>. Invoked via <code>boto3</code> client upon <code>LOGISTICS_DIRECTOR</code> disaster plan approval.", table_cell_style),
            Paragraph("Decoupled publish/subscribe architecture. Fans out critical disaster supply dispatches to field teams, hospitals, and email/SMS subscribers concurrently.", table_cell_style)
        ]
    ]

    svc_table = Table(services_data, colWidths=[85, 95, 165, 159])
    svc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(svc_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # SECTION 3: HOW AWS WORKS IN THE BACKEND (END-TO-END WORKFLOW)
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("3. How AWS Works in the Backend — End-to-End Execution Trace", h1_style))
    story.append(Paragraph(
        "When an incident is processed in CloudShield, data flows across 8 discrete cloud subsystems:",
        body_style
    ))

    workflow_steps = [
        ("Step 1: Network Ingress & Hardware Inspection",
         "The user connects to <code>http://32.236.173.240:8000</code>. The AWS edge router routes packets to <code>vpc-02a4493bff64cb2c9</code>. "
         "Security Group <code>cloudshield-app-sg</code> inspects the source IPv4. Packets from <code>182.66.218.113/32</code> pass; all others are dropped at the hypervisor level."),
        
        ("Step 2: EC2 Host & Systemd Daemon Supervision",
         "The Linux kernel delivers the stream to port 8000. Supervised by <code>cloudshield.service</code>, Uvicorn processes the request. "
         "If the application process encounters an unhandled exception, systemd restarts it in 5 seconds automatically."),
        
        ("Step 3: IMDSv2 Authentication Handshake",
         "When Python initializes <code>boto3.client('sns')</code>, it issues a <code>PUT</code> request to <code>169.254.169.254/latest/api/token</code> "
         "to fetch a cryptographic session token, and retrieves rotating temporary STS credentials for <code>CloudShieldEC2AppRole</code>. No static keys exist on disk."),
        
        ("Step 4: Deterministic DPRI & Humanitarian Demand Prediction",
         "The core engine calculates the Disaster Priority Risk Index: "
         "DPRI = [(Hazard * Multiplier) + (Vuln * 0.3) + ((1 - Coping) * 0.25) + (Infra * 0.2)] / 2.05. "
         "It estimates supply requirements for Water (15L/day), Food (1 pack/day), Medical, Shelter, and Power according to Sphere Standards."),
        
        ("Step 5: Two-Stage Human-in-the-Loop Approval Gate",
         "The incident is persisted with status <code>PENDING_APPROVAL</code>. <b>Zero depot inventory is deducted</b>. "
         "Only an authorized user with role <code>LOGISTICS_DIRECTOR</code> can approve the plan. Unauthorized roles receive <b>HTTP 403 Forbidden</b>."),
        
        ("Step 6: Atomic Database Transaction on EBS Volume",
         "Upon Director approval, an atomic SQLite transaction decrements regional stock (Sydney, Brisbane, Melbourne, Perth), "
         "records the dispatch manifest, and sets status to <code>APPROVED_DISPATCHED</code>. Duplicate approvals are rejected with <b>HTTP 400 Bad Request</b>."),
        
        ("Step 7: Real-Time Amazon SNS Event Broadcasting",
         "The approval service publishes an event payload to <code>arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts</code>. "
         "SNS broadcasts the message to subscribers, returning a unique MessageId stored in the audit history."),
        
        ("Step 8: CloudWatch Log Streaming & S3 Snapshot Backup",
         "The CloudWatch Agent tails <code>/var/log/cloudshield.log</code> and streams events to <code>/cloudshield/application</code>. "
         "Concurrently, an hourly cron job executes <code>sqlite3 .backup</code> and uploads database snapshots to S3.")
    ]

    for title, desc in workflow_steps:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, bullet_style))

    story.append(Spacer(1, 8))

    # ==========================================
    # SECTION 4: AWS WELL-ARCHITECTED FRAMEWORK ALIGNMENT
    # ==========================================
    story.append(Paragraph("4. AWS Well-Architected Framework (6 Pillars Defense)", h1_style))
    story.append(Paragraph(
        "Module 7 requires demonstration of the six pillars of the AWS Well-Architected Framework:",
        body_style
    ))

    waf_data = [
        [Paragraph("Pillar", table_header_style), Paragraph("CloudShield Implementation & Design Choice", table_header_style)],
        [Paragraph("<b>1. Operational Excellence</b>", table_cell_style), Paragraph("Infrastructure-as-Code via automated bash bootstrap; CloudWatch centralized logging; systemd automatic process recovery; S3 automated backups; /api/health probes.", table_cell_style)],
        [Paragraph("<b>2. Security</b>", table_cell_style), Paragraph("IMDSv2 session tokens; least-privilege IAM instance role; /32 restricted Security Group; S3 Block Public Access; zero secrets in source code; backend RBAC.", table_cell_style)],
        [Paragraph("<b>3. Reliability</b>", table_cell_style), Paragraph("Atomic ACID transactions on EBS; stateless API tier; S3 99.999999999% durability; automatic systemd restart within 5s; deterministic mathematical models.", table_cell_style)],
        [Paragraph("<b>4. Performance Efficiency</b>", table_cell_style), Paragraph("Python 3.11 asynchronous event loop; zero network database latency (local EBS); burstable T3 CPU architecture; low-latency in-memory prediction calculations.", table_cell_style)],
        [Paragraph("<b>5. Cost Optimization</b>", table_cell_style), Paragraph("Avoided $32.85/mo NAT Gateway; avoided $16.50/mo ALB; avoided $15/mo RDS; t3.micro Free Tier eligible in Sydney; 1-day CloudWatch retention; 7-day S3 lifecycle.", table_cell_style)],
        [Paragraph("<b>6. Sustainability</b>", table_cell_style), Paragraph("Right-sized micro instance; minimal package dependencies; idempotent single-command decommissioning scripts to eliminate idle cloud energy waste.", table_cell_style)]
    ]
    waf_table = Table(waf_data, colWidths=[120, 384])
    waf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(waf_table)

    # ==========================================
    # SECTION 5: PROFESSOR VIVA DEFENSE — TOP 6 EXAM QUESTIONS
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("5. College Viva Defense — High-Weightage Examination Q&A", h1_style))
    story.append(Paragraph(
        "Expected questions from the BCSE355L examination committee with exact model answers:",
        body_style
    ))

    viva_qa = [
        ("Q1: Why didn't you deploy an Application Load Balancer (ALB) or NAT Gateway?",
         "In AWS, an ALB costs ~$16.50/month and a NAT Gateway costs ~$32.85/month plus data processing fees. "
         "In BCSE355L Module 5 & 7, Cost Optimization is a core pillar. For a single-instance disaster intake node, "
         "routing traffic through a direct Internet Gateway with a stateful Security Group locked to our /32 CIDR "
         "provides identical security isolation while eliminating over $50/month in idle cloud expenditure."),
        
        ("Q2: How does IMDSv2 protect your EC2 instance compared to IMDSv1?",
         "IMDSv1 relied on unauthenticated HTTP GET requests to 169.254.169.254, making it vulnerable to Server-Side Request Forgery (SSRF) attacks. "
         "CloudShield explicitly configured HttpTokens=required (IMDSv2). This enforces session-oriented PUT requests with custom header tokens, "
         "preventing SSRF exploits and unauthorized extraction of temporary IAM instance credentials."),
        
        ("Q3: What is the architectural difference between your Security Group and a Network ACL?",
         "A Security Group is stateful and operates at the virtual network interface (ENI) level; allowing inbound traffic on port 8000 "
         "automatically permits the return response. A Network ACL (NACL) is stateless and operates at the subnet boundary, requiring explicit "
         "rules for both inbound traffic and ephemeral outbound ports (1024-65535). CloudShield utilizes Security Groups for fine-grained host protection."),
        
        ("Q4: Why did you choose t3.micro instead of t2.micro for the Sydney region?",
         "Querying the AWS CLI in ap-southeast-2 (aws ec2 describe-instance-types) reveals that t2.micro is NOT Free Tier eligible in Sydney, "
         "whereas t3.micro is explicitly Free Tier eligible (750 hours/month). Furthermore, T3 runs on the modern AWS Nitro System with 2 vCPUs "
         "and Enhanced Networking (ENA), providing significantly better burstable throughput than T2."),
        
        ("Q5: How does your S3 Lifecycle Policy prevent cloud billing overrun?",
         "Our EC2 instance captures hourly backups of the SQLite database. Over several months, unmanaged backups would exceed the 5 GB Free Tier limit. "
         "We deployed an S3 lifecycle configuration that permanently deletes backup objects after 7 days, maintaining steady-state storage under 100 MB."),
        
        ("Q6: How does CloudShield comply with the AWS Shared Responsibility Model?",
         "Under the Shared Responsibility Model (Module 1 & 6), AWS manages Security OF the Cloud (physical data centers in Sydney, Nitro chips, power, and hypervisors). "
         "We as the customer manage Security IN the Cloud: configuring least-privilege IAM policies, restricting Security Group ingress, patching the Amazon Linux OS, "
         "enforcing IMDSv2, and managing application-level RBAC authorization.")
    ]

    for q, a in viva_qa:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(f"<i>Model Answer:</i> {a}", bullet_style))
        story.append(Spacer(1, 2))

    # ==========================================
    # SECTION 6: LIVE DEPLOYMENT VERIFICATION & CLEANUP COMMANDS
    # ==========================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("6. Verified Post-Demo Cleanup Protocol", h1_style))
    story.append(Paragraph(
        "To decommission all AWS resources and return the account to $0.00 recurring charges after your presentation:",
        body_style
    ))

    cleanup_code = (
        "# 1. Terminate EC2 Instance & wait\n"
        "aws ec2 terminate-instances --instance-ids i-0f5a671d1b8a31d23 --region ap-southeast-2\n"
        "aws ec2 wait instance-terminated --instance-ids i-0f5a671d1b8a31d23 --region ap-southeast-2\n\n"
        "# 2. Delete Security Group\n"
        "aws ec2 delete-security-group --group-id sg-08249050614cb6db9 --region ap-southeast-2\n\n"
        "# 3. Empty & Delete S3 Bucket\n"
        "aws s3 rm s3://cloudshield-artifacts-206238482111-ap-southeast-2 --recursive --region ap-southeast-2\n"
        "aws s3api delete-bucket --bucket cloudshield-artifacts-206238482111-ap-southeast-2 --region ap-southeast-2\n\n"
        "# 4. Delete SNS Topic & CloudWatch Log Group\n"
        "aws sns delete-topic --topic-arn arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts --region ap-southeast-2\n"
        "aws logs delete-log-group --log-group-name /cloudshield/application --region ap-southeast-2\n\n"
        "# 5. Delete IAM Instance Profile & Role\n"
        "aws iam remove-role-from-instance-profile --instance-profile-name CloudShieldEC2Profile --role-name CloudShieldEC2AppRole\n"
        "aws iam delete-instance-profile --instance-profile-name CloudShieldEC2Profile\n"
        "aws iam delete-role-policy --role-name CloudShieldEC2AppRole --policy-name CloudShieldAppPolicy\n"
        "aws iam delete-role --role-name CloudShieldEC2AppRole"
    )
    cleanup_table = Table([[Paragraph(cleanup_code.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)]], colWidths=[504])
    cleanup_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(cleanup_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF built successfully: {filename}")

if __name__ == "__main__":
    build_pdf()
