from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D


class TrajectoryPlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        super().__init__(fig)
        self.setParent(parent)

        self.ax = fig.add_subplot(111, projection="3d")

        self.x = []
        self.y = []
        self.z = []

        (self.line,) = self.ax.plot([], [], [], "b-")

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
