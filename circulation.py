import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt


class Circulation:
    def __init__(self, x_coord: np.array, y_coord: np.array,
                 name: str = ''):
        self.name = name
        self.x_coord = x_coord
        self.y_coord = y_coord
        Circulation.init_mesh_grid(self, x_coord, y_coord)
        Circulation.circulation(self, x_coord, y_coord)

    @staticmethod
    def init_mesh_grid(cls, x_coord: np.array, y_coord: np.array) -> None:
        # Grid boundaries
        min_x_value = int(x_coord.min() - 1)
        max_x_value = int(x_coord.max() + 1)
        min_y_value = int(y_coord.min() - 1)
        max_y_value = int(y_coord.max() + 1)
        points_x = max_x_value - min_x_value + 1
        points_y = max_y_value - min_y_value + 1

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
        plt.plot(self.x_coord, self.y_coord, 'b.')
        plt.quiver(self.x_coord, self.y_coord, self.vx, self.vy, color='b')
        plt.title('{} Circulation'.format(self.name))
        plt.xlim([self.xx.min()-1, self.xx.max()+1])
        plt.ylim([self.yy.min()-1, self.yy.max()+1])
        plt.gca().set_aspect('equal')
        plt.show()


class EllipseCirculation(Circulation):
    def __init__(self, a: float, b: float,
                 x0: float = 0, y0: float = 0,
                 num_points: int = 100):
        assert a > 0 and b > 0
        # X, Y coordinates of ellipse
        tetta = np.linspace(0.0, 2.0 * np.pi, num_points)
        coord_x = a * np.cos(tetta) + x0
        coord_y = b * np.sin(tetta) + y0
        super().__init__(coord_x, coord_y, 'Ellipse')


if __name__ == '__main__':
    ellipse = EllipseCirculation(10, 10, 0, 0)
    ellipse.plot()
