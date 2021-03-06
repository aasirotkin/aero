import matplotlib.pyplot as plt
from flow import Flow
from figure import Grid, Figure
from source_panel_method import Geometry


class Plot:
    """
    This class helps you to visualise your figure and flow.
    """
    def __init__(self, grid: Grid):
        self.grid = grid
        plt.xlim([grid.xx.min(), grid.xx.max()])
        plt.ylim([grid.yy.min(), grid.yy.max()])
        plt.gca().set_aspect('equal')

    def plot_flow(self, flow: Flow) -> None:
        """
        This method draws velocities and their directions.
        """
        self.__plot(flow, is_plot=True)

    def plot_stream_line(self, flow: Flow) -> None:
        """
        This method draws streamlines which start from the
        left side of the plot.
        """
        self.__plot(flow, is_stream_line=True)

    def plot_contour(self, flow: Flow) -> None:
        self.__plot(flow, is_contour=True)

    @staticmethod
    def plot_figure(figure: Figure, style: str = 'k') -> None:
        plt.plot(figure.x, figure.y, style)

    @staticmethod
    def plot_filled_figure(figure: Figure, style: str = 'k') -> None:
        plt.fill(figure.x, figure.y, style)

    @staticmethod
    def invert_y_axis() -> None:
        plt.gca().invert_yaxis()

    @staticmethod
    def plot_source_panel_method(geometry: Geometry):
        for i in range(geometry.length):
            x1, y1 = geometry.xc[i], geometry.yc[i]
            x2, y2 = geometry.nx[i], geometry.ny[i]
            if i == 0:
                color = 'r'
            elif i == 1:
                color = 'b'
            else:
                color = 'k'
            plt.plot((x1, x2), (y1, y2), color)

    def __plot(self, flow: Flow,
               is_plot: bool = False,
               is_stream_line: bool = False,
               is_contour: bool = False) -> None:
        if is_plot:
            plt.plot(self.grid.xx, self.grid.yy, 'k.')
            plt.quiver(self.grid.xx, self.grid.yy, flow.vx, flow.vy, color='r')

        if is_stream_line:
            plt.streamplot(self.grid.xx, self.grid.yy, flow.vx, flow.vy,
                           linewidth=0.5, density=10,
                           color='r', arrowstyle='-',
                           start_points=self.grid.stream_line_start)
            plt.quiver(self.grid.x, self.grid.y, flow.vx, flow.vy)

        if is_contour:
            plt.contourf(self.grid.xx, self.grid.yy,
                         flow.cp, 500, cmap='jet')

        plt.title('{} Flow'.format(flow.name))

    @staticmethod
    def plot_text(xy: tuple, text: str) -> None:
        assert len(xy) == 2
        plt.text(xy[0], xy[1], text,
                 horizontalalignment='center',
                 verticalalignment='center')

    @staticmethod
    def plot_point(x: float, y: float, style: str = '.k'):
        plt.plot(x, y, style)

    @staticmethod
    def title(text: str) -> None:
        plt.title(text)

    @staticmethod
    def save_image(path: str) -> None:
        plt.savefig(path, bbox_inches='tight')

    @staticmethod
    def close() -> None:
        plt.clf()

    @staticmethod
    def show():
        """
        This method must be called after all
        flows and figures were plotted.
        """
        plt.show()
