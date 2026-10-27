---
name: building-study-guide-pdfs
description: Use when asked to create a study guide, exam-prep, certification, or technology reference PDF (e.g. "Snowflake PDF", "DP-700 guide", "make me notes on X as a PDF") that must cover every topic with syntax and examples, interview Q&A, and a cheat sheet.
---

# Building Study Guide PDFs

## Overview

A study guide is a **topic tree with runnable examples at every leaf**, closed by interview Q&A and a one-page cheat sheet. Write it as Markdown, render it to PDF with `scripts/build_pdf.py` (Playwright Chromium). The guide is only done when every leaf has an explanation + syntax + a real example, and the rendered PDF has been looked at.

## Required document shape (in this order)

1. **Cover** — raw HTML `<div class="cover">` with `<h1>`, subtitle, persona line ("Written from the seat of a data engineer with 15 years…"), exam code/version and "current as of <month year>".
2. **Contents** — `<h1>Contents</h1>` raw, then `<div class="toc" markdown="1">[TOC]</div>`.
3. **Exam / scope overview** (certifications only) — skills-measured domains with official % weights, format, passing score, renewal.
4. **Body** — one `#` per domain/topic → `##` subtopic → `###` sub-subtopic → `####` types/variants. Every `###`/`####` leaf contains:
   - **What it is** — 2–5 plain sentences, why a practitioner cares.
   - **Types / options** — table when there are 3+ variants (columns: type, when to use, gotcha).
   - **Syntax** — fenced block with the generic grammar.
   - **Example** — fenced block, realistic names (`sales.orders`, not `foo`), commented, copy-paste runnable.
   - **Exam trap / best practice** — `<div class="callout warn" markdown="1">` where one exists.
5. **Interview Q&A** — the last 5–6 pages before the cheat sheet: 30–45 `<div class="qa" markdown="1">` blocks, each `#### Qn. question` + answer with the *why*, a code snippet where it helps, and a "follow-up they'll ask" line. Mix fundamentals, scenario/design, troubleshooting/performance, and behavioral-technical.
6. **Cheat sheet** — final page, `<div class="cheatsheet" markdown="1">`, 3 dense columns filling the whole page: `##` mini-headers, one-line syntax snippets, decision tables, limits/defaults, keyboard of key functions. No prose paragraphs.

Insert `<div class="page-break"></div>` before Interview Q&A and before the cheat sheet.

## Code language per domain

| Domain | Fence languages |
|---|---|
| Warehouses / SQL engines | `sql` (T-SQL, Snowflake SQL, Spark SQL) |
| Spark / notebooks | `python` (PySpark), `sql` (Spark SQL), `scala` rarely |
| Real-time / logs | `kql` → use `sql` fence if unhighlighted |
| APIs / agents / LLM | `python`, `json`, `bash`, `typescript` |
| CI/CD, infra | `yaml`, `bash`, `powershell` |

A concept with no code (governance, licensing, capacity) still gets a concrete artifact: a config JSON, an admin-portal step list, a CLI/REST call, or a worked numeric example.

## Workflow

1. **Research first** (REQUIRED: use deep-research / parallel-web-search / web search). Pull the *current* official skills outline (e.g. learn.microsoft.com study guide, vendor certification page) and record its "as of" date. Build the topic tree from the official outline, then add practitioner topics it omits. Never invent exam weights, limits, or product names — mark unverifiable facts or drop them.
2. **Outline** the tree in the Markdown file before writing bodies; check it against the official outline line by line.
3. **Write** section by section into `guides/<slug>/<slug>.md`. Multiple guides → one parallel agent per guide (REQUIRED: superpowers:dispatching-parallel-agents).
4. **Interview Q&A** (REQUIRED: interview-prep skill if available) — questions real panels ask for the target role.
5. **Humanize** (REQUIRED: humanizer skill) — the prose, not the code: cut "delve", "robust", "seamless", "it's important to note", rule-of-three padding, em-dash chains.
6. **Build**: `NODE_PATH=$(npm root -g) python3 .claude/skills/building-study-guide-pdfs/scripts/build_pdf.py guides/<slug>/<slug>.md guides/<slug>/<Title>.pdf --title "<footer>"`
7. **Verify visually**: render pages to PNG (`pymupdf`) and look at the cover, a body page, a Q&A page and the cheat sheet. Cheat sheet must fill exactly one page — trim or add until it does.

## Quick reference — markup

| Need | Markup |
|---|---|
| New page | `<div class="page-break"></div>` |
| Tip box / exam trap | `<div class="callout" markdown="1">` / `class="callout warn"` |
| Q&A card | `<div class="qa" markdown="1">#### Q1. …</div>` |
| Dense last page | `<div class="cheatsheet" markdown="1">…</div>` |
| Every `#` heading | starts a new page automatically |

## Common mistakes

| Mistake | Fix |
|---|---|
| Leaf topics with explanation but no example | Every leaf: syntax **and** example. Grep for `###` sections lacking a fence before building. |
| Toy names (`table1`, `foo`) | Realistic schema the reader would meet at work. |
| Stale outline (retired exam, renamed product) | Cite official outline date on the cover; re-check retirements. |
| Q&A answers one line long | Answer = what + why + trade-off + snippet. |
| Cheat sheet spills to 2 pages or is half empty | Adjust content, re-render, look again. |
| Shipping without opening the PDF | Always render PNGs and inspect. |
