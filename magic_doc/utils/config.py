import json
import os


def read_config():
    home_dir = os.path.expanduser("~")

    config_file = os.path.join(home_dir, "magic-doc.json")

    if not os.path.exists(config_file):
        raise Exception(f"{config_file} not found")

    with open(config_file, "r") as f:
        config = json.load(f)
    return config


def get_s3_config(bucket_name: str):
    """
    从 ~/magic-doc.json 读取配置
    """
    config = read_config()

    bucket_info = config.get("bucket_info")
    if bucket_name not in bucket_info:
        access_key, secret_key, storage_endpoint = bucket_info["[default]"]
    else:
        access_key, secret_key, storage_endpoint = bucket_info[bucket_name]

    if access_key is None or secret_key is None or storage_endpoint is None:
        raise Exception("ak, sk or endpoint not found in magic-doc.json")

    # logger.info(f"get_s3_config: ak={access_key}, sk={secret_key}, endpoint={storage_endpoint}")

    return access_key, secret_key, storage_endpoint

