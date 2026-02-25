---
name: arxiv-to-markdown
description: >
  Convert arxiv HTML papers to complete, well-formatted Markdown with local images.
  Use when user provides an arxiv URL (arxiv.org/html/... or arxiv.org/abs/...) and wants to
  save, read, extract, or convert the paper to markdown/md format. Also triggers when user asks
  to "download this paper", "save this arxiv paper", or "extract paper content".
---

# Arxiv to Markdown

Convert arxiv HTML papers into structured Markdown files with locally saved images.

## Prerequisites

Install once if missing:

```bash
pip3 install trafilatura lxml_html_clean
```

## Workflow

### Step 1: Normalize the URL

Convert any arxiv URL to HTML format:
- `arxiv.org/abs/XXXX.XXXXX` → `arxiv.org/html/XXXX.XXXXX`
- `arxiv.org/pdf/XXXX.XXXXX` → `arxiv.org/html/XXXX.XXXXX`
- `arxiv.org/html/XXXX.XXXXX` → use as-is
- Strip URL fragments (`#S3`, `#S4`, etc.)

Extract the **paper ID** (e.g. `2503.02247v5`) for naming.

### Step 2: Run extraction script

```bash
python3 <skill-dir>/scripts/arxiv_extract.py "<arxiv_html_url>" /tmp/arxiv_<paper_id> --images-dir /tmp/arxiv_<paper_id>/assets
```

This produces:
- `raw_content.txt` — plain text from trafilatura
- `images_map.json` — `{filename: {caption, size_bytes, local_path}}`
- `assets/` — downloaded figure images

### Step 3: Convert raw text to structured Markdown

Read `raw_content.txt` and `images_map.json`, then write a well-formatted Markdown file.

---

#### CRITICAL — Content fidelity

The goal is to produce a Markdown file that reads like the original PDF paper. Follow these rules strictly:

- **Keep all original English text verbatim.** Do NOT translate, summarize, paraphrase, or interpret. Every sentence from the paper must appear in the output.
- **Do NOT add your own content**: no commentary, no analysis sections, no bullet-point summaries, no interpretive headings (e.g., "关键发现", "核心创新", "性能分析").
- **Do NOT reorganize.** Preserve the original section ordering and titles exactly as they appear in the paper.
- **Do NOT convert prose to bullet points.** If the original is a paragraph, keep it as a paragraph. Only use bullet points where the paper itself uses a list.

---

#### File structure & metadata

**No YAML frontmatter.** Use this exact structure:

```markdown
# Paper Title (from first line of raw text)

> **来源**: arXiv:<paper_id>
> **链接**: https://arxiv.org/html/<paper_id>
> **项目主页**: <url if found in paper, otherwise omit this line>

## Abstract

<abstract text>

---

## I. Introduction

<content>

---

## II. Related Work

...
```

---

#### Section headings

Map the paper's section numbering to markdown heading levels. Keep original English titles exactly:

| Paper format | Markdown | Example |
|---|---|---|
| Top-level (`I.`, `II.`) | `##` | `## I. Introduction` |
| Sub-section (`II-A`, `III-B`) | `###` | `### II-A. Zero-shot ObjectNav` |
| Sub-sub-section (`III-C1`) | `####` | `#### III-C1. VLM-based State Prediction` |
| Named subsection (no number) | `###` or `####` | `### Contributions` |
| `Abstract` | `##` | `## Abstract` |
| `References` | `##` | `## References` |
| `Acknowledgment` | `##` | `## Acknowledgment` |

**Section separators**: Use `---` only between major top-level sections (after Abstract, after each Roman-numeral section, before References). Do NOT put `---` between subsections.

---

#### Text formatting

- **Bold** key terms, method names, model names, and contributions on first mention only (e.g., **WMNav**, **Curiosity Value Map**, **BLIP-2**)
- **Inline math variables**: Use `*italics*` for simple variable names (e.g., *I_pano*, *S_final*, *a = (θ, d)*). Use `$...$` for expressions with operators/subscripts that need LaTeX rendering.
- **Equations**: Display equations use `$$...$$`. Preserve equation numbers from the paper:
  ```markdown
  $$S_t = \text{PredictVLM}(I_{pano,t}) \quad (1)$$
  ```
- **Tables**: Place a bold title line before each table:
  ```markdown
  **Table I: Comparison with state-of-the-art methods on HM3D and MP3D**
  
  | Model | SR(%) | SPL(%) |
  |---|---|---|
  | ... | ... | ... |
  ```
- **References**: Numbered list format:
  ```markdown
  1. D. Batra et al., "Objectnav revisited: On evaluation of embodied agents navigating to objects," arXiv:2006.13171, 2020.
  2. A. Majumdar et al., "ZSON: Zero-shot object-goal navigation using multimodal goal embeddings," NeurIPS 2022.
  ```

---

#### Image embedding

Format (Obsidian wikilinks):

```markdown
> **Figure N**: Caption text from images_map.json
> ![[assets/<slug>/<filename>]]
```

**Placement**: Insert each figure immediately after the paragraph that first references it (e.g., "as shown in Figure 3" or "depicted in Fig. 2").

**Image slug**: Use the paper's short acronym/name in lowercase (e.g., `wmnav`, `vlfm`, `esc`). If no clear acronym, use a short dash-separated slug from the title.

---

### Step 4: Save output

**File location** (in order of priority):
1. User-specified path
2. Current working directory

**File naming**: `<Paper Title>.md`
- Replace `:` with ` -` (e.g., `WMNav: Integrating...` → `WMNav - Integrating...`)
- Replace other special characters (`/`, `?`, `"`, `<`, `>`, `|`) with `-`

**Image assets**: Copy from `/tmp/` to `assets/<slug>/` relative to the markdown file.
- Slug = paper acronym in lowercase (e.g., `vlfm`, `wmnav`)
- Example: `paper/assets/vlfm/overview_v1.jpg`

### Step 5: Confirm output

Report to user:
1. Markdown file path and size
2. Number of images saved and their locations
3. Any sections that may need manual review (e.g., complex equations, missing figures)

## Error Handling

| Issue | Solution |
|---|---|
| `trafilatura` not installed | Run `pip3 install trafilatura lxml_html_clean` |
| `lxml.html.clean` import error | Run `pip3 install lxml_html_clean` |
| Empty text extraction | Try `trafilatura` with `--recall` flag; fall back to curl + basic HTML parsing |
| Paper has no HTML version | Inform user: only arxiv papers with HTML rendering are supported; suggest using the `pdf` skill instead |
| Images fail to download | Log failures, continue with remaining images; note missing figures in output |
