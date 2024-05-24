import json
import traceback
from datetime import datetime
import click
from pathlib import Path
from magic_doc.docconv import DocConverter
from loguru import logger

s3_config_path = '~/magic-doc.json'
log_level = "ERROR"
if not Path("magic_doc/logs/").exists():
    Path("magic_doc/logs/").mkdir(parents=True, exist_ok=True)
log_name = f'log_{datetime.now().strftime("%Y-%m-%d")}.log'
log_file_path = "magic_doc/logs/" + log_name
logger.add(str(log_file_path), rotation='00:00', encoding='utf-8', level=log_level, enqueue=True)


def abort(message=None, exit_code=1):
    click.echo(click.style(message, fg='red'))
    exit(exit_code)


def get_s3_config(s3_config_key):
    with open(Path(s3_config_path).expanduser(), 'r') as f:
        return json.load(f)[s3_config_key]


@click.command()
@click.option('-s', '--s3cfg', 's3_config_key', type=click.STRING, help='s3 config')
@click.option('-f', '--file-path', 'doc_path', type=click.STRING, help='file path')
@click.option('-p', '--progress-file-path', 'progress_file_path', default="", type=click.STRING, help='path to the progress file to save')
@click.option('-t', '--conv-timeout', 'conv_timeout', default=60, type=click.INT, help='timeout')
def cli_conv(doc_path, progress_file_path, conv_timeout=None, s3_config_key=None):
    try:
        if s3_config_key:
            try:
                s3_config = get_s3_config(s3_config_key)[s3_config_path]
            except KeyError:
                logger.error(f"Error: argument '--s3cfg' is error.")
                abort(f"Error: argument '--s3cfg' is error.")
        else:
            s3_config = None
        if not doc_path:
            logger.error(f"Error: Missing argument '--file-path'.")
            abort(f"Error: Missing argument '--file-path'.")
        if not progress_file_path:
            progress_file_path = f"/tmp/{doc_path}.txt"
        docconv = DocConverter(s3_config)
        markdown_string = docconv.convert(doc_path, progress_file_path, conv_timeout)
        click.echo(markdown_string)
    except Exception as e:
        logger.error(traceback.format_exc())
        abort(f'Error: {traceback.format_exc()}')


if __name__ == '__main__':
    cli_conv()
