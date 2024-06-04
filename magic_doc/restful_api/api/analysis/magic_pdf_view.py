import json
import re
import time
import requests
from flask import request, current_app
from flask_restful import Resource
from marshmallow import ValidationError
from pathlib import Path
from magic_doc.pdf_transform import DocConverter, S3Config
from .serialization import MagicPdfSchema
from magic_pdf.dict2md.ocr_mkcontent import ocr_mk_mm_markdown_with_para_and_pagination
from magic_doc.restful_api.common.oss.oss import Oss
from .ext import upload_image_to_oss, upload_md_to_oss
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from magic_doc.restful_api.common.custom_response import generate_response
from loguru import logger

executor = ThreadPoolExecutor()


class MagicPdfView(Resource):
    @logger.catch
    def post(self):
        """
        PDF解析，将markdown结果上传至服务器
        """
        t0 = time.time()
        magic_pdf_schema = MagicPdfSchema()
        try:
            params = magic_pdf_schema.load(request.get_json())
        except ValidationError as err:
            return generate_response(code=400, msg=err.messages)
        pdf_path = params.get('pageUrl')
        # ############ pdf解析  ###############
        file_name = str(Path(pdf_path).stem)
        pf_path = f"/tmp/{file_name}.txt"
        pdf_dir = f"{current_app.static_folder}/pdf/{file_name}"
        NULL_IMG_DIR = f"{current_app.static_folder}/pdf/{file_name}"
        app_config = current_app.config
        if not Path(NULL_IMG_DIR).exists():
            Path(NULL_IMG_DIR).mkdir(parents=True, exist_ok=True)
        if pdf_path.startswith("http://") or pdf_path.startswith("https://"):
            download_pdf = requests.get(pdf_path, stream=True)
            pdf_path = f"{pdf_dir}/{file_name}.pdf"
            with open(pdf_path, "wb") as wf:
                wf.write(download_pdf.content)
            doc_conv = DocConverter(None)
        elif pdf_path.startswith("s3://"):
            s3_config = S3Config(app_config["S3AK"], app_config["S3SK"], app_config["S3ENDPOINT"])
            doc_conv = DocConverter(s3_config)
        else:
            doc_conv = DocConverter(None)
        t1 = time.time()
        logger.info(f"param init cost_time:{t1 - t0}")
        result = doc_conv.convert_to_mid_result(pdf_path, pf_path, 60)
        t2 = time.time()
        logger.info(f"pdf doc_conv cost_time:{t2 - t1}")
        md_content = json.dumps(ocr_mk_mm_markdown_with_para_and_pagination(result[0], NULL_IMG_DIR), ensure_ascii=False)
        t3 = time.time()
        logger.info(f"make markdown cost_time:{t3 - t2}")
        # local_md_path = f"{pdf_dir}/{file_name}.md"
        # with open(local_md_path, "w", encoding="utf-8") as f:
        #     f.write(md_content)
        # t4 = time.time()
        # logger.info(f"save markdown cost_time:{t4 - t3}")
        _t0 = time.time()
        oss_client = Oss(
            app_config["AccessKeyID"],
            app_config["AccessKeySecret"],
            app_config["BucketName"],
            app_config["Endpoint"],
            app_config["UrlExpires"]
        )
        img_list = Path(f"{NULL_IMG_DIR}/images").glob('*') if Path(f"{NULL_IMG_DIR}/images").exists() else []
        all_task = [executor.submit(upload_image_to_oss, oss_client, file_name, img_path, NULL_IMG_DIR, app_config["BucketName"]) for img_path in img_list]
        wait(all_task, return_when=ALL_COMPLETED)
        for task in all_task:
            task_result = task.result()
            regex = re.compile(fr'.*\((.*?{Path(task_result[0]).name})')
            regex_result = regex.search(md_content)
            if regex_result:
                md_content = md_content.replace(regex_result.group(1), task_result[1])
        _t1 = time.time()
        logger.info(f"upload img cost_time:{_t1 - _t0}")

        all_md_task = [executor.submit(upload_md_to_oss, oss_client, app_config["BucketName"], f"pdf/{file_name}/{md.get('page_no', n)}.md", md["md_content"]) for n, md in enumerate(json.loads(md_content))]
        wait(all_md_task, return_when=ALL_COMPLETED)
        md_link_list = []
        for task in all_md_task:
            task_result = task.result()
            md_link_list.append(task_result)
        _t2 = time.time()
        logger.info(f"upload md cost_time:{_t2 - _t1}")

        return generate_response(markDownUrl=md_link_list)
