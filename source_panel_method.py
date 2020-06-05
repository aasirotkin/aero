from figure import Figure, Geometry, Grid
from flow import UniformFlow
import numpy as np
from shapely.geometry.polygon import Polygon


class SourcePanelMethod:
    def __init__(self, figure: Figure, flow: UniformFlow, grid: Grid = None):
        self.v_inf = flow.vel
        self.alpha = flow.alpha
        self.geometry = Geometry(figure.length - 1)

        self.n_variables = np.zeros(shape=(self.geometry.length,
                                           self.geometry.length))
        self.t_variables = np.zeros(shape=(self.geometry.length,
                                           self.geometry.length))
        self.vn_variables = np.empty(0)
        self.vt_variables = np.empty(0)
        self.lambdas = np.empty(0)
        self.n_velocities = np.empty(self.geometry.length)
        self.t_velocities = np.empty(self.geometry.length)
        self.cp = np.empty(0)

        self.calc_geometry(figure)
        self.calc_integrand()
        self.calc_lambdas()
        self.calc_velocities()
        self.calc_pressure_coef()
        if grid:
            pass

    def calc_geometry(self, figure: Figure):
        self.geometry.xi = figure.x[:-1]
        self.geometry.yi = figure.y[:-1]
        self.geometry.xc = 0.5 * (figure.x[0:-1] + figure.x[1:])
        self.geometry.yc = 0.5 * (figure.y[0:-1] + figure.y[1:])
        dx = figure.x[1:] - figure.x[0:-1]
        dy = figure.y[1:] - figure.y[0:-1]
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
        i0 = 0.5*c
        i1 = (s**2 + 2*a*s + b) / b if b > 0.0 else 0.0
        i2 = (d - a*c) / e if e > 0.0 else 0.0
        i3 = (s + a) / e if e > 0.0 else 0.0
        i4 = a / e if e > 0.0 else 0.0
        i5 = i0 * np.log(i1)
        i6 = i2 * (np.arctan(i3) - np.arctan(i4))
        return i5 + i6

    def calc_integrand(self):
        self.vn_variables = 2.0 * np.pi * self.v_inf * \
                            self.geometry.cos_de
        self.vt_variables = 2.0 * np.pi * self.v_inf * \
                            self.geometry.sin_de
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
                self.n_variables[i][j] = \
                    self.integrand(i, j, self.geometry.s[j],
                                   a[j], b[j], c_n[j], d_n[j], e[j])
                self.t_variables[i][j] = \
                    self.integrand(i, j, self.geometry.s[j],
                                   a[j], b[j], c_t[j], d_t[j], e[j], 0.0)

    def calc_lambdas(self):
        self.lambdas = np.linalg.solve(self.n_variables,
                                       -self.vn_variables)
        assert sum(self.lambdas * self.geometry.s) < 1**-10

    def calc_velocities(self):
        coef = 1.0 / (2.0 * np.pi)
        for i in range(self.geometry.length):
            n_summary = sum(self.lambdas*self.n_variables[i])
            t_summary = sum(self.lambdas*self.t_variables[i])
            self.n_velocities[i] = coef * (self.vn_variables[i] + n_summary)
            self.t_velocities[i] = coef * (self.vt_variables[i] + t_summary)

    def calc_pressure_coef(self):
        v = (self.t_velocities ** 2 + self.n_velocities ** 2) ** 0.5
        self.cp = 1.0 - (v / self.v_inf) ** 2
