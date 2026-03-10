#!/usr/bin/env python3
import argparse
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def paragraphize(text: str) -> str:
    chunks = [c.strip() for c in re.split(r"[\n\r]+", text) if c.strip()]
    if not chunks:
        return "<p></p>"
    return "\n".join(f"    <p>{escape(c)}</p>" for c in chunks)


def chinese_numeral(n: int) -> str:
    if n <= 0:
        raise ValueError("Chapter number must be positive")

    digits = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]

    if n < 10:
        return digits[n]
    if n < 20:
        return "十" + (digits[n % 10] if n % 10 else "")
    if n < 100:
        tens = n // 10
        ones = n % 10
        return digits[tens] + "十" + (digits[ones] if ones else "")
    if n < 1000:
        hundreds = n // 100
        rem = n % 100
        if rem == 0:
            return digits[hundreds] + "百"
        if rem < 10:
            return digits[hundreds] + "百零" + digits[rem]
        return digits[hundreds] + "百" + chinese_numeral(rem)
    raise ValueError("Chapter number too large for chinese_numeral")


def chapter_title(n: int) -> str:
    return f"第{chinese_numeral(n)}章"


def chapter_xhtml(title: str, content: str) -> str:
    return f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
<!DOCTYPE html>
<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"zh\" lang=\"zh\">
  <head>
    <title>{escape(title)}</title>
    <meta charset=\"utf-8\" />
  </head>
  <body>
    <h1>{escape(title)}</h1>
{paragraphize(content)}
  </body>
</html>
"""


def nav_xhtml(chapters: list[str]) -> str:
    items = "\n".join(
        f'        <li><a href="chapter-{i+1}.xhtml">{escape(ch)}</a></li>'
        for i, ch in enumerate(chapters)
    )
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE html>
<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\" lang=\"zh\" xml:lang=\"zh\">
  <head>
    <meta charset=\"utf-8\" />
    <title>目录</title>
  </head>
  <body>
    <nav epub:type=\"toc\" id=\"toc\">
      <h1>目录</h1>
      <ol>
{items}
      </ol>
    </nav>
  </body>
</html>
"""


def toc_ncx(book_id: str, chapters: list[str]) -> str:
    nav_points = []
    for i, ch in enumerate(chapters, start=1):
        nav_points.append(
            f"""    <navPoint id=\"navPoint-{i}\" playOrder=\"{i}\">
      <navLabel><text>{escape(ch)}</text></navLabel>
      <content src=\"chapter-{i}.xhtml\"/>
    </navPoint>"""
        )
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">
  <head>
    <meta name=\"dtb:uid\" content=\"{escape(book_id)}\"/>
    <meta name=\"dtb:depth\" content=\"1\"/>
    <meta name=\"dtb:totalPageCount\" content=\"0\"/>
    <meta name=\"dtb:maxPageNumber\" content=\"0\"/>
  </head>
  <docTitle><text>道德经</text></docTitle>
  <navMap>
{chr(10).join(nav_points)}
  </navMap>
</ncx>
"""


def content_opf(book_id: str, modified: str, chapters: list[str]) -> str:
    manifest_items = [
        '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
    ]
    spine_items = ['    <itemref idref="nav" linear="no"/>']

    for i, _ in enumerate(chapters, start=1):
        manifest_items.append(
            f'    <item id="chapter-{i}" href="chapter-{i}.xhtml" media-type="application/xhtml+xml"/>'
        )
        spine_items.append(f'    <itemref idref="chapter-{i}"/>')

    return f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
<package xmlns=\"http://www.idpf.org/2007/opf\" unique-identifier=\"bookid\" version=\"2.0\">
  <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">
    <dc:title>道德经</dc:title>
    <dc:creator opf:role=\"aut\">老子</dc:creator>
    <dc:language>zh</dc:language>
    <dc:identifier id=\"bookid\">{escape(book_id)}</dc:identifier>
    <dc:date>{escape(modified)}</dc:date>
  </metadata>
  <manifest>
{chr(10).join(manifest_items)}
  </manifest>
  <spine toc=\"ncx\">
{chr(10).join(spine_items)}
  </spine>
</package>
"""


def container_xml() -> str:
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<container version=\"1.0\" xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\">
  <rootfiles>
    <rootfile full-path=\"OEBPS/content.opf\" media-type=\"application/oebps-package+xml\"/>
  </rootfiles>
</container>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Laozi JSON chapter array into EPUB")
    parser.add_argument("input", type=Path, help="Path to input JSON (array of chapter strings)")
    parser.add_argument("output", type=Path, help="Path to output EPUB file")
    args = parser.parse_args()

    chapters_raw = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(chapters_raw, list) or not all(isinstance(c, str) for c in chapters_raw):
        raise ValueError("Input JSON must be an array of strings")

    chapters = [normalize_whitespace(c) for c in chapters_raw]
    chapter_titles = [chapter_title(i) for i in range(1, len(chapters) + 1)]

    book_id = f"urn:uuid:{uuid.uuid4()}"
    modified = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(args.output, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
        zf.writestr("META-INF/container.xml", container_xml(), compress_type=ZIP_DEFLATED)
        zf.writestr("OEBPS/content.opf", content_opf(book_id, modified, chapter_titles), compress_type=ZIP_DEFLATED)
        zf.writestr("OEBPS/toc.ncx", toc_ncx(book_id, chapter_titles), compress_type=ZIP_DEFLATED)
        zf.writestr("OEBPS/nav.xhtml", nav_xhtml(chapter_titles), compress_type=ZIP_DEFLATED)

        for i, content in enumerate(chapters, start=1):
            title = chapter_title(i)
            zf.writestr(
                f"OEBPS/chapter-{i}.xhtml",
                chapter_xhtml(title, content),
                compress_type=ZIP_DEFLATED,
            )


if __name__ == "__main__":
    main()
