
<div id="top"></div>
<div align="center">

[![license](https://img.shields.io/github/license/magicpdf/Magic-Doc.svg)](https://github.com/magicpdf/Magic-Doc/tree/main/LICENSE)
[![issue resolution](https://img.shields.io/github/issues-closed-raw/magicpdf/Magic-Doc)](https://github.com/magicpdf/Magic-Doc/issues)
[![open issues](https://img.shields.io/github/issues-raw/magicpdf/Magic-Doc)](https://github.com/magicpdf/Magic-Doc/issues)

[English](READMD.md) | [简体中文](README_zh-CN.md)

</div>

<div align="center">

</div>


### Install

Install Dependencies

**linux/osx** 

```bash
apt-get/yum/brew install libreoffice
```

**windows**
```text
install libreoffice 
append "install_dir\LibreOffice\program" to ENVIRONMENT PATH
```


Install Magic-Doc

```bash
git clone https://github.com/magicpdf/Magic-Doc (#TODO)
cd Magic-Doc
pip install -r requirements.txt
python setup.py install
```


## Introduction

Magic-Doc is a lightweight open-source tool that allows users to convert mulitple file type (PPT/PPTX/DOC/DOCX/PDF) to markdown. It supports both local file and S3 file.


## Example
```python
from magic_doc.docconv import DocConverter, S3Config

s3_config = S3Config(ak='${ak}', sk='${sk}', endpoint='${endpoint}')
converter = DocConverter(s3_config=s3_config)
markdown_cotent, time_cost = converter("some_doc.pptx", "/tmp/convert_progress.txt", conv_timeout=300)
```

## Performance

| File Type        | Speed | 
| ------------------ | -------- | 
| PDF (digital)        | 347 (page/s) | 
| PDF (OCR)           | 2.7 (page/s)  |   #TODO 需要更新为多线程版本的 OCR 识别程序
| PPT                 | 20 (page/s)   | 
| PPTX                | 149 (page/s)   | 
| DOC                 | 600 (page/s)   | 
| DOCX                | 1482 (page/s)   | 

### All Thanks To Our Contributors:

<a href="https://github.com/magicpdf/Magic-Doc/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=magicpdf/Magic-Doc" />
</a>

## License

This project is released under the [Apache 2.0 license](LICENSE).

<p align="right"><a href="#top">🔼 Back to top</a></p>
