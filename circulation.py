import numpy as np
from scipy import interpolate
from figure import Grid, Figure
from flow import Flow


class Circulation:
    """
    This class contains only one method,
    which helps you calculate circulation
    using trapezoid method.
    """
    @staticmethod
    def circulation(grid: Grid, flow: Flow, figure: Figure) -> float:
        """
        Calculate circulation for given Grid, Flow and Figure
        using the trapezoid method
        """
        # Interpolate X velocities from grid
        fx = interpolate.RectBivariateSpline(grid.y, grid.x, flow.vx)
        # Interpolate Y velocities from grid
        fy = interpolate.RectBivariateSpline(grid.y, grid.x, flow.vy)
        # X velocity component on figure
        vx = fx.ev(figure.y, figure.x)
        # Y velocity component on figure
        vy = fy.ev(figure.y, figure.x)
        # Get circulation by computing integral using trapezoid rule
        gamma = -(np.trapz(vx, figure.x) +
                  np.trapz(vy, figure.y))
        return gamma
