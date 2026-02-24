# arxiv-to-markdown

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that converts arxiv HTML papers into well-structured Markdown files with locally saved images.

## What It Does

When you give Claude Code an arxiv paper URL, this skill automatically:

1. **Extracts** the full paper text using [trafilatura](https://github.com/adbar/trafilatura)
2. **Downloads** all figures from the HTML page
3. **Converts** raw text into structured Markdown with proper headings, tables, equations (LaTeX), and reference lists
4. **Embeds** images at their correct locations with figure captions

### Before & After

**Input:** `https://arxiv.org/html/2503.02247v5`

**Output:** A complete Markdown file with:
- Metadata header (source URL, arxiv ID, project page)
- Hierarchical section headings (`##`, `###`, `####`)
- LaTeX equations in `$$...$$` blocks
- Properly formatted Markdown tables
- Locally saved figures with captions embedded inline

## Installation

### Prerequisites

```bash
pip install trafilatura lxml_html_clean
```

### Install the Skill

**Option 1: Install from `.skill` file** (recommended)

```bash
claude install-skill arxiv-to-markdown.skill
```

**Option 2: Manual installation**

Copy the skill folder to your Claude Code skills directory:

```bash
cp -r arxiv-to-markdown ~/.claude/skills/
```

## Usage

Once installed, the skill triggers automatically when you mention an arxiv URL in Claude Code:

```
> Save this paper as markdown: https://arxiv.org/html/2503.02247v5
```

```
> Download this arxiv paper: https://arxiv.org/abs/2401.12345
```

```
> Extract this paper to markdown with images: https://arxiv.org/pdf/2312.67890
```

The skill accepts `arxiv.org/html/`, `arxiv.org/abs/`, and `arxiv.org/pdf/` URLs — it automatically converts them to the HTML version for extraction.

### Standalone Script

You can also use the extraction script directly:

```bash
python3 scripts/arxiv_extract.py <arxiv_html_url> <output_dir> [--images-dir <dir>]
```

**Example:**

```bash
python3 scripts/arxiv_extract.py \
  "https://arxiv.org/html/2503.02247v5" \
  ./output \
  --images-dir ./output/assets
```

This produces:
- `output/raw_content.txt` — extracted plain text
- `output/images_map.json` — figure filename → caption mapping
- `output/assets/*.png` — downloaded figure images

## Output Format

### Image Embedding

The skill supports two image formats:

| Environment | Format |
|---|---|
| **Obsidian** (default) | `![[assets/paper-slug/figure.png]]` |
| **Standard Markdown** | `![Figure caption](assets/paper-slug/figure.png)` |

### Markdown Structure

```markdown
# Paper Title

> **Source**: arXiv:XXXX.XXXXX
> **Link**: https://arxiv.org/html/XXXX.XXXXX

## Abstract
...

## I. Introduction
...
> **Figure 1**: Caption text
> ![[assets/paper-slug/x1.png]]

## II. Related Work
...

## III. Method
### III-A. Sub-section
#### III-A1. Sub-sub-section
$$equation in LaTeX$$

## IV. Experiments
| Model | Metric 1 | Metric 2 |
|---|---|---|
| ...   | ...      | ...      |

## References
1. Author et al., "Title," Venue, Year.
```

## File Structure

```
arxiv-to-markdown/
├── SKILL.md                    # Skill definition (triggers & workflow)
├── scripts/
│   └── arxiv_extract.py        # Core extraction script
└── README.md
```

## Limitations

- **HTML version required**: Only works with arxiv papers that have an HTML rendering (most papers after 2023). Falls back to suggesting the `pdf` skill for older papers.
- **Equations**: LaTeX equations are reconstructed from context since trafilatura extracts plain text. Complex equations may need manual review.
- **Tables**: Simple tables are converted accurately; complex multi-row/column tables may need adjustment.

## License

MIT
