import click
from .redactor import Redactor
import os


@click.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--attorney', '-a', help='Attorney email address.')
@click.option('--client', '-c', help='Client email address.')
@click.option('--output', '-o', help='Output file name. If not provided, a default name will be generated.')
def main(file, attorney, client, output):
    """Redact specified text from a PDF file."""
    if not attorney or not client:
        click.echo("Please provide both attorney and client email addresses.")
        return

    click.echo(f"Redacting conversations between attorney:{attorney} and client:{client}  from {file}\n")
    
    redactor = Redactor(file, attorney=attorney, client=client)
    output_file = redactor.redact()
    
    if output:
        os.rename(output_file, output)
        output_file = output

    click.echo(f"Redacted PDF saved as: {output_file}")

if __name__ == '__main__':
    main()
