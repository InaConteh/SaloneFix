"""Convert a Markdown document to .docx without third-party dependencies.

    python scripts/md_to_docx.py docs/report/chapter-1-introduction.md
    python scripts/md_to_docx.py <input.md> -o <output.docx>

Written for the written-report chapters under docs/report/, which use a small
Markdown subset: headings, paragraphs, bullet lists, pipe tables, horizontal
rules, and inline bold/italic/code. Anything outside that subset is emitted as
plain text rather than silently dropped.

A .docx is a zip of OOXML parts, so this builds the parts directly. That avoids
adding python-docx or pandoc to the project for a documentation task, and it
produces real Word styles (Title, Heading 1/2/3, List Paragraph, Table Grid)
that can be restyled in Word to match an institutional template.
"""
from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""


def _heading_style(style_id: str, name: str, size_half_points: int, before: int, color: str) -> str:
    return (
        f'<w:style w:type="paragraph" w:styleId="{style_id}">'
        f'<w:name w:val="{name}"/><w:basedOn w:val="Normal"/><w:qFormat/>'
        f'<w:pPr><w:keepNext/><w:spacing w:before="{before}" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr>'
        f'<w:rPr><w:b/><w:color w:val="{color}"/><w:sz w:val="{size_half_points}"/></w:rPr>'
        f"</w:style>"
    )


STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W_NS}">
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="en-GB"/>
</w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr></w:pPrDefault>
</w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:jc w:val="center"/><w:spacing w:after="240"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style>
{_heading_style("Heading1", "heading 1", 30, 320, "1F3864")}
{_heading_style("Heading2", "heading 2", 26, 280, "2E5496")}
{_heading_style("Heading3", "heading 3", 24, 240, "2E5496")}
<w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:ind w:left="720"/><w:spacing w:after="80"/></w:pPr></w:style>
<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>
<w:tblPr><w:tblBorders>
<w:top w:val="single" w:sz="4" w:color="7F7F7F"/><w:left w:val="single" w:sz="4" w:color="7F7F7F"/>
<w:bottom w:val="single" w:sz="4" w:color="7F7F7F"/><w:right w:val="single" w:sz="4" w:color="7F7F7F"/>
<w:insideH w:val="single" w:sz="4" w:color="7F7F7F"/><w:insideV w:val="single" w:sz="4" w:color="7F7F7F"/>
</w:tblBorders></w:tblPr></w:style>
</w:styles>"""

SECT_PR = (
    '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
    '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1701" w:header="708" w:footer="708"/>'
    "</w:sectPr>"
)

INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)", re.DOTALL)


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def runs(text: str) -> str:
    """Inline bold / italic / code to Word runs."""
    out = []
    for piece in INLINE.split(text):
        if not piece:
            continue
        props = ""
        if piece.startswith("**") and piece.endswith("**"):
            piece, props = piece[2:-2], "<w:b/>"
        elif piece.startswith("*") and piece.endswith("*"):
            piece, props = piece[1:-1], "<w:i/>"
        elif piece.startswith("`") and piece.endswith("`"):
            piece = piece[1:-1]
            props = '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
        rpr = f"<w:rPr>{props}</w:rPr>" if props else ""
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{esc(piece)}</w:t></w:r>')
    return "".join(out)


def para(text: str, style: str | None = None, bullet: bool = False) -> str:
    props = []
    if style:
        props.append(f'<w:pStyle w:val="{style}"/>')
    if bullet:
        props.append('<w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr>')
    ppr = f"<w:pPr>{''.join(props)}</w:pPr>" if props else ""
    return f"<w:p>{ppr}{runs(text)}</w:p>"


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table(rows: list[list[str]]) -> str:
    width = max(len(r) for r in rows)
    header, *body = rows
    # A pipe table whose header cells are all empty is a layout table (the title
    # block), not a real header - do not bold a blank row.
    has_header = any(c for c in header)

    grid = "".join(f'<w:gridCol w:w="{int(9000 / width)}"/>' for _ in range(width))
    xml = [
        '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
        '<w:tblLayout w:type="autofit"/></w:tblPr>',
        f"<w:tblGrid>{grid}</w:tblGrid>",
    ]
    for index, row in enumerate(rows):
        cells = row + [""] * (width - len(row))
        is_header_row = index == 0 and has_header
        tr = ['<w:tr>']
        if is_header_row:
            tr.insert(1, "<w:trPr><w:tblHeader/></w:trPr>")
        for cell in cells:
            content = f"**{cell}**" if is_header_row and cell and "**" not in cell else cell
            shading = '<w:shd w:val="clear" w:fill="EDF2F7"/>' if is_header_row else ""
            tr.append(
                f'<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/>{shading}</w:tcPr>'
                f"{para(content or '')}</w:tc>"
            )
        tr.append("</w:tr>")
        xml.append("".join(tr))
    xml.append("</w:tbl>")
    # Word requires a paragraph after a table, otherwise consecutive tables merge.
    xml.append("<w:p/>")
    return "".join(xml)


def convert(markdown: str) -> str:
    body: list[str] = []
    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped or stripped in {"---", "***", "___"}:
            i += 1
            continue

        # Pipe table: a row, a separator of dashes, then rows.
        if stripped.startswith("|") and i + 1 < len(lines) and re.fullmatch(
            r"\|[\s:\-|]+\|", lines[i + 1].strip()
        ):
            rows = [split_row(stripped)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i].strip()))
                i += 1
            body.append(table(rows))
            continue

        heading = re.match(r"(#{1,6})\s+(.*)", stripped)
        if heading:
            level = len(heading.group(1))
            style = "Title" if level == 1 else f"Heading{min(level - 1, 3)}"
            body.append(para(heading.group(2), style))
            i += 1
            continue

        if re.match(r"[-*]\s+", stripped):
            body.append(para("\u2022\u2003" + re.sub(r"^[-*]\s+", "", stripped), "ListParagraph"))
            i += 1
            continue

        numbered = re.match(r"(\d+)\.\s+(.*)", stripped)
        if numbered:
            body.append(para(f"{numbered.group(1)}.\u2003{numbered.group(2)}", "ListParagraph"))
            i += 1
            continue

        body.append(para(stripped))
        i += 1

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}"><w:body>{"".join(body)}{SECT_PR}</w:body></w:document>'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a Markdown file to .docx.")
    parser.add_argument("source", help="Markdown file to convert.")
    parser.add_argument("-o", "--output", help="Output .docx (default: alongside the source).")
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output) if args.output else source.with_suffix(".docx")
    document = convert(source.read_text(encoding="utf-8"))

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/document.xml", document)

    print(f"{source} -> {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
