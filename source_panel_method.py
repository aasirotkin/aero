from figure import Figure
from flow import UniformFlow
import numpy as np


class SourcePanelMethod:
    def __init__(self, figure: Figure, flow: UniformFlow):
        self.flow = flow
        self.geometry = list()
        self.n_variables = list()
        self.t_variables = list()
        self.calc_geometry(figure)
        self.calc_integrand()

    def calc_geometry(self, figure: Figure):
        coords = figure.coordinates
        for i in range(figure.length - 1):
            x_i, y_i = coords[i]
            x_i_1, y_i_1 = coords[i+1]
            xc = 0.5 * (x_i + x_i_1)
            yc = 0.5 * (y_i + y_i_1)
            dx = x_i - x_i_1
            dy = y_i - y_i_1
            s = (dx ** 2 + dy ** 2) ** 0.5
            fi = np.arctan2(dy, dx)
            fi_ge = fi*180./np.pi
            if fi < 0.0:
                fi += 2.0 * np.pi
            betta = fi + 0.5 * np.pi
            delta = betta - self.flow.alpha
            nx = xc + s*np.cos(betta)
            ny = yc + s*np.sin(betta)
            sin_fi = np.sin(fi)
            cos_fi = np.cos(fi)
            sin_de = np.sin(delta)
            cos_de = np.cos(delta)

            self.geometry.append((xc, yc,
                                  nx, ny,
                                  s, x_i, y_i,
                                  fi, sin_fi, cos_fi,
                                  delta, sin_de, cos_de))

    @staticmethod
    def integrand(i: int, j: int, s: float,
                  a: float, b: float, c: float,
                  d: float, e: float) -> float:
        if i == j:
            return np.pi
        i0 = 0.5*c
        i1 = (s**2 + 2*a*s + b) / b if b > 0.0 else 0.0
        i2 = (d - a*c) / e if e > 0.0 else 0.0
        i3 = (s + a) / e if e > 0.0 else 0.0
        i4 = a / e if e > 0.0 else 0.0
        i5 = i0 * np.log(i1)
        i6 = i2 * (np.arctan(i3) - np.arctan(i4))
        return i5 + i6

    def calc_integrand(self):
        two_pi_vel = -2.0 * np.pi * self.flow.vel
        for i, g1 in enumerate(self.geometry):
            (xc_i, yc_i, nx, ny,
             s, x_i, y_i, f_i, sin_fi_i, cos_fi_i,
             delta, sin_de_i, cos_de_i) = g1
            self.n_variables.append(
                [-two_pi_vel * cos_de_i])
            self.t_variables.append(
                [-two_pi_vel * sin_de_i])
            for j, g2 in enumerate(self.geometry):
                (xc_j, yc_j, nx, ny,
                 s, x_j, y_j, f_j, sin_fi_j, cos_fi_j,
                 delta, sin_de_j, cos_de_j) = g2
                a = - (xc_i - x_j) * cos_fi_j \
                    - (yc_i - y_j) * sin_fi_j
                b = (xc_i - x_j) ** 2 \
                    + (yc_i - y_j) ** 2
                c_n = np.sin(f_i - f_j)
                c_t = -np.cos(f_i - f_j)
                d_n = - (xc_i - x_j) * sin_fi_i \
                    + (yc_i - y_j) * cos_fi_i
                d_t = (xc_i - x_j) * cos_fi_i \
                    + (yc_i - y_j) * sin_fi_i
                e_sqrt = b - a ** 2
                e = e_sqrt ** 0.5 if e_sqrt > 0.0 else 0.0

                self.n_variables[i].append(
                    self.integrand(i, j, s, a, b, c_n, d_n, e))

                self.t_variables[i].append(
                    self.integrand(i, j, s, a, b, c_t, d_t, e))
