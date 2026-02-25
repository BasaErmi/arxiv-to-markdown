# arxiv-to-markdown

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that converts arxiv HTML papers into faithful, well-structured Markdown reproductions with locally saved images.

## What It Does

When you give Claude Code an arxiv paper URL, this skill automatically:

1. **Extracts** the full paper text using [trafilatura](https://github.com/adbar/trafilatura)
2. **Downloads** all figures from the HTML page
3. **Converts** raw text into structured Markdown — faithfully reproducing the original paper with proper headings, tables, equations (LaTeX), and reference lists
4. **Embeds** images at their correct locations with figure captions

### Key Principle: Faithful Reproduction

The output reads like the original PDF paper in Markdown format. The skill enforces strict content fidelity:

- All original English text preserved verbatim — no translation, summarization, or paraphrasing
- Original section structure and titles kept exactly as they appear
- Prose stays as prose — no conversion to bullet points unless the paper uses lists
- No added commentary, analysis sections, or interpretive headings

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
> Save this paper as markdown: https://arxiv.org/html/XXXX.XXXXX
```

```
> Download this arxiv paper: https://arxiv.org/abs/XXXX.XXXXX
```

```
> Extract this paper to markdown with images: https://arxiv.org/pdf/XXXX.XXXXX
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
- `output/assets/*` — downloaded figure images

## Output Format

### File Naming

- **Markdown file**: `<Paper Title>.md` with `:` replaced by ` -`
  - Example: `WMNav: Integrating...` → `WMNav - Integrating...`
- **Image directory**: `assets/<acronym>/` using the paper's short name in lowercase
  - Example: `assets/wmnav/`, `assets/vlfm/`

### Markdown Structure

```markdown
# WMNav: Integrating Vision-Language Models into World Models for Object Goal Navigation

> **来源**: arXiv:2503.02247v5
> **链接**: https://arxiv.org/html/2503.02247v5
> **项目主页**: https://example.com

## Abstract

Full abstract text reproduced verbatim...

---

## I. Introduction

Full introduction paragraphs...

> **Figure 1**: Caption text from the paper
> ![[assets/wmnav/x1.png]]

---

## II. Related Work

### II-A. Sub-section Title

...

---

## III. Method

### III-A. Overview

#### III-A1. Sub-sub-section

$$S_t = \text{PredictVLM}(I_{pano,t}) \quad (1)$$

---

## IV. Experiments

**Table I: Comparison with state-of-the-art methods**

| Model | SR(%) | SPL(%) |
|---|---|---|
| Baseline | 42.0 | 26.0 |
| **Ours** | **58.1** | **31.2** |

---

## V. Conclusion

...

---

## References

1. D. Batra et al., "Objectnav revisited," arXiv:2006.13171, 2020.
2. A. Majumdar et al., "ZSON," NeurIPS 2022.
```

### Section Heading Mapping

| Paper format | Markdown level | Example |
|---|---|---|
| Top-level (`I.`, `II.`) | `##` | `## I. Introduction` |
| Sub-section (`II-A`, `III-B`) | `###` | `### II-A. Zero-shot ObjectNav` |
| Sub-sub-section (`III-C1`) | `####` | `#### III-C1. VLM-based Prediction` |
| Named subsection | `###` or `####` | `### Contributions` |

### Image Embedding

Default format uses Obsidian wikilinks:

```markdown
> **Figure 1**: Caption text
> ![[assets/wmnav/x1.png]]
```

Standard Markdown is also supported:

```markdown
> **Figure 1**: Caption text
> ![Figure 1](assets/wmnav/x1.png)
```

### Text Formatting

| Element | Format | Example |
|---|---|---|
| Key terms (first mention) | **Bold** | **WMNav**, **BLIP-2** |
| Simple variables | *Italics* | *I_pano*, *S_final* |
| LaTeX expressions | `$...$` | `$\cos(\theta)$` |
| Display equations | `$$...$$` | `$$S_t = f(x) \quad (1)$$` |
| Section separators | `---` | Only between top-level sections |

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
