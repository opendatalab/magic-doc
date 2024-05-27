import json
import os
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
    从 ~/magic-doc.json 读取配置
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


def prepare_env(doc_file_name, doc_type="") -> str:
    if doc_type == "":
        doc_type = "unknown"
    local_parent_dir = os.path.join(
        get_local_dir(), "magic-doc", doc_type, doc_file_name
    )

    # local_image_dir = os.path.join(local_parent_dir, "images")
    local_md_dir = local_parent_dir
    # os.makedirs(local_image_dir, exist_ok=True)
    os.makedirs(local_md_dir, exist_ok=True)
    return str(local_md_dir)


def remove_non_official_s3_args(s3path):
    """
    example: s3://abc/xxxx.json?bytes=0,81350 ==> s3://abc/xxxx.json
    """
    arr = s3path.split("?")
    return arr[0]


def parse_s3path(s3path: str):
    p = S3Path(remove_non_official_s3_args(s3path))
    return p.bucket, p.key


total_error_files = 0
total_cost_time = 0


@click.command()
@click.option('-f', '--file-path', 'input_file_path', type=click.STRING,
              help='file path, support s3/local/list, list file need end with ".list"')
@click.option('-p', '--progress-file-path', 'progress_file_path', default="", type=click.STRING,
              help='path to the progress file to save')
@click.option('-t', '--conv-timeout', 'conv_timeout', default=60, type=click.INT, help='timeout')
def cli_conv(input_file_path, progress_file_path, conv_timeout=None):

    def parse_doc(doc_path, pf_path=None):
        """使用两个全局变量统计耗时和error数量"""
        global total_cost_time
        global total_error_files
        try:
            '''创建同名进度缓存文件'''
            if not pf_path:
                file_name = str(Path(doc_path).stem)
                pf_path = f"/tmp/{file_name}.txt"
            '''如果文档路径为s3链接，先获取s3配置并初始化'''
            if doc_path.startswith("s3://"):
                bucket, key = parse_s3path(doc_path)
                ak, sk, endpoint = get_s3_config(bucket)
                s3_config = S3Config(ak, sk, endpoint)
            else:
                '''非s3路径不需要初始化s3配置'''
                s3_config = None
            doc_conv = DocConverter(s3_config)
            markdown_string, cost_time = doc_conv.convert(doc_path, pf_path, conv_timeout)
            total_cost_time += cost_time
            logger.info(f"convert {doc_path} to markdown, cost {cost_time} seconds")
            # click.echo(markdown_string)
            base_name, doc_type = os.path.splitext(doc_path)
            out_put_dir = prepare_env(file_name, doc_type.lstrip("."))
            with open(os.path.join(out_put_dir, file_name + ".md"), "w") as md_file:
                md_file.write(markdown_string)
            return cost_time
        except Exception as e:
            logger.error(traceback.format_exc())
            total_error_files += 1
            # abort(f'Error: {traceback.format_exc()}')

    if not input_file_path:
        logger.error(f"Error: Missing argument '--file-path'.")
        abort(f"Error: Missing argument '--file-path'.")
    else:
        '''适配多个文档的list文件输入'''
        if input_file_path.endswith(".list"):
            with open(input_file_path, "r") as f:
                for line in f.readlines():
                    line = line.strip()
                    parse_doc(line, progress_file_path)
        else:
            '''适配单个文档的输入'''
            parse_doc(input_file_path, progress_file_path)

    logger.info(f"total cost time: {int(total_cost_time)} seconds")
    logger.info(f"total error files: {total_error_files}")


if __name__ == '__main__':
    cli_conv()
