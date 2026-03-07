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
        self.replaying = False
        self.waiting = True  # 初始进入waiting状态
        self.trajectory = []

        self.ui.btn_start_record.clicked.connect(self.start_recording)
        self.ui.btn_stop_record.clicked.connect(self.stop_recording)
        self.ui.btn_replay.clicked.connect(self.replay_trajectory)
        self.ui.btn_exit.clicked.connect(self.exit_app)

        self.controller.move_to_start()
        #self.controller.init_force_mode()
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
        
        # 根据当前模式选择不同的轨迹更新方法
        if self.replaying:
            self.ui.trajectory_plot.update_replay_trajectory(
                state["tcp_pose"][0], state["tcp_pose"][1], state["tcp_pose"][2]
            )
        elif not self.waiting:
            self.ui.trajectory_plot.update_trajectory(
                state["tcp_pose"][0], state["tcp_pose"][1], state["tcp_pose"][2]
            )

        self.logger.log(state)

        if self.recording:
            self.trajectory.append(state["q"])

    def start_recording(self):
        # 检查是否处于waiting状态
        if not self.waiting:
            return
            
        self.controller.init_force_mode()
        self.trajectory = []
        self.recording = True
        self.waiting = False  # 点击start后退出waiting状态

        self.ui.set_status("Recording...")
        self.ui.btn_start_record.setEnabled(False)
        self.ui.btn_stop_record.setEnabled(True)
        self.ui.btn_replay.setEnabled(False)

    def stop_recording(self):
        self.recording = False
        self.controller.c.forceModeStop()
        self.controller.c.zeroFtSensor()
        self.waiting = True  # 点击stop后进入waiting状态

        self.ui.set_status("Recorded")
        self.ui.btn_start_record.setEnabled(True)
        self.ui.btn_stop_record.setEnabled(False)
        if len(self.trajectory) > 0:
            self.ui.btn_replay.setEnabled(True)

    def replay_trajectory(self):
        # 点击轨迹复现退出waiting状态
        self.waiting = False
        
        self.ui.set_status("Replaying...")
        self.controller.c.forceModeStop()
        
        # 禁用操作按钮防止重复触发
        self.ui.btn_start_record.setEnabled(False)
        self.ui.btn_replay.setEnabled(False)
        self.ui.btn_stop_record.setEnabled(False)
        
        # 清除之前的复现轨迹
        self.ui.trajectory_plot.clear_replay_trajectory()
        
        if len(self.trajectory) > 0:
            path = []
            for q in reversed(self.trajectory):
                p = list(q) + [0.2, 0.2, 0.02]
                path.append(p)
            
            # 设置复现模式标志
            self.replaying = True
            
            # 创建线程执行moveJ，避免阻塞主线程
            import threading
            def execute_replay():
                self.controller.c.moveJ(path, False)
                self.replaying = False
                # 轨迹复现结束后进入waiting状态
                self.waiting = True
                self.controller.c.forceModeStop()
                self.ui.set_status("Replay completed")
                # 恢复按钮状态
                self.ui.btn_start_record.setEnabled(True)
                self.ui.btn_replay.setEnabled(True)
            
            threading.Thread(target=execute_replay, daemon=True).start()
        else:
            # 没有轨迹时直接进入waiting状态
            self.waiting = True
            self.controller.c.forceModeStop()
            self.ui.set_status("No trajectory to replay")
            # 恢复按钮状态
            self.ui.btn_start_record.setEnabled(True)



    def exit_app(self):
        self.timer.stop()
        self.logger.close()
        self.controller.shutdown()
        self.ui.close()
