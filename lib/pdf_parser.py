"""
pdf_parser.py – Extract text from a PDF resume and parse it into structured YAML
via the Anthropic Claude API.

Note: load_dotenv() is intentionally NOT called here; that is handled in resume.py.
"""

import os
import sys

import anthropic
import pdfplumber
import yaml

SYSTEM_PROMPT = """\
You are a resume parser. Extract all information from the provided resume text and \
output ONLY valid YAML — no markdown fences, no preamble, no explanation. \
Use exactly the schema below, preserving every key even if the value is empty or null.

personal:
  name:
  title:
  email:
  phone:
  location:
  linkedin:
  certifications: []

summary: >
  ...

experience:
  - company:
    title:
    start:        # YYYY-MM format
    end:          # YYYY-MM or "present"
    location:
    highlights: []

education:
  - institution:
    degree:
    year:

skills:
  category: []    # free-form categories as keys, list of strings as values

languages:
  - Language (level)
"""


def extract_text(pdf_path: str) -> str:
    """Open a PDF with pdfplumber and return all page text joined by double newlines."""
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n\n".join(pages)


def parse_pdf(pdf_path: str) -> str:
    """Extract text from a PDF and parse it into a YAML string via the Claude API.

    Returns the raw YAML string (not the parsed dict).
    Exits with an error message if ANTHROPIC_API_KEY is not set.
    Raises ValueError if the API response is not valid YAML.
    """
    raw_text = extract_text(pdf_path)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "Error: ANTHROPIC_API_KEY is not set. "
            "Add it to .env or export it in your shell."
        )

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": raw_text},
        ],
    )

    if message.stop_reason == "max_tokens":
        raise RuntimeError(
            "Claude response was truncated (max_tokens reached). "
            "The resume may be too long — try reducing content or contact the "
            "developer to increase max_tokens."
        )
    if not message.content or message.content[0].type != "text":
        received = (
            f"content blocks of types {[b.type for b in message.content]}"
            if message.content
            else "empty content"
        )
        raise RuntimeError(
            f"Unexpected Claude API response: expected a text content block, "
            f"got {received} (stop_reason={message.stop_reason!r})."
        )
    yaml_text: str = message.content[0].text

    # Strip markdown fences if the model included them despite instructions
    if yaml_text.startswith("```"):
        lines = yaml_text.splitlines()
        yaml_text = "\n".join(
            line for line in lines if not line.startswith("```")
        ).strip()

    try:
        yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Claude returned invalid YAML. Parse error: {exc}\n\nRaw response:\n{yaml_text}"
        ) from exc

    return yaml_text
