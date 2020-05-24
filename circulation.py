import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt


class Figure:
    def __init__(self, name: str, x_coord: np.array, y_coord: np.array):
        self.name = name
        self.x_coord = x_coord
        self.y_coord = y_coord


class Ellipse(Figure):
    def __init__(self, a: float, b: float,
                 x0: float = 0, y0: float = 0,
                 num_points: int = 100):
        assert a > 0 and b > 0
        # X, Y coordinates of ellipse
        tetta = np.linspace(0.0, 2.0 * np.pi, num_points)
        coord_x = a * np.cos(tetta) + x0
        coord_y = b * np.sin(tetta) + y0
        super().__init__('Ellipse', coord_x, coord_y)


class Square(Figure):
    def __init__(self, a: float, b: float,
                 x0: float = 0, y0: float = 0,
                 num_points: int = 400):
        assert a > 0 and b > 0
        quarter_points = int(0.25*num_points)
        # X, Y coordinates of square
        x1 = np.array([x0 + 0.5*a]*quarter_points)
        y1 = np.linspace(y0 - 0.5*b, y0 + 0.5*b, quarter_points)

        x2 = np.linspace(x0 + 0.5 * a, x0 - 0.5 * a, quarter_points)
        y2 = np.array([y0 + 0.5*b]*quarter_points)

        x3 = np.array([x0 - 0.5*a]*quarter_points)
        y3 = y1[::-1]

        x4 = x2[::-1]
        y4 = np.array([y0 - 0.5*b]*quarter_points)

        coord_x = np.concatenate([x1, x2, x3, x4])
        coord_y = np.concatenate([y1, y2, y3, y4])
        super().__init__('Square', coord_x, coord_y)


class Triangle(Figure):
    @staticmethod
    def lin_space(p1: tuple, p2: tuple, num_points: int) -> tuple:
        k = (p2[1] - p1[1])/(p2[0] - p1[0]) \
            if p2[0] != p1[0] else 0
        b = p1[1] - k*p1[0]

        x = np.linspace(p1[0], p2[0], num_points) if k != 0 or p1[1] == p2[1] \
            else np.array([p1[0]]*num_points)
        y = k * x + b if k != 0 \
            else np.linspace(p1[1], p2[1], num_points)

        return x, y

    def __init__(self, p1: tuple, p2: tuple, p3: tuple,
                 num_points: int = 15):
        assert len(p1) == len(p2) == len(p3) == 2
        assert p1 != p2 != p3
        # X, Y coordinates of triangle
        x1, y1 = self.lin_space(p1, p2, num_points)
        x2, y2 = self.lin_space(p2, p3, num_points)
        x3, y3 = self.lin_space(p3, p1, num_points)

        coord_x = np.concatenate([x1, x2, x3])
        coord_y = np.concatenate([y1, y2, y3])
        super().__init__('Triangle', coord_x, coord_y)


class Ogive(Figure):
    @staticmethod
    def tangent(xc: float, yc: float, r: float, xt: float, yt: float):
        h1 = abs(yc - yt)
        h2 = abs(xc - xt)
        h1h2 = np.sqrt(h1 * h1 + h2 * h2)
        a = np.arcsin(r / h1h2)
        b = np.arcsin(h1 / h1h2)
        kt = np.tan(a + b)
        kc = -1.0 / kt
        bt = yt - kt*xt
        bc = yc - kc*xc
        x0 = (bc - bt) / (kt - kc)
        y0 = kt * x0 + bt
        h4 = abs(y0 - yc)
        gamma = 2.0 * np.arccos(h4 / r)
        return x0, y0, kt, bt, gamma

    def __init__(self, base_r: float, nose_r: float, length: float,
                 num_points: int = 20):
        assert length > base_r > nose_r > 0
        # X, Y coordinates of ogive (it look's like warhead)
        x0, y0, kt, bt, gamma = \
            self.tangent(0.0, length - nose_r, nose_r, -base_r, 0.0)
        gamma1 = 0.5 * (np.pi - gamma)
        gamma2 = gamma1 + gamma

        x1 = np.linspace(-base_r, x0, num_points)
        y1 = kt * x1 + bt

        tetta = np.linspace(gamma2, gamma1, num_points)
        x2 = nose_r * np.cos(tetta)
        y2 = nose_r * np.sin(tetta) + length - nose_r

        x3 = -1.0 * x1[::-1]
        y3 = y1[::-1]

        x4 = np.linspace(base_r, -base_r, num_points)
        y4 = np.array([0]*num_points)

        coord_x = np.concatenate([x1, x2, x3, x4])
        coord_y = np.concatenate([y1, y2, y3, y4])
        super().__init__('Ogive', coord_x, coord_y)


class Circulation:
    def __init__(self, figure: Figure):
        self.figure = figure
        Circulation.init_mesh_grid(self, figure.x_coord, figure.y_coord)
        Circulation.circulation(self, figure.x_coord, figure.y_coord)

    @staticmethod
    def init_mesh_grid(cls, x_coord: np.array, y_coord: np.array) -> None:
        # Grid boundaries
        min_x_value = int(x_coord.min() - 1)
        max_x_value = int(x_coord.max() + 1)
        min_y_value = int(y_coord.min() - 1)
        max_y_value = int(y_coord.max() + 1)
        points_x = max(5, max_x_value - min_x_value + 1)
        points_y = max(5, max_y_value - min_y_value + 1)

        # X, Y grid points
        cls.x = np.linspace(min_x_value, max_x_value, points_x)
        cls.y = np.linspace(min_y_value, max_y_value, points_y)

        # Random X, Y velocities
        cls.rvx = np.random.rand(points_x, points_y)
        cls.rvy = np.random.rand(points_x, points_y)

        # Create the meshgrid
        cls.xx, cls.yy = np.meshgrid(cls.x, cls.y)

    @staticmethod
    def circulation(cls, x_coord: np.array, y_coord: np.array) -> None:
        # Interpolate X velocities from grid to ellipse points
        fx = interpolate.RectBivariateSpline(cls.x, cls.y, cls.rvx)
        # Interpolate Y velocities from grid to ellipse points
        fy = interpolate.RectBivariateSpline(cls.x, cls.y, cls.rvy)
        # X velocity component on ellipse
        cls.vx = fx.ev(x_coord, y_coord)
        # Y velocity component on ellipse
        cls.vy = fy.ev(x_coord, y_coord)
        # Get circulation by computing integral using trapezoid rule
        cls.gamma = -(np.trapz(cls.vx, x_coord) +
                      np.trapz(cls.vy, y_coord))

    def plot(self) -> None:
        plt.plot(self.xx, self.yy, 'k.')
        plt.quiver(self.xx, self.yy, self.rvx, self.rvy, color='r')
        plt.plot(self.figure.x_coord, self.figure.y_coord, 'b.')
        plt.quiver(self.figure.x_coord, self.figure.y_coord,
                   self.vx, self.vy, color='b')
        plt.title('{} Circulation = {:.3f}'.format(self.figure.name, self.gamma))
        plt.xlim([self.xx.min()-1, self.xx.max()+1])
        plt.ylim([self.yy.min()-1, self.yy.max()+1])
        plt.gca().set_aspect('equal')
        plt.show()


if __name__ == '__main__':
    # fig = Ellipse(15, 15, 10, 10)
    # circulation = Circulation(fig)
    # circulation.plot()

    # fig = Square(15, 10, -5, 10)
    # circulation = Circulation(fig)
    # circulation.plot()

    # fig = Triangle((10, 10), (20, 20), (15, -5))
    # circulation = Circulation(fig)
    # circulation.plot()

    fig = Ogive(3, 1, 9)
    circulation = Circulation(fig)
    circulation.plot()

