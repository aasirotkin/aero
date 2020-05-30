import re
import numpy as np
from bs4 import BeautifulSoup
import urllib.request as urllib2


class Grid:
    """
    This class creates a grid, which you can use
    to plot your figures and graphics.
    It seemed to be more convenient to create it here,
    in spite of on the first glance it is not
    appropriate place for it.
    """
    def __init__(self, x0: int = 0, y0: int = 0,
                 width: int = 50, height: int = 50,
                 num_points: int = 0):
        assert width > 0 and height > 0 and num_points >= 0
        self.x_num = width + 1 if num_points == 0 else num_points
        self.y_num = height + 1 if num_points == 0 else num_points
        self.x = np.linspace(x0, x0 + width, self.x_num)
        self.y = np.linspace(y0, y0 + height, self.y_num)
        self.xx, self.yy = np.meshgrid(self.x, self.y)

        x_stream_line = self.xx.min() * np.ones(self.y_num)
        y_stream_line = self.y
        self.stream_line_start = \
            np.vstack((x_stream_line, y_stream_line)).T


class Figure:
    """
    Figure is a class to create the figure you want,
    only one thing you need is coordinates.
    Don't forget that coordinate length might
    be the same for both 'x' and 'y' coordinates.
    x, y - coordinates
    x0, y0 - displacement coordinates
    num_points - number of split points
    """
    def __init__(self, name: str, x: np.array, y: np.array,
                 x0: float = 0, y0: float = 0,
                 num_points: int = 100):
        assert len(x) == len(y)
        self.name = name
        self.x, self.y = x, y
        self.x0, self.y0 = x0, y0
        self.num_points = num_points


class Ellipse(Figure):
    """
    Ellipse figure:
    a - semi-major axis
    b - semi-minor axis
    """
    def __init__(self, a: float, b: float,
                 x0: float = 0, y0: float = 0,
                 num_points: int = 100):
        assert a > 0 and b > 0
        # X, Y coordinates of ellipse
        tetta = np.linspace(0.0, 2.0 * np.pi, num_points)
        coord_x = a * np.cos(tetta) + x0
        coord_y = b * np.sin(tetta) + y0
        super().__init__('Ellipse', coord_x, coord_y,
                         x0, y0, num_points)


class Square(Figure):
    """
    Square figure:
    a - length (Ox axis)
    b - width (Oy axis)
    """
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
        super().__init__('Square', coord_x, coord_y,
                         x0, y0, num_points)


class Triangle(Figure):
    """
    Triangle figure:
    p1, p2, p3 - coordinate points,
    they might be a tuple with length equals 2
    """
    @staticmethod
    def lin_space(p1: tuple, p2: tuple, num_points: int) -> tuple:
        """
        This function creates line and divide it
        on points.
        """
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
        super().__init__('Triangle', coord_x, coord_y,
                         p1[0], p1[1])


class UIUSHelper:
    """
    This class helps yot to download
    airfoil shape from the site:
    https://m-selig.ae.illinois.edu/ads/coord_database.html
    Next this class parse download data
    and return airfoil coordinates.
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(UIUSHelper, cls).__new__(cls)
            cls.base_file_path = 'https://m-selig.ae.illinois.edu/ads/'
            cls.html_page = urllib2.urlopen('{}coord_database.html'.format(cls.base_file_path))
            cls.soup = BeautifulSoup(cls.html_page, 'html.parser')
        return cls.instance

    @staticmethod
    def parse_data(data: str) -> tuple:
        """
        Parse data using the pattern:
        \s*(\d+\.?\d+)\s+(\d+\.?\d+)\s*
        Returns result as bool and two coordinates.
        """
        find_numbers = re.fullmatch(r'\s*(\d+\.?\d+)\s+(\d+\.?\d+)\s*',
                                    data)
        if find_numbers and len(find_numbers.groups()) > 1:
            x, y = find_numbers.group(1), find_numbers.group(2)
            return True, float(x), float(y)
        return False, 0, 0

    def get_data(self, name: str) -> tuple:
        """
        Trying to download and parse data by given name.
        """
        coord_x, coord_y = np.empty(0), np.empty(0)
        attrs = {'href': re.compile(f'{name}\\.dat', re.IGNORECASE)}
        data = self.soup.find('a', attrs=attrs)
        if not data:
            return coord_x, coord_y
        read = urllib2.urlopen(self.base_file_path + data.get('href'))
        if not read:
            return coord_x, coord_y
        coords = read.read().decode().split('\r\n')
        for coord in coords:
            res, x, y = self.parse_data(coord)
            if res:
                coord_x = np.append(coord_x, x)
                coord_y = np.append(coord_y, y)
        return coord_x, coord_y


class Airfoil(Figure):
    """
    Airfoil figure:
    Any airfoil you might want to have from the site:
    https://m-selig.ae.illinois.edu/ads/coord_database.html
    Name should be writen without .dat!
    """
    def __init__(self, name: str):
        helper = UIUSHelper()
        coord_x, coord_y = helper.get_data(name)
        assert len(coord_x) == len(coord_y) > 0
        super().__init__(name, coord_x, coord_y)


class Ogive(Figure):
    """
    Ogive figure:
    base_r - base radius
    nose_r - nose radius
    length - whole length
    """
    @staticmethod
    def tangent(xc: float, yc: float, r: float, xt: float, yt: float):
        """
        This function helps to find the tangent point
        between base and nose!
        """
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
