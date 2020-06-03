from figure import Figure
import numpy as np


class SourcePanelMethod:
    def __init__(self, figure: Figure):
        self.geometry = list()
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
            nx = xc + np.cos(betta)
            ny = yc + np.sin(betta)

            self.geometry.append((xc, yc, nx, ny))
