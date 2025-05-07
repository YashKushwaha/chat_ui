import yaml
import os
from pathlib import Path

DEFAULT_CONFIG_PATH = os.path.join(Path(__file__).resolve().parents[1] , "config", "settings.yaml")

def get_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config
