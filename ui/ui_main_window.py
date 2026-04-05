from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
)
from PyQt5.QtGui import QFont
from ui.force_plot_canvas import ForcePlotCanvas
from ui.trajectory_plot_canvas import TrajectoryPlotCanvas


class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置全局字体为更大字号
        font = QFont()
        font.setPointSize(14)  # 你可以根据需要调整字号
        self.setFont(font)

        self.setWindowTitle("UR5e Real Time Monitoring")
        self.resize(1080, 900)

        self.central = QWidget(self)
        self.setCentralWidget(self.central)

        self.position_labels = self._create_pose_display()
        self.coordinate_status = self._create_status_label()
        self.button_panel = self._create_button_panel()

        from PyQt5.QtWidgets import QSizePolicy

        self.plot_widget = QWidget(self)
        self.plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.trajectory_widget = QWidget(self)
        self.trajectory_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout_plot = QVBoxLayout(self.plot_widget)
        self.force_plot = ForcePlotCanvas(self.plot_widget)
        self.force_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout_plot.addWidget(self.force_plot)

        layout_traj = QVBoxLayout(self.trajectory_widget)
        self.trajectory_plot = TrajectoryPlotCanvas(self.trajectory_widget)
        self.trajectory_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout_traj.addWidget(self.trajectory_plot)

        self._apply_layout()

    def _create_pose_display(self):
        g = QGridLayout()
        font_label = QFont()
        font_label.setBold(True)

        names = ["X", "Y", "Z", "Rx", "Ry", "Rz"]
        self.vals = []

        for i, name in enumerate(names):
            lbl = QLabel(name)
            lbl.setFont(font_label)
            val = QLabel("0.0000")
            val.setFont(QFont("", 10))
            g.addWidget(lbl, i // 3, (i % 3) * 2)
            g.addWidget(val, i // 3, (i % 3) * 2 + 1)
            self.vals.append(val)

        container = QWidget()
        container.setLayout(g)
        return container

    def _create_status_label(self):
        btn = QPushButton("Monitoring...")
        btn.setEnabled(False)
        font = QFont()
        font.setPointSize(16)
        btn.setFont(font)
        btn.setStyleSheet(
            "QPushButton{background:#e0e0e0;border-radius:6px;padding:6px;font-weight:bold;}"
        )
        return btn

    def _create_button_panel(self):
        layout = QHBoxLayout()

        self.btn_start_record = QPushButton("Start")
        self.btn_stop_record = QPushButton("Stop")
        self.btn_replay = QPushButton("Return")
        self.btn_exit = QPushButton("Exit")

        self.btn_stop_record.setEnabled(False)
        self.btn_replay.setEnabled(False)

        buttons = [
            self.btn_start_record,
            self.btn_stop_record,
            self.btn_replay,
            self.btn_exit,
        ]

        for b in buttons:
            b.setFixedHeight(48)
            b.setMinimumWidth(120)
            font = QFont()
            font.setPointSize(16)
            b.setFont(font)
            b.setStyleSheet("QPushButton{padding:10px 24px;}")

        for b in buttons:
            layout.addWidget(b)

        container = QWidget()
        container.setLayout(layout)
        return container

    def _apply_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.position_labels)
        layout.addWidget(self.coordinate_status)
        layout.addWidget(self.button_panel)

        two_plots = QHBoxLayout()
        two_plots.addWidget(self.plot_widget, stretch=1)
        two_plots.addWidget(self.trajectory_widget, stretch=1)

        layout.addLayout(two_plots)
        layout.setSpacing(12)

        self.central.setLayout(layout)

    def update_tcp_pose(self, tcp_pose):
        for i in range(6):
            self.vals[i].setText(f"{tcp_pose[i]:.4f}")

    def set_status(self, text):
        self.coordinate_status.setText(text)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    ui = UIMainWindow()
    ui.show()
    app.exec_()
