import os
import yaml
import re

# Hàm thay thế ${VAR_NAME} bằng giá trị từ os.environ
def resolve_env_vars(value):
    if isinstance(value, str):
        return re.sub(r'\$\{([^}]+)\}', lambda m: os.environ.get(m.group(1), ""), value)
    elif isinstance(value, dict):
        return {k: resolve_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [resolve_env_vars(v) for v in value]
    else:
        return value

def load_config(config_path):
    with open(config_path, 'r') as file:
        raw_config = yaml.safe_load(file)
    config = resolve_env_vars(raw_config)
    return config