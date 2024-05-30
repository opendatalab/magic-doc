import os

from s3pathlib import S3Path

from magic_doc.utils.config import read_config


def get_local_dir():
    config = read_config()
    return config.get("temp-output-dir", "/tmp")


def prepare_env(doc_file_name, doc_type="") -> str:
    if doc_type == "":
        doc_type = "unknown"
    local_parent_dir = os.path.join(
        get_local_dir(), "magic-doc", doc_type, doc_file_name
    )

    # local_image_dir = os.path.join(local_parent_dir, "images")
    local_md_dir = local_parent_dir
    # os.makedirs(local_image_dir, exist_ok=True)
    os.makedirs(local_md_dir, exist_ok=True)
    return str(local_md_dir)


def remove_non_official_s3_args(s3path):
    """
    example: s3://abc/xxxx.json?bytes=0,81350 ==> s3://abc/xxxx.json
    """
    arr = s3path.split("?")
    return arr[0]


def parse_s3path(s3path: str):
    p = S3Path(remove_non_official_s3_args(s3path))
    return p.bucket, p.key
