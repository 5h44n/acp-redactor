import click
from .redactor import Redactor
import os
import pymupdf


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--redact', '-r', multiple=True, help='Text to redact. Can be used multiple times.')
@click.option('--output', '-o', help='Output file name. If not provided, a default name will be generated.')
def main(input_file, redact, output):
    """Redact specified text from a PDF file."""
    if not redact:
        click.echo("No text specified for redaction. Use --redact option.")
        return

    click.echo(f"Redacting {len(redact)} text item(s) from {input_file}")
    
    redactor = Redactor(input_file, list(redact))
    output_file = redactor.redact()
    
    if output:
        os.rename(output_file, output)
        output_file = output

    click.echo(f"Redacted PDF saved as: {output_file}")

if __name__ == '__main__':
    main()
