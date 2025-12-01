import csv
from pathlib import Path
from datetime import datetime
from commons.config_loader import ConfigLoader

class DataLogger:
    def __init__(self, cfg: ConfigLoader):
        out_root = Path(cfg.get("logging", "out_dir"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.out_dir = out_root / f"run_{timestamp}"
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.csv_path = self.out_dir / "ur5e_data.csv"
        self.file = self.csv_path.open("w", newline="")
        self.writer = csv.writer(self.file)

        self.writer.writerow(
            ["timestamp"]
            + [f"tcp_pose_{i}" for i in range(6)]
            + [f"tcp_speed_{i}" for i in range(6)]
            + [f"q_{i}" for i in range(6)]
            + [f"qd_{i}" for i in range(6)]
            + [f"curr_{i}" for i in range(6)]
            + [f"volt_{i}" for i in range(6)]
            + [f"torq_{i}" for i in range(6)]
        )

    def log(self, state: dict):
        row = (
            [state["timestamp"]]
            + state["tcp_pose"].tolist()
            + state["tcp_speed"].tolist()
            + state["q"].tolist()
            + state["qd"].tolist()
            + state["curr"].tolist()
            + state["volt"].tolist()
            + state["torq"].tolist()
        )
        self.writer.writerow(row)

    def close(self):
        self.file.close()
