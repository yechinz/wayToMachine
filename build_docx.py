# -*- coding: utf-8 -*-
"""把 机器视觉学习路线图.md 转成排版良好的 docx。"""
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = "机器视觉学习路线图.md"
OUT = "机器视觉学习路线图.docx"

BODY_FONT = "微软雅黑"
BODY_EA = "微软雅黑"
CODE_FONT = "Consolas"
CONTENT_W = 16.6  # cm

DARK = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x1F, 0x4E, 0x79)
MID = RGBColor(0x2E, 0x74, 0xB5)
GRAY = RGBColor(0x59, 0x59, 0x59)


def set_font(run, ascii_font=BODY_FONT, ea_font=BODY_EA, size=None,
             bold=None, color=None, italic=None):
    run.font.name = ascii_font
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), ascii_font)
    rFonts.set(qn("w:hAnsi"), ascii_font)
    rFonts.set(qn("w:eastAsia"), ea_font)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color


def shade(element, fill):
    pPr = element.get_or_add_pPr() if hasattr(element, "get_or_add_pPr") else element
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def para_border(p, edge="left", color="4472C4", sz=18, space=6):
    pPr = p._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    el = OxmlElement(f"w:{edge}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), str(space))
    el.set(qn("w:color"), color)
    pBdr.append(el)


INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|\*[^*\n]+\*)")


def add_inline(p, text, size=10.5, color=None, bold_all=False):
    for tok in INLINE.split(text):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            r = p.add_run(tok[2:-2])
            set_font(r, size=size, bold=True, color=color)
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            r = p.add_run(tok[1:-1])
            set_font(r, ascii_font=CODE_FONT, ea_font=BODY_EA,
                     size=size - 0.5, color=RGBColor(0xC7, 0x25, 0x4E))
        elif tok.startswith("[") and "](" in tok:
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", tok)
            label, url = m.group(1), m.group(2)
            r = p.add_run(label)
            set_font(r, size=size, color=color, bold=bold_all)
            if not url.startswith("#"):
                r2 = p.add_run(f"（{url}）")
                set_font(r2, ascii_font=CODE_FONT, ea_font=BODY_EA,
                         size=size - 1, color=RGBColor(0x2E, 0x74, 0xB5))
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            r = p.add_run(tok[1:-1])
            set_font(r, size=size, color=color, bold=bold_all, italic=True)
        else:
            r = p.add_run(tok)
            set_font(r, size=size, color=color, bold=bold_all)


def add_heading(doc, level, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.keep_with_next = True
    sizes = {1: 24, 2: 17, 3: 13.5, 4: 11.5}
    colors = {1: DARK, 2: BLUE, 3: MID, 4: RGBColor(0x40, 0x40, 0x40)}
    pf.space_before = {1: 0, 2: 20, 3: 14, 4: 10}[level]
    pf.space_after = {1: 8, 2: 8, 3: 6, 4: 4}[level]
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if level == 2:
        para_border(p, "bottom", "BFBFBF", 8, 4)
    r = p.add_run(text)
    set_font(r, size=sizes[level], bold=True, color=colors[level])
    return p


def add_table(doc, rows):
    header, body = rows[0], rows[1:]
    ncol = len(header)
    table = doc.add_table(rows=len(rows), cols=ncol)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    if ncol == 2:
        ratios = [0.28, 0.72]
    elif ncol == 3:
        ratios = [0.22, 0.39, 0.39]
    elif ncol == 4:
        ratios = [0.18, 0.28, 0.27, 0.27]
    elif ncol == 5:
        ratios = [0.16, 0.21, 0.21, 0.21, 0.21]
    else:
        ratios = [1.0 / ncol] * ncol

    widths = [Cm(CONTENT_W * r) for r in ratios]

    # 表头重复 + 行不跨页
    trPr = table.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)
    for row in table.rows:
        rp = row._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        cant.set(qn("w:val"), "true")
        rp.append(cant)

    for i, row_data in enumerate(rows):
        for j in range(ncol):
            cell = table.cell(i, j)
            cell.width = widths[j]
            txt = row_data[j] if j < len(row_data) else ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.1
            if i == 0:
                add_inline(p, txt, size=9, color=RGBColor(0xFF, 0xFF, 0xFF), bold_all=True)
                tcPr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:fill"), "1F3864")
                tcPr.append(shd)
            else:
                add_inline(p, txt, size=8.5)
                if i % 2 == 0:
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:fill"), "F2F5FA")
                    tcPr.append(shd)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_code(doc, lines):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.35)
    pf.space_before = Pt(6)
    pf.space_after = Pt(8)
    pf.line_spacing = 1.0
    pf.keep_together = True
    shade(p._p, "F7F7F7")
    para_border(p, "left", "4472C4", 18, 8)
    for idx, line in enumerate(lines):
        if idx:
            p.add_run().add_break()
        r = p.add_run(line if line else " ")
        set_font(r, ascii_font=CODE_FONT, ea_font=BODY_EA, size=8.5,
                 color=RGBColor(0x1A, 0x1A, 0x1A))


def add_quote(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.5)
    pf.space_before = Pt(6)
    pf.space_after = Pt(6)
    shade(p._p, "EDF3FB")
    para_border(p, "left", "2E74B5", 24, 8)
    add_inline(p, text, size=9.5, color=RGBColor(0x1F, 0x38, 0x64))


def add_rule(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    para_border(p, "bottom", "D0D0D0", 6, 1)


def add_page_number(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    set_font(run, size=9, color=GRAY)
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def main():
    with open(SRC, encoding="utf-8") as f:
        lines = f.read().splitlines()

    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_EA)
    normal.paragraph_format.line_spacing = 1.35
    normal.paragraph_format.space_after = Pt(4)

    add_page_number(sec)

    i, n = 0, len(lines)
    first_heading = True
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # 代码块
        if stripped.startswith("```"):
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            i += 1
            add_code(doc, code)
            continue

        # 表格
        if stripped.startswith("|") and i + 1 < n and re.match(
                r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            rows = []
            header = [c.strip() for c in stripped.strip("|").split("|")]
            rows.append(header)
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            add_table(doc, rows)
            continue

        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            if level == 1 and not first_heading:
                doc.add_page_break()
            if level == 2 and text == "目录":
                doc.add_page_break()
            is_first = first_heading
            first_heading = False
            p = add_heading(doc, level, text)
            if is_first:
                p.paragraph_format.space_before = Pt(150)
            i += 1
            continue

        # 分隔线
        if re.match(r"^-{3,}$", stripped):
            add_rule(doc)
            i += 1
            continue

        # 引用
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            add_quote(doc, " ".join(buf))
            continue

        # 有序列表
        mo = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if mo:
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Cm(0.7)
            pf.first_line_indent = Cm(-0.5)
            pf.space_before = Pt(1)
            pf.space_after = Pt(2)
            r = p.add_run(f"{mo.group(1)}. ")
            set_font(r, size=10.5, color=MID, bold=True)
            add_inline(p, mo.group(2), size=10.5)
            i += 1
            continue

        # 无序列表
        if re.match(r"^[-*]\s+", stripped):
            text = re.sub(r"^[-*]\s+", "", stripped)
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Cm(0.6)
            pf.first_line_indent = Cm(-0.35)
            pf.space_before = Pt(1)
            pf.space_after = Pt(2)
            r = p.add_run("• ")
            set_font(r, size=10.5, color=MID)
            add_inline(p, text, size=10)
            i += 1
            continue

        # 普通段落（合并连续行）
        buf = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(("#", "|", "```", ">", "- ", "* "))
                    or re.match(r"^-{3,}$", nxt)
                    or re.match(r"^\d+\.\s", nxt)):
                break
            buf.append(nxt)
            i += 1
        text = "".join(buf)
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        add_inline(p, text, size=10.5)
        if text.startswith("**") and re.match(r"^\*\*\d+[\.、]", text):
            p.paragraph_format.left_indent = Cm(0.3)
            p.paragraph_format.space_before = Pt(8)

        # "目录" 前分页
        if text == "目录":
            pass

    # 在 "## 目录" 前插入分页：重新处理比较复杂，改为在标题为 目录 时换页
    doc.save(OUT)
    print("saved:", OUT)


if __name__ == "__main__":
    main()
