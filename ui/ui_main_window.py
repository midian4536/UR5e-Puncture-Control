from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)
from ui.force_plot_canvas import ForcePlotCanvas
from ui.trajectory_plot_canvas import TrajectoryPlotCanvas


class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("UR5e Real Time Monitoring")
        self.resize(1020, 900)

        self.central = QWidget(self)
        self.setCentralWidget(self.central)

        self.position_labels = self._create_pose_display()
        self.coordinate_status = self._create_status_label()

        self.plot_widget = QWidget(self)
        self.plot_widget.setFixedSize(420, 570)

        self.trajectory_widget = QWidget(self)
        self.trajectory_widget.setFixedSize(420, 570)

        self.button_panel = self._create_button_panel()

        self._apply_layout()

        layout_plot = QVBoxLayout(self.plot_widget)
        self.force_plot = ForcePlotCanvas(self.plot_widget)
        layout_plot.addWidget(self.force_plot)

        layout_traj = QVBoxLayout(self.trajectory_widget)
        self.trajectory_plot = TrajectoryPlotCanvas(self.trajectory_widget)
        layout_traj.addWidget(self.trajectory_plot)

    def _create_pose_display(self):
        labels_xyz = QHBoxLayout()
        labels_rpy = QHBoxLayout()

        self.lbl_x = QLabel("X")
        self.lbl_y = QLabel("Y")
        self.lbl_z = QLabel("Z")
        self.lbl_rx = QLabel("Rx")
        self.lbl_ry = QLabel("Ry")
        self.lbl_rz = QLabel("Rz")

        for lbl in [self.lbl_x, self.lbl_y, self.lbl_z]:
            labels_xyz.addWidget(lbl)
        for lbl in [self.lbl_rx, self.lbl_ry, self.lbl_rz]:
            labels_rpy.addWidget(lbl)

        self.val_x = QLabel("0.0000")
        self.val_y = QLabel("0.0000")
        self.val_z = QLabel("0.0000")
        self.val_rx = QLabel("0.0000")
        self.val_ry = QLabel("0.0000")
        self.val_rz = QLabel("0.0000")

        labels_val_xyz = QHBoxLayout()
        labels_val_rpy = QHBoxLayout()

        for val in [self.val_x, self.val_y, self.val_z]:
            labels_val_xyz.addWidget(val)
        for val in [self.val_rx, self.val_ry, self.val_rz]:
            labels_val_rpy.addWidget(val)

        pose_layout = QVBoxLayout()
        pose_layout.addLayout(labels_xyz)
        pose_layout.addLayout(labels_val_xyz)
        pose_layout.addLayout(labels_rpy)
        pose_layout.addLayout(labels_val_rpy)

        container = QWidget()
        container.setLayout(pose_layout)
        return container

    def _create_status_label(self):
        label = QPushButton("Monitoring...")
        label.setEnabled(False)
        return label

    def _create_button_panel(self):
        layout = QHBoxLayout()

        self.btn_start_record = QPushButton("Start")
        self.btn_stop_record = QPushButton("Stop")
        self.btn_replay = QPushButton("Return")
        self.btn_exit = QPushButton("Exit")

        self.btn_stop_record.setEnabled(False)
        self.btn_replay.setEnabled(False)

        layout.addWidget(self.btn_start_record)
        layout.addWidget(self.btn_stop_record)
        layout.addWidget(self.btn_replay)
        layout.addWidget(self.btn_exit)

        container = QWidget()
        container.setLayout(layout)
        return container


    def _apply_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.position_labels)
        layout.addWidget(self.coordinate_status)
        layout.addWidget(self.button_panel)

        two_plots = QHBoxLayout()
        two_plots.addWidget(self.plot_widget)
        two_plots.addWidget(self.trajectory_widget)

        layout.addLayout(two_plots)

        self.central.setLayout(layout)

    def update_tcp_pose(self, tcp_pose):
        self.val_x.setText(f"{tcp_pose[0]:.4f}")
        self.val_y.setText(f"{tcp_pose[1]:.4f}")
        self.val_z.setText(f"{tcp_pose[2]:.4f}")

        self.val_rx.setText(f"{tcp_pose[3]:.4f}")
        self.val_ry.setText(f"{tcp_pose[4]:.4f}")
        self.val_rz.setText(f"{tcp_pose[5]:.4f}")

    def set_status(self, text):
        self.coordinate_status.setText(text)
