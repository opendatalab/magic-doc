import os
from func_timeout import func_timeout, FunctionTimedOut
from loguru import logger
import boto3
from botocore.client import Config
from magic_doc.conv.base import BaseConv
from magic_doc.conv.doc_antiword import Doc
from magic_doc.conv.docx_xml_parse import Docx
from magic_doc.conv.pdf import Pdf
from smart_open import open



MODEL_LAYOUT_PATH_VAR = "MAGIC_DOC_LAYOUT_MODEL_PATH" # 模型路径环境变量
MODEL_EQUATION_RECOG_PATH_VAR = "MAGIC_DOC_EQUATION_RECOG_MODEL_PATH" # 公式识别模型路径环境变量
MODEL_EQUATION_DETECT_PATH_VAR = "MAGIC_DOC_EQUATION_DETECT_MODEL_PATH" # 公式检测模型路径环境变量




class ConvException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    


class S3Config(object):
    def __init__(self, ak:str, sk:str, endpoint:str, address_style:str="path"):
        self.ak = ak
        self.sk = sk
        self.endpoint = endpoint
        self.address_style = address_style
    

class DocConverter(object):
    def __init__(self, s3_config:S3Config, temp_dir:str='/tmp/', conv_timeout=60):
        """
        初始化一次，多次调用convert方法。避免模型加载和构造s3client的性能开销。
        """
        self.__s3cfg = s3_config
        if self.__s3cfg:
            self.__s3cli = boto3.client(
            "s3",
            aws_access_key_id=self.__s3cfg.ak,
            aws_secret_access_key=self.__s3cfg.sk,
            endpoint_url=self.__s3cfg.endpoint,
            config=Config(s3={"addressing_style": "path"}, retries={"max_attempts": 8}),
        )
        self.__temp_dir = temp_dir
        self.__conv_timeout = conv_timeout # 转换超时时间，单位秒      
        
        """
        从环境变量加载模型路径
        """  
        self.__model_equation_recog_path = os.getenv(MODEL_EQUATION_RECOG_PATH_VAR)
        self.__model_equation_detect_path = os.getenv(MODEL_EQUATION_DETECT_PATH_VAR)
        self.__model_layout_path = os.getenv(MODEL_LAYOUT_PATH_VAR)
        # if not self.__model_equation_recog_path or not self.__model_equation_detect_path or not self.__model_layout_path:
        #     raise ConvException("Model path not found in environment variables: %s, %s, %s" % (MODEL_EQUATION_RECOG_PATH_VAR, MODEL_EQUATION_DETECT_PATH_VAR, MODEL_LAYOUT_PATH_VAR))
        # else:
        #     pass # TODO 初始化模型
        
        ############################
        # 初始化转换器，每个只实例化一次
        self.__init_conv()
        
        
    def __init_conv(self):
        self.docconv = Doc()
        self.docx_conv = Docx()
        self.pdf_conv = Pdf()
        
    def __select_conv(self, doc_path:str):
        """根据文件后缀选择转换器"""
        lower_case_path = doc_path.lower()
        if lower_case_path.endswith(".doc"):
            return self.docconv
        elif lower_case_path.endswith(".docx"):
            return self.docx_conv
        elif lower_case_path.endswith(".pdf"):
            return self.pdf_conv
        else:
            raise ConvException("Unsupported file format.")
        
    def __read_file_as_bytes(self, doc_path:str):
        """
        支持从本地文件和s3文件读取
        """
        if doc_path.startswith("s3://"):
            transport_params = {'client': self.__s3cli}
            with open(doc_path, 'rb', transport_params=transport_params) as fin:
                content_bytes = fin.read()
                return content_bytes
        else:
            with open(doc_path, 'rb') as fin:
                content_bytes = fin.read()
                return content_bytes
    

    def convert(self, doc_path:str, progress_file_path:str, conv_timeout=None):
        """
        在线快速解析
        doc_path: str, path to the document, support local file path and s3 path.
        progress_file_path: str, path to the progress file, support local file path only.
        return markdown string or raise ConvException.
        """
        conv_timeout = conv_timeout or self.__conv_timeout # 根据这个时间判断函数超时
        markdown_string = ""
        try:
            conv: BaseConv = self.__select_conv(doc_path)
            byte_content = self.__read_file_as_bytes(doc_path)
            markdown_string = func_timeout(self.__conv_timeout, conv.to_md, args=(byte_content,))
        except FunctionTimedOut as e1:
            logger.exception(e1)
            raise ConvException("Convert timeout.")
        except Exception as e2:
            logger.exception(e2)
            raise ConvException("Convert failed: %s" % str(e2))
            
        return markdown_string


