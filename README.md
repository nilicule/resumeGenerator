# resume

A CLI tool that turns a LinkedIn PDF export into a polished CV. It uses the Claude API to parse the PDF into structured YAML, then renders that YAML into a clean HTML and PDF resume.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- macOS: native libraries for weasyprint — `brew install pango`

> **macOS tip:** if you get `cannot load library 'libgobject-2.0'` when running `generate`, run:
> ```bash
> export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
> ```

## Setup

```bash
git clone <repo>
cd resumeGenerator
uv sync
```

Create a `.env` file in the project root with your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

The `.env` file is gitignored and must be created manually.

## Usage

### 1. Export your LinkedIn profile as PDF

Go to your LinkedIn profile page → click **More** → **Save to PDF**. This downloads a PDF of your public profile.

### 2. Parse the PDF into YAML

```bash
uv run resume.py parse path/to/linkedin.pdf
```

This calls the Claude API and writes a structured YAML file alongside the PDF (e.g. `linkedin.yaml`).

To specify a custom output path:

```bash
uv run resume.py parse path/to/linkedin.pdf -o my_resume.yaml
```

You can review and edit the YAML before generating the final document.

### 3. Generate HTML and PDF

```bash
uv run resume.py generate my_resume.yaml
```

This writes `my_resume.html` and `my_resume.pdf` in the same directory as the YAML file. The generate command works offline — no API key is required.

To generate only HTML (no system PDF libraries required):

```bash
uv run resume.py generate my_resume.yaml --format html
```

## Project structure

```
resumeGenerator/
├── resume.py            # CLI entry point — defines the `parse` and `generate` commands
├── lib/
│   ├── pdf_parser.py    # Extracts text from a PDF and calls the Claude API to produce YAML
│   └── generator.py     # Renders a YAML CV into a self-contained HTML and PDF file
├── pyproject.toml       # Project metadata and dependencies
└── uv.lock              # Locked dependency versions
```
