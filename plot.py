import matplotlib.pyplot as plt
from flow import Flow
from figure import Grid, Figure


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

    @staticmethod
    def plot_figure(figure: Figure):
        plt.plot(figure.x, figure.y)

    def __plot(self, flow: Flow,
               is_plot: bool = False,
               is_stream_line: bool = False) -> None:
        if is_plot:
            plt.plot(self.grid.xx, self.grid.yy, 'k.')
            plt.quiver(self.grid.xx, self.grid.yy, flow.vx, flow.vy, color='r')

        if is_stream_line:
            plt.streamplot(self.grid.xx, self.grid.yy, flow.vx, flow.vy,
                           linewidth=0.5, density=10,
                           color='r', arrowstyle='-',
                           start_points=self.grid.stream_line_start)
            plt.quiver(self.grid.x, self.grid.y, flow.vx, flow.vy)

        plt.title('{} Flow'.format(flow.name))

    @staticmethod
    def plot_text(x: float, y: float, text: str) -> None:
        plt.text(x, y, text,
                 horizontalalignment='center',
                 verticalalignment='center')

    @staticmethod
    def title(text: str) -> None:
        plt.title(text)

    @staticmethod
    def show():
        """
        This method must be called after all
        flows and figures were plotted.
        """
        plt.show()
