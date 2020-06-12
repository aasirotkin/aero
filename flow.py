import numpy as np
from itertools import product
from figure import Grid


class Flow:
    """
    This class creates pattern flow.
    You can combine pattern to create your own!
    x0, y0 is coordinates of origin.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        """
        This method should be implemented by your own.
        """
        raise NotImplementedError

    def velocity(self, xx: np.array, yy: np.array) -> tuple:
        """
        Loop through the all points on the plot.
        """
        xl, yl = len(xx[0]), len(xx)
        vx = np.zeros([xl, yl])
        vy = np.zeros([xl, yl])
        for i, j in product(range(xl), range(yl)):
            vx[i, j], vy[i, j] =\
                self.calc_velocity(xx[i, j], yy[i, j])
        return vx, vy

    def set_grid(self, grid: Grid):
        """
        Calculates velocities at every point on the plot.
        """
        self.vx, self.vy = self.velocity(grid.xx, grid.yy)

    def __init__(self, name: str,
                 x0: float = 0.0, y0: float = 0.0):
        self.name = name
        self.x0, self.y0 = x0, y0
        self.vx, self.vy = np.array, np.array
        self.cp = np.array


class RandomFlow(Flow):
    """
    Random velocity magnitude at every point on the plot.
    max_value is the absolute maximum velocity.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        return np.random.uniform(-self.max_value, self.max_value),\
               np.random.uniform(-self.max_value, self.max_value)

    def __init__(self, max_value: float):
        self.max_value = max_value
        super().__init__('Random')


class UniformFlow(Flow):
    """
    The same velocity magnitude at every point on the plot.
    vel is the magnitude of the velocity.
    alpha is the angel between velocity and horizontal axis.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        return self.vel * np.cos(self.alpha),\
               self.vel * np.sin(self.alpha)

    def __init__(self, vel: float, alpha: float = 0.0):
        self.vel = vel
        self.alpha = alpha
        super().__init__('Uniform')


class SourceFlow(Flow):
    """
    The flow in which velocities come from single point.
    lam is the strength, if it is positive the flow is called
    source, if it is negative the flow is called sink.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        dx, dy = x - self.x0, y - self.y0
        r2 = dx ** 2 + dy ** 2
        lam_pi_r2 = (self.lam_pi / r2) if r2 > 0.0 else 0.0
        vx, vy = lam_pi_r2 * dx, lam_pi_r2 * dy
        return vx, vy

    def __init__(self, lam: float, x0: float = 0.0, y0: float = 0.0):
        self.lam = lam
        self.lam_pi = 0.5 * self.lam / np.pi
        super().__init__('Source L = {:.02f}'.format(self.lam), x0, y0)


class SemiInfiniteFlow(Flow):
    """
    This flow is combined from Uniform and Source (Sink) flows.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        u_vx, u_vy = self.uniform.calc_velocity(x, y)
        s_vx, s_vy = self.source.calc_velocity(x, y)
        return (u_vx + s_vx), \
               (u_vy + s_vy)

    def __init__(self, vel: float, lam: float,
                 x0: float = 0.0, y0: float = 0.0,
                 alpha: float = 0.0):
        self.uniform = UniformFlow(vel, alpha)
        self.source = SourceFlow(lam, x0, y0)
        super().__init__('Semi V = {:.02f} L = {:.02f}'
                         .format(vel, lam), x0, y0)


class OvalShapedFlow(Flow):
    """
    This flow is combined from Uniform and both
    Source and Sink flows.
    dist is a distance between source and sink.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        u_vx, u_vy = self.uniform.calc_velocity(x, y)
        s_vx, s_vy = self.source.calc_velocity(x, y)
        si_vx, si_vy = self.sink.calc_velocity(x, y)
        return (u_vx + s_vx + si_vx), \
               (u_vy + s_vy + si_vy)

    def __init__(self, vel: float, lam: float, dist: float,
                 x0: float = 0.0, y0: float = 0.0,
                 alpha: float = 0.0):
        self.uniform = UniformFlow(vel, alpha)
        self.source = SourceFlow(lam, x0-0.5*dist, y0)
        self.sink = SourceFlow(-lam, x0+0.5*dist, y0)
        super().__init__('Oval V = {:.02f} L = {:.02f} D = {:.02f}'
                         .format(vel, lam, dist), x0, y0)


class DoubletFlow(Flow):
    """
    This flow is appeared if source and sink
    are united in one point.
    kappa is the strength of such flow.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        dx, dy = x - self.x0, y - self.y0
        r2 = dx ** 2 + dy ** 2
        if r2 > 0.0:
            r4 = r2 ** 2
            vx = (self.kappa_pi / r4) * (dy ** 2 - dx ** 2)
            vy = -(self.kappa_pi / r4) * dx * dy
            return vx, vy
        else:
            return 0.0, 0.0

    def __init__(self, kappa: float,
                 x0: float = 0.0, y0: float = 0.0):
        self.kappa_pi = 0.5 * kappa / np.pi
        super().__init__('Doublet K = {:.02f}'
                         .format(kappa), x0, y0)


class NonLiftingCylinderFlow(Flow):
    """
    This flow is combined from Uniform flow
    and Doublet flow.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        u_vx, u_vy = self.uniform.calc_velocity(x, y)
        d_vx, d_vy = self.doublet.calc_velocity(x, y)
        return (u_vx + d_vx), \
               (u_vy + d_vy)

    def __init__(self, vel: float, kappa: float,
                 x0: float = 0.0, y0: float = 0.0,
                 alpha: float = 0.0):
        assert abs(vel) > 0
        self.rad = (0.5 * kappa / (np.pi * abs(vel)))**0.5
        self.uniform = UniformFlow(vel, alpha)
        self.doublet = DoubletFlow(kappa, x0, y0)
        super().__init__('NonLift V = {:.02f} K = {:.02f} R = {:.02f}'
                         .format(vel, kappa, self.rad), x0, y0)


class VortexFlow(Flow):
    """
    In such type of flow velocities are directed
    tangential to the circles.
    gamma is a circulation.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        dx, dy = x - self.x0, y - self.y0
        r2 = dx ** 2 + dy ** 2
        gamma_pi_r2 = (self.gamma_pi / r2) if r2 > 0.0 else 0.0
        vx, vy = gamma_pi_r2 * dy, -gamma_pi_r2 * dx
        return vx, vy

    def __init__(self, gamma: float,
                 x0: float = 0.0, y0: float = 0.0):
        self.gamma_pi = 0.5 * gamma / np.pi
        super().__init__('Vortex G = {:.02f}'.format(gamma), x0, y0)


class LiftingCylinderFlow(Flow):
    """
    This flow is combined from Non Lifting Cylinder flow
    and Vortex flow.
    """
    def calc_velocity(self, x: float, y: float) -> tuple:
        nl_vx, nl_vy = self.non_lift.calc_velocity(x, y)
        v_vx, v_vy = self.vortex.calc_velocity(x, y)
        return (nl_vx + v_vx), \
               (nl_vy + v_vy)

    def __init__(self, vel: float, kappa: float, gamma: float,
                 x0: float = 0.0, y0: float = 0.0, alpha: float = 0.0):
        self.non_lift = NonLiftingCylinderFlow(vel, kappa, x0, y0, alpha)
        self.vortex = VortexFlow(gamma, x0, y0)
        super().__init__('Lift Cylinder R = {:.02f}'
                         .format(self.non_lift.rad), x0, y0)
