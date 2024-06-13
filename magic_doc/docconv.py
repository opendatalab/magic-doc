import os
import platform
import time
from functools import partial

import boto3
from botocore.client import Config
from func_timeout import FunctionTimedOut, func_timeout
from magic_pdf.libs.path_utils import (
    remove_non_official_s3_args,
)
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter
from magic_pdf.rw.S3ReaderWriter import S3ReaderWriter
from smart_open import open

from magic_doc.conv.base import BaseConv
from magic_doc.conv.doc_antiword import Doc as Doc_antiword
from magic_doc.conv.doc_libreoffice import Doc as Doc_libreoffice
from magic_doc.conv.docx_xml_parse import Docx
from magic_doc.conv.pdf import Pdf as fastTextPdf
from magic_doc.conv.pdf_pp_structurev2 import Pdf as liteOcrPdf
from magic_doc.conv.pdf_magicpdf import Pdf as fullPdf
from magic_doc.conv.ppt_libreoffice import Ppt
from magic_doc.conv.pptx_python_pptx import Pptx
from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.utils import is_digital


class ParsePDFType:
    FAST = "fast"
    FULL = "full"


class ConvException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class S3Config(object):
    def __init__(self, ak: str, sk: str, endpoint: str, address_style: str = "path"):
        self.ak = ak
        self.sk = sk
        self.endpoint = endpoint
        self.address_style = address_style


class DocConverter(object):
    def __init__(
        self,
        s3_config: S3Config,
        temp_dir: str = "/tmp/",
        parse_pdf_type=ParsePDFType.FAST,
        conv_timeout=60,
    ):
        self.__s3cfg = s3_config
        if self.__s3cfg:
            self.__s3cli = boto3.client(
                service_name="s3",
                aws_access_key_id=self.__s3cfg.ak,
                aws_secret_access_key=self.__s3cfg.sk,
                endpoint_url=self.__s3cfg.endpoint,
                config=Config(
                    s3={"addressing_style": "path"}, retries={"max_attempts": 8}
                ),
            )
        self.parse_pdf_type = parse_pdf_type
        self.__temp_dir = temp_dir
        self.__conv_timeout = conv_timeout
        self.__init_conv()

    def __init_conv(self):
        # 根据系统选择doc解析方式
        system = platform.system()
        if system == "Linux":
            self.doc_conv = Doc_antiword()
        else:
            self.doc_conv = Doc_libreoffice()
        self.docx_conv = Docx()
        self.full_pdf_conv = fullPdf()
        self.fast_textpdf_conv = fastTextPdf()
        self.lite_ocrpdf_conv = liteOcrPdf()
        self.ppt_conv = Ppt()
        self.pptx_conv = Pptx()

    def __select_conv(self, doc_path: str, doc_bytes: bytes):
        def check_magic_header(magic_header: bytes) -> bool:
            if doc_bytes.startswith(magic_header):
                return True
            else:
                raise ConvException("File is broken.")

        """根据文件后缀选择转换器"""
        lower_case_path = doc_path.lower()
        if lower_case_path.endswith(".doc"):
            # OLE2
            if check_magic_header(b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"):
                return self.doc_conv
        elif lower_case_path.endswith(".docx"):
            # PK
            if check_magic_header(b"\x50\x4b\x03\x04"):
                return self.docx_conv
        elif lower_case_path.endswith(".pdf"):
            # %PDF
            if check_magic_header(b"%PDF"):
                if self.parse_pdf_type == ParsePDFType.FAST:
                    if is_digital(doc_bytes):
                        return self.fast_textpdf_conv
                    else:
                        return self.lite_ocrpdf_conv
                else:
                    return self.full_pdf_conv

        elif lower_case_path.endswith(".ppt"):
            # OLE2
            if check_magic_header(b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"):
                return self.ppt_conv
        elif lower_case_path.endswith(".pptx"):
            # PK
            if check_magic_header(b"\x50\x4b\x03\x04"):
                return self.pptx_conv
        else:
            raise ConvException("Unsupported file format.")

    def __read_file_as_bytes(self, doc_path: str) -> bytes:
        """
        支持从本地文件和s3文件读取
        """
        if doc_path.startswith("s3://"):
            transport_params = {"client": self.__s3cli}
            with open(doc_path, "rb", transport_params=transport_params) as fin:
                content_bytes = fin.read()
                return content_bytes
        else:
            with open(doc_path, "rb") as fin:
                content_bytes = fin.read()
                return content_bytes

    def _timeout_convert(
        self,
        byte_content: bytes,
        progress_file_path: str,
        conv_method,
        conv_timeout=None,
    ):
        """
        在线快速解析
        doc_path: str, path to the document, support local file path and s3 path.
        progress_file_path: str, path to the progress file, support local file path only.
        return markdown string or raise ConvException.
        """
        conv_timeout = conv_timeout or self.__conv_timeout  # 根据这个时间判断函数超时
        res = ""
        cost_time = 0
        try:
            prog_updator = FileBaseProgressUpdator(progress_file_path)
            start_time = time.time()
            res = func_timeout(
                conv_timeout, conv_method, args=(byte_content, prog_updator)
            )
            end_time = time.time()
            cost_time = round(end_time - start_time, 3)

        except FunctionTimedOut as e1:
            # logger.exception(e1)
            raise ConvException("Convert timeout.")
        except Exception as e2:
            # logger.exception(e2)
            raise ConvException("Convert failed: %s" % str(e2))

        return res, cost_time

    def convert(self, doc_path: str, progress_file_path: str, conv_timeout=None):
        """
        在线快速解析
        doc_path: str, path to the document, support local file path and s3 path.
        progress_file_path: str, path to the progress file, support local file path only.
        return markdown string or raise ConvException.
        """
        byte_content = self.__read_file_as_bytes(doc_path)
        conv: BaseConv = self.__select_conv(doc_path, byte_content)
        return self._timeout_convert(
            byte_content, progress_file_path, conv.to_md, conv_timeout
        )

    def convert_to_mid_result(
        self, doc_path: str, progress_file_path: str, conv_timeout=None
    ):
        """
        在线快速解析
        doc_path: str, path to the document, support local file path and s3 path.
        progress_file_path: str, path to the progress file, support local file path only.
        return markdown string or raise ConvException.
        """
        byte_content = self.__read_file_as_bytes(doc_path)
        conv: BaseConv = self.__select_conv(doc_path, byte_content)

        parent_path = os.path.dirname(doc_path)
        if doc_path.startswith("s3://"):
            image_writer = S3ReaderWriter(
                self.__s3cfg.ak,
                self.__s3cfg.sk,
                self.__s3cfg.endpoint,
                "auto",
                os.path.join(
                    os.path.dirname(remove_non_official_s3_args(doc_path)), "images"
                ),
            )
        else:
            image_writer = DiskReaderWriter(os.path.join(parent_path, "images"))

        return self._timeout_convert(
            byte_content,
            progress_file_path,
            partial(conv.to_mid_result, image_writer),
            conv_timeout,
        )
