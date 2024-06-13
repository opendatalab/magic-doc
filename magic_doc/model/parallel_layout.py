
import torch

from magic_doc.model.sub_modules.layoutlmv3.model_init import Layoutlmv3_Predictor
from magic_doc.utils import split_to_chunks
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

class ParallelLayout:
    def __init__(self, config, model_load_on_each_gpu_count=1):
        models = []
        for i in range(torch.cuda.device_count()):
            torch.cuda.set_device(i)
            for _ in range(model_load_on_each_gpu_count):
                models.append(Layoutlmv3_Predictor(config))
        self.models = models

    def __call__(self, params):
        """
        params: list[(idx, image)]
        """
        if len(params) == 0:
            return []
        chunks = list(split_to_chunks(params, max(math.ceil(len(params) *1.0/ len(self.models)), 1)))
        return self._run_layout_concurrently(chunks)


    def _run_layout_concurrently(self, chunks):
        results = []

        def run_layout(chunk, i):
            result = []
            for idx, image in chunk:
                layout_res = self.models[i](image, ignore_catids=[])
                result.append((idx, layout_res))
            return result

        with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
            future_to_ocr = {executor.submit(run_layout, chunk, i): i for i, chunk in enumerate(chunks)}
            for future in as_completed(future_to_ocr):
                try:
                    data = future.result()
                    results.extend(data)
                except Exception as exc:
                    print(f"failed to process layout, reason: ", exc)
        return sorted(results, key=lambda x: x[0])

