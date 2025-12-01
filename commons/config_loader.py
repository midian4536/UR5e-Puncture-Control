import yaml, shutil
from pathlib import Path
from typing import Any


class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with self.config_path.open("r") as f:
            self.cfg = yaml.safe_load(f)

    def get(self, *keys, default: Any = None) -> Any:
        val = self.cfg
        for k in keys:
            if not isinstance(val, dict) or k not in val:
                return default
            val = val[k]
        return val

    def save_copy(self, out_dir):
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        dst = out_dir / "config.yaml"
        shutil.copy(self.config_path, dst)
        return dst
