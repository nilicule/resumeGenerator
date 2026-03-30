"""generator.py — Render a YAML CV data file into HTML and PDF."""

import html
import os
import yaml


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def _e(value) -> str:
    """HTML-escape a value that may be None or non-string."""
    if value is None:
        return ""
    return html.escape(str(value))


def render_html(data: dict) -> str:
    """Build and return a complete, self-contained HTML string for a CV."""

    personal: dict = data.get("personal") or {}
    summary: str = (data.get("summary") or "").strip()
    experience: list = data.get("experience") or []
    education: list = data.get("education") or []
    skills: dict = data.get("skills") or {}
    languages: list = data.get("languages") or []
    certifications: list = personal.get("certifications") or []

    # ------------------------------------------------------------------
    # CSS
    # ------------------------------------------------------------------
    css = """
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, "Segoe UI", "Helvetica Neue", sans-serif;
            font-size: 11px;
            line-height: 1.5;
            color: #222;
            background: #fff;
            max-width: 800px;
            margin: 0 auto;
            padding: 36px 40px;
        }
        /* ---- Header ---- */
        #header { margin-bottom: 14px; }
        #header h1 {
            font-size: 26px;
            font-weight: 700;
            color: #222;
            margin-bottom: 2px;
        }
        #header .title {
            font-size: 13px;
            color: #555;
            margin-bottom: 6px;
        }
        #header .contact {
            font-size: 10px;
            color: #444;
        }
        #header .contact span { margin-right: 14px; }
        .header-rule {
            border: none;
            border-top: 2px solid #2c4a7c;
            margin: 10px 0 18px 0;
        }
        /* ---- Sections ---- */
        .section { margin-bottom: 16px; }
        .section-rule {
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 10px 0 10px 0;
        }
        .section-title {
            font-size: 11px;
            font-variant: small-caps;
            letter-spacing: 0.1em;
            color: #2c4a7c;
            font-weight: 700;
            text-transform: lowercase;
            margin-bottom: 8px;
        }
        /* ---- Experience ---- */
        .job { margin-bottom: 10px; }
        .job-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }
        .job-title { font-weight: 700; font-size: 11px; }
        .job-meta { font-size: 10px; color: #555; text-align: right; }
        .job-company { font-size: 11px; color: #444; margin-bottom: 2px; }
        .job ul { margin: 4px 0 0 16px; }
        .job ul li { margin-bottom: 2px; }
        /* ---- Education ---- */
        .edu-entry { margin-bottom: 6px; }
        .edu-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }
        .edu-degree { font-weight: 700; }
        .edu-year { font-size: 10px; color: #555; }
        .edu-institution { font-size: 10px; color: #444; }
        /* ---- Skills ---- */
        .skill-row { margin-bottom: 3px; }
        .skill-category { font-weight: 700; }
        /* ---- Languages / Certifications ---- */
        .lang-list { }
        .cert-list { }
        .cert-list li, .lang-list li {
            list-style: none;
            display: inline;
        }
        .cert-list li::after, .lang-list li::after { content: " · "; }
        .cert-list li:last-child::after, .lang-list li:last-child::after { content: ""; }
    """

    # ------------------------------------------------------------------
    # Helper: section wrapper
    # ------------------------------------------------------------------
    def section(title: str, inner_html: str) -> str:
        return (
            f'<hr class="section-rule">'
            f'<div class="section">'
            f'<div class="section-title">{_e(title)}</div>'
            f'{inner_html}'
            f'</div>'
        )

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    contact_parts = []
    if personal.get("email"):
        contact_parts.append(f'<span>&#9993; {_e(personal["email"])}</span>')
    if personal.get("phone"):
        contact_parts.append(f'<span>&#9742; {_e(personal["phone"])}</span>')
    if personal.get("location"):
        contact_parts.append(f'<span>&#9679; {_e(personal["location"])}</span>')
    if personal.get("linkedin"):
        linkedin_val = personal["linkedin"]
        if linkedin_val.startswith("https://") or linkedin_val.startswith("http://"):
            linkedin_display = f'<a href="{linkedin_val}" style="color: #2c4a7c;">{_e(linkedin_val)}</a>'
        else:
            linkedin_display = _e(linkedin_val)
        contact_parts.append(f'<span>&#128279; {linkedin_display}</span>')

    header_html = (
        f'<div id="header">'
        f'<h1>{_e(personal.get("name", ""))}</h1>'
    )
    if personal.get("title"):
        header_html += f'<div class="title">{_e(personal["title"])}</div>'
    if contact_parts:
        header_html += f'<div class="contact">{"".join(contact_parts)}</div>'
    header_html += '</div>'
    header_html += '<hr class="header-rule">'

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    summary_html = ""
    if summary:
        summary_html = section("Summary", f'<p>{_e(summary)}</p>')

    # ------------------------------------------------------------------
    # Experience
    # ------------------------------------------------------------------
    experience_html = ""
    if experience:
        jobs_html = ""
        for job in experience:
            company = _e(job.get("company", ""))
            job_title = _e(job.get("title", ""))
            start = _e(job.get("start", ""))
            end_val = job.get("end", "")
            end = _e(end_val) if end_val else "Present"
            location = _e(job.get("location", ""))
            highlights = job.get("highlights") or []

            date_range = f"{start} – {end}" if start else end
            meta_parts = [date_range]
            if location:
                meta_parts.append(location)

            highlights_html = ""
            if highlights:
                items = "".join(f"<li>{_e(h)}</li>" for h in highlights)
                highlights_html = f"<ul>{items}</ul>"

            jobs_html += (
                f'<div class="job">'
                f'<div class="job-header">'
                f'<div class="job-title">{job_title}</div>'
                f'<div class="job-meta">{" &nbsp;|&nbsp; ".join(meta_parts)}</div>'
                f'</div>'
                f'<div class="job-company">{company}</div>'
                f'{highlights_html}'
                f'</div>'
            )
        experience_html = section("Experience", jobs_html)

    # ------------------------------------------------------------------
    # Education
    # ------------------------------------------------------------------
    education_html = ""
    if education:
        edu_items = ""
        for edu in education:
            institution = _e(edu.get("institution", ""))
            degree = _e(edu.get("degree", ""))
            year = _e(edu.get("year", ""))
            edu_items += (
                f'<div class="edu-entry">'
                f'<div class="edu-header">'
                f'<div class="edu-degree">{degree}</div>'
                f'<div class="edu-year">{year}</div>'
                f'</div>'
                f'<div class="edu-institution">{institution}</div>'
                f'</div>'
            )
        education_html = section("Education", edu_items)

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------
    skills_html = ""
    if skills:
        rows = ""
        for category, items in skills.items():
            if items:
                items_str = ", ".join(_e(i) for i in items)
                rows += (
                    f'<div class="skill-row">'
                    f'<span class="skill-category">{_e(category)}:</span> {items_str}'
                    f'</div>'
                )
        if rows:
            skills_html = section("Skills", rows)

    # ------------------------------------------------------------------
    # Languages
    # ------------------------------------------------------------------
    languages_html = ""
    if languages:
        items = "".join(f"<li>{_e(lang)}</li>" for lang in languages)
        languages_html = section("Languages", f'<ul class="lang-list">{items}</ul>')

    # ------------------------------------------------------------------
    # Certifications (from personal block)
    # ------------------------------------------------------------------
    certifications_html = ""
    if certifications:
        items = "".join(f"<li>{_e(cert)}</li>" for cert in certifications)
        certifications_html = section("Certifications", f'<ul class="cert-list">{items}</ul>')

    # ------------------------------------------------------------------
    # Assemble full document
    # ------------------------------------------------------------------
    body_content = (
        header_html
        + summary_html
        + experience_html
        + education_html
        + skills_html
        + languages_html
        + certifications_html
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_e(personal.get("name", "CV"))}</title>
<style>
{css}
</style>
</head>
<body>
{body_content}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# File generation
# ---------------------------------------------------------------------------

def generate(yaml_path: str, formats: str = "both") -> list[str]:
    """Load a YAML CV file and write outputs alongside it.

    formats: "html", "pdf", or "both" (default).
    Returns a list of paths that were written.
    """
    try:
        with open(yaml_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise SystemExit(f"Error: Failed to parse YAML in '{yaml_path}': {exc}")

    if not isinstance(data, dict):
        raise SystemExit(f"Error: '{yaml_path}' is empty or not a valid YAML document.")

    html_string = render_html(data)
    base, _ = os.path.splitext(yaml_path)
    written = []

    if formats in ("html", "both"):
        html_path = base + ".html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html_string)
        written.append(html_path)

    if formats in ("pdf", "both"):
        import weasyprint  # lazy import — only needed for PDF generation
        pdf_path = base + ".pdf"
        weasyprint.HTML(
            string=html_string,
            base_url=os.path.dirname(os.path.abspath(yaml_path)),
        ).write_pdf(pdf_path)
        written.append(pdf_path)

    return written
