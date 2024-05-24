import json
import traceback
import click
from magic_doc.docconv import DocConverter


def abort(message=None, exit_code=1):
    click.echo(click.style(message, fg='red'))
    exit(exit_code)


class S3ConfigType(click.ParamType):
    name = "s3_config"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except ValueError:
            self.fail(f"{value!r} is not a valid json", param, ctx)


@click.command()
@click.argument('doc_path', type=click.Path(exists=True), required=True)
@click.option('-p', '--progress_file_path', default="", type=click.STRING, help='Path to the progress file to save')
@click.option('-t', '--conv_timeout', default=60, type=click.INT, help='Timeout')
@click.option('-s3', '--s3_config', default=None, type=S3ConfigType(), help='S3 configuration')
def cli_conv(doc_path, progress_file_path, conv_timeout=None, s3_config=None):
    try:
        docconv = DocConverter(s3_config)
        markdown_string = docconv.convert(doc_path, progress_file_path, conv_timeout)
        click.echo(markdown_string)
    except Exception as e:
        abort(f'Error: {traceback.format_exc()}')


if __name__ == '__main__':
    cli_conv()
