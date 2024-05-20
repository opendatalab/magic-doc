

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

    def convert(self, doc_path:str, progress_file_path:str, conv_timeout=None):
        """
        doc_path: str, path to the document, support local file path and s3 path.
        progress_file_path: str, path to the progress file, support local file path only.
        return markdown string or raise ConvException.
        """
        conv_timeout = conv_timeout or self.__conv_timeout # 根据这个时间判断函数超时
        markdown_string = ""
        # TODO
        return markdown_string
