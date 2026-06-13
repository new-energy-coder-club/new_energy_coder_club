# Xiaohongshu Images Skill

A Claude Code skill that transforms markdown, HTML, or text content into beautifully styled HTML pages with AI-generated cover images, then captures them as sequential screenshots at 3:4 ratio for Xiaohongshu posting.

## Features

- **Content Processing**: Accepts markdown, HTML, or plain text content
- **AI Cover Images**: Generates editorial-style cover illustrations using `/baoyu-cover-image` skill
- **Styled HTML Output**: Creates beautifully formatted HTML pages with modern typography
- **Screenshot Capture**: Takes sequential 3:4 ratio screenshots optimized for Xiaohongshu
- **Smart Text Boundaries**: Ensures no text is cut off in screenshots

## Installation

### Prerequisites

- Python 3.8 or higher
- Claude Code CLI
- `/baoyu-cover-image` skill installed in `~/.claude/skills/`

### Setup

1. **Clone or copy this skill to your Claude skills directory:**

```bash
# Copy to global skills
cp -r xiaohongshu-images-skill ~/.claude/skills/

# Or symlink for development
ln -s /path/to/xiaohongshu-images-skill ~/.claude/skills/xiaohongshu-images-skill
```

2. **Install Python dependencies:**

```bash
pip install playwright
playwright install chromium
```

3. **Ensure baoyu-cover-image skill is installed:**

```bash
# Verify the skill exists
ls ~/.claude/skills/baoyu-cover-image/SKILL.md
```

## Usage

### Via Claude Code

Invoke the skill in Claude Code:

```
/xiaohongshu-images
```

Then provide your content:
- Paste markdown/HTML content directly
- Provide a file path: `/path/to/article.md`
- Provide a URL to fetch content from

### Example

```markdown
/xiaohongshu-images

# My Article Title

This is the introduction paragraph explaining the topic...

## Section 1

Content for section 1 with detailed explanation...

## Section 2

More content here with examples...
```

### Output

The skill generates output in `~/Dev/obsidian/articles/<date-title>/`:
- `xhs-preview.html` - Styled HTML preview page
- `_attachments/cover-xhs.png` - AI-generated cover image
- `_attachments/xhs-01.png, xhs-02.png, ...` - Sequential screenshots

## Directory Structure

```
xiaohongshu-images-skill/
├── SKILL.md              # Main skill definition
├── README.md             # This file
├── prompts/
│   └── default.md        # Default HTML/CSS styling prompt
├── scripts/
│   └── screenshot.py     # Screenshot capture
└── .gitignore

Output directory (outside skill folder):
~/Dev/obsidian/articles/<date>-<title>/
├── xhs-preview.html          # Styled HTML preview page
├── imgs/                     # Created by baoyu-cover-image
│   ├── prompts/
│   │   └── cover.md          # Cover image prompt
│   └── cover.png             # Generated cover (moved to _attachments/)
└── _attachments/             # Obsidian-style attachments folder
    ├── cover-xhs.png         # Cover image (moved from imgs/cover.png)
    ├── xhs-01.png            # Screenshot page 1
    ├── xhs-02.png            # Screenshot page 2
    └── ...
```

## Customization

### Custom Prompt Templates

Create custom styling templates in the `prompts/` directory:

1. Create a new `.md` file (e.g., `prompts/minimal.md`)
2. Define your HTML/CSS specifications
3. Invoke with: "Use the minimal template for this article"

### Modifying Styles

Edit `prompts/default.md` to customize:
- Card dimensions and colors
- Font families and sizes
- Typography hierarchy
- Code block styling
- Responsive breakpoints

## Configuration

### Screenshot Settings

Default screenshot dimensions (3:4 ratio for Xiaohongshu):
- Width: 1080px
- Height: 1440px
- Scale factor: 2x (Retina quality)

To modify, edit `scripts/screenshot.py`:
```python
SCREENSHOT_WIDTH = 1080
SCREENSHOT_HEIGHT = 1440
```

## Scripts

### screenshot.py

Captures sequential screenshots of HTML pages.

```bash
python scripts/screenshot.py ~/Dev/obsidian/articles/<date>-<title>/xhs-preview.html
```

Output: `~/Dev/obsidian/articles/<date>-<title>/_attachments/xhs-01.png`, `xhs-02.png`, etc.

Features:
- Automatic page scrolling
- Smart text boundary detection
- No text cut-off at boundaries
- 3:4 aspect ratio output

## Troubleshooting

### Cover Image Issues

- Ensure `/baoyu-cover-image` skill is installed and working
- Check that the skill has proper access to image generation models
- Try running `/baoyu-cover-image` directly to debug

### Screenshot Issues

- Install Playwright browsers: `playwright install chromium`
- Check file paths are correct
- Ensure HTML file is valid and accessible

### Font Loading

If fonts don't load in screenshots:
- Increase wait time in `screenshot.py`
- Check Google Fonts availability
- Consider using local fonts

## License

MIT License - See LICENSE file for details.

## Related Skills

- `baoyu-cover-image` - Cover image generation (required dependency)
- `chinese-viral-writer` - Chinese viral content creation
- `wechat-article-formatter` - WeChat article formatting
- `wechat-article-publisher` - WeChat publishing automation
