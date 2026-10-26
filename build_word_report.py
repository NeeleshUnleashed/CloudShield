"""
CloudShield Master Project Report Word Document Generator
Generates: CloudShield_Complete_Project_Report.docx
Complies strictly with all academic guidelines:
- Times New Roman typography throughout (12 pt body, 14 pt headings)
- Page 1: Strict Cover Page (Name, Teacher Name, VIT Crest, Title - nothing extra)
- Page 2: Table of Contents & Declaration
- Page 3+: Full 12 Chapters with all 14 figures, 4 data tables, formula boxes, and references
- Running Header and Footer with dynamic Page X of Y (suppressed on Page 1)
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

# Import story structure and content from build_complete_report
sys.path.append('e:/cloud')
from build_complete_report import build_story


# =========================================================================
# HELPER FUNCTIONS: XML & STYLING
# =========================================================================

def add_field(p, field_text):
    """Inserts dynamic Word field codes such as PAGE and NUMPAGES."""
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


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Sets internal cell padding (in dxa: 20 dxa = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)


# =========================================================================
# HTML-TO-DOCX PARSER FOR RICH TEXT RUNS
# =========================================================================

class DocxHTMLParser(HTMLParser):
    """Parses HTML tags (b, i, sub, sup, font, br, code) into formatted docx Runs."""
    def __init__(self, paragraph, default_font="Times New Roman", default_size=12, default_color=None, bold_base=False, italic_base=False):
        super().__init__()
        self.p = paragraph
        self.default_font = default_font
        self.default_size = default_size
        self.default_color = default_color
        
        self.bold = bold_base
        self.italic = italic_base
        self.subscript = False
        self.superscript = False
        self.is_code = False
        self.font_color = None
        
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
        elif t == 'font':
            for k, v in attrs:
                if k.lower() == 'color':
                    c = v.strip().lstrip('#')
                    if len(c) == 6:
                        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
                        self.font_color = RGBColor(r, g, b)
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
        elif t == 'font':
            self.font_color = None
            
    def handle_data(self, data):
        if not data:
            return
        run = self.p.add_run(data)
        if self.is_code:
            run.font.name = 'Consolas'
            run.font.size = Pt(self.default_size * 0.9)
            run.font.color.rgb = RGBColor(0x0F, 0x2B, 0x5C)
        else:
            run.font.name = self.default_font
            run.font.size = Pt(self.default_size)
            if self.font_color:
                run.font.color.rgb = self.font_color
            elif self.default_color:
                run.font.color.rgb = self.default_color
                
        run.bold = self.bold
        run.italic = self.italic
        if self.subscript:
            run.font.subscript = True
        if self.superscript:
            run.font.superscript = True


def add_html_to_paragraph(p, html_text, default_font="Times New Roman", default_size=12, default_color=None, bold_base=False, italic_base=False):
    """Converts HTML text string into formatted docx Runs inside paragraph p."""
    if not html_text:
        return
    # Replace XML non-breaking spaces and symbols
    clean_text = html_text.replace('&nbsp;', ' ')
    clean_text = html.unescape(clean_text)
    parser = DocxHTMLParser(p, default_font, default_size, default_color, bold_base, italic_base)
    parser.feed(clean_text)


# =========================================================================
# MAIN BUILD SCRIPT
# =========================================================================

def build_word_document(output_docx_path="e:/cloud/CloudShield_Complete_Project_Report.docx"):
    print(f"[*] Starting compilation of Word document: {output_docx_path}...")
    doc = Document()

    # 1. Page Setup: Standard Letter, 1-inch margins (72 pt) all around
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.different_first_page_header_footer = True

    # 2. Configure Global Document Styles
    # Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Heading 1 Style (Chapter Titles: 14 pt, Bold, Navy Blue #0F2B5C)
    h1_style = doc.styles['Heading 1']
    h1_style.font.name = 'Times New Roman'
    h1_style.font.size = Pt(14)
    h1_style.font.bold = True
    h1_style.font.color.rgb = RGBColor(0x0F, 0x2B, 0x5C)
    h1_style.paragraph_format.space_before = Pt(14)
    h1_style.paragraph_format.space_after = Pt(6)
    h1_style.paragraph_format.keep_with_next = True

    # Heading 2 Style (Subheadings: 13 pt, Bold, Dark Blue #1E3A8A)
    h2_style = doc.styles['Heading 2']
    h2_style.font.name = 'Times New Roman'
    h2_style.font.size = Pt(13)
    h2_style.font.bold = True
    h2_style.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    h2_style.paragraph_format.space_before = Pt(10)
    h2_style.paragraph_format.space_after = Pt(4)
    h2_style.paragraph_format.keep_with_next = True

    # 3. Configure Running Header and Footer (Pages 2+)
    # Running Header
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run("CloudShield — Predictive Disaster Resource and Logistic Allocation System")
    hrun.font.name = 'Times New Roman'
    hrun.font.size = Pt(8.5)
    hrun.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Running Footer: 1-row, 2-column borderless table
    footer = section.footer
    tbl_f = footer.add_table(1, 2, Inches(6.5))
    tbl_f.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in tbl_f.rows:
        for c in r.cells:
            tcPr = c._tc.get_or_add_tcPr()
            tcBorders = parse_xml(r'<w:tcBorders {}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>'.format(nsdecls('w')))
            tcPr.append(tcBorders)

    c_left, c_right = tbl_f.rows[0].cells
    c_left.width = Inches(4.7)
    c_right.width = Inches(1.8)

    p_fl = c_left.paragraphs[0]
    r_fl = p_fl.add_run("School of Computer Science Engineering and Information Systems (SCORE), VIT Vellore")
    r_fl.font.name = 'Times New Roman'
    r_fl.font.size = Pt(8.5)
    r_fl.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    p_fr = c_right.paragraphs[0]
    p_fr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_fr1 = p_fr.add_run("Page ")
    r_fr1.font.name = 'Times New Roman'
    r_fr1.font.size = Pt(8.5)
    r_fr1.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    add_field(p_fr, "PAGE")
    r_fr2 = p_fr.add_run(" of ")
    r_fr2.font.name = 'Times New Roman'
    r_fr2.font.size = Pt(8.5)
    r_fr2.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    add_field(p_fr, "NUMPAGES")

    # =========================================================================
    # PAGE 1: STRICT COVER PAGE (Name, Teacher Name, VIT Crest, Title - Nothing Extra)
    # =========================================================================
    print("[*] Generating Page 1: Strict Cover Page...")

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(12)
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst1 = p_inst.add_run("VELLORE INSTITUTE OF TECHNOLOGY\n")
    r_inst1.font.name = 'Times New Roman'
    r_inst1.font.size = Pt(15)
    r_inst1.bold = True
    r_inst1.font.color.rgb = RGBColor(0x0F, 0x2B, 0x5C)

    r_inst2 = p_inst.add_run("(Deemed to be University under section 3 of UGC Act, 1956)\nVellore — 632014, Tamil Nadu, India")
    r_inst2.font.name = 'Times New Roman'
    r_inst2.font.size = Pt(11)
    r_inst2.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

    # VIT Crest Emblem Image
    crest_path = "e:/cloud/docs/screenshots/vit_crest.png"
    if os.path.exists(crest_path):
        p_crest = doc.add_paragraph()
        p_crest.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_crest.paragraph_format.space_before = Pt(10)
        p_crest.paragraph_format.space_after = Pt(12)
        r_crest = p_crest.add_run()
        r_crest.add_picture(crest_path, width=Inches(2.3))

    # Department and Course
    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(4)
    p_dept.paragraph_format.space_after = Pt(2)
    r_dept = p_dept.add_run("SCHOOL OF COMPUTER SCIENCE ENGINEERING AND INFORMATION SYSTEMS (SCORE)\n")
    r_dept.font.name = 'Times New Roman'
    r_dept.font.size = Pt(12)
    r_dept.bold = True
    r_dept.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    r_course = p_dept.add_run("Course: BCSE355L — Cloud Architecture Design\nFall Semester 2026–2027")
    r_course.font.name = 'Times New Roman'
    r_course.font.size = Pt(11)
    r_course.font.color.rgb = RGBColor(0x37, 0x41, 0x51)

    # Project Title Box (Framed Box Table 1x1)
    t_title = doc.add_table(1, 1)
    t_title.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_title = t_title.rows[0].cells[0]
    c_title.width = Inches(6.5)
    set_cell_shading(c_title, "F8FAFC")
    border_navy = {"val": "single", "sz": "10", "color": "0F2B5C"}
    set_cell_borders(c_title, top=border_navy, bottom=border_navy, left=border_navy, right=border_navy)
    set_cell_margins(c_title, top=160, bottom=160, left=200, right=200)

    p_tb = c_title.paragraphs[0]
    p_tb.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t1 = p_tb.add_run("CLOUDSHIELD: PREDICTIVE DISASTER RESOURCE AND LOGISTIC ALLOCATION SYSTEM\n")
    r_t1.font.name = 'Times New Roman'
    r_t1.font.size = Pt(15)
    r_t1.bold = True
    r_t1.font.color.rgb = RGBColor(0x0F, 0x2B, 0x5C)

    r_t2 = p_tb.add_run("A Human-Centric, Sphere-Calibrated Decision Support and Inventory Optimization Architecture for Acute Climate Emergencies")
    r_t2.font.name = 'Times New Roman'
    r_t2.font.size = Pt(11)
    r_t2.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

    # Spacer before metadata grid
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(16)
    p_sp.paragraph_format.space_after = Pt(0)

    # Metadata Grid (Submitted By and Faculty Guide: 1 row x 2 cols)
    t_meta = doc.add_table(1, 2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_stu, c_fac = t_meta.rows[0].cells
    c_stu.width = Inches(3.25)
    c_fac.width = Inches(3.25)

    border_grey = {"val": "single", "sz": "6", "color": "CBD5E1"}
    for c in (c_stu, c_fac):
        set_cell_shading(c, "F1F5F9")
        set_cell_borders(c, top=border_grey, bottom=border_grey, left=border_grey, right=border_grey)
        set_cell_margins(c, top=140, bottom=140, left=160, right=160)

    # Students Column
    p_stu = c_stu.paragraphs[0]
    r_sh = p_stu.add_run("SUBMITTED BY:\n")
    r_sh.font.name = 'Times New Roman'
    r_sh.font.size = Pt(11)
    r_sh.bold = True
    r_sh.font.color.rgb = RGBColor(0x0F, 0x2B, 0x5C)

    stu_text = (
        "Dev Arpit Patel (Reg. No: 24BIT0491)\n"
        "Neelesh A (Reg. No: 24BIT0437)\n"
        "Satwik Jaiswal (Reg. No: 24BIT0527)\n"
    )
    r_sbody = p_stu.add_run(stu_text)
    r_sbody.font.name = 'Times New Roman'
    r_sbody.font.size = Pt(10.5)
    r_sbody.bold = True
    r_sbody.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    r_sdeg = p_stu.add_run("B.Tech Information Technology")
    r_sdeg.font.name = 'Times New Roman'
    r_sdeg.font.size = Pt(10.5)
    r_sdeg.italic = True
    r_sdeg.font.color.rgb = RGBColor(0x37, 0x41, 0x51)

    # Faculty Guide Column
    p_fac = c_fac.paragraphs[0]
    r_fh = p_fac.add_run("FACULTY GUIDE:\n")
    r_fh.font.name = 'Times New Roman'
    r_fh.font.size = Pt(11)
    r_fh.bold = True
    r_fh.font.color.rgb = RGBColor(0x0F, 0x2B, 0x5C)

    r_fname = p_fac.add_run("Prof. Venketesh P.\n")
    r_fname.font.name = 'Times New Roman'
    r_fname.font.size = Pt(10.5)
    r_fname.bold = True
    r_fname.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    r_fbody = p_fac.add_run(
        "Associate Professor\n"
        "School of Computer Science Engineering and Information Systems (SCORE)\n"
        "VIT Vellore — 632014, Tamil Nadu"
    )
    r_fbody.font.name = 'Times New Roman'
    r_fbody.font.size = Pt(10.5)
    r_fbody.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    # End of Page 1: Strict Break
    doc.add_page_break()

    # =========================================================================
    # PAGE 2: TABLE OF CONTENTS & DECLARATION
    # =========================================================================
    print("[*] Generating Page 2: Table of Contents & Academic Declaration...")

    p_toc_head = doc.add_paragraph("TABLE OF CONTENTS", style='Heading 1')
    p_toc_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_toc_head.paragraph_format.space_before = Pt(6)
    p_toc_head.paragraph_format.space_after = Pt(8)

    toc_items = [
        ("Chapter 1: The Humanistic Imperative: Disaster Reality & The Genesis of CloudShield", "Page 3"),
        ("Chapter 2: Structural Gaps and Pathologies in Traditional Emergency Logistics", "Page 5"),
        ("Chapter 3: Intellectual Property & Core Technical Novelty (IDF-B Alignment)", "Page 8"),
        ("Chapter 4: Mathematical Foundations & Sphere Minimum Survival Standards", "Page 11"),
        ("Chapter 5: Algorithmic Logistics Optimization: The Multi-Depot Knapsack Engine", "Page 14"),
        ("Chapter 6: Two-Stage Human-in-the-Loop Governance & State Machine Architecture", "Page 17"),
        ("Chapter 7: Comprehensive AWS Cloud Architecture: Service-by-Service Deep Dive", "Page 20"),
        ("Chapter 8: AWS Production Deployment, Operational Hardening & Rigorous Cost Audit", "Page 24"),
        ("Chapter 9: End-to-End Frontend Interface & Live Operational Demonstration", "Page 27"),
        ("Chapter 10: Performance Profiling, Latency Benchmarking & Scalability Roadmap", "Page 31"),
        ("Chapter 11: Future Scope, Remote Sensing & Edge Mesh Frontiers", "Page 33"),
        ("Chapter 12: Comprehensive Academic Literature Review & Bibliographic References", "Page 35"),
    ]

    t_toc = doc.add_table(len(toc_items), 2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    border_subtle = {"val": "single", "sz": "3", "color": "E2E8F0"}

    for i, (title, pg) in enumerate(toc_items):
        row = t_toc.rows[i]
        c_title, c_page = row.cells
        c_title.width = Inches(5.6)
        c_page.width = Inches(0.9)

        set_cell_borders(c_title, bottom=border_subtle)
        set_cell_borders(c_page, bottom=border_subtle)
        set_cell_margins(c_title, top=50, bottom=50, left=80, right=80)
        set_cell_margins(c_page, top=50, bottom=50, left=80, right=80)

        p_t = c_title.paragraphs[0]
        p_t.paragraph_format.space_after = Pt(2)
        r_t = p_t.add_run(title)
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(10.5)
        r_t.bold = True
        r_t.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

        p_p = c_page.paragraphs[0]
        p_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_p.paragraph_format.space_after = Pt(2)
        r_p = p_p.add_run(pg)
        r_p.font.name = 'Times New Roman'
        r_p.font.size = Pt(10.5)
        r_p.bold = True
        r_p.font.color.rgb = RGBColor(0x0F, 0x2B, 0x5C)

    # Academic Declaration Box
    p_dec_sp = doc.add_paragraph()
    p_dec_sp.paragraph_format.space_before = Pt(14)
    p_dec_sp.paragraph_format.space_after = Pt(0)

    t_dec = doc.add_table(1, 1)
    t_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_dec = t_dec.rows[0].cells[0]
    c_dec.width = Inches(6.5)
    set_cell_shading(c_dec, "F8FAFC")
    border_slate = {"val": "single", "sz": "6", "color": "94A3B8"}
    set_cell_borders(c_dec, top=border_slate, bottom=border_slate, left=border_slate, right=border_slate)
    set_cell_margins(c_dec, top=120, bottom=120, left=160, right=160)

    p_d = c_dec.paragraphs[0]
    p_d.paragraph_format.space_after = Pt(0)
    p_d.paragraph_format.line_spacing = 1.15
    add_html_to_paragraph(
        p_d,
        "<b>Academic Declaration & Capstone Framework:</b> This comprehensive master technical report embodies both the "
        "humanitarian imperative and the rigorous cloud engineering architecture of the CloudShield project. "
        "Developed under course BCSE355L (Cloud Architecture Design), all architectural components reflect real-world "
        "disaster response challenges, validated through an active AWS deployment in Sydney (ap-southeast-2) and compliant "
        "with International Sphere Humanitarian minimum survival standards. Grounded in institutional Invention Disclosure "
        "Form (IDF) Doc No. 02-IPR-R003, this document provides an exhaustive, production-grade examination of cloud "
        "resilience, predictive modeling, and human-in-the-loop ethical governance.",
        default_font="Times New Roman",
        default_size=10,
        default_color=RGBColor(0x33, 0x41, 0x55),
        italic_base=True
    )

    # End of Page 2: Strict Break
    doc.add_page_break()

    # =========================================================================
    # PAGES 3+: FULL 12 CHAPTERS FROM STORY PIPELINE
    # =========================================================================
    print("[*] Processing all 12 chapters from report story...")
    raw_story = build_story(toc_data=None)

    # Find the second PageBreak which marks the end of Page 2
    page_break_count = 0
    start_index = 0
    for idx, item in enumerate(raw_story):
        if type(item).__name__ == 'PageBreak':
            page_break_count += 1
            if page_break_count == 2:
                start_index = idx + 1
                break

    body_flowables = raw_story[start_index:]
    print(f"[*] Processing {len(body_flowables)} narrative elements...")

    for elem_idx, elem in enumerate(body_flowables):
        tname = type(elem).__name__

        # ---------------------------------------------------------------------
        # 1. CHAPTER HEADINGS
        # ---------------------------------------------------------------------
        if tname == 'HeadingWithMarker':
            p = doc.add_paragraph(style='Heading 1')
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            add_html_to_paragraph(p, elem.text, default_size=14, default_color=RGBColor(0x0F, 0x2B, 0x5C), bold_base=True)

        # ---------------------------------------------------------------------
        # 2. PARAGRAPHS (SUBHEADINGS, BODY TEXT, BULLETS, CALLOUTS)
        # ---------------------------------------------------------------------
        elif tname == 'Paragraph':
            style_name = getattr(elem.style, 'name', '')
            text = elem.text

            if style_name == 'FormalSubHeading':
                p = doc.add_paragraph(style='Heading 2')
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                add_html_to_paragraph(p, text, default_size=13, default_color=RGBColor(0x1E, 0x3A, 0x8A), bold_base=True)

            elif style_name == 'FormalBodyBold':
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                add_html_to_paragraph(p, text, default_size=12, default_color=RGBColor(0x11, 0x18, 0x27), bold_base=True)

            elif style_name == 'FormalBullet':
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.15
                add_html_to_paragraph(p, text, default_size=11.5, default_color=RGBColor(0x1F, 0x29, 0x37))

            elif style_name == 'FormalCallout':
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.2)
                p.paragraph_format.right_indent = Inches(0.2)
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.15
                add_html_to_paragraph(p, text, default_size=10, default_color=RGBColor(0x33, 0x41, 0x55), italic_base=True)

            else:  # Default FormalBody
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.15
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                add_html_to_paragraph(p, text, default_size=12, default_color=RGBColor(0x1F, 0x29, 0x37))

        # ---------------------------------------------------------------------
        # 3. KEEP TOGETHER (EMBEDDED FIGURES & SCREENSHOTS WITH CAPTIONS)
        # ---------------------------------------------------------------------
        elif tname == 'KeepTogether':
            content = getattr(elem, '_content', [])
            img_obj = None
            caption_obj = None
            for sub_elem in content:
                if type(sub_elem).__name__ == 'Image':
                    img_obj = sub_elem
                elif type(sub_elem).__name__ == 'Paragraph':
                    caption_obj = sub_elem

            if img_obj and hasattr(img_obj, 'filename'):
                img_path = img_obj.filename
                if os.path.exists(img_path):
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(8)
                    p_img.paragraph_format.space_after = Pt(4)
                    p_img.paragraph_format.keep_with_next = True
                    r_img = p_img.add_run()
                    r_img.add_picture(img_path, width=Inches(6.0))

            if caption_obj:
                p_cap = doc.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.left_indent = Inches(0.25)
                p_cap.paragraph_format.right_indent = Inches(0.25)
                p_cap.paragraph_format.space_before = Pt(2)
                p_cap.paragraph_format.space_after = Pt(10)
                p_cap.paragraph_format.line_spacing = 1.15
                add_html_to_paragraph(p_cap, caption_obj.text, default_size=9.5, default_color=RGBColor(0x33, 0x41, 0x55), italic_base=True)

        # ---------------------------------------------------------------------
        # 4. TABLES (DATA MATRICES & FORMULA CALLOUT BOXES)
        # ---------------------------------------------------------------------
        elif tname == 'Table':
            cell_data = getattr(elem, '_cellvalues', None)
            if not cell_data or len(cell_data) == 0:
                continue

            num_rows = len(cell_data)
            num_cols = len(cell_data[0])

            # Case A: 1x1 Formula / Standard Callout Box
            if num_rows == 1 and num_cols == 1:
                t_box = doc.add_table(1, 1)
                t_box.alignment = WD_TABLE_ALIGNMENT.CENTER
                c = t_box.rows[0].cells[0]
                c.width = Inches(6.5)
                set_cell_shading(c, "F8FAFC")
                border_box = {"val": "single", "sz": "6", "color": "CBD5E1"}
                border_left_accent = {"val": "single", "sz": "16", "color": "0F2B5C"}
                set_cell_borders(c, top=border_box, bottom=border_box, left=border_left_accent, right=border_box)
                set_cell_margins(c, top=120, bottom=120, left=160, right=160)

                raw_cell = cell_data[0][0]
                p_box = c.paragraphs[0]
                p_box.paragraph_format.space_after = Pt(0)
                p_box.paragraph_format.line_spacing = 1.15
                cell_text = getattr(raw_cell, 'text', str(raw_cell))
                add_html_to_paragraph(p_box, cell_text, default_size=10.5, default_color=RGBColor(0x1F, 0x29, 0x37))

                # Add small spacer after callout table
                p_post = doc.add_paragraph()
                p_post.paragraph_format.space_before = Pt(4)
                p_post.paragraph_format.space_after = Pt(0)

            # Case B: Multi-Column Data Table (Tables 3.1, 6.1, 7.1, 12.1)
            else:
                t_grid = doc.add_table(num_rows, num_cols)
                t_grid.alignment = WD_TABLE_ALIGNMENT.CENTER
                border_grid = {"val": "single", "sz": "4", "color": "CBD5E1"}

                # Calculate proportional column widths
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

                        # Cell background shading
                        if is_header:
                            set_cell_shading(c, "0F2B5C")
                        elif r_idx % 2 == 1:
                            set_cell_shading(c, "FFFFFF")
                        else:
                            set_cell_shading(c, "F8FAFC")

                        set_cell_borders(c, top=border_grid, bottom=border_grid, left=border_grid, right=border_grid)
                        set_cell_margins(c, top=80, bottom=80, left=100, right=100)

                        p_cell = c.paragraphs[0]
                        p_cell.paragraph_format.space_after = Pt(0)
                        p_cell.paragraph_format.line_spacing = 1.1

                        # Get cell text
                        if hasattr(cell_val, 'text'):
                            cell_text = cell_val.text
                        elif isinstance(cell_val, list):
                            cell_text = "<br/>".join([getattr(x, 'text', str(x)) for x in cell_val])
                        else:
                            cell_text = str(cell_val)

                        if is_header:
                            add_html_to_paragraph(p_cell, cell_text, default_size=9.5, default_color=RGBColor(0xFF, 0xFF, 0xFF), bold_base=True)
                        else:
                            add_html_to_paragraph(p_cell, cell_text, default_size=9.5, default_color=RGBColor(0x1F, 0x29, 0x37))

                # Add spacer after grid table
                p_post = doc.add_paragraph()
                p_post.paragraph_format.space_before = Pt(6)
                p_post.paragraph_format.space_after = Pt(0)

        # ---------------------------------------------------------------------
        # 5. PAGE BREAKS
        # ---------------------------------------------------------------------
        elif tname == 'PageBreak':
            doc.add_page_break()

    # Save Word document
    print(f"[*] Saving Word document to {output_docx_path}...")
    doc.save(output_docx_path)
    file_size_bytes = os.path.getsize(output_docx_path)
    print(f"[+] Successfully generated Word document: {output_docx_path} ({file_size_bytes / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    build_word_document()
