"""
CloudShield Master Project Report Word Document Generator
Generates: CloudShield_Complete_Project_Report.docx
Matches strictly all style, layout, font, color, and design of the uploaded reference PDF:
- Pure academic monochrome color scheme: pure black text, light grey table headers (#E5E7EB), thin black borders
- Times New Roman font throughout (12 pt body, 14 pt bold chapter headings)
- Page 1: Official VIT Header Image, School/Dept/Course, Project Title, Submitted By, Faculty Guide, Fall 2026-27
- Page 2: Declaration with Digital Signature
- Page 3: Table of Contents (3-Column Table: S. No. | Contents | Page No.)
- Page 4: Abstract
- Chapters 1 to 12: Centered Chapter Headings (All Caps, 14 pt Bold Black), Left-Aligned Subheadings (12.5 pt Bold Black)
- Tables with title above, light grey header, thin black borders
- Figures centered with caption below in Times New Roman 10.5 pt
- Clean top margin (no running header)
- Only page number centered at the bottom of EVERY page (dynamic PAGE field)
- Total Pages: Exactly 40 pages
"""

import os
import sys
import html
from html.parser import HTMLParser

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

sys.path.append('e:/cloud')
from build_complete_report_original import build_story as get_raw_story


def add_field(p, field_text):
    """Inserts dynamic Word field codes such as PAGE."""
    run = p.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = field_text
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def set_cell_shading(cell, color_hex):
    """Sets background fill color for a table cell."""
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)


def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    """Sets explicit borders for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    b_top = f'<w:top w:val="{top.get("val","single")}" w:sz="{top.get("sz","4")}" w:space="0" w:color="{top.get("color","auto")}"/>' if top else '<w:top w:val="none"/>'
    b_left = f'<w:left w:val="{left.get("val","single")}" w:sz="{left.get("sz","4")}" w:space="0" w:color="{left.get("color","auto")}"/>' if left else '<w:left w:val="none"/>'
    b_bottom = f'<w:bottom w:val="{bottom.get("val","single")}" w:sz="{bottom.get("sz","4")}" w:space="0" w:color="{bottom.get("color","auto")}"/>' if bottom else '<w:bottom w:val="none"/>'
    b_right = f'<w:right w:val="{right.get("val","single")}" w:sz="{right.get("sz","4")}" w:space="0" w:color="{right.get("color","auto")}"/>' if right else '<w:right w:val="none"/>'
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}>{b_top}{b_left}{b_bottom}{b_right}</w:tcBorders>')
    tcPr.append(tcBorders)


def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    """Sets internal cell padding (in dxa: 20 dxa = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)


class DocxHTMLParser(HTMLParser):
    def __init__(self, paragraph, default_font="Times New Roman", default_size=12, default_color=None, bold_base=False, italic_base=False):
        super().__init__()
        self.p = paragraph
        self.default_font = default_font
        self.default_size = default_size
        self.default_color = default_color or RGBColor(0x00, 0x00, 0x00)
        
        self.bold = bold_base
        self.italic = italic_base
        self.subscript = False
        self.superscript = False
        self.is_code = False
        
    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in ('b', 'strong'):
            self.bold = True
        elif t in ('i', 'em'):
            self.italic = True
        elif t == 'sub':
            self.subscript = True
        elif t == 'sup':
            self.superscript = True
        elif t == 'code':
            self.is_code = True
        elif t == 'br':
            self.p.add_run().add_break()
            
    def handle_endtag(self, tag):
        t = tag.lower()
        if t in ('b', 'strong'):
            self.bold = False
        elif t in ('i', 'em'):
            self.italic = False
        elif t == 'sub':
            self.subscript = False
        elif t == 'sup':
            self.superscript = False
        elif t == 'code':
            self.is_code = False
            
    def handle_data(self, data):
        if not data:
            return
        run = self.p.add_run(data)
        if self.is_code:
            run.font.name = 'Consolas'
            run.font.size = Pt(self.default_size * 0.9)
            run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        else:
            run.font.name = self.default_font
            run.font.size = Pt(self.default_size)
            run.font.color.rgb = self.default_color
                
        run.bold = self.bold
        run.italic = self.italic
        if self.subscript:
            run.font.subscript = True
        if self.superscript:
            run.font.superscript = True


def add_html_to_paragraph(p, html_text, default_font="Times New Roman", default_size=12, default_color=None, bold_base=False, italic_base=False):
    if not html_text:
        return
    clean_text = html_text.replace('&nbsp;', ' ')
    clean_text = html.unescape(clean_text)
    parser = DocxHTMLParser(p, default_font, default_size, default_color, bold_base, italic_base)
    parser.feed(clean_text)


def build_word_document(output_docx_path="e:/cloud/CloudShield_Complete_Project_Report.docx"):
    print(f"[*] Starting compilation of Word document: {output_docx_path} in reference styling...")
    doc = Document()

    # 1. Page Setup: Standard Letter, 1-inch margins (72 pt) all around
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.different_first_page_header_footer = False  # Page number on ALL pages including page 1

    # 2. Configure Global Document Styles (Pure Black Typography)
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    h1_style = doc.styles['Heading 1']
    h1_style.font.name = 'Times New Roman'
    h1_style.font.size = Pt(14)
    h1_style.font.bold = True
    h1_style.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    h1_style.paragraph_format.space_before = Pt(14)
    h1_style.paragraph_format.space_after = Pt(14)
    h1_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1_style.paragraph_format.keep_with_next = True

    h2_style = doc.styles['Heading 2']
    h2_style.font.name = 'Times New Roman'
    h2_style.font.size = Pt(12.5)
    h2_style.font.bold = True
    h2_style.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    h2_style.paragraph_format.space_before = Pt(10)
    h2_style.paragraph_format.space_after = Pt(4)
    h2_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h2_style.paragraph_format.keep_with_next = True

    # 3. Header & Footer (Matching Reference PDF: Clean top, centered page number only)
    # Header: None
    header = section.header
    header.paragraphs[0].text = ""

    # Footer: Centered page number
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.text = ""
    add_field(fp, "PAGE")
    for r in fp.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # =========================================================================
    # PAGE 1: COVER PAGE (EXACT REFERENCE PDF LAYOUT)
    # =========================================================================
    print("[*] Generating Page 1: Cover Page...")
    header_img_path = "e:/cloud/docs/screenshots/vit_official_header.png"
    if os.path.exists(header_img_path):
        p_hdr = doc.add_paragraph()
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hdr.paragraph_format.space_before = Pt(0)
        p_hdr.paragraph_format.space_after = Pt(14)
        p_hdr.add_run().add_picture(header_img_path, width=Inches(5.6))

    # Academic Department Header
    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(0)
    p_dept.paragraph_format.space_after = Pt(36)
    
    r_d1 = p_dept.add_run("School of Computer Science Engineering and Information Systems\nDepartment of Information Technology\n")
    r_d1.font.name = 'Times New Roman'
    r_d1.font.size = Pt(12)
    r_d1.bold = True
    r_d1.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    r_d2 = p_dept.add_run("Fall 2026-27\nCloud Architecture Design BCSE355L")
    r_d2.font.name = 'Times New Roman'
    r_d2.font.size = Pt(11)
    r_d2.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Capstone Report Header
    p_crep = doc.add_paragraph()
    p_crep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_crep.paragraph_format.space_before = Pt(0)
    p_crep.paragraph_format.space_after = Pt(18)
    r_cr = p_crep.add_run("CAPSTONE PROJECT REPORT")
    r_cr.font.name = 'Times New Roman'
    r_cr.font.size = Pt(14)
    r_cr.bold = True
    r_cr.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Project Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(36)
    r_tit = p_title.add_run(
        "CLOUDSHIELD: A REAL-TIME PREDICTIVE CLOUD ARCHITECTURE FOR DISASTER LOGISTICS ALLOCATION, "
        "SEVERITY-DRIVEN RESCUE OPTIMIZATION, AND RESILIENT EMERGENCY GOVERNANCE"
    )
    r_tit.font.name = 'Times New Roman'
    r_tit.font.size = Pt(14)
    r_tit.bold = True
    r_tit.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Submitted By
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(32)
    r_sl = p_sub.add_run("Submitted by\n")
    r_sl.font.name = 'Times New Roman'
    r_sl.font.size = Pt(11)
    r_sl.italic = True
    r_sl.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    r_sn = p_sub.add_run(
        "NEELESH A    24BIT0437\n"
        "DEV ARPIT PATEL    24BIT0491\n"
        "SATWIK JAISWAL    24BIT0527"
    )
    r_sn.font.name = 'Times New Roman'
    r_sn.font.size = Pt(11.5)
    r_sn.bold = True
    r_sn.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Under Guidance Of
    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_before = Pt(0)
    p_guide.paragraph_format.space_after = Pt(28)
    r_gl = p_guide.add_run("Under the Guidance of\n")
    r_gl.font.name = 'Times New Roman'
    r_gl.font.size = Pt(11)
    r_gl.italic = True
    r_gl.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    r_gn = p_guide.add_run("Prof. VENKETESH P.\n")
    r_gn.font.name = 'Times New Roman'
    r_gn.font.size = Pt(12)
    r_gn.bold = True
    r_gn.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    r_gb = p_guide.add_run(
        "Associate Professor Grade 2\n"
        "SCORE\n"
        "Department of Information Technology\n"
        "School of Computer Science Engineering and Information Systems\n"
        "VIT, Vellore."
    )
    r_gb.font.name = 'Times New Roman'
    r_gb.font.size = Pt(10.5)
    r_gb.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    p_fall = doc.add_paragraph()
    p_fall.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fall.paragraph_format.space_before = Pt(0)
    p_fall.paragraph_format.space_after = Pt(0)
    r_f = p_fall.add_run("Fall 2026-27")
    r_f.font.name = 'Times New Roman'
    r_f.font.size = Pt(11)
    r_f.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    doc.add_page_break()

    # =========================================================================
    # PAGE 2: DECLARATION (EXACT MATCH)
    # =========================================================================
    print("[*] Generating Page 2: Declaration...")
    p_dh = doc.add_paragraph("DECLARATION", style='Heading 1')
    p_dh.paragraph_format.space_after = Pt(16)

    p_d1 = doc.add_paragraph()
    p_d1.paragraph_format.line_spacing = 1.15
    p_d1.paragraph_format.space_after = Pt(6)
    p_d1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_html_to_paragraph(
        p_d1,
        "I hereby declare that the capstone project report titled \"A Practical Cloud Architecture Design: CloudShield — "
        "Predictive Disaster Resource and Logistic Allocation System\", submitted in partial fulfillment of the requirements "
        "for BCSE355L – Cloud Architecture Design, is my original work."
    )

    p_d2 = doc.add_paragraph()
    p_d2.paragraph_format.line_spacing = 1.15
    p_d2.paragraph_format.space_after = Pt(6)
    p_d2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_html_to_paragraph(
        p_d2,
        "I affirm that this report has been prepared collaboratively and has not been submitted, either in part or in full, "
        "to any other course, institution, or university for the award of any degree, diploma, or academic certification."
    )

    p_d3 = doc.add_paragraph("I further declare that:")
    p_d3.paragraph_format.space_after = Pt(4)

    dec_bullets = [
        "All sources of technical information, system architectures, and cloud service documentation have been acknowledged and cited using standard academic referencing.",
        "Figures, structural diagrams, benchmark scripts, and analytical models taken from external sources or technical literature are appropriately credited and documented.",
        "The architectural analysis, algorithmic breakdown, and technical evaluation represent my own conceptual understanding and academic synthesis, except where explicitly stated.",
        "Any academic or technical assistance received during the conceptualization, execution, and preparation of this report has been duly acknowledged."
    ]

    for b in dec_bullets:
        pb = doc.add_paragraph()
        pb.paragraph_format.left_indent = Inches(0.25)
        pb.paragraph_format.space_after = Pt(4)
        pb.paragraph_format.line_spacing = 1.15
        pb.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_html_to_paragraph(pb, f"&bull;&nbsp;&nbsp;{b}")

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(18)
    p_sp.paragraph_format.space_after = Pt(0)

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(14)
    add_html_to_paragraph(p_meta, "<b>Student Name:</b>&nbsp;&nbsp;&nbsp;&nbsp;Neelesh A<br/><b>Register Number:</b>&nbsp;&nbsp;24BIT0437")

    p_sig_l = doc.add_paragraph()
    p_sig_l.paragraph_format.space_after = Pt(6)
    add_html_to_paragraph(p_sig_l, "<b>Signature:</b>")

    sig_img_path = "e:/cloud/docs/screenshots/neelesh_signature.png"
    if os.path.exists(sig_img_path):
        p_sig_img = doc.add_paragraph()
        p_sig_img.paragraph_format.space_after = Pt(0)
        p_sig_img.add_run().add_picture(sig_img_path, width=Inches(1.5))

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: TABLE OF CONTENTS (EXACT 3-COLUMN TABLE)
    # =========================================================================
    print("[*] Generating Page 3: Table of Contents...")
    p_th = doc.add_paragraph("TABLE OF CONTENTS", style='Heading 1')
    p_th.paragraph_format.space_after = Pt(14)

    toc_raw = [
        ("1", "<b>Abstract</b>", "4"),
        ("2", "<b>Chapter 1: The Humanistic Imperative: Disaster Reality & The Genesis of CloudShield</b><br/>"
              "1.1 The Lived Reality of Acute Climate Catastrophes; 1.2 The Emotional and Operational Fracture; "
              "1.3 Shifting the Paradigm; 1.4 Ethical Principles of Algorithmic Humanitarianism; 1.5 Comparative Case Study Analysis", "5"),
        ("3", "<b>Chapter 2: Structural Gaps and Pathologies in Traditional Emergency Logistics</b><br/>"
              "2.1 The 'Last-Mile Void'; 2.2 The Pathology of Spreadsheet Logistics; 2.3 The Fatal 'Route Pruning' Fallacy; "
              "2.4 Distributive Inequity and Panic Dispatching; 2.5 Information Cascades and Resource Hoarding", "8"),
        ("4", "<b>Chapter 3: Intellectual Property & Core Technical Novelty (IDF-B Alignment)</b><br/>"
              "3.1 Institutional IP Alignment (Doc No. 02-IPR-R003); 3.2 Novelty 1: Version-Linked Snapshots; "
              "3.3 Novelty 2: Decoupled Need Urgency & Route Feasibility; 3.4 Novelty 3: Two-Stage Plan-Commit Protocol; "
              "3.5 Novelty 4: Sphere International Standards Calibration", "10"),
        ("5", "<b>Chapter 4: Mathematical Foundations & Sphere Minimum Survival Standards</b><br/>"
              "4.1 Disaster Priority and Relief Index (DPRI) Derivation; 4.2 Sphere Minimum Survival Standards; "
              "4.3 Potable Water Logistics; 4.4 Nutritional Baselines & Pediatric Vulnerabilities", "13"),
        ("6", "<b>Chapter 5: Algorithmic Logistics Optimization: The Multi-Depot Knapsack Engine</b><br/>"
              "5.1 Constrained Multi-Facility Formulation; 5.2 Distance Decay & Road Impairment Transit Modeling; "
              "5.3 Greedy Priority Knapsack Solver; 5.4 Buffer Non-Depletion Invariants; 5.5 Non-Linear Convoy Congestion Modeling", "16"),
        ("7", "<b>Chapter 6: Two-Stage Human-in-the-Loop Governance & State Machine Architecture</b><br/>"
              "6.1 Ethical Rationale for Human Oversight; 6.2 Formal State Machine Model; 6.3 Cryptographic Action ID Idempotency; "
              "6.4 Immutable Audit Ledger & Non-Repudiation", "19"),
        ("8", "<b>Chapter 7: Comprehensive AWS Cloud Architecture: Service-by-Service Deep Dive</b><br/>"
              "7.1 Cloud Architectural Philosophy; 7.2 Amazon EC2 Compute Engine; 7.3 Amazon EBS Storage; "
              "7.4 Amazon S3 Artifact Vault; 7.5 Amazon SNS Incident Notification; 7.6 Amazon CloudWatch Logging; "
              "7.7 AWS IAM Role Security; 7.8 VPC & Security Group Isolation", "21"),
        ("9", "<b>Chapter 8: AWS Production Deployment, Operational Hardening & Rigorous Cost Audit</b><br/>"
              "8.1 Sydney Region (ap-southeast-2) Deployment; 8.2 Rigorous AWS Cost-Safety Audit; "
              "8.3 Safe Resource Teardown Protocol; 8.4 Multi-Cloud Standby & SLA Analysis", "25"),
        ("10", "<b>Chapter 9: End-to-End Frontend Interface & Live Operational Demonstration</b><br/>"
               "9.1 Crisis Command UI Engineering; 9.2 Real-Time Intake & DPRI Heatmap; "
               "9.3 Sphere Shortage & Multi-Depot Manifest; 9.4 Single-Pane Command Overview; "
               "9.5 Approval Action Card & SNS Alert; 9.6 Interactive Swagger API Docs", "27"),
        ("11", "<b>Chapter 10: Performance Profiling, Latency Benchmarking & Scalability Roadmap</b><br/>"
               "10.1 Empirical Performance Profiling; 10.2 In-Memory Caching via Amazon ElastiCache Redis; "
               "10.3 Global Edge Acceleration via CloudFront CDN & WAF; 10.4 Asynchronous SQS & Lambda Decoupling; "
               "10.5 Distributed Mutual Exclusion via Redlock", "33"),
        ("12", "<b>Chapter 11: Future Scope, Remote Sensing & Edge Mesh Frontiers</b><br/>"
               "11.1 Synthetic Aperture Radar (SAR) Telemetry; 11.2 Dynamic Road Graph Invalidation; "
               "11.3 Offline Edge Deployments via AWS Snowcone; 11.4 Multimodal Conversational AI Field Triage; "
               "11.5 UAV Drone Swarm Air-Drop Integration", "35"),
        ("13", "<b>References</b><br/>Exhaustive Academic Bibliographic References (MLA Format)", "38"),
        ("14", "<b>Appendices</b><br/>Source Excerpts (DPRI, Knapsack, Action ID), Build & Run Summary, System Screenshots", "39"),
    ]

    t_toc = doc.add_table(len(toc_raw) + 1, 3)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    border_black = {"val": "single", "sz": "4", "color": "000000"}

    # Header Row
    headers = [("S. No.", Inches(0.6), WD_ALIGN_PARAGRAPH.CENTER),
               ("Contents", Inches(5.1), WD_ALIGN_PARAGRAPH.LEFT),
               ("Page No.", Inches(0.8), WD_ALIGN_PARAGRAPH.CENTER)]
    
    for c_i, (h_text, h_w, h_align) in enumerate(headers):
        c = t_toc.rows[0].cells[c_i]
        c.width = h_w
        set_cell_shading(c, "E5E7EB")
        set_cell_borders(c, top=border_black, bottom=border_black, left=border_black, right=border_black)
        set_cell_margins(c, top=40, bottom=40, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = h_align
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)
        r.bold = True
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Content Rows
    for r_i, (s_no, c_html, pg) in enumerate(toc_raw):
        row = t_toc.rows[r_i + 1]
        c0, c1, c2 = row.cells
        c0.width = Inches(0.6)
        c1.width = Inches(5.1)
        c2.width = Inches(0.8)

        for cell in (c0, c1, c2):
            set_cell_borders(cell, top=border_black, bottom=border_black, left=border_black, right=border_black)
            set_cell_margins(cell, top=30, bottom=30, left=60, right=60)

        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(s_no)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(8.5)
        r0.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.05
        add_html_to_paragraph(p1, c_html, default_font="Times New Roman", default_size=8.2, default_color=RGBColor(0x00, 0x00, 0x00))

        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(0)
        r2 = p2.add_run(pg)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    doc.add_page_break()

    # =========================================================================
    # PAGE 4: ABSTRACT
    # =========================================================================
    print("[*] Generating Page 4: Abstract...")
    p_ah = doc.add_paragraph("ABSTRACT", style='Heading 1')
    p_ah.paragraph_format.space_after = Pt(14)

    abstract_paras = [
        "This case study presents an in-depth architectural and analytical investigation of <b>CloudShield</b>, a resilient, "
        "human-centric predictive cloud architecture designed for emergency logistics and resource allocation during acute climate "
        "catastrophes. Built upon foundational cloud computing primitives in Amazon Web Services (AWS) Asia-Pacific Sydney region "
        "(<code>ap-southeast-2</code>), the primary objective is to evaluate how CloudShield's architectural design decisions—specifically "
        "the mathematical decoupling of human survival urgency from physical transport feasibility—eliminate systemic pathologies in "
        "traditional emergency logistics, including spreadsheet lock contention, phantom inventory commitments, and commercial supply chain "
        "route pruning.",

        "We systematically examine the mathematical formulation of the <b>Disaster Priority and Relief Index (DPRI)</b>, an objective, "
        "multi-parametric severity function that integrates flood water inundation depth, displaced population magnitude, road network isolation, "
        "and demographic vulnerability. The report deconstructs how CloudShield calibrates relief demand against international empirical benchmarks "
        "established by the Sphere Project (15.0 liters of potable water per person/day, 2,100 kcal nutritional survival rations, family shelter units, "
        "and triage trauma kits). Furthermore, we evaluate the algorithmic mechanics of the <b>Multi-Depot Priority Knapsack Engine</b>, analyzing "
        "how greedy value-to-weight heuristics, Haversine spherical transit modeling, and dynamic road impairment degradation curves optimize "
        "cross-warehouse stock distribution while strictly preserving baseline emergency buffer reserves across all municipal depots.",

        "The study also scrutinizes system-level reliability and ethical governance mechanisms, focusing on CloudShield's <b>Two-Stage "
        "Human-in-the-Loop Governance Protocol</b>. We evaluate the formal finite-state machine governing state transitions (from provisional "
        "<code>DRAFT</code> to <code>PENDING_APPROVAL</code>, <code>APPROVED</code>, and <code>COMMITTED</code>), analyzing how client-generated "
        "cryptographic Action IDs guarantee transactional idempotency and prevent duplicate warehouse stock deductions under erratic disaster-zone "
        "network retries. An immutable, tamper-evident audit ledger maintains complete forensic non-repudiation.",

        "Finally, the report reviews the production deployment topology across Amazon EC2, persistent EBS NVMe block storage, private S3 artifact "
        "vaults, Amazon SNS real-time notifications, and centralized CloudWatch logging. A comprehensive cost audit confirms verified 2-hour viva "
        "operating expenditure of strictly $0.01 to $0.03 USD, bounded by AWS 12-Month Free Tier allowances. Concurrent stress testing reveals "
        "P95 response latencies of 42 ms under typical operational load, and presents an architectural roadmap for sub-10ms global edge delivery via "
        "Amazon ElastiCache Redis and CloudFront CDN."
    ]

    for p_txt in abstract_paras:
        p_abs = doc.add_paragraph()
        p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_abs.paragraph_format.line_spacing = 1.15
        p_abs.paragraph_format.space_after = Pt(6)
        add_html_to_paragraph(p_abs, p_txt, default_font="Times New Roman", default_size=12, default_color=RGBColor(0x00, 0x00, 0x00))

    doc.add_page_break()

    # =========================================================================
    # CHAPTERS 1 TO 12 ADAPTED FROM RAW STORY
    # =========================================================================
    print("[*] Processing chapters from raw story...")
    raw_story = get_raw_story(toc_data=None)

    ch1_idx = None
    for i, itm in enumerate(raw_story):
        if getattr(itm, 'key', None) == 'chap_1':
            ch1_idx = i
            break

    raw_body = raw_story[ch1_idx:]
    in_references = False

    for elem in raw_body:
        tname = type(elem).__name__

        # 1. Chapter Headings
        if tname == 'HeadingWithMarker':
            p = doc.add_paragraph(style='Heading 1')
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(14)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            raw_text = elem.text.upper()
            add_html_to_paragraph(p, raw_text, default_size=14, default_color=RGBColor(0x00, 0x00, 0x00), bold_base=True)

        # 2. Paragraphs
        elif tname == 'Paragraph':
            sname = getattr(elem.style, 'name', '')
            p_text = elem.text

            if '12.2' in p_text and 'References' in p_text:
                in_references = True
                doc.add_page_break()
                p_ref_h = doc.add_paragraph("REFERENCES", style='Heading 1')
                p_ref_h.paragraph_format.space_after = Pt(14)
                continue

            if in_references:
                if p_text.startswith('<b>[') or p_text.startswith('['):
                    p_ref = doc.add_paragraph()
                    p_ref.paragraph_format.left_indent = Inches(0.25)
                    p_ref.paragraph_format.first_line_indent = Inches(-0.25)
                    p_ref.paragraph_format.space_after = Pt(4)
                    p_ref.paragraph_format.line_spacing = 1.15
                    p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    add_html_to_paragraph(p_ref, p_text, default_size=9.5, default_color=RGBColor(0x00, 0x00, 0x00))
                continue

            if sname == 'FormalSubHeading':
                p = doc.add_paragraph(style='Heading 2')
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                add_html_to_paragraph(p, p_text, default_size=12.5, default_color=RGBColor(0x00, 0x00, 0x00), bold_base=True)

            elif sname == 'FormalBodyBold':
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                # If table title
                if p_text.startswith('<b>Table ') or p_text.startswith('Table '):
                    clean_t = p_text.replace('<b>', '').replace('</b>', '')
                    add_html_to_paragraph(p, clean_t, default_size=11, default_color=RGBColor(0x00, 0x00, 0x00), bold_base=True)
                else:
                    add_html_to_paragraph(p, p_text, default_size=12, default_color=RGBColor(0x00, 0x00, 0x00), bold_base=True)

            elif sname == 'FormalBullet':
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.15
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                add_html_to_paragraph(p, p_text, default_size=12, default_color=RGBColor(0x00, 0x00, 0x00))

            else:  # Body text
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.15
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                add_html_to_paragraph(p, p_text, default_size=12, default_color=RGBColor(0x00, 0x00, 0x00))

        # 3. Figures (KeepTogether with Image + Caption)
        elif tname == 'KeepTogether':
            content = getattr(elem, '_content', [])
            img_obj = None
            caption_obj = None
            for sub in content:
                if type(sub).__name__ == 'Image':
                    img_obj = sub
                elif type(sub).__name__ == 'Paragraph':
                    caption_obj = sub

            if img_obj and hasattr(img_obj, 'filename'):
                img_path = img_obj.filename
                if os.path.exists(img_path):
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(8)
                    p_img.paragraph_format.space_after = Pt(4)
                    p_img.paragraph_format.keep_with_next = True
                    p_img.add_run().add_picture(img_path, width=Inches(5.8))

            if caption_obj:
                p_cap = doc.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_before = Pt(2)
                p_cap.paragraph_format.space_after = Pt(8)
                p_cap.paragraph_format.line_spacing = 1.15
                add_html_to_paragraph(p_cap, caption_obj.text, default_size=10.5, default_color=RGBColor(0x00, 0x00, 0x00))

        # 4. Tables (Data Tables & Boxed Formulas)
        elif tname == 'Table':
            cell_data = getattr(elem, '_cellvalues', None)
            if not cell_data or len(cell_data) == 0:
                continue

            num_rows = len(cell_data)
            num_cols = len(cell_data[0])

            # Case A: 1x1 Formula / Callout Box
            if num_rows == 1 and num_cols == 1:
                t_box = doc.add_table(1, 1)
                t_box.alignment = WD_TABLE_ALIGNMENT.CENTER
                c = t_box.rows[0].cells[0]
                c.width = Inches(6.5)
                set_cell_shading(c, "F9FAFB")
                border_box = {"val": "single", "sz": "4", "color": "000000"}
                set_cell_borders(c, top=border_box, bottom=border_box, left=border_box, right=border_box)
                set_cell_margins(c, top=80, bottom=80, left=100, right=100)

                raw_cell = cell_data[0][0]
                p_box = c.paragraphs[0]
                p_box.paragraph_format.space_after = Pt(0)
                p_box.paragraph_format.line_spacing = 1.15
                cell_text = getattr(raw_cell, 'text', str(raw_cell))
                add_html_to_paragraph(p_box, cell_text, default_size=10.5, default_color=RGBColor(0x00, 0x00, 0x00))

                p_post = doc.add_paragraph()
                p_post.paragraph_format.space_before = Pt(4)
                p_post.paragraph_format.space_after = Pt(0)

            # Case B: Multi-Column Data Table
            else:
                t_grid = doc.add_table(num_rows, num_cols)
                t_grid.alignment = WD_TABLE_ALIGNMENT.CENTER
                border_black = {"val": "single", "sz": "4", "color": "000000"}

                base_widths = getattr(elem, '_argW', None)
                if base_widths and len(base_widths) == num_cols:
                    tot_w = sum(base_widths)
                    col_inches = [(w / tot_w) * 6.5 for w in base_widths]
                else:
                    col_inches = [6.5 / num_cols] * num_cols

                for r_idx, row in enumerate(cell_data):
                    t_row = t_grid.rows[r_idx]
                    is_header = (r_idx == 0)

                    for c_idx, cell_val in enumerate(row):
                        c = t_row.cells[c_idx]
                        c.width = Inches(col_inches[c_idx])

                        if is_header:
                            set_cell_shading(c, "E5E7EB")
                        else:
                            set_cell_shading(c, "FFFFFF")

                        set_cell_borders(c, top=border_black, bottom=border_black, left=border_black, right=border_black)
                        set_cell_margins(c, top=60, bottom=60, left=80, right=80)

                        p_cell = c.paragraphs[0]
                        p_cell.paragraph_format.space_after = Pt(0)
                        p_cell.paragraph_format.line_spacing = 1.1

                        if hasattr(cell_val, 'text'):
                            cell_text = cell_val.text
                        elif isinstance(cell_val, list):
                            cell_text = "<br/>".join([getattr(x, 'text', str(x)) for x in cell_val])
                        else:
                            cell_text = str(cell_val)

                        add_html_to_paragraph(p_cell, cell_text, default_size=9.5, default_color=RGBColor(0x00, 0x00, 0x00), bold_base=is_header)

                p_post = doc.add_paragraph()
                p_post.paragraph_format.space_before = Pt(6)
                p_post.paragraph_format.space_after = Pt(0)

        elif tname == 'PageBreak':
            doc.add_page_break()

    # =========================================================================
    # APPENDICES SECTION (PAGES 39 & 40)
    # =========================================================================
    print("[*] Generating Appendices...")
    doc.add_page_break()
    p_app_h = doc.add_paragraph("APPENDICES", style='Heading 1')
    p_app_h.paragraph_format.space_after = Pt(12)

    p_a_sub = doc.add_paragraph("Appendix A: Key Source Excerpts", style='Heading 2')
    p_a_sub.paragraph_format.space_after = Pt(4)

    p_a_intro = doc.add_paragraph(
        "The following source code excerpts from the CloudShield engine illustrate the mathematical evaluation "
        "of the Disaster Priority and Relief Index (DPRI), the multi-depot knapsack solver, and the cryptographic "
        "Action ID idempotency governance protocol."
    )
    p_a_intro.paragraph_format.space_after = Pt(6)

    # Listing A.1
    p_l1_t = doc.add_paragraph()
    p_l1_t.paragraph_format.space_before = Pt(4)
    p_l1_t.paragraph_format.space_after = Pt(2)
    p_l1_t.paragraph_format.keep_with_next = True
    add_html_to_paragraph(p_l1_t, "<b>Listing A.1: Disaster Priority and Relief Index (DPRI) Evaluation Engine (app/services/dpri_service.py)</b>", default_size=10, bold_base=True)

    t_l1 = doc.add_table(1, 1)
    t_l1.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_l1 = t_l1.rows[0].cells[0]
    c_l1.width = Inches(6.5)
    border_black = {"val": "single", "sz": "4", "color": "000000"}
    set_cell_borders(c_l1, top=border_black, bottom=border_black, left=border_black, right=border_black)
    set_cell_margins(c_l1, top=60, bottom=60, left=80, right=80)
    p_code1 = c_l1.paragraphs[0]
    p_code1.paragraph_format.space_after = Pt(0)
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
    r_c1 = p_code1.add_run(code_a1)
    r_c1.font.name = 'Consolas'
    r_c1.font.size = Pt(8.5)
    r_c1.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Listing A.2
    p_l2_t = doc.add_paragraph()
    p_l2_t.paragraph_format.space_before = Pt(8)
    p_l2_t.paragraph_format.space_after = Pt(2)
    p_l2_t.paragraph_format.keep_with_next = True
    add_html_to_paragraph(p_l2_t, "<b>Listing A.2: Constrained Multi-Depot Knapsack Allocation Solver (app/services/allocation_service.py)</b>", default_size=10, bold_base=True)

    t_l2 = doc.add_table(1, 1)
    t_l2.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_l2 = t_l2.rows[0].cells[0]
    c_l2.width = Inches(6.5)
    set_cell_borders(c_l2, top=border_black, bottom=border_black, left=border_black, right=border_black)
    set_cell_margins(c_l2, top=60, bottom=60, left=80, right=80)
    p_code2 = c_l2.paragraphs[0]
    p_code2.paragraph_format.space_after = Pt(0)
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
    r_c2 = p_code2.add_run(code_a2)
    r_c2.font.name = 'Consolas'
    r_c2.font.size = Pt(8.5)
    r_c2.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # PAGE 40: Listing A.3, Appendix B & Appendix C
    doc.add_page_break()

    # Listing A.3
    p_l3_t = doc.add_paragraph()
    p_l3_t.paragraph_format.space_before = Pt(4)
    p_l3_t.paragraph_format.space_after = Pt(2)
    p_l3_t.paragraph_format.keep_with_next = True
    add_html_to_paragraph(p_l3_t, "<b>Listing A.3: Two-Stage Action ID Idempotent State Machine & Audit Governance Engine (app/services/audit_service.py)</b>", default_size=10, bold_base=True)

    t_l3 = doc.add_table(1, 1)
    t_l3.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_l3 = t_l3.rows[0].cells[0]
    c_l3.width = Inches(6.5)
    set_cell_borders(c_l3, top=border_black, bottom=border_black, left=border_black, right=border_black)
    set_cell_margins(c_l3, top=60, bottom=60, left=80, right=80)
    p_code3 = c_l3.paragraphs[0]
    p_code3.paragraph_format.space_after = Pt(0)
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
    r_c3 = p_code3.add_run(code_a3)
    r_c3.font.name = 'Consolas'
    r_c3.font.size = Pt(8.5)
    r_c3.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Appendix B: Build and Run Summary
    p_b_sub = doc.add_paragraph("Appendix B: Build, Deployment, and Test Verification Summary", style='Heading 2')
    p_b_sub.paragraph_format.space_before = Pt(8)
    p_b_sub.paragraph_format.space_after = Pt(4)

    p_b_intro = doc.add_paragraph(
        "The reproducible CloudShield verification harness is automated via Python 3.11 and AWS CLI v2 in <code>ap-southeast-2</code>:"
    )
    p_b_intro.paragraph_format.space_after = Pt(4)

    app_b_bullets = [
        "<b>Automated Test Suite:</b> Execute full unit & integration verification: <code>pytest tests/ -v --cov=app</code>",
        "<b>AWS EC2 Deployment Bootstrap:</b> Idempotent cloud provisioning: <code>bash deployment/aws/ec2_bootstrap.sh</code>",
        "<b>Live Production Health Check:</b> Operational endpoint probe: <code>curl -s http://32.236.173.240:8000/health</code>",
        "<b>Audit Trail Ingestion:</b> Retrieve cryptographic audit logs: <code>curl -s http://32.236.173.240:8000/api/audit</code>"
    ]

    for b in app_b_bullets:
        pb = doc.add_paragraph()
        pb.paragraph_format.left_indent = Inches(0.25)
        pb.paragraph_format.space_after = Pt(3)
        add_html_to_paragraph(pb, f"&bull;&nbsp;&nbsp;{b}")

    # Appendix C: System and Benchmark Screenshots
    p_c_sub = doc.add_paragraph("Appendix C: System and Benchmark Screenshots", style='Heading 2')
    p_c_sub.paragraph_format.space_before = Pt(8)
    p_c_sub.paragraph_format.space_after = Pt(4)

    p_c_intro = doc.add_paragraph(
        "Screenshots capturing real-time incident command telemetry in CloudShield and AWS CloudWatch audit streaming:"
    )
    p_c_intro.paragraph_format.space_after = Pt(4)

    ui_app_img1 = "e:/cloud/docs/screenshots/ui_1_intake_and_dpri.png"
    ui_app_img2 = "e:/cloud/docs/screenshots/ui_3_approval_and_audit.png"

    if os.path.exists(ui_app_img1) and os.path.exists(ui_app_img2):
        t_imgs = doc.add_table(1, 2)
        t_imgs.alignment = WD_TABLE_ALIGNMENT.CENTER
        c_i1, c_i2 = t_imgs.rows[0].cells
        c_i1.width = Inches(3.2)
        c_i2.width = Inches(3.2)
        for c in (c_i1, c_i2):
            set_cell_borders(c)
            set_cell_margins(c, top=0, bottom=0, left=40, right=40)

        p_img1 = c_i1.paragraphs[0]
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.add_run().add_picture(ui_app_img1, width=Inches(3.1))

        p_img2 = c_i2.paragraphs[0]
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.add_run().add_picture(ui_app_img2, width=Inches(3.1))

        p_cap_c = doc.add_paragraph()
        p_cap_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap_c.paragraph_format.space_before = Pt(4)
        p_cap_c.paragraph_format.space_after = Pt(0)
        add_html_to_paragraph(
            p_cap_c,
            "<b>Figure C.1: Live Incident Intake and DPRI Urgency Heatmap.</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            "<b>Figure C.2: Real-Time Human Governance & Immutable Audit Log.</b>",
            default_size=10.5
        )

    # Save Word document
    print(f"[*] Saving Word document to {output_docx_path}...")
    doc.save(output_docx_path)
    file_size_bytes = os.path.getsize(output_docx_path)
    print(f"[+] Successfully generated Word document: {output_docx_path} ({file_size_bytes / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    build_word_document()
