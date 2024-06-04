import os
import traceback
from datetime import datetime
import click
from pathlib import Path
from magic_doc.libs.version import __version__

from magic_doc.utils.config import get_s3_config
from magic_doc.utils.path_utils import get_local_dir, parse_s3path, prepare_env
from magic_doc.docconv import DocConverter, S3Config, ParsePDFType
from loguru import logger

log_level = "ERROR"
log_dir = os.path.join(get_local_dir(), "magic-doc", "logs")
if not Path(log_dir).exists():
    Path(log_dir).mkdir(parents=True, exist_ok=True)
log_name = f'log_{datetime.now().strftime("%Y-%m-%d")}.log'
log_file_path = os.path.join(log_dir, log_name)
logger.add(str(log_file_path), rotation='00:00', encoding='utf-8', level=log_level, enqueue=True)


def abort(message=None, exit_code=1):
    click.echo(click.style(message, fg='red'))
    exit(exit_code)


total_cost_time = 0
total_convert_error = 0
total_file_broken = 0
total_unsupported_files = 0
total_time_out = 0
total_success_convert = 0


@click.command()
@click.version_option(__version__, "--version", "-v", help="显示版本信息")
@click.option('-f', '--file-path', 'input_file_path', type=click.STRING,
              help='file path, support s3/local/list, list file need end with ".list"')
@click.option('-p', '--progress-file-path', 'progress_file_path', default="", type=click.STRING,
              help='path to the progress file to save')
@click.option('-t', '--conv-timeout', 'conv_timeout', default=60, type=click.INT, help='timeout')
@click.option('-m', "--mode", "parse_mode", type=click.Choice([ParsePDFType.FAST, ParsePDFType.FULL]), default=ParsePDFType.FAST, help="fast: without math formula, full: with math formula")
def cli_conv(input_file_path, progress_file_path, parse_mode, conv_timeout=None):
    global total_cost_time, total_convert_error, total_file_broken, \
        total_unsupported_files, total_time_out, total_success_convert

    def parse_doc(doc_path, pf_path=None):
        """使用全局变量统计耗时和error数量"""
        global total_cost_time, total_convert_error, total_file_broken, \
            total_unsupported_files, total_time_out, total_success_convert
        try:
            file_name = str(Path(doc_path).stem)
            '''创建同名进度缓存文件'''
            if not pf_path:
                pf_path = f"/tmp/{file_name}.txt"
            '''如果文档路径为s3链接，先获取s3配置并初始化'''
            if doc_path.startswith("s3://"):
                bucket, key = parse_s3path(doc_path)
                ak, sk, endpoint = get_s3_config(bucket)
                s3_config = S3Config(ak, sk, endpoint)
            else:
                '''非s3路径不需要初始化s3配置'''
                s3_config = None
            doc_conv = DocConverter(s3_config, parse_pdf_type=parse_mode)
            markdown_string, cost_time = doc_conv.convert(doc_path, pf_path, conv_timeout)
            total_cost_time += cost_time
            logger.info(f"convert {doc_path} to markdown, cost {cost_time} seconds")
            # click.echo(markdown_string)
            base_name, doc_type = os.path.splitext(doc_path)
            out_put_dir = prepare_env(file_name, doc_type.lstrip(".").lower())
            with open(os.path.join(out_put_dir, file_name + ".md"), "w", encoding='utf-8') as md_file:
                md_file.write(markdown_string)
            total_success_convert += 1
            return cost_time
        except Exception as e:
            logger.error(traceback.format_exc())
            # 只统计转换出错的数量
            if "Convert failed" in str(e):
                total_convert_error += 1
            elif "Convert timeout" in str(e):
                total_time_out += 1
            elif "File is broken" in str(e):
                total_file_broken += 1
            elif "Unsupported file format" in str(e):
                total_unsupported_files += 1
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
    logger.info(f"total convert error: {total_convert_error}")
    logger.info(f"total file broken: {total_file_broken}")
    logger.info(f"total unsupported files: {total_unsupported_files}")
    logger.info(f"total time out: {total_time_out}")
    logger.info(f"total success: {total_success_convert}")


if __name__ == '__main__':
    cli_conv()
