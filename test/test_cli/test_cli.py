import pytest
import os
import logging
from conf import conf
from magic_doc.docconv import DocConverter, S3Config

code_path = conf.conf["code_path"] 
output_path = conf.conf["pdf_res_path"]

class TestDocConversion:

    def test_convert_doc_to_md(self):
        """
        将DOC文件转换为Markdown
        """
        file_path = os.path.join(code_path, "datas/test01.doc")
        cmd = f"python {code_path}/magic_doc/cli.py --file-path {file_path} --output {output_path}"
        logging.info(cmd)
        res = os.system(cmd)
        assert res == 0 

    def test_convert_docx_to_md(self):
        """
        将DOCX文件转换为Markdown
        """
        file_path = os.path.join(code_path, "datas/test02.docx")
        cmd = f"python {code_path}/magic_doc/cli.py --file-path {file_path} --output {output_path}"
        logging.info(cmd)
        res = os.system(cmd)
        assert res == 0

    def test_convert_html_to_md(self):
        """
        将HTML文件转换为Markdown
        """
        file_path = os.path.join(code_path, "datas/test03.html")
        cmd = f"python {code_path}/magic_doc/cli.py --file-path {file_path} --output {output_path}"
        logging.info(cmd)
        res = os.system(cmd)
        assert res == 0

    def test_convert_pdf_to_md(self):
        """
        将PDF文件转换为Markdown
        """
        file_path = os.path.join(code_path, "datas/test04.pdf")
        cmd = f"python {code_path}/magic_doc/cli.py --file-path {file_path} --output {output_path}"
        logging.info(cmd)
        res = os.system(cmd)
        assert res == 0

    def test_convert_ppt_to_md(self):
        """
        将PPT文件转换为Markdown
        """
        file_path = os.path.join(code_path, "datas/test05.ppt")
        cmd = f"python {code_path}/magic_doc/cli.py --file-path {file_path} --output {output_path}"
        logging.info(cmd)
        res = os.system(cmd)
        assert res == 0

    def test_convert_pptx_to_md(self):
        """
        将PPTX文件转换为Markdown
        """
        file_path = os.path.join(code_path, "datas/test06.pptx")
        cmd = f"python {code_path}/magic_doc/cli.py --file-path {file_path} --output {output_path}"
        logging.info(cmd)
        res = os.system(cmd)
        assert res == 0

    def test_convert_pptx_to_md_sdk(self):
        """
        sdk转换PPTx文件为Markdown
        """
        # for local file
        file_path = os.path.join(code_path, "datas/test06.pptx")
        converter = DocConverter(s3_config=None)
        markdown_content, time_cost = converter.convert(file_path, conv_timeout=300)
        assert len(markdown_content) > 0
        assert time_cost > 0

    def test_convert_pdf_to_md_sdk(self):
        """
        sdk转换PDF文件为Markdown
        """
        # for local file
        file_path = os.path.join(code_path, "datas/test04.pdf")
        converter = DocConverter(s3_config=None)
        markdown_content, time_cost = converter.convert(file_path, conv_timeout=300)
        assert len(markdown_content) > 0
        assert time_cost > 0
    
    def test_convert_doc_to_md_sdk(self):
        """
        sdk转换DOC文件为Markdown
        """
        # for local file
        file_path = os.path.join(code_path, "datas/test01.doc")
        converter = DocConverter(s3_config=None)
        markdown_content, time_cost = converter.convert(file_path, conv_timeout=300)
        assert len(markdown_content) > 0
        assert time_cost > 0

    def test_convert_docx_to_md_sdk(self):
        """
        sdk转换DOCX文件为Markdown
        """
        # for local file
        file_path = os.path.join(code_path, "datas/test02.docx")
        converter = DocConverter(s3_config=None)
        markdown_content, time_cost = converter.convert(file_path, conv_timeout=300)
        assert len(markdown_content) > 0
        assert time_cost > 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
