from pathlib import Path


def find_config_path(filename: str, target_dir: str = "configs") -> Path:
    current = Path(__file__).resolve().parent

    while True:
        candidate_dir = current / target_dir
        if candidate_dir.exists() and candidate_dir.is_dir():
            cfg_path = candidate_dir / filename
            if cfg_path.exists():
                return cfg_path
            else:
                raise FileNotFoundError(
                    f"Found '{target_dir}' but '{filename}' does not exist: {cfg_path}"
                )

        if current.parent == current:
            break
        current = current.parent

    raise FileNotFoundError(
        f"Cannot find '{target_dir}/{filename}' in any parent directory of {Path(__file__).resolve()}"
    )
