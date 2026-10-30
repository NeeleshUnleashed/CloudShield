"""
Reference-Style Master Report Generator for CloudShield
Builds: CloudShield_Complete_Project_Report.pdf
Conforms strictly to the layout, font, color, and design of the uploaded reference PDF:
- Page 1: Official VIT Header Image, School/Dept/Course, Project Title, Submitted By, Faculty Guide, Fall 2026-27
- Page 2: Declaration with Digital Signature
- Page 3: Table of Contents (3-Column Table: S. No. | Contents | Page No.)
- Page 4: Abstract
- Chapters 1 to 12: Centered Chapter Headings (All Caps, 14 pt Bold Black), Left-Aligned Subheadings (12.5 pt Bold Black)
- Pure academic monochrome color scheme: Black text, light grey table headers (#E5E7EB), thin black borders
- Centered page numbers at the bottom of EVERY page (no top running headers, no footer lines)
- Total Pages: Exactly 40 pages
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, Preformatted
)
from reportlab.pdfgen import canvas

sys.path.append('e:/cloud')
from build_complete_report_original import build_story as get_raw_story

section_page_registry = {}

class HeadingWithMarker(Paragraph):
    def __init__(self, text, style, key):
        super().__init__(text, style)
        self.key = key

    def draw(self):
        section_page_registry[self.key] = self.canv._pageNumber
        super().draw()


class ReferenceNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas matching reference PDF:
    - NO running header, clean top margin.
    - Centered page number at the bottom of EVERY page.
    """
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
            self.draw_page_decorations()
            super().showPage()
        super().save()

    def draw_page_decorations(self):
        self.saveState()
        self.setFont("Times-Roman", 11)
        self.setFillColor(colors.black)
        # Centered page number at bottom of every page
        self.drawCentredString(306, 36, str(self._pageNumber))
        self.restoreState()


def build_story(toc_data=None):
    story = []

    # Typography styles matching reference PDF exactly:
    # Times New Roman throughout, pure black text (#000000)
    style_body = ParagraphStyle(
        'FormalBody',
        fontName='Times-Roman',
        fontSize=12,
        leading=16,
        textColor=colors.black,
        spaceAfter=6,
        alignment=4 # Justified
    )

    style_body_bold = ParagraphStyle(
        'FormalBodyBold',
        fontName='Times-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.black,
        spaceAfter=4,
        alignment=4
    )

    style_chapter_heading = ParagraphStyle(
        'ChapterHeading',
        fontName='Times-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.black,
        spaceBefore=14,
        spaceAfter=14,
        alignment=1, # Centered, ALL CAPS
        keepWithNext=True
    )

    style_section_heading = ParagraphStyle(
        'SectionHeading',
        fontName='Times-Bold',
        fontSize=12.5,
        leading=16.5,
        textColor=colors.black,
        spaceBefore=10,
        spaceAfter=4,
        alignment=0, # Left-aligned
        keepWithNext=True
    )

    style_bullet = ParagraphStyle(
        'FormalBullet',
        fontName='Times-Roman',
        fontSize=12,
        leading=16,
        textColor=colors.black,
        leftIndent=18,
        firstLineIndent=-12,
        spaceAfter=4,
        alignment=4
    )

    style_fig_caption = ParagraphStyle(
        'FigCaption',
        fontName='Times-Roman',
        fontSize=10.5,
        leading=14.5,
        textColor=colors.black,
        alignment=1, # Centered
        spaceBefore=4,
        spaceAfter=8
    )

    style_table_title = ParagraphStyle(
        'TableTitle',
        fontName='Times-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.black,
        alignment=0, # Left-aligned
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    style_toc_head = ParagraphStyle(
        'TOCHead',
        fontName='Times-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=0
    )

    style_toc_head_center = ParagraphStyle(
        'TOCHeadCenter',
        fontName='Times-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=1
    )

    style_toc_body = ParagraphStyle(
        'TOCBody',
        fontName='Times-Roman',
        fontSize=8.2,
        leading=10.2,
        textColor=colors.black,
        alignment=0
    )

    style_toc_body_center = ParagraphStyle(
        'TOCBodyCenter',
        fontName='Times-Roman',
        fontSize=8.5,
        leading=10.5,
        textColor=colors.black,
        alignment=1
    )

    style_table_head = ParagraphStyle(
        'TableHead',
        fontName='Times-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.black,
        alignment=0
    )

    style_table_head_center = ParagraphStyle(
        'TableHeadCenter',
        fontName='Times-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.black,
        alignment=1
    )

    style_table_body = ParagraphStyle(
        'TableBody',
        fontName='Times-Roman',
        fontSize=9,
        leading=12,
        textColor=colors.black,
        alignment=0
    )

    style_table_body_center = ParagraphStyle(
        'TableBodyCenter',
        fontName='Times-Roman',
        fontSize=9,
        leading=12,
        textColor=colors.black,
        alignment=1
    )

    style_reference = ParagraphStyle(
        'FormalReference',
        fontName='Times-Roman',
        fontSize=8.8,
        leading=11.8,
        textColor=colors.black,
        leftIndent=16,
        firstLineIndent=-16,
        spaceAfter=3,
        alignment=4
    )

    style_code = ParagraphStyle(
        'CodeListing',
        fontName='Courier',
        fontSize=8.2,
        leading=10.2,
        textColor=colors.black
    )

    # =========================================================================
    # PAGE 1: COVER PAGE (EXACT LAYOUT OF REFERENCE PDF)
    # =========================================================================
    header_img_path = "e:/cloud/docs/screenshots/vit_official_header.png"
    if os.path.exists(header_img_path):
        # 420 pt wide, 103 pt tall to preserve aspect ratio (1681x414)
        img_hdr = Image(header_img_path, width=420, height=103.4)
        t_hdr = Table([[img_hdr]], colWidths=[504])
        t_hdr.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t_hdr)
    story.append(Spacer(1, 14))

    # Academic Department Header
    dept_style_1 = ParagraphStyle('Dept1', fontName='Times-Bold', fontSize=12, leading=16, alignment=1, textColor=colors.black)
    dept_style_2 = ParagraphStyle('Dept2', fontName='Times-Roman', fontSize=11, leading=15, alignment=1, textColor=colors.black)
    
    story.append(Paragraph("School of Computer Science Engineering and Information Systems", dept_style_1))
    story.append(Paragraph("Department of Information Technology", dept_style_1))
    story.append(Paragraph("Fall 2026-27", dept_style_2))
    story.append(Paragraph("Cloud Architecture Design BCSE355L", dept_style_2))
    story.append(Spacer(1, 38))

    # Case Study / Capstone Report Header
    case_report_style = ParagraphStyle('CaseReport', fontName='Times-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.black)
    story.append(Paragraph("CAPSTONE PROJECT REPORT", case_report_style))
    story.append(Spacer(1, 18))

    # Project Title
    title_style = ParagraphStyle('CoverTitle', fontName='Times-Bold', fontSize=14, leading=19, alignment=1, textColor=colors.black)
    story.append(Paragraph(
        "CLOUDSHIELD: A REAL-TIME PREDICTIVE CLOUD ARCHITECTURE FOR DISASTER LOGISTICS ALLOCATION, "
        "SEVERITY-DRIVEN RESCUE OPTIMIZATION, AND RESILIENT EMERGENCY GOVERNANCE",
        title_style
    ))
    story.append(Spacer(1, 36))

    # Submitted By Block
    sub_label_style = ParagraphStyle('SubLabel', fontName='Times-Italic', fontSize=11, leading=15, alignment=1, textColor=colors.black)
    sub_name_style = ParagraphStyle('SubName', fontName='Times-Bold', fontSize=11.5, leading=16, alignment=1, textColor=colors.black)
    
    story.append(Paragraph("Submitted by", sub_label_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("NEELESH A&nbsp;&nbsp;&nbsp;&nbsp;24BIT0437", sub_name_style))
    story.append(Paragraph("DEV ARPIT PATEL&nbsp;&nbsp;&nbsp;&nbsp;24BIT0491", sub_name_style))
    story.append(Paragraph("SATWIK JAISWAL&nbsp;&nbsp;&nbsp;&nbsp;24BIT0527", sub_name_style))
    story.append(Spacer(1, 32))

    # Under the Guidance of Block
    guide_body_style = ParagraphStyle('GuideBody', fontName='Times-Roman', fontSize=10.5, leading=14.5, alignment=1, textColor=colors.black)
    guide_head_style = ParagraphStyle('GuideHead', fontName='Times-Bold', fontSize=12, leading=16, alignment=1, textColor=colors.black)
    
    story.append(Paragraph("Under the Guidance of", sub_label_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Prof. VENKETESH P.", guide_head_style))
    story.append(Paragraph("Associate Professor Grade 2", guide_body_style))
    story.append(Paragraph("SCORE", guide_body_style))
    story.append(Paragraph("Department of Information Technology", guide_body_style))
    story.append(Paragraph("School of Computer Science Engineering and Information Systems", guide_body_style))
    story.append(Paragraph("VIT, Vellore.", guide_body_style))
    story.append(Spacer(1, 28))

    story.append(Paragraph("Fall 2026-27", dept_style_2))
    
    # End of Page 1
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: TABLE OF CONTENTS (EXACT 3-COLUMN TABLE MATCHING REFERENCE PDF)
    # =========================================================================
    dec_title_style = ParagraphStyle('DecTitleStyle', fontName='Times-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.black)
    story.append(Paragraph("TABLE OF CONTENTS", dec_title_style))
    story.append(Spacer(1, 14))

    toc_raw = [
        ("1", "Abstract", "chap_abstract", 4),
        ("2", "Chapter 1: The Humanistic Imperative: Disaster Reality & The Genesis of CloudShield<br/>"
              "1.1 The Lived Reality of Acute Climate Catastrophes; 1.2 The Emotional and Operational Fracture; "
              "1.3 Shifting the Paradigm; 1.4 Ethical Principles of Algorithmic Humanitarianism; 1.5 Comparative Case Study Analysis", "chap_1", 5),
        ("3", "Chapter 2: Structural Gaps and Pathologies in Traditional Emergency Logistics<br/>"
              "2.1 The 'Last-Mile Void'; 2.2 The Pathology of Spreadsheet Logistics; 2.3 The Fatal 'Route Pruning' Fallacy; "
              "2.4 Distributive Inequity and Panic Dispatching; 2.5 Information Cascades and Resource Hoarding", "chap_2", 9),
        ("4", "Chapter 3: Intellectual Property & Core Technical Novelty (IDF-B Alignment)<br/>"
              "3.1 Institutional IP Alignment (Doc No. 02-IPR-R003); 3.2 Novelty 1: Version-Linked Snapshots; "
              "3.3 Novelty 2: Decoupled Need Urgency & Route Feasibility; 3.4 Novelty 3: Two-Stage Plan-Commit Protocol; "
              "3.5 Novelty 4: Sphere International Standards Calibration", "chap_3", 12),
        ("5", "Chapter 4: Mathematical Foundations & Sphere Minimum Survival Standards<br/>"
              "4.1 Disaster Priority and Relief Index (DPRI) Derivation; 4.2 Sphere Minimum Survival Standards; "
              "4.3 Potable Water Logistics; 4.4 Nutritional Baselines & Pediatric Vulnerabilities", "chap_4", 16),
        ("6", "Chapter 5: Algorithmic Logistics Optimization: The Multi-Depot Knapsack Engine<br/>"
              "5.1 Constrained Multi-Facility Formulation; 5.2 Distance Decay & Road Impairment Transit Modeling; "
              "5.3 Greedy Priority Knapsack Solver; 5.4 Buffer Non-Depletion Invariants; 5.5 Non-Linear Convoy Congestion Modeling", "chap_5", 20),
        ("7", "Chapter 6: Two-Stage Human-in-the-Loop Governance & State Machine Architecture<br/>"
              "6.1 Ethical Rationale for Human Oversight; 6.2 Formal State Machine Model; 6.3 Cryptographic Action ID Idempotency; "
              "6.4 Immutable Audit Ledger & Non-Repudiation", "chap_6", 24),
        ("8", "Chapter 7: Comprehensive AWS Cloud Architecture: Service-by-Service Deep Dive<br/>"
              "7.1 Cloud Architectural Philosophy; 7.2 Amazon EC2 Compute Engine; 7.3 Amazon EBS Storage; "
              "7.4 Amazon S3 Artifact Vault; 7.5 Amazon SNS Incident Notification; 7.6 Amazon CloudWatch Logging; "
              "7.7 AWS IAM Role Security; 7.8 VPC & Security Group Isolation", "chap_7", 27),
        ("9", "Chapter 8: AWS Production Deployment, Operational Hardening & Rigorous Cost Audit<br/>"
              "8.1 Sydney Region (ap-southeast-2) Deployment; 8.2 Rigorous AWS Cost-Safety Audit; "
              "8.3 Safe Resource Teardown Protocol; 8.4 Multi-Cloud Standby & SLA Analysis", "chap_8", 31),
        ("10", "Chapter 9: End-to-End Frontend Interface & Live Operational Demonstration<br/>"
               "9.1 Crisis Command UI Engineering; 9.2 Real-Time Intake & DPRI Heatmap; "
               "9.3 Sphere Shortage & Multi-Depot Manifest; 9.4 Single-Pane Command Overview; "
               "9.5 Approval Action Card & SNS Alert; 9.6 Interactive Swagger API Docs", "chap_9", 34),
        ("11", "Chapter 10: Performance Profiling, Latency Benchmarking & Scalability Roadmap<br/>"
               "10.1 Empirical Performance Profiling; 10.2 In-Memory Caching via Amazon ElastiCache Redis; "
               "10.3 Global Edge Acceleration via CloudFront CDN & WAF; 10.4 Asynchronous SQS & Lambda Decoupling; "
               "10.5 Distributed Mutual Exclusion via Redlock", "chap_10", 37),
        ("12", "Chapter 11: Future Scope, Remote Sensing & Edge Mesh Frontiers<br/>"
               "11.1 Synthetic Aperture Radar (SAR) Telemetry; 11.2 Dynamic Road Graph Invalidation; "
               "11.3 Offline Edge Deployments via AWS Snowcone; 11.4 Multimodal Conversational AI Field Triage; "
               "11.5 UAV Drone Swarm Air-Drop Integration", "chap_11", 38),
        ("13", "References<br/>Exhaustive Academic Bibliographic References (MLA Format)", "chap_refs", 39),
        ("14", "Appendices<br/>Source Excerpts (DPRI, Knapsack, Action ID), Build & Run Summary, System Screenshots", "chap_apps", 40),
    ]

    toc_rows = [
        [
            Paragraph("<b>S. No.</b>", style_toc_head_center),
            Paragraph("<b>Contents</b>", style_toc_head),
            Paragraph("<b>Page No.</b>", style_toc_head_center)
        ]
    ]

    for s_no, contents_html, key, default_page in toc_raw:
        pg_val = str(toc_data.get(key, default_page)) if toc_data else str(default_page)
        p_sno = Paragraph(s_no, style_toc_body_center)
        p_content = Paragraph(contents_html, style_toc_body)
        p_page = Paragraph(pg_val, style_toc_body_center)
        toc_rows.append([p_sno, p_content, p_page])

    # Table of contents table: 40 pt, 400 pt, 64 pt (total 504 pt)
    t_toc = Table(toc_rows, colWidths=[40, 400, 64])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E5E7EB')),
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_toc)

    # End of Page 3
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: ABSTRACT (EXACT MATCH TO REFERENCE PDF PAGE 4)
    # =========================================================================
    story.append(HeadingWithMarker("ABSTRACT", dec_title_style, "chap_abstract"))
    story.append(Spacer(1, 14))

    story.append(Paragraph(
        "This case study presents an in-depth architectural and analytical investigation of <b>CloudShield</b>, a resilient, "
        "human-centric predictive cloud architecture designed for emergency logistics and resource allocation during acute climate "
        "catastrophes. Built upon foundational cloud computing primitives in Amazon Web Services (AWS) Asia-Pacific Sydney region "
        "(<code>ap-southeast-2</code>), the primary objective is to evaluate how CloudShield's architectural design decisions—specifically "
        "the mathematical decoupling of human survival urgency from physical transport feasibility—eliminate systemic pathologies in "
        "traditional emergency logistics, including spreadsheet lock contention, phantom inventory commitments, and commercial supply chain "
        "route pruning.",
        style_body
    ))

    story.append(Paragraph(
        "We systematically examine the mathematical formulation of the <b>Disaster Priority and Relief Index (DPRI)</b>, an objective, "
        "multi-parametric severity function that integrates flood water inundation depth, displaced population magnitude, road network isolation, "
        "and demographic vulnerability. The report deconstructs how CloudShield calibrates relief demand against international empirical benchmarks "
        "established by the Sphere Project (15.0 liters of potable water per person/day, 2,100 kcal nutritional survival rations, family shelter units, "
        "and triage trauma kits). Furthermore, we evaluate the algorithmic mechanics of the <b>Multi-Depot Priority Knapsack Engine</b>, analyzing "
        "how greedy value-to-weight heuristics, Haversine spherical transit modeling, and dynamic road impairment degradation curves optimize "
        "cross-warehouse stock distribution while strictly preserving baseline emergency buffer reserves across all municipal depots.",
        style_body
    ))

    story.append(Paragraph(
        "The study also scrutinizes system-level reliability and ethical governance mechanisms, focusing on CloudShield's <b>Two-Stage "
        "Human-in-the-Loop Governance Protocol</b>. We evaluate the formal finite-state machine governing state transitions (from provisional "
        "<code>DRAFT</code> to <code>PENDING_APPROVAL</code>, <code>APPROVED</code>, and <code>COMMITTED</code>), analyzing how client-generated "
        "cryptographic Action IDs guarantee transactional idempotency and prevent duplicate warehouse stock deductions under erratic disaster-zone "
        "network retries. An immutable, tamper-evident audit ledger maintains complete forensic non-repudiation.",
        style_body
    ))

    story.append(Paragraph(
        "Finally, the report reviews the production deployment topology across Amazon EC2, persistent EBS NVMe block storage, private S3 artifact "
        "vaults, Amazon SNS real-time notifications, and centralized CloudWatch logging. A comprehensive cost audit confirms verified 2-hour viva "
        "operating expenditure of strictly $0.01 to $0.03 USD, bounded by AWS 12-Month Free Tier allowances. Concurrent stress testing reveals "
        "P95 response latencies of 42 ms under typical operational load, and presents an architectural roadmap for sub-10ms global edge delivery via "
        "Amazon ElastiCache Redis and CloudFront CDN.",
        style_body
    ))

    # End of Page 4
    story.append(PageBreak())

    # =========================================================================
    # ADAPT CHAPTERS 1 TO 12 FROM RAW STORY
    # =========================================================================
    raw_story = get_raw_story(toc_data=None)

    # Locate where Chapter 1 starts in raw_story
    ch1_idx = None
    for i, itm in enumerate(raw_story):
        if getattr(itm, 'key', None) == 'chap_1':
            ch1_idx = i
            break

    if ch1_idx is None:
        raise RuntimeError("Could not find Chapter 1 in raw_story")

    raw_body = raw_story[ch1_idx:]
    print(f"[*] Adapting {len(raw_body)} narrative elements into reference styling...")

    in_references = False
    for elem in raw_body:
        tname = type(elem).__name__

        # 1. Chapter Headings
        if tname == 'HeadingWithMarker':
            raw_text = elem.text
            upper_text = raw_text.upper()
            story.append(HeadingWithMarker(upper_text, style_chapter_heading, elem.key))

        # 2. Paragraphs (Subheadings, Body, Bullets, References)
        elif tname == 'Paragraph':
            sname = getattr(elem.style, 'name', '')
            p_text = elem.text

            if '12.2' in p_text and 'References' in p_text:
                in_references = True
                story.append(PageBreak())
                story.append(HeadingWithMarker("REFERENCES", dec_title_style, "chap_refs"))
                story.append(Spacer(1, 10))
                continue

            if in_references:
                if p_text.startswith('<b>[') or p_text.startswith('['):
                    story.append(Paragraph(p_text, style_reference))
                continue

            if sname == 'FormalSubHeading':
                story.append(Paragraph(p_text, style_section_heading))
            elif sname == 'FormalBodyBold':
                if p_text.startswith('<b>Table ') or p_text.startswith('Table '):
                    clean_title = p_text.replace('<b>', '').replace('</b>', '')
                    story.append(Paragraph(clean_title, style_table_title))
                else:
                    story.append(Paragraph(p_text, style_body_bold))
            elif sname == 'FormalBullet':
                story.append(Paragraph(p_text, style_bullet))
            elif sname == 'FormalCallout':
                story.append(Paragraph(p_text, style_body))
            else:
                story.append(Paragraph(p_text, style_body))

        # 3. Figures (KeepTogether with Image + Caption)
        elif tname == 'KeepTogether':
            content = getattr(elem, '_content', [])
            img_obj = None
            cap_obj = None
            for sub in content:
                if type(sub).__name__ == 'Image':
                    img_obj = sub
                elif type(sub).__name__ == 'Paragraph':
                    cap_obj = sub

            if img_obj:
                img_path = getattr(img_obj, 'filename', getattr(img_obj, '_filename', None))
                if img_path and os.path.exists(img_path):
                    img_table = Table([[Image(img_path, width=470, height=img_obj.drawHeight * (470.0 / img_obj.drawWidth))]], colWidths=[504])
                    img_table.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                        ('TOPPADDING', (0,0), (-1,-1), 0),
                    ]))
                    
                    cap_text = cap_obj.text if cap_obj else ""
                    story.append(KeepTogether([
                        img_table,
                        Spacer(1, 4),
                        Paragraph(cap_text, style_fig_caption)
                    ]))

        # 4. Tables (Data Tables & Boxed Listings/Formulas)
        elif tname == 'Table':
            cell_data = getattr(elem, '_cellvalues', None)
            if not cell_data or len(cell_data) == 0:
                continue

            num_r = len(cell_data)
            num_c = len(cell_data[0])

            # Case A: 1x1 Formula / Callout Box
            if num_r == 1 and num_c == 1:
                raw_cell = cell_data[0][0]
                cell_text = getattr(raw_cell, 'text', str(raw_cell))
                p_box = Paragraph(cell_text, style_body)
                t_box = Table([[p_box]], colWidths=[504])
                t_box.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9FAFB')),
                    ('BOX', (0,0), (-1,-1), 0.6, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_box)
                story.append(Spacer(1, 6))

            # Case B: Multi-Column Data Table
            else:
                table_matrix = []
                for r_idx, row in enumerate(cell_data):
                    row_cells = []
                    is_head = (r_idx == 0)
                    for cell_val in row:
                        if hasattr(cell_val, 'text'):
                            c_text = cell_val.text
                        elif isinstance(cell_val, list):
                            c_text = "<br/>".join([getattr(x, 'text', str(x)) for x in cell_val])
                        else:
                            c_text = str(cell_val)
                            
                        if is_head:
                            row_cells.append(Paragraph(c_text, style_table_head))
                        else:
                            row_cells.append(Paragraph(c_text, style_table_body))
                    table_matrix.append(row_cells)

                base_widths = getattr(elem, '_argW', None)
                if base_widths and len(base_widths) == num_c:
                    tot_w = sum(base_widths)
                    actual_widths = [(w / tot_w) * 504.0 for w in base_widths]
                else:
                    actual_widths = [504.0 / num_c] * num_c

                t_data = Table(table_matrix, colWidths=actual_widths)
                t_data.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E5E7EB')),
                    ('BOX', (0,0), (-1,-1), 0.6, colors.black),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('TOPPADDING', (0,0), (-1,-1), 3),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                    ('LEFTPADDING', (0,0), (-1,-1), 4),
                    ('RIGHTPADDING', (0,0), (-1,-1), 4),
                ]))
                story.append(t_data)
                story.append(Spacer(1, 8))

        # 5. Page Breaks
        elif tname == 'PageBreak':
            story.append(PageBreak())

    # =========================================================================
    # APPENDICES SECTION (EXACT MATCH TO REFERENCE PDF PAGES 39 - 40)
    # =========================================================================
    story.append(PageBreak())
    story.append(HeadingWithMarker("APPENDICES", dec_title_style, "chap_apps"))
    story.append(Spacer(1, 10))

    # Appendix A: Key Source Excerpts
    story.append(Paragraph("<b>Appendix A: Key Source Excerpts</b>", style_section_heading))
    story.append(Paragraph(
        "The following source code excerpts from the CloudShield engine illustrate the mathematical evaluation "
        "of the Disaster Priority and Relief Index (DPRI), the multi-depot knapsack solver, and the cryptographic "
        "Action ID idempotency governance protocol.",
        style_body
    ))
    story.append(Spacer(1, 4))

    # Listing A.1: DPRI
    story.append(Paragraph("<b>Listing A.1: Disaster Priority and Relief Index (DPRI) Evaluation Engine (app/services/dpri_service.py)</b>", style_table_title))
    code_a1 = (
        "def calculate_dpri(hazard_depth: float, displaced_persons: int, road_blockage: float, vulnerability_ratio: float) -> float:\n"
        "    \"\"\"Calculates normalized DPRI urgency score: w1*H + w2*P + w3*I + w4*V (weights strictly sum to 1.0).\"\"\"\n"
        "    norm_h = min(max(hazard_depth / 4.0, 0.0), 1.0)           # 4.0m max inundation baseline\n"
        "    norm_p = min(max(displaced_persons / 10000.0, 0.0), 1.0)   # 10,000 evacuee taluk baseline\n"
        "    norm_b = min(max(road_blockage / 100.0, 0.0), 1.0)        # 100% complete road severance\n"
        "    norm_v = min(max(vulnerability_ratio, 0.0), 1.0)          # Pediatric / geriatric ratio\n"
        "    dpri_raw = 0.30 * norm_h + 0.25 * norm_p + 0.25 * norm_b + 0.20 * norm_v\n"
        "    return round(dpri_raw, 4)"
    )
    t_code1 = Table([[Preformatted(code_a1, style_code)]], colWidths=[504])
    t_code1.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code1)
    story.append(Spacer(1, 6))

    # Listing A.2: Knapsack Solver
    story.append(Paragraph("<b>Listing A.2: Constrained Multi-Depot Knapsack Allocation Solver (app/services/allocation_service.py)</b>", style_table_title))
    code_a2 = (
        "def allocate_resources_greedy(demand: Dict[str, float], depots: List[DepotInventory], buffer_reserve: float = 0.15) -> Dict:\n"
        "    \"\"\"Allocates survival items across depots optimizing transit time while strictly holding 15% safety buffer.\"\"\"\n"
        "    allocations = {}\n"
        "    for item, req_qty in demand.items():\n"
        "        sorted_depots = sorted(depots, key=lambda d: d.transit_hours)\n"
        "        for depot in sorted_depots:\n"
        "            available = depot.stock[item] * (1.0 - buffer_reserve)\n"
        "            fill = min(req_qty, available)\n"
        "            if fill > 0:\n"
        "                allocations[depot.id] = allocations.get(depot.id, 0) + fill\n"
        "                req_qty -= fill\n"
        "                if req_qty <= 0: break\n"
        "    return allocations"
    )
    t_code2 = Table([[Preformatted(code_a2, style_code)]], colWidths=[504])
    t_code2.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code2)

    # PAGE 40: Listing A.3, Appendix B & Appendix C
    story.append(PageBreak())

    # Listing A.3: Action ID Idempotency
    story.append(Paragraph("<b>Listing A.3: Two-Stage Action ID Idempotent State Machine & Audit Governance Engine (app/services/audit_service.py)</b>", style_table_title))
    code_a3 = (
        "def commit_approved_manifest(action_id: str, plan_id: str, director_role: str, db: Session) -> Dict:\n"
        "    \"\"\"Guarantees cryptographic Action ID idempotency: returns existing receipt on duplicate submission.\"\"\"\n"
        "    existing_action = db.query(AuditLedger).filter(AuditLedger.action_id == action_id).first()\n"
        "    if existing_action:\n"
        "        return {\"status\": \"ALREADY_COMMITTED\", \"receipt\": existing_action.id, \"idempotent_replay\": True}\n"
        "    plan = db.query(AllocationPlan).filter(AllocationPlan.id == plan_id).with_for_update().first()\n"
        "    if plan.status != PlanStatus.PENDING_APPROVAL:\n"
        "        raise StateTransitionError(f\"Cannot approve plan in {plan.status} state\")\n"
        "    plan.status = PlanStatus.APPROVED\n"
        "    audit_entry = AuditLedger(action_id=action_id, plan_id=plan.id, actor=director_role, status=\"COMMITTED\")\n"
        "    db.add(audit_entry)\n"
        "    db.commit()\n"
        "    return {\"status\": \"COMMITTED\", \"action_id\": action_id}"
    )
    t_code3 = Table([[Preformatted(code_a3, style_code)]], colWidths=[504])
    t_code3.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code3)
    story.append(Spacer(1, 5))

    # Appendix B: Build and Run Summary
    story.append(Paragraph("<b>Appendix B: Build, Deployment, and Test Verification Summary</b>", style_section_heading))
    story.append(Paragraph(
        "The reproducible CloudShield verification harness is automated via Python 3.11 and AWS CLI v2 in <code>ap-southeast-2</code>:",
        style_body
    ))
    story.append(Paragraph(
        "&bull;&nbsp;&nbsp;<b>Automated Test Suite:</b> Execute full unit & integration verification: <code>pytest tests/ -v --cov=app</code>",
        style_bullet
    ))
    story.append(Paragraph(
        "&bull;&nbsp;&nbsp;<b>AWS EC2 Deployment Bootstrap:</b> Idempotent cloud provisioning: <code>bash deployment/aws/ec2_bootstrap.sh</code>",
        style_bullet
    ))
    story.append(Paragraph(
        "&bull;&nbsp;&nbsp;<b>Live Production Health Check:</b> Operational endpoint probe: <code>curl -s http://32.236.173.240:8000/health</code>",
        style_bullet
    ))
    story.append(Paragraph(
        "&bull;&nbsp;&nbsp;<b>Audit Trail Ingestion:</b> Retrieve cryptographic audit logs: <code>curl -s http://32.236.173.240:8000/api/audit</code>",
        style_bullet
    ))
    story.append(Spacer(1, 5))

    # Appendix C: System and Benchmark Screenshots
    story.append(Paragraph("<b>Appendix C: System and Benchmark Screenshots</b>", style_section_heading))
    story.append(Paragraph(
        "Screenshots capturing real-time incident command telemetry in CloudShield and AWS CloudWatch audit streaming:",
        style_body
    ))
    story.append(Spacer(1, 4))

    ui_app_img1 = "e:/cloud/docs/screenshots/ui_1_intake_and_dpri.png"
    ui_app_img2 = "e:/cloud/docs/screenshots/ui_3_approval_and_audit.png"

    if os.path.exists(ui_app_img1) and os.path.exists(ui_app_img2):
        im1 = Image(ui_app_img1, width=245, height=130)
        im2 = Image(ui_app_img2, width=245, height=130)
        t_app_imgs = Table([[im1, im2]], colWidths=[250, 254])
        t_app_imgs.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t_app_imgs)
        story.append(Spacer(1, 4))
        
        cap_c = (
            "<b>Figure C.1: Live Incident Intake and DPRI Urgency Heatmap.</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            "<b>Figure C.2: Real-Time Human Governance & Immutable Audit Log.</b>"
        )
        story.append(Paragraph(cap_c, style_fig_caption))

    return story


def generate_pdf(output_filename="CloudShield_Complete_Project_Report.pdf"):
    print(f"[*] Starting compilation for {output_filename} in reference styling...")
    
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    # PASS 1: Build story to capture exact page numbers for Table of Contents
    print("[*] Executing Pass 1: Calculating Section Page Offsets...")
    section_page_registry.clear()
    story_pass1 = build_story(toc_data=None)
    doc.build(story_pass1, canvasmaker=ReferenceNumberedCanvas)
    
    captured_pages = dict(section_page_registry)
    print(f"[*] Pass 1 Complete. Captured Page Mapping: {captured_pages}")

    # PASS 2: Rebuild document injecting verified Table of Contents page numbers
    print("[*] Executing Pass 2: Rendering final publication-grade PDF with verified TOC...")
    section_page_registry.clear()
    story_pass2 = build_story(toc_data=captured_pages)
    doc.build(story_pass2, canvasmaker=ReferenceNumberedCanvas)
    
    print(f"[*] Pass 2 Complete. Final Page Mapping: {section_page_registry}")
    print(f"[+] PDF Generation Successful: {output_filename}")
    if os.path.exists(output_filename):
        size_kb = os.path.getsize(output_filename) / 1024
        print(f"[+] Output File Size: {size_kb:.2f} KB")


if __name__ == "__main__":
    generate_pdf()
