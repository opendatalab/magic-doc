from magic_doc.model.parallel_paddle import ParallelPaddle


class PaddleDocAnalysis:
    def __init__(self, **kwargs):
        self.model = ParallelPaddle(**kwargs)

    def __call__(self, image_dicts):
        images = [(i, image_dicts[i]["img"]) for i in range(len(image_dicts))]
        results = sorted(self.model(images), key=lambda x: x[0])
        if len(results) != len(image_dicts):
            raise Exception("fatal error: failed to inference using paddleocr")

        model_json = []
        for index, img_dict in enumerate(image_dicts):
            img = img_dict["img"]
            page_width = img_dict["width"]
            page_height = img_dict["height"]
            page_info = {"page_no": index, "height": page_height, "width": page_width}
            page_dict = {"layout_dets": results[index][1], "page_info": page_info}
            model_json.append(page_dict)
        return model_json

