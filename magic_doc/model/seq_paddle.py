
from magic_pdf.model.pp_structure_v2 import CustomPaddleModel
from magic_doc.utils import split_to_chunks
import paddle 
from concurrent.futures import ThreadPoolExecutor, as_completed


class SeqPaddle:
    def __init__(self, **kwargs):
        self.model = CustomPaddleModel(ocr=True, show_log=False)

    def __call__(self, params):
        """
        params: list[(idx, image, *args)]
        """
        results = [] 
        for idx, img in params:
            ocr_res = self.model(img) or []
            results.append((idx, ocr_res))

        return results 
