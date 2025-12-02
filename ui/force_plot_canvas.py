from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ForcePlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        super().__init__(fig)
        self.setParent(parent)

        self.ax = fig.add_subplot(111)
        self.ax.grid(True)

        self.t_data = []
        self.fx = []
        self.fy = []
        self.fz = []

        (self.line_fx,) = self.ax.plot([], [], "r-")
        (self.line_fy,) = self.ax.plot([], [], "g-")
        (self.line_fz,) = self.ax.plot([], [], "b-")

        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Force")

    def update_plot(self, fx, fy, fz, t):
        self.t_data.append(t)
        self.fx.append(fx)
        self.fy.append(fy)
        self.fz.append(fz)

        self.line_fx.set_data(self.t_data, self.fx)
        self.line_fy.set_data(self.t_data, self.fy)
        self.line_fz.set_data(self.t_data, self.fz)

        self.ax.relim()
        self.ax.autoscale_view()
        self.draw()
