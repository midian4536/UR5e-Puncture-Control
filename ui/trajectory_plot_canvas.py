from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D


class TrajectoryPlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        super().__init__(fig)
        self.setParent(parent)

        self.ax = fig.add_subplot(111, projection="3d")
        # 初始轨迹数据
        self.x = []
        self.y = []
        self.z = []
        # 复现轨迹数据
        self.replay_x = []
        self.replay_y = []
        self.replay_z = []

        # 初始轨迹线条（蓝色）
        (self.line,) = self.ax.plot([], [], [], "b-")
        # 复现轨迹线条（红色）
        (self.replay_line,) = self.ax.plot([], [], [], "r-")

        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")

    def update_trajectory(self, x, y, z):
        self.x.append(x)
        self.y.append(y)
        self.z.append(z)

        self.line.set_data(self.x, self.y)
        self.line.set_3d_properties(self.z)

        xmin, xmax = min(self.x), max(self.x)
        ymin, ymax = min(self.y), max(self.y)
        zmin, zmax = min(self.z), max(self.z)

        margin = 0.05

        self.ax.set_xlim(xmin - margin, xmax + margin)
        self.ax.set_ylim(ymin - margin, ymax + margin)
        self.ax.set_zlim(zmin - margin, zmax + margin)

        self.draw()

    def update_replay_trajectory(self, x, y, z):
        self.replay_x.append(x)
        self.replay_y.append(y)
        self.replay_z.append(z)
        

        self.replay_line.set_data(self.replay_x, self.replay_y)
        self.replay_line.set_3d_properties(self.replay_z)

        # 确保坐标轴范围包含所有轨迹
        all_x = self.x + self.replay_x
        all_y = self.y + self.replay_y
        all_z = self.z + self.replay_z
        xmin, xmax = min(all_x), max(all_x)
        ymin, ymax = min(all_y), max(all_y)
        zmin, zmax = min(all_z), max(all_z)

        margin = 0.05

        self.ax.set_xlim(xmin - margin, xmax + margin)
        self.ax.set_ylim(ymin - margin, ymax + margin)
        self.ax.set_zlim(zmin - margin, zmax + margin)

        self.draw()

    def clear_replay_trajectory(self):
        # 清除复现轨迹数据
        self.replay_x = []
        self.replay_y = []
        self.replay_z = []
        self.replay_line.set_data([], [])
        self.replay_line.set_3d_properties([])
        self.draw()
