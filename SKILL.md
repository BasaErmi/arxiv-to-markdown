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

**Formatting rules:**
- **Frontmatter block**: Source URL, arxiv ID, project page (if any)
- **Headings**: Map section numbers to markdown levels (`I.` → `##`, `I-A` → `###`, `I-A1` → `####`)
- **Bold** key terms, method names, and contributions on first mention
- **Equations**: Wrap in `$$..$$` with LaTeX notation; reconstruct variable names from context
- **Tables**: Convert to proper markdown tables with `|` separators and alignment
- **Lists**: Use `-` for bullet points, numbered lists where appropriate
- **References**: Numbered list, include venue/year when present in the text
- **Images**: Insert at the relevant section using the caption from `images_map.json`

**Image embedding format** (adapt to user's environment):
- Obsidian: `> ![[assets/<subfolder>/<filename>]]`
- Standard Markdown: `> ![Figure N caption](assets/<subfolder>/<filename>)`

Ask user preference if unclear. Default to Obsidian wikilink format.

**Image placement**: Insert each figure immediately after the paragraph that first references it (e.g., "as shown in Figure 3"). Use a blockquote with the caption:

```markdown
> **Figure N**: Caption text from images_map.json
> ![[assets/subfolder/filename.png]]
```

### Step 4: Save output

Determine save location based on context:
- If user specifies a path, use it
- Otherwise save to current working directory

**File naming**: `<Paper Title>.md` (clean special characters: replace `/`, `:`, `?`, `"`, `<`, `>`, `|` with `-`)

**Image assets**: Copy from `/tmp/` to `assets/<paper-slug>/` relative to the markdown file.

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
