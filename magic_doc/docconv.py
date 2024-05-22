import os
from func_timeout import func_timeout, FunctionTimedOut
from loguru import logger



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
            self.__s3cli = S3Client(self.__s3cfg) # TODO
        self.__temp_dir = temp_dir
        self.__conv_timeout = conv_timeout # 转换超时时间，单位秒      
        
        """
        从环境变量加载模型路径
        """  
        self.__model_equation_recog_path = os.getenv(MODEL_EQUATION_RECOG_PATH_VAR)
        self.__model_equation_detect_path = os.getenv(MODEL_EQUATION_DETECT_PATH_VAR)
        self.__model_layout_path = os.getenv(MODEL_LAYOUT_PATH_VAR)
        if not self.__model_equation_recog_path or not self.__model_equation_detect_path or not self.__model_layout_path:
            raise ConvException("Model path not found in environment variables: %s, %s, %s" % (MODEL_EQUATION_RECOG_PATH_VAR, MODEL_EQUATION_DETECT_PATH_VAR, MODEL_LAYOUT_PATH_VAR))
        else:
            pass # TODO 初始化模型

    def convert(self, doc_path:str, progress_file_path:str, conv_timeout=None, to_format="markdown"):
        """
        在线快速解析
        doc_path: str, path to the document, support local file path and s3 path.
        progress_file_path: str, path to the progress file, support local file path only.
        return markdown string or raise ConvException.
        """
        conv_timeout = conv_timeout or self.__conv_timeout # 根据这个时间判断函数超时
        markdown_string = ""
        try:
            markdown_string = func_timeout(self.__conv_timeout, some_function, args=(arg1,)) # TODO
        except FunctionTimedOut as e1:
            logger.exception(e1)
            raise ConvException("Convert timeout.")
        except Exception as e2:
            logger.exception(e2)
            raise ConvException("Convert failed: %s" % str(e2))
            
        return markdown_string
    
