
from magic_doc.model.sub_modules.self_modify import ModifiedPaddleOCR
from magic_doc.utils import split_to_chunks
import paddle 
from concurrent.futures import ThreadPoolExecutor, as_completed


class SeqOCR:
    def __init__(self, **kwargs):
        self.model = ModifiedPaddleOCR(show_log=False, **kwargs)

    def __call__(self, params):
        """
        params: list[(idx, image, *args)]
        """
        results = [] 
        for idx, cropped_image, single_page_mfdetrec_res in params:
                ocr_res = self.model.ocr(cropped_image, mfd_res=single_page_mfdetrec_res)[0]
                if ocr_res:
                    results.append((idx, ocr_res))

        return results 

