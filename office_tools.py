# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx", "openpyxl"]
# ///
"""
office_tools.py - make and read real Word (.docx) and Excel (.xlsx) files.

Run with uv (no Python setup needed):
    uv run office_tools.py <command> [args]

Commands:
    md2docx   input.md   output.docx     Markdown -> formatted Word document
    docx2md   input.docx [output.md]     Word document -> Markdown text
    csv2xlsx  input.csv  output.xlsx     CSV -> formatted Excel sheet
    xlsx2csv  input.xlsx [output.csv] [--sheet NAME]
                                         Excel sheet -> CSV (prints if no output)
    xlsxinfo  input.xlsx                 Show sheets, sizes, first rows, formulas
"""
import csv
import re
import sys
from pathlib import Path


# ---------- Markdown -> Word ----------

INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def add_inline(paragraph, text):
    """Add text with **bold**, *italic*, `code` and [links](url) to a paragraph."""
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
        elif part.startswith("[") and "](" in part:
            label, url = part[1:-1].split("](", 1)
            run = paragraph.add_run(f"{label} ({url})")
            run.underline = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            paragraph.add_run(part[1:-1]).italic = True
        else:
            paragraph.add_run(part)


def is_table_row(line):
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and len(s) > 1


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def md2docx(src, dst):
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)

    lines = Path(src).read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if not s:
            i += 1
            continue

        # fenced code block
        if s.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            p = doc.add_paragraph()
            run = p.add_run("\n".join(code))
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
            i += 1
            continue

        # table
        if is_table_row(s) and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1]):
            header = split_row(s)
            rows = []
            i += 2
            while i < len(lines) and is_table_row(lines[i]):
                rows.append(split_row(lines[i]))
                i += 1
            table = doc.add_table(rows=1, cols=len(header))
            table.style = "Table Grid"
            for c, h in enumerate(header):
                cell = table.rows[0].cells[c]
                cell.text = ""
                cell.paragraphs[0].add_run(h).bold = True
            for r in rows:
                cells = table.add_row().cells
                for c in range(len(header)):
                    cells[c].text = ""
                    add_inline(cells[c].paragraphs[0], r[c] if c < len(r) else "")
            doc.add_paragraph()
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)", s)
        if m:
            level = min(len(m.group(1)), 4)
            if level == 1 and not doc.paragraphs:
                doc.add_heading(m.group(2), level=0)  # first H1 = title
            else:
                doc.add_heading(m.group(2), level=level)
            i += 1
            continue

        # horizontal rule -> page break
        if re.match(r"^(-{3,}|\*{3,})$", s):
            doc.add_page_break()
            i += 1
            continue

        # bullet / numbered list
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)", line)
        if m:
            indent = len(m.group(1).replace("\t", "    ")) // 2
            numbered = m.group(2)[0].isdigit()
            style = "List Number" if numbered else "List Bullet"
            if indent >= 1:
                style += " 2"
            p = doc.add_paragraph(style=style)
            add_inline(p, m.group(3))
            i += 1
            continue

        # quote
        if s.startswith(">"):
            p = doc.add_paragraph(style="Quote")
            add_inline(p, s.lstrip("> "))
            i += 1
            continue

        # normal paragraph (join wrapped lines)
        para = [s]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#|```|>|\s*([-*+]|\d+[.)])\s|\|)", lines[i].strip()
        ):
            para.append(lines[i].strip())
            i += 1
        add_inline(doc.add_paragraph(), " ".join(para))

    doc.save(dst)
    print(f"Saved {dst}")


# ---------- Word -> Markdown ----------

def docx2md(src, dst=None):
    from docx import Document

    doc = Document(src)
    out = []
    body = doc.element.body
    tables = iter(doc.tables)
    paras = iter(doc.paragraphs)
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            p = next(paras)
            text = p.text.strip()
            if not text:
                continue
            style = (p.style.name or "").lower()
            if style == "title":
                out.append(f"# {text}")
            elif style.startswith("heading"):
                n = re.findall(r"\d+", style)
                out.append("#" * (int(n[0]) if n else 2) + " " + text)
            elif "list" in style:
                out.append(("1. " if "number" in style else "- ") + text)
            else:
                out.append(text)
            out.append("")
        elif tag == "tbl":
            t = next(tables)
            rows = [[c.text.strip().replace("\n", " ") for c in r.cells] for r in t.rows]
            if rows:
                out.append("| " + " | ".join(rows[0]) + " |")
                out.append("|" + "---|" * len(rows[0]))
                for r in rows[1:]:
                    out.append("| " + " | ".join(r) + " |")
                out.append("")
    text = "\n".join(out).strip() + "\n"
    if dst:
        Path(dst).write_text(text, encoding="utf-8")
        print(f"Saved {dst}")
    else:
        sys.stdout.write(text)


# ---------- CSV <-> Excel ----------

def _convert(value):
    v = value.strip()
    if v.startswith("="):
        return v  # keep formulas
    try:
        if re.fullmatch(r"-?\d+", v):
            return int(v)
        if re.fullmatch(r"-?\d*\.\d+", v):
            return float(v)
    except ValueError:
        pass
    return value


def csv2xlsx(src, dst):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    with open(src, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    wb = Workbook()
    ws = wb.active
    ws.title = Path(src).stem[:31] or "Sheet1"
    for r in rows:
        ws.append([_convert(c) for c in r])
    if rows:
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="305496")
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for col in range(1, len(rows[0]) + 1):
            width = max(len(str(r[col - 1])) if col - 1 < len(r) else 0 for r in rows)
            ws.column_dimensions[get_column_letter(col)].width = min(max(10, width + 2), 50)
    wb.save(dst)
    print(f"Saved {dst} ({len(rows)} rows)")


def xlsx2csv(src, dst=None, sheet=None):
    from openpyxl import load_workbook

    # values as last saved by Excel; fall back to the formula text if not calculated yet
    wb_vals = load_workbook(src, data_only=True)
    wb_form = load_workbook(src)
    ws = wb_vals[sheet] if sheet else wb_vals.active
    wf = wb_form[ws.title]
    out = open(dst, "w", newline="", encoding="utf-8") if dst else sys.stdout
    w = csv.writer(out)
    for rv, rf in zip(ws.iter_rows(values_only=True), wf.iter_rows(values_only=True)):
        w.writerow(["" if (v if v is not None else f) is None else (v if v is not None else f)
                    for v, f in zip(rv, rf)])
    if dst:
        out.close()
        print(f"Saved {dst}")


def xlsxinfo(src):
    from openpyxl import load_workbook

    wb = load_workbook(src)  # formulas visible
    for ws in wb.worksheets:
        print(f"== Sheet '{ws.title}': {ws.max_row} rows x {ws.max_column} cols")
        formulas = 0
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i < 5:
                print("   ", ["" if v is None else v for v in row])
            formulas += sum(1 for v in row if isinstance(v, str) and v.startswith("="))
        print(f"   formulas: {formulas}")


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, args = argv[1], argv[2:]
    if cmd == "md2docx" and len(args) == 2:
        md2docx(*args)
    elif cmd == "docx2md" and len(args) in (1, 2):
        docx2md(*args)
    elif cmd == "csv2xlsx" and len(args) == 2:
        csv2xlsx(*args)
    elif cmd == "xlsx2csv" and args:
        sheet = None
        if "--sheet" in args:
            k = args.index("--sheet")
            sheet = args[k + 1]
            args = args[:k] + args[k + 2:]
        xlsx2csv(args[0], args[1] if len(args) > 1 else None, sheet)
    elif cmd == "xlsxinfo" and len(args) == 1:
        xlsxinfo(args[0])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
