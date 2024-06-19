
from magic_doc.utils.yaml_load import patch_dict_with_env

class PdfFastParseMethod:
    AUTO = "auto"
    FAST = "fast"
    LITEOCR = "lite_ocr"


DEFAULT_CONFIG = {
    "pdf": {
        "fast": {
            "parsemethod": PdfFastParseMethod.AUTO,
            "liteocrmodelinstance": 1,
        }
    }
}




DEFAULT_CONFIG = patch_dict_with_env("filter", DEFAULT_CONFIG)

