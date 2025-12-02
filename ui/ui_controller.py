from PyQt5.QtCore import QTimer
from commons.config_loader import ConfigLoader
from commons.robot_controller import RobotController
from commons.data_logger import DataLogger


class UIController:
    def __init__(self, ui, config_path="robot.yaml"):
        self.ui = ui

        self.cfg = ConfigLoader(config_path)

        self.controller = RobotController(self.cfg)
        self.logger = DataLogger(self.cfg)

        self.recording = False
        self.trajectory = []

        self.ui.btn_start_record.clicked.connect(self.start_recording)
        self.ui.btn_stop_record.clicked.connect(self.stop_recording)
        self.ui.btn_replay.clicked.connect(self.replay_trajectory)
        self.ui.btn_exit.clicked.connect(self.exit_app)

        self.controller.move_to_start()
        self.controller.init_force_mode()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(20)  # 50Hz

    def update_loop(self):
        state = self.controller.step()

        self.ui.update_tcp_pose(state["tcp_pose"])

        self.ui.force_plot.update_plot(
            state["tcp_pose"][0],
            state["tcp_pose"][1],
            state["tcp_pose"][2],
            state["timestamp"],
        )
        self.ui.trajectory_plot.update_trajectory(
            state["tcp_pose"][0], state["tcp_pose"][1], state["tcp_pose"][2]
        )

        self.logger.log(state)

        if self.recording:
            self.trajectory.append(state["q"])

    def start_recording(self):
        self.trajectory = []
        self.recording = True

        self.ui.set_status("Recording...")
        self.ui.btn_start_record.setEnabled(False)
        self.ui.btn_stop_record.setEnabled(True)
        self.ui.btn_replay.setEnabled(False)

    def stop_recording(self):
        self.recording = False

        self.ui.set_status("Recorded")
        self.ui.btn_start_record.setEnabled(True)
        self.ui.btn_stop_record.setEnabled(False)
        if len(self.trajectory) > 0:
            self.ui.btn_replay.setEnabled(True)

    def replay_trajectory(self):
        self.ui.set_status("Returning...")

        if len(self.trajectory) > 0:
            path = []
            for q in reversed(self.trajectory):
                p = list(q) + [0.2, 0.2, 0.02]
                path.append(p)
            self.controller.c.moveJ(path, False)

        self.ui.set_status("Returned")

    def exit_app(self):
        self.controller.shutdown()
        self.ui.close()
