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

3.Run the command line

```sh
linux/osx
export PYTHONPATH=.
win
$env:PYTHONPATH += ";.\Magic-Doc\magic_doc"    
```
```
python magic_doc/cli.py --help
```


## TODO
* 安装三方库依赖的说明     p0
* contrib/{html, pdf, office} 函数改造以及调通    p1
* magic 系列仓库和 model 仓库共享 config-parser 模块  p1
