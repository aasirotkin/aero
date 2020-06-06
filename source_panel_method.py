from flow import Flow
from figure import Circle
import numpy as np


class Geometry:
    def __init__(self, length):
        self.length = length
        self.s = np.empty(0)
        self.xc = np.empty(0)
        self.yc = np.empty(0)
        self.ac = np.empty(0)
        self.nx = np.empty(0)
        self.ny = np.empty(0)
        self.xi = np.empty(0)
        self.yi = np.empty(0)
        self.fi = np.empty(0)
        self.sin_fi = np.empty(0)
        self.cos_fi = np.empty(0)
        self.delta = np.empty(0)
        self.sin_de = np.empty(0)
        self.cos_de = np.empty(0)


class SourcePanelMethodOverCylinderBody(Flow):
    def calc_velocity(self, x: float, y: float) -> tuple:
        if (x ** 2 + y ** 2) ** 0.5 <= self.radius:
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

    def __init__(self, circle: Circle, velocity: float, alpha: float = 0.0):
        self.v_inf = velocity
        self.alpha = alpha
        self.radius = circle.radius
        self.geometry = Geometry(circle.length - 1)
        self.calc_geometry(circle)

        self.lambdas = np.empty(0)
        self.n_velocities = np.empty(self.geometry.length)
        self.t_velocities = np.empty(self.geometry.length)
        self.cp = np.empty(0)

        self.calc_lambdas()
        self.calc_pressure_coef()

        super().__init__('SPM Cylinder')

    def calc_xy_integrand(self,
                          n_variables: np.array,
                          t_variables: np.array,
                          x: float, y: float):
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
            n_variables[j] = \
                self.integrand(-1, j, self.geometry.s[j],
                               a[j], b[j], c_x[j], d_x[j], e[j])
            t_variables[j] = \
                self.integrand(-1, j, self.geometry.s[j],
                               a[j], b[j], c_y[j], d_y[j], e[j], 0.0)

    def calc_geometry(self, circle: Circle):
        self.geometry.xi = circle.x[:-1]
        self.geometry.yi = circle.y[:-1]
        self.geometry.xc = 0.5 * (circle.x[0:-1] + circle.x[1:])
        self.geometry.yc = 0.5 * (circle.y[0:-1] + circle.y[1:])
        dx = circle.x[1:] - circle.x[0:-1]
        dy = circle.y[1:] - circle.y[0:-1]
        self.geometry.ac = np.arctan2(self.geometry.yc, self.geometry.xc)
        for i, a in enumerate(self.geometry.ac):
            if a < 0.0:
                self.geometry.ac[i] += 2.0 * np.pi
        self.geometry.s = (dx ** 2 + dy ** 2) ** 0.5
        self.geometry.fi = np.arctan2(dy, dx)
        for i, f in enumerate(self.geometry.fi):
            if f < 0.0:
                self.geometry.fi[i] += 2.0 * np.pi
        betta = self.geometry.fi + 0.5 * np.pi
        self.geometry.delta = betta - self.alpha
        self.geometry.nx = self.geometry.xc + \
                           self.geometry.s * np.cos(betta)
        self.geometry.ny = self.geometry.yc + \
                           self.geometry.s * np.sin(betta)
        self.geometry.sin_fi = np.sin(self.geometry.fi)
        self.geometry.cos_fi = np.cos(self.geometry.fi)
        self.geometry.sin_de = np.sin(self.geometry.delta)
        self.geometry.cos_de = np.cos(self.geometry.delta)

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

    def calc_surface_integrand(self,
                               n_variables: np.array,
                               t_variables: np.array):
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
                n_variables[i][j] = \
                    self.integrand(i, j, self.geometry.s[j],
                                   a[j], b[j], c_n[j], d_n[j], e[j])
                t_variables[i][j] = \
                    self.integrand(i, j, self.geometry.s[j],
                                   a[j], b[j], c_t[j], d_t[j], e[j], 0.0)

    def calc_velocities(self,
                        vn_inf: np.array, vt_inf: np.array,
                        n_integrand: np.array, t_integrand: np.array):
        coef = 1.0 / (2.0 * np.pi)
        for i in range(self.geometry.length):
            n_summary = sum(self.lambdas * n_integrand[i])
            t_summary = sum(self.lambdas * t_integrand[i])
            self.n_velocities[i] = coef * (vn_inf[i] + n_summary)
            self.t_velocities[i] = coef * (vt_inf[i] + t_summary)

    def calc_lambdas(self):
        vn_inf = 2.0 * np.pi * self.v_inf * \
                 self.geometry.cos_de
        vt_inf = 2.0 * np.pi * self.v_inf * \
                 self.geometry.sin_de
        n_integrand = np.zeros(shape=(self.geometry.length,
                                      self.geometry.length))
        t_integrand = np.zeros(shape=(self.geometry.length,
                                      self.geometry.length))

        self.calc_surface_integrand(n_integrand, t_integrand)

        self.lambdas = np.linalg.solve(n_integrand, -vn_inf)
        assert sum(self.lambdas * self.geometry.s) < 1 ** -10

        self.calc_velocities(vn_inf, vt_inf,
                             n_integrand, t_integrand)

    def calc_pressure_coef(self):
        v = (self.t_velocities ** 2 + self.n_velocities ** 2) ** 0.5
        self.cp = 1.0 - (v / self.v_inf) ** 2
        assert max(self.cp) <= 1.0 and min(self.cp) >= -3.0
