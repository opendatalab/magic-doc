import json
import os
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


def read_config():
    home_dir = os.path.expanduser("~")

    config_file = os.path.join(home_dir, "magic-doc.json")

    if not os.path.exists(config_file):
        raise Exception(f"{config_file} not found")

    with open(config_file, "r") as f:
        config = json.load(f)
    return config


def get_s3_config(bucket_name: str):
    """
    ~/magic-pdf.json 读出来
    """
    config = read_config()

    bucket_info = config.get("bucket_info")
    if bucket_name not in bucket_info:
        access_key, secret_key, storage_endpoint = bucket_info["[default]"]
    else:
        access_key, secret_key, storage_endpoint = bucket_info[bucket_name]

    if access_key is None or secret_key is None or storage_endpoint is None:
        raise Exception("ak, sk or endpoint not found in magic-doc.json")

    # logger.info(f"get_s3_config: ak={access_key}, sk={secret_key}, endpoint={storage_endpoint}")

    return access_key, secret_key, storage_endpoint


def get_local_dir():
    config = read_config()
    return config.get("temp-output-dir", "/tmp")


def prepare_env(doc_file_name):
    local_parent_dir = os.path.join(
        get_local_dir(), "magic-doc", doc_file_name
    )

    # local_image_dir = os.path.join(local_parent_dir, "images")
    local_md_dir = local_parent_dir
    # os.makedirs(local_image_dir, exist_ok=True)
    os.makedirs(local_md_dir, exist_ok=True)
    return local_md_dir


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
        # click.echo(markdown_string)
        with open(os.path.join(prepare_env(file_name), file_name), "w") as f:
            f.write(markdown_string)
    except Exception as e:
        logger.error(traceback.format_exc())
        abort(f'Error: {traceback.format_exc()}')


if __name__ == '__main__':
    cli_conv()
