from setuptools import setup, find_packages
import subprocess
def parse_requirements(filename):
    with open(filename) as f:
        lines = f.read().splitlines()

    requires = []

    for line in lines:
        if "http" in line:
            pkg_name_with_version = line.split('/')[-1].split('-')[0]
            requires.append(pkg_name_with_version)
        else:
            requires.append(line)

    return requires

def get_version():
    command = ["git", "describe", "--tags"]
    try:
        version = subprocess.check_output(command).decode().strip()
        version_parts = version.split("-")
        if len(version_parts) > 1 and version_parts[0].startswith("magic_doc"):
            return version_parts[1]
        else:
            raise ValueError(f"Invalid version tag {version}. Expected format is magic_pdf-<version>-released.")
    except Exception as e:
        print(e)
        return "0.0.0"


requires = parse_requirements('requirements.txt')

setup(
    name="magic_doc",  # 项目名
    # version="0.1.3",  # 版本号
    version=get_version(),  # 自动从tag中获取版本号
    packages=find_packages()+['magic_doc.bin', 'magic_doc.resources'],  # 包含所有的包
    package_data={
            # 'magic_doc.bin': ['linux/*', 'linux/share/antiword/*'],  # 包含magic_doc.bin目录下的所有文件
            'magic_doc.bin': ['**'],  # 包含magic_doc.bin目录下的所有文件
            'magic_doc.resources': ['**']  # 包含magic_doc.resources目录下的所有文件
    },
    install_requires=requires,  # 项目依赖的第三方库
    python_requires=">=3.10",  # 项目依赖的 Python 版本
    # entry_points={"console_scripts": ["my_command=my_project.main:run"]}, # 项目提供的可执行命令
    include_package_data=True,
    zip_safe=False,  # 是否使用 zip 文件格式打包，一般设为 False
)
