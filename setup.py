from setuptools import setup, find_packages
from magic_doc.libs.version import __version__
def parse_requirements(filename):
    with open(filename) as f:
        lines = f.read().splitlines()

    requires = []

    for line in lines:
        if "http" in line:
            pkg_name_without_url = line.split('@')[0].strip()
            if pkg_name_without_url == "magic_pdf":
                pkg_name_without_url = "magic_pdf>=0.4.27"
            requires.append(pkg_name_without_url)
        else:
            requires.append(line)

    return requires


setup(
    name="magic_doc",  # 项目名
    version=__version__,  # 自动从tag中获取版本号
    packages=find_packages()+['magic_doc.bin', 'magic_doc.resources'],  # 包含所有的包
    package_data={
            'magic_doc.bin': ['**'],  # 包含magic_doc.bin目录下的所有文件
            'magic_doc.resources': ['**'],  # 包含magic_doc.resources目录下的所有文件
            'magic_doc.contrib.office.formula': ['**']  # 包含magic_doc.contrib.office.formula目录下的所有文件
    },
    install_requires=parse_requirements('requirements.txt'),  # 项目依赖的第三方库
    python_requires=">=3.10",  # 项目依赖的 Python 版本
    # entry_points={"console_scripts": ["my_command=my_project.main:run"]}, # 项目提供的可执行命令
    include_package_data=True,
    zip_safe=False,  # 是否使用 zip 文件格式打包，一般设为 False
)
