
import os
import yaml
from collections import deque


def patch_dict_with_env(env_namespace, configs):
    for env_var in os.environ:
        arr = deque(map(lambda x: x.lower(), env_var.split("_")))
        if arr[0] != env_namespace:
            continue
        arr.popleft()
        d = configs
        while arr:
            if arr[0] not in d:
                break
            if len(arr) > 1:
                d = d[arr[0]]
                arr.popleft()
            else:
                d[arr[0]] = os.environ[env_var]
                break
    return configs


def patch_yaml_load_with_env(yaml_file, env_namespace, loader=yaml.FullLoader):
    with open(yaml_file, "r") as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)

    return patch_dict_with_env(env_namespace, configs)

