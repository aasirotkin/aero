from flow import Flow
from figure import Figure, Grid
import numpy as np


class Geometry:
    def __init__(self, figure: Figure, alpha: float = 0.0):
        # amount of panels
        self.length = figure.length - 1
        # start coordinates
        self.xi = figure.x[:-1]
        self.yi = figure.y[:-1]
        # control point coordinates
        self.xc = 0.5 * (figure.x[0:-1] + figure.x[1:])
        self.yc = 0.5 * (figure.y[0:-1] + figure.y[1:])
        # length of each panel
        self.dx = figure.x[1:] - figure.x[0:-1]
        self.dy = figure.y[1:] - figure.y[0:-1]
        self.s = (self.dx ** 2 + self.dy ** 2) ** 0.5
        # main angle of each panel
        self.fi = self.arc_tan_2(self.dy, self.dx)
        # angle between normal vector and panel
        self.betta = self.fi + 0.5 * np.pi
        # angle between normal vector and free stream velocity
        self.delta = self.betta - alpha
        # normal vector components
        self.nx = self.xc + self.s * np.cos(self.betta)
        self.ny = self.yc + self.s * np.sin(self.betta)
        # sin, cos for angles
        self.sin_fi = np.sin(self.fi)
        self.cos_fi = np.cos(self.fi)
        self.sin_de = np.sin(self.delta)
        self.cos_de = np.cos(self.delta)

    @staticmethod
    def arc_tan_2(y: np.array, x: np.array) -> np.array:
        fi = np.arctan2(y, x)
        for i, f in enumerate(fi):
            if f < 0.0:
                fi[i] += 2.0 * np.pi
        return fi


class CircleGeometry(Geometry):
    def __init__(self, figure: Figure, alpha: float = 0.0):
        super().__init__(figure, alpha)
        # angle between control point and Ox axis
        self.angle_cp = self.arc_tan_2(self.yc, self.xc)


class SourcePanelMethod(Flow):
    def __init__(self, figure: Figure, velocity: float, alpha: float = 0.0,
                 geometry: Geometry = None):
        self.figure = figure
        self.v_inf = velocity
        self.alpha = alpha
        self.geometry = geometry if geometry else Geometry(figure, alpha)

        self.lambdas = np.empty(0)
        self.surface_velocity = np.empty(0)
        self.surface_cp = np.empty(0)

        self.calc_lambdas()

        super().__init__('SPM {}'.format(figure.name))

    def set_grid(self, grid: Grid):
        """
        Calculates velocities at every point on the plot.
        """
        self.vx, self.vy = self.velocity(grid.xx, grid.yy)
        v = (self.vx ** 2 + self.vy ** 2) ** 0.5
        self.cp = 1.0 - (v / self.v_inf) ** 2

    def calc_velocity(self, x: float, y: float) -> tuple:
        if self.figure.is_inside(x, y):
            return 0.0, 0.0
        coef = 1.0 / (2.0 * np.pi)
        mx = np.empty(self.geometry.length)
        my = np.empty(self.geometry.length)
        self.calc_xy_integrand(mx, my, x, y)
        n_summary = sum(self.lambdas * mx)
        t_summary = sum(self.lambdas * my)
        vx = self.v_inf * np.cos(self.alpha) + coef * n_summary
        vy = self.v_inf * np.sin(self.alpha) + coef * t_summary
        return vx, vy

    def calc_xy_integrand(self, mx: np.array, my: np.array,
                          x: float, y: float) -> None:
        a = - (x - self.geometry.xi) * self.geometry.cos_fi \
            - (y - self.geometry.yi) * self.geometry.sin_fi
        b = (x - self.geometry.xi) ** 2 + (y - self.geometry.yi) ** 2
        c_x = -self.geometry.cos_fi
        c_y = -self.geometry.sin_fi
        d_x = (x - self.geometry.xi)
        d_y = (y - self.geometry.yi)
        e_sqrt = b - a ** 2
        e = np.empty(self.geometry.length)
        for j, ei in enumerate(e_sqrt):
            e[j] = e_sqrt[j] ** 0.5 if e_sqrt[j] > 0.0 else 0.0

        for j in range(self.geometry.length):
            mx[j] = self.integrand(-1, j, self.geometry.s[j],
                                   a[j], b[j], c_x[j], d_x[j], e[j])
            my[j] = self.integrand(-1, j, self.geometry.s[j],
                                   a[j], b[j], c_y[j], d_y[j], e[j], 0.0)

    @staticmethod
    def integrand(i: int, j: int, s: float,
                  a: float, b: float, c: float,
                  d: float, e: float, equal: float = np.pi) -> float:
        if i == j:
            return equal
        i0 = 0.5 * c
        i1 = (s ** 2 + 2 * a * s + b) / b if b > 0.0 else 0.0
        i2 = (d - a * c) / e if e > 0.0 else 0.0
        i3 = (s + a) / e if e > 0.0 else 0.0
        i4 = a / e if e > 0.0 else 0.0
        i5 = i0 * np.log(i1)
        i6 = i2 * (np.arctan(i3) - np.arctan(i4))
        return i5 + i6

    def calc_surface_integrand(self, mn: np.array, mt: np.array) -> None:
        for i in range(self.geometry.length):
            a = - (self.geometry.xc[i] - self.geometry.xi) * \
                self.geometry.cos_fi \
                - (self.geometry.yc[i] - self.geometry.yi) * \
                self.geometry.sin_fi
            b = (self.geometry.xc[i] - self.geometry.xi) ** 2 \
                + (self.geometry.yc[i] - self.geometry.yi) ** 2
            c_n = np.sin(self.geometry.fi[i] - self.geometry.fi)
            c_t = -np.cos(self.geometry.fi[i] - self.geometry.fi)
            d_n = - (self.geometry.xc[i] - self.geometry.xi) * \
                self.geometry.sin_fi[i] \
                + (self.geometry.yc[i] - self.geometry.yi) * \
                self.geometry.cos_fi[i]
            d_t = (self.geometry.xc[i] - self.geometry.xi) * \
                self.geometry.cos_fi[i] \
                + (self.geometry.yc[i] - self.geometry.yi) * \
                self.geometry.sin_fi[i]
            e_sqrt = b - a ** 2
            e = np.empty(self.geometry.length)
            for j, ei in enumerate(e_sqrt):
                e[j] = e_sqrt[j] ** 0.5 if e_sqrt[j] > 0.0 else 0.0

            for j in range(self.geometry.length):
                mn[i][j] = self.integrand(i, j, self.geometry.s[j],
                                          a[j], b[j], c_n[j], d_n[j], e[j])
                mt[i][j] = self.integrand(i, j, self.geometry.s[j],
                                          a[j], b[j], c_t[j], d_t[j], e[j], 0.0)

    def calc_surface_cp(self, vn_inf: np.array, vt_inf: np.array,
                        mn: np.array, mt: np.array):
        coef = 1.0 / (2.0 * np.pi)
        n_velocities = np.empty(self.geometry.length)
        t_velocities = np.empty(self.geometry.length)
        for i in range(self.geometry.length):
            n_summary = sum(self.lambdas * mn[i])
            t_summary = sum(self.lambdas * mt[i])
            n_velocities[i] = coef * (vn_inf[i] + n_summary)
            t_velocities[i] = coef * (vt_inf[i] + t_summary)
        assert all(vn < 1e-12 for vn in n_velocities)
        self.surface_cp = 1.0 - (t_velocities / self.v_inf) ** 2

    def calc_lambdas(self):
        vn_inf = 2.0 * np.pi * self.v_inf * self.geometry.cos_de
        vt_inf = 2.0 * np.pi * self.v_inf * self.geometry.sin_de
        mn = np.zeros(shape=(self.geometry.length,
                             self.geometry.length))
        mt = np.zeros(shape=(self.geometry.length,
                             self.geometry.length))
        self.calc_surface_integrand(mn, mt)

        self.lambdas = np.linalg.solve(mn, -vn_inf)
        # print(sum(self.lambdas * self.geometry.s))
        # assert sum(self.lambdas * self.geometry.s) < 1e-12

        self.calc_surface_cp(vn_inf, vt_inf, mn, mt)


class SPMCircle(SourcePanelMethod):
    def __init__(self, figure: Figure, velocity: float, alpha: float = 0.0):
        geometry = CircleGeometry(figure, alpha)
        super().__init__(figure, velocity, alpha, geometry)

    def calc_surface_cp(self, vn_inf: np.array, vt_inf: np.array,
                        mn: np.array, mt: np.array):
        super().calc_surface_cp(vn_inf, vt_inf, mn, mt)
        assert min(self.surface_cp) > -(3.0 + 1e-12) and \
            max(self.surface_cp) < (1.0 + 1e-12)
