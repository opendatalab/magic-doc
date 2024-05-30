
import magic_doc
import os
import random
import fitz

def get_repo_directory():
    return os.path.dirname(magic_doc.__file__)


def is_digital(bits: bytes) -> bool:
    def _is_digital(doc, check_page=10, text_len_thrs=100):
        sample_page_num = min(check_page, doc.page_count)
        page_ids = random.sample(range(doc.page_count), sample_page_num)
        page_text_len = [
            len(doc[pno].get_text("text")) > text_len_thrs for pno in page_ids
        ]
        if any(page_text_len):
            return True
        return False
    
    with fitz.open(stream=bits) as doc:
        return _is_digital(doc)
