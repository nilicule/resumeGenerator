import os

import click
from dotenv import load_dotenv

from lib import pdf_parser, generator

load_dotenv()


@click.group()
def cli():
    """Resume generator CLI."""
    pass


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, type=click.Path(), help="Output YAML path.")
def parse(pdf_path, output):
    """Parse a LinkedIn PDF export into a YAML resume."""
    if output is None:
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        directory = os.path.dirname(pdf_path) or "."
        output = os.path.join(directory, base + ".yaml")

    try:
        yaml_str = pdf_parser.parse_pdf(pdf_path)
    except Exception as exc:
        raise SystemExit(f"Error: {exc}")

    with open(output, "w", encoding="utf-8") as f:
        f.write(yaml_str)

    click.echo(f"Wrote {output}")


@cli.command()
@click.argument("yaml_path", type=click.Path(exists=True))
@click.option(
    "-f", "--format",
    "fmt",
    type=click.Choice(["html", "pdf", "both"], case_sensitive=False),
    default="both",
    show_default=True,
    help="Output format: html, pdf, or both.",
)
def generate(yaml_path, fmt):
    """Generate an HTML and/or PDF resume from a YAML file."""
    try:
        written = generator.generate(yaml_path, formats=fmt)
    except Exception as exc:
        raise SystemExit(f"Error: {exc}")

    for path in written:
        click.echo(f"Wrote {path}")


if __name__ == "__main__":
    cli()
