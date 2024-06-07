

from magic_doc.model.sub_modules.layoutlmv3.model_init import Layoutlmv3_Predictor

class SeqLayout:
    def __init__(self, config):
        self.model = Layoutlmv3_Predictor(config)

    def __call__(self, params):
        """
        params: list[(idx, image)]
        """
        if len(params) == 0:
            return []

        results = []
        for idx, image in params:
            layout_res = self.model(image)
            results.append((idx, layout_res))
        return results

