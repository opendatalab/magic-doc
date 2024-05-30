# Magic-Doc
convert doc（pdf/html/doc/docx/ppt/pptx）to markdown

### 上手指南

###### 开发前的配置要求

python 3.10+

###### **安装步骤**

1.Clone the repo

```sh
git clone https://github.com/magicpdf/Magic-Doc.git
```

2.Install the requirements

```sh
cd Magic-Doc
pip install -r requirements.txt
```
install libreoffice to convert doc/ppt
```sh
linux/osx
apt-get/yum/brew install libreoffice
win
install libreoffice and add "install_dir\LibreOffice\program" to PATH
```

3.Run the command line

```sh
linux/osx
export PYTHONPATH=.
win
$env:PYTHONPATH += ";.\Magic-Doc\magic_doc"    
```
```sh
python magic_doc/cli.py --help
```


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
pip install -r requirements.model.txt

pip install unimernet

pip install --extra-index-url https://miropsota.github.io/torch_packages_builder detectron2==0.6+pt2.2.2cu121

pip uninstall PyMuPDF

pip install PyMuPDF

pip install pillow==8.4.0

```

* 下载模型及配置文件 （TODO）

