import json
import re
import traceback
from datetime import datetime
import click
from pathlib import Path
from magic_doc.docconv import DocConverter, S3Config
from loguru import logger
from s3pathlib import S3Path

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


def get_s3_config(bucket_name: str):
    with open(Path(s3_config_path).expanduser(), 'r') as f:
        s3_config_json = json.load(f)
        bucket_info = s3_config_json.get("bucket_info")
        return bucket_info.get(bucket_name)


def remove_non_official_s3_args(s3path):
    """
    example: s3://abc/xxxx.json?bytes=0,81350 ==> s3://abc/xxxx.json
    """
    arr = s3path.split("?")
    return arr[0]


def parse_s3path(s3path: str):
    p = S3Path(remove_non_official_s3_args(s3path))
    return p.bucket, p.key


@click.command()
@click.option('-f', '--file-path', 'doc_path', type=click.STRING, help='file path')
@click.option('-p', '--progress-file-path', 'progress_file_path', default="", type=click.STRING,
              help='path to the progress file to save')
@click.option('-t', '--conv-timeout', 'conv_timeout', default=60, type=click.INT, help='timeout')
def cli_conv(doc_path, progress_file_path, conv_timeout=None):
    try:
        s3_config = None
        if not doc_path:
            logger.error(f"Error: Missing argument '--file-path'.")
            abort(f"Error: Missing argument '--file-path'.")
        else:
            if doc_path.startswith("s3://"):
                bucket, key = parse_s3path(doc_path)
                ak, sk, endpoint = get_s3_config(bucket)
                s3_config = S3Config(ak, sk, endpoint)
        if not progress_file_path:
            file_name = str(Path(doc_path).stem)
            progress_file_path = f"/tmp/{file_name}.txt"
        doc_conv = DocConverter(s3_config)
        markdown_string = doc_conv.convert(doc_path, progress_file_path, conv_timeout)
        click.echo(markdown_string)
    except Exception as e:
        logger.error(traceback.format_exc())
        abort(f'Error: {traceback.format_exc()}')


if __name__ == '__main__':
    cli_conv()
