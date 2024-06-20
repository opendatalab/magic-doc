
from magic_doc.utils.yaml_load import patch_dict_with_env

class PdfFastParseMethod:
    AUTO = "auto"
    FAST = "fast"
    LITEOCR = "lite_ocr"

class PdfHqParseMethod:
    AUTO = "auto"
    OCR = "ocr"
    TXT = "txt"


DEFAULT_CONFIG = {
    "pdf": {
        "fast": {
            "parsemethod": PdfFastParseMethod.AUTO,
            "liteocrmodelinstance": 1,
        }, 
        "hq": {
            "parsemethod": PdfHqParseMethod.OCR,
        }
    }
}


DEFAULT_CONFIG = patch_dict_with_env("filter", DEFAULT_CONFIG)

