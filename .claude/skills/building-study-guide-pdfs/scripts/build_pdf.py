#!/usr/bin/env python3
"""Build a study-guide PDF from a Markdown source.

Usage: python3 build_pdf.py <guide.md> <out.pdf> [--title "Footer title"]

Markdown conventions (see SKILL.md):
  - Cover and Contents headings are raw HTML (<h1>) so they stay out of the TOC.
  - <div class="cover" markdown="1">...</div>        cover page
  - <div class="page-break"></div>                    force a new page
  - <div class="callout" markdown="1">...</div>       tip / exam-trap box
  - <div class="qa" markdown="1">...</div>            interview Q&A block
  - <div class="cheatsheet" markdown="1">...</div>    dense 3-column final page
  - [TOC] marker renders the table of contents
"""
import argparse
import pathlib
import subprocess
import sys

import markdown
from pygments.formatters import HtmlFormatter

HERE = pathlib.Path(__file__).resolve().parent

CSS = """
@page { size: A4; }
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 10pt;
       line-height: 1.45; color: #1f2933; }
h1 { font-size: 20pt; color: #0b3d91; border-bottom: 3px solid #0b3d91; padding-bottom: 4px;
     margin-top: 0; break-before: page; }
h2 { font-size: 14.5pt; color: #0b5cad; border-bottom: 1px solid #c8d6e5; padding-bottom: 2px;
     margin-top: 18px; break-after: avoid; }
h3 { font-size: 12pt; color: #12723e; margin: 14px 0 4px; break-after: avoid; }
h4 { font-size: 10.5pt; color: #7a3e00; margin: 10px 0 3px; break-after: avoid; }
h5 { font-size: 10pt; color: #444; margin: 8px 0 2px; }
p { margin: 4px 0 6px; }
ul, ol { margin: 3px 0 6px; padding-left: 20px; }
li { margin: 1px 0; }
code { font-family: 'Consolas', 'DejaVu Sans Mono', monospace; font-size: 8.6pt;
       background: #f1f4f8; padding: 0 3px; border-radius: 3px; }
.codehilite { background: #f7f9fc; border: 1px solid #dbe3ec; border-left: 4px solid #0b5cad;
              border-radius: 4px; padding: 6px 9px; margin: 5px 0 9px; break-inside: avoid; }
.codehilite pre { margin: 0; white-space: pre-wrap; word-break: break-word; }
.codehilite code { background: none; padding: 0; font-size: 8.3pt; line-height: 1.35; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 8.8pt;
        break-inside: auto; }
th { background: #0b3d91; color: #fff; text-align: left; padding: 4px 6px; }
td { border: 1px solid #d5dde6; padding: 3px 6px; vertical-align: top; }
tr:nth-child(even) td { background: #f5f8fb; }
blockquote { margin: 6px 0; padding: 4px 10px; border-left: 4px solid #f0a500;
             background: #fff8e6; }
.page-break { break-after: page; }
.cover { height: 255mm; display: flex; flex-direction: column; justify-content: center;
         text-align: center; break-after: page; }
.cover h1 { break-before: avoid; border: none; font-size: 30pt; }
.cover p { font-size: 12pt; color: #52606d; }
.callout { background: #eef6ff; border-left: 4px solid #0b5cad; padding: 5px 10px;
           margin: 6px 0 9px; border-radius: 3px; break-inside: avoid; }
.callout.warn { background: #fff4e5; border-left-color: #e8590c; }
.qa { border: 1px solid #d5dde6; border-radius: 5px; padding: 6px 10px; margin: 7px 0;
      break-inside: avoid; background: #fbfcfe; }
.qa h4 { margin-top: 2px; color: #0b3d91; }
.toc { columns: 2; column-gap: 20px; font-size: 9pt; }
.toc ul { padding-left: 14px; margin: 0; }
.toc > ul > li { font-weight: 600; margin-top: 3px; }
.toc li li { font-weight: 400; }
.toc ul ul ul { display: none; }
.toc a { color: #1f2933; text-decoration: none; }
.cheatsheet { columns: 3; column-gap: 9px; font-size: 6.6pt; line-height: 1.22; }
.cheatsheet h2 { font-size: 8pt; margin: 4px 0 2px; padding: 1px 4px; color: #fff;
                 background: #0b3d91; border: none; break-after: avoid; }
.cheatsheet h3 { font-size: 7.2pt; margin: 3px 0 1px; }
.cheatsheet p, .cheatsheet ul { margin: 1px 0 2px; }
.cheatsheet ul { padding-left: 10px; }
.cheatsheet .codehilite { padding: 2px 4px; margin: 1px 0 3px; border-left-width: 2px; }
.cheatsheet .codehilite code, .cheatsheet code { font-size: 6.1pt; line-height: 1.18; }
.cheatsheet table { font-size: 6.2pt; margin: 2px 0 3px; }
.cheatsheet th, .cheatsheet td { padding: 1px 3px; }
"""


def build(src: pathlib.Path, out: pathlib.Path, title: str) -> None:
    md = markdown.Markdown(
        extensions=["extra", "codehilite", "toc", "sane_lists", "md_in_html"],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
            "toc": {"toc_depth": "1-2", "title": "Table of Contents"},
        },
    )
    body = md.convert(src.read_text(encoding="utf-8"))
    pyg = HtmlFormatter(style="friendly").get_style_defs(".codehilite")
    html = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{title}</title><style>{CSS}\n{pyg}</style></head>"
        f"<body>{body}</body></html>"
    )
    html_path = out.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    subprocess.run(
        ["node", str(HERE / "render_pdf.js"), str(html_path), str(out), title],
        check=True,
    )
    html_path.unlink()
    print(f"wrote {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    build(pathlib.Path(a.src), pathlib.Path(a.out), a.title)
    sys.exit(0)
