
<div id="top"></div>
<div align="center">

[![license](https://img.shields.io/github/license/InternLM/magic-doc.svg)](https://github.com/InternLM/magic-doc/tree/main/LICENSE)
[![issue resolution](https://img.shields.io/github/issues-closed-raw/InternLM/magic-doc)](https://github.com/InternLM/magic-doc/issues)
[![open issues](https://img.shields.io/github/issues-raw/InternLM/magic-doc)](https://github.com/InternLM/magic-doc/issues)

<p align="center">
    👋 join us on <a href="https://discord.gg/xa29JuW87d" target="_blank">Discord</a> and <a href="https://github.com/InternLM/InternLM/assets/25839884/a6aad896-7232-4220-ac84-9e070c2633ce" target="_blank">WeChat</a>
</p>

[English](README.md) | [简体中文](README_zh-CN.md)

</div>

<div align="center">

</div>


### Install

Prerequisites: python3.10+

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
pip install fairy-doc[cpu] # cpu version
or
pip install fairy-doc[gpu] # gpu version
```



## Introduction

Magic-Doc is a lightweight open-source tool that allows users to convert multiple file type (PPT/PPTX/DOC/DOCX/PDF) to markdown. It supports both local file and S3 file.


## Example

```python
# for local file
from magic_doc.docconv import DocConverter, S3Config
converter = DocConverter(s3_config=None)
markdown_content, time_cost = converter.convert("some_doc.pptx", conv_timeout=300)
```

```python
# for remote file located in aws s3
from magic_doc.docconv import DocConverter, S3Config

s3_config = S3Config(ak='${ak}', sk='${sk}', endpoint='${endpoint}')
converter = DocConverter(s3_config=s3_config)
markdown_content, time_cost = converter.convert("s3://some_bucket/some_doc.pptx", conv_timeout=300)
```

## Performance

ENV: AMD EPYC 7742 64-Core Processor, NVIDIA A100, Centos 7

| File Type        | Speed | 
| ------------------ | -------- | 
| PDF (digital)        | 347 (page/s) | 
| PDF (ocr)           | 2.7 (page/s)  | 
| PPT                 | 20 (page/s)   | 
| PPTX                | 149 (page/s)   | 
| DOC                 | 600 (page/s)   | 
| DOCX                | 1482 (page/s)   | 

### All Thanks To Our Contributors:

![image](https://github.com/InternLM/magic-doc/blob/main/assets/contributor.png)


## 🖊️ Citation

```bibtex
@misc{2024magic-doc,
    title={Magic-Doc: A Toolkit that Converts Multiple File Types to Markdown},
    author={Magic-Doc Contributors},
    howpublished = {\url{https://github.com/InternLM/magic-doc}},
    year={2024}
}
```

## License

This project is released under the [Apache 2.0 license](LICENSE).

<p align="right"><a href="#top">🔼 Back to top</a></p>
