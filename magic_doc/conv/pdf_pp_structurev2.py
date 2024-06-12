from pathlib import Path

import cv2
import numpy as np
from magic_pdf.dict2md.ocr_mkcontent import union_make
from magic_pdf.libs.MakeContentConfig import MakeMode, DropMode
from magic_pdf.libs.json_compressor import JsonCompressor
from magic_pdf.rw.AbsReaderWriter import AbsReaderWriter
from paddleocr import PPStructure
from PIL import Image
from loguru import logger
import fitz

from magic_doc.conv.base import BaseConv
from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.progress.pupdator import ConvProgressUpdator
from magic_doc.utils.null_writer import NullWriter

from magic_pdf.pipe.UNIPipe import UNIPipe

NULL_IMG_DIR = "/tmp"

def doc_analyze(pdf_bytes: bytes, ocr: bool = False):
    ocr_engine = PPStructure(table=False, ocr=ocr, show_log=True)

    imgs = []
    with fitz.open("pdf", pdf_bytes) as doc:
        for index in range(0, doc.page_count):
            page = doc[index]
            mat = fitz.Matrix(2, 2)
            pm = page.get_pixmap(matrix=mat, alpha=False)

            # if width or height > 2000 pixels, don't enlarge the image
            if pm.width > 2000 or pm.height > 2000:
                pm = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)

            img = Image.frombytes("RGB", [pm.width, pm.height], pm.samples)
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            img_dict = {
                "img": img,
                "width": pm.width,
                "height": pm.height
            }
            imgs.append(img_dict)

    def region_to_bbox(region):
        x0 = region[0][0]
        y0 = region[0][1]
        x1 = region[2][0]
        y1 = region[2][1]
        return [x0, y0, x1, y1]

    def dict_compare(d1, d2):
        return d1.items() == d2.items()

    def remove_duplicates_dicts(lst):
        unique_dicts = []
        for dict_item in lst:
            if not any(dict_compare(dict_item, existing_dict) for existing_dict in unique_dicts):
                unique_dicts.append(dict_item)
        return unique_dicts

    model_json = []
    for index, img_dict in enumerate(imgs):
        img = img_dict['img']
        page_width = img_dict['width']
        page_height = img_dict['height']
        result = ocr_engine(img)
        spans = []
        for line in result:
            line.pop('img')
            '''
            为paddle输出适配type no.    
            title: 0 # 标题
            text: 1 # 文本
            header: 2 # abandon
            footer: 2 # abandon
            reference: 1 # 文本 or abandon
            equation: 8 # 行间公式 block
            equation: 14 # 行间公式 text
            figure: 3 # 图片
            figure_caption: 4 # 图片描述
            table: 5 # 表格
            table_caption: 6 # 表格描述
            '''
            if line['type'] == 'title':
                line['category_id'] = 0
            elif line['type'] in ['text', 'reference']:
                line['category_id'] = 1
            elif line['type'] == 'figure':
                line['category_id'] = 3
            elif line['type'] == 'figure_caption':
                line['category_id'] = 4
            elif line['type'] == 'table':
                line['category_id'] = 5
            elif line['type'] == 'table_caption':
                line['category_id'] = 6
            elif line['type'] == 'equation':
                line['category_id'] = 8
            elif line['type'] in ['header', 'footer']:
                line['category_id'] = 2
            else:
                logger.warning(f"unknown type: {line['type']}")
            line['score'] = 0.5

            res = line.pop('res', None)
            if res is not None and len(res) > 0:
                for span in res:
                    new_span = {'category_id': 15,
                                'bbox': region_to_bbox(span['text_region']),
                                'score': span['confidence'],
                                'text': span['text']
                                }
                    spans.append(new_span)
        if len(spans) > 0:
            result.extend(spans)

        result = remove_duplicates_dicts(result)

        page_info = {
            "page_no": index,
            "height": page_height,
            "width": page_width
        }
        page_dict = {
            "layout_dets": result,
            "page_info": page_info
        }

        model_json.append(page_dict)

    return model_json


class Pdf(BaseConv):
    def to_md(self, bits: bytes | str, pupdator: ConvProgressUpdator) -> str:

        model_list = doc_analyze(bits)  # type: ignore
        pupdator.update(50)
        jso_useful_key = {
            "_pdf_type": "",
            "model_list": model_list,
        }
        image_writer = NullWriter()
        pipe = UNIPipe(bits, jso_useful_key, image_writer, is_debug=True)  # type: ignore
        pipe.pipe_classify() # 默认ocrpipe的时候不需要再做分类，可以节省时间
        pipe.pipe_parse()
        pupdator.update(100)

        pdf_mid_data = JsonCompressor.decompress_json(pipe.get_compress_pdf_mid_data())
        pdf_info_list = pdf_mid_data["pdf_info"]
        md_content = union_make(pdf_info_list, MakeMode.NLP_MD, DropMode.NONE, NULL_IMG_DIR)
        return md_content  # type: ignore

    def to_mid_result(self, image_writer: AbsReaderWriter, bits: bytes | str, pupdator: ConvProgressUpdator) \
            -> list[dict] | dict:

        pupdator.update(0)

        model_list = doc_analyze(bits)  # type: ignore
        pupdator.update(50)
        jso_useful_key = {
            "_pdf_type": "",
            "model_list": model_list,
        }

        pipe = UNIPipe(bits, jso_useful_key, image_writer, is_debug=True)  # type: ignore
        pipe.pipe_classify()
        pipe.pipe_parse()
        pupdator.update(100)

        pdf_mid_data = JsonCompressor.decompress_json(pipe.get_compress_pdf_mid_data())
        pdf_info_list = pdf_mid_data["pdf_info"]
        return pdf_info_list


if __name__ == "__main__":
    pupdator = FileBaseProgressUpdator("/tmp/p.txt")
    pdf = Pdf()
    logger.info(
        pdf.to_md(Path(r"D:\project\20231108code-clean\linshixuqiu\pdf_dev\新模型\j.sna.2004.11.030.pdf").read_bytes(), pupdator))
