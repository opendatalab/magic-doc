# Magic-Doc
convert doc（pdf/html/doc/docx/ppt/pptx）to markdown


## TODO
* 安装三方库依赖的说明     p0
* 模型相关的 env 环境变量 p0
* contrib/{html, pdf, office} 函数改造以及调通    p1
* magic 系列仓库和 model 仓库共享 config-parser 模块  p1


## 安装说明
* python 版本 3.10

* 安装程序依赖的三方库
```text

pip install -r requirements.txt

```

* 安装模型依赖的三方库
```text
pip install unimernet

pip install -r requirements.model.txt

pip install --extra-index-url https://miropsota.github.io/torch_packages_builder detectron2==0.6+pt2.2.2cu121

pip uninstall PyMuPDF

pip install PyMuPDF

pip install pillow==8.4.0

```

* 下载模型及配置文件 （TODO）

