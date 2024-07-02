
from magic_doc.model.sub_modules.self_modify import ModifiedPaddleOCR
from magic_doc.utils import split_to_chunks
import paddle 
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

class ParallelOCR:
    def __init__(self, model_load_on_each_gpu_count=1):
        models = []
        for i in range(paddle.device.cuda.device_count()):
            for _ in range(model_load_on_each_gpu_count):
                models.append(ModifiedPaddleOCR(use_gpu=True, show_log=False, gpu_id=i))
        self.models = models

    def __call__(self, params):
        """
        params: list[(idx, image, *args)]
        """
        if len(params) == 0:
            return []
        chunks = list(split_to_chunks(params, max(math.ceil(len(params) *1.0/ len(self.models)), 1)))
        return self._run_ocr_concurrently(chunks)

    def _run_ocr_concurrently(self, chunks):
        results = []

        def run_ocr(chunk, i):
            result = []
            for idx, cropped_image, single_page_mfdetrec_res in chunk:
                ocr_res = self.models[i].ocr(cropped_image, mfd_res=single_page_mfdetrec_res)[0]
                if ocr_res:
                    result.append((idx, ocr_res))
            return result

        with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
            future_to_ocr = {executor.submit(run_ocr, chunk, i): i for i, chunk in enumerate(chunks)}
            for future in as_completed(future_to_ocr):
                try:
                    data = future.result()
                    results.extend(data)
                except Exception as exc:
                    print(f"failed to process ocr, reason: ", exc)
        return results