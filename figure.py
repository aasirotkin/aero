import re
import numpy as np
from bs4 import BeautifulSoup
import urllib.request as urllib2
from os.path import exists
from os import getcwd
from urllib.error import URLError


class Grid:
    """
    This class creates a grid, which you can use
    to plot your figures and graphics.
    It seemed to be more convenient to create it here,
    in spite of on the first glance it is not
    appropriate place for it.
    """
    def __init__(self, x0: float = 0.0, y0: float = 0.0,
                 width: float = 50.0, height: float = 50.0,
                 num_points: int = 0):
        assert width > 0.0 and height > 0.0 and num_points >= 0
        self.x_num = int(max(width, 1) + 1) \
            if num_points == 0 else num_points
        self.y_num = int(max(height, 1) + 1) \
            if num_points == 0 else num_points
        self.x = np.linspace(x0, x0 + width, self.x_num)
        self.y = np.linspace(y0, y0 + height, self.y_num)
        self.xx, self.yy = np.meshgrid(self.x, self.y)

        x_stream_line = self.xx.min() * np.ones(self.y_num)
        y_stream_line = self.y
        self.stream_line_start = \
            np.vstack((x_stream_line, y_stream_line)).T


class DownloadHelper:
    """
    This class helps you to download
    airfoil shape from the site:
    https://m-selig.ae.illinois.edu/ads/coord_database.html
    Next this class parses downloaded data
    and returns airfoil coordinates.
    Also it can get data from the given directory.
    First initialization required a lot of time.
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DownloadHelper, cls).__new__(cls)
            cls.base_file_path = 'https://m-selig.ae.illinois.edu/ads/'
            cls.is_internet_on = cls.internet_on()
            cls.number = r'\s*([-+]?\d*\.\d*[eE]?[+-]?\d*)\s+([-+]?\d*\.\d*[eE]?[+-]?\d*)\s*'
            if cls.is_internet_on:
                cls.html_page = urllib2.urlopen('{}coord_database.html'
                                                .format(cls.base_file_path))
                cls.soup = BeautifulSoup(cls.html_page, 'html.parser')
        return cls.instance

    @staticmethod
    def internet_on():
        try:
            urllib2.urlopen('http://216.58.192.142', timeout=1)
            return True
        except URLError:
            return False

    def __download_data(self, name: str) -> str:
        """
        Tries to download and parse data by given name.
        """
        attrs = {'href': re.compile(f'{name}\\.dat', re.IGNORECASE)}
        data = self.soup.find('a', attrs=attrs)
        if not data:
            return ''
        read = urllib2.urlopen(self.base_file_path + data.get('href'))
        if not read:
            return ''
        return read.read().decode()

    def __parse_text(self, xy: list, text: list, name: str):
        max_value = 1.1 if 'n642415' not in name else 100.1
        for coord in text:
            find_numbers = re.fullmatch(self.number, coord)
            if find_numbers:
                x = float(find_numbers.group(1))
                y = float(find_numbers.group(2))
                if x > max_value or y > max_value:
                    continue
                xy.append([x, y])

    @staticmethod
    def __check_xy(xy: list, name: str):
        x_previous = xy[0][0]
        if -0.1 < x_previous < 0.1 or \
                'ua79sff' in name:
            direction_changed = False
            xy_up, xy_down = list(), list()
            for i, (x, y) in enumerate(xy):
                if not direction_changed and \
                        x_previous <= x:
                    xy_up.append((x, y))
                    x_previous = x
                else:
                    xy_down.append((x, y))
                    direction_changed = True
            xy_down.sort(key=lambda c: c[0],
                         reverse=True)
            xy.clear()
            xy.extend(xy_up)
            xy.extend(xy_down)
        else:
            xy_reverse = xy[::-1]
            xy.clear()
            xy.extend(xy_reverse)

    def __parse_data(self, text: list, name: str) -> tuple:
        """
        Parses data.
        Returns x and y arrays.
        """
        xy = list()
        self.__parse_text(xy, text, name)
        self.__check_xy(xy, name)
        coord_x, coord_y = np.empty(0), np.empty(0)
        for x, y in xy:
            coord_x = np.append(coord_x, x)
            coord_y = np.append(coord_y, y)
        if coord_x[0] != coord_x[-1] or \
                coord_y[0] != coord_y[-1]:
            coord_x = np.append(coord_x, coord_x[0])
            coord_y = np.append(coord_y, coord_y[0])
        return coord_x, coord_y

    def get_online_data(self, name: str) -> tuple:
        """
        Get data from the internet.
        Name should be writen without extension.
        """
        assert self.is_internet_on
        text = self.__download_data(name)
        return self.__parse_data(text.split('\n'), name)

    def get_data(self, name: str, path: str = '') -> tuple:
        """
        Get data from the local repository.
        """
        if not path:
            path = getcwd()
        path = '{}/{}'.format(path, name)
        if not exists(path):
            return None, None
        with open(path, 'r') as file:
            text = file.read().split('\n')
        return self.__parse_data(text, name)

    def download_all_data(self, path: str = '', ext: str = 'txt') -> None:
        """
        Downloads all data in the given path.
        More than 1500 airfoils.
        """
        assert self.is_internet_on
        if not path:
            path = getcwd()
        attrs = {'href': re.compile(f'.*\\.dat', re.IGNORECASE)}
        data = self.soup.find_all('a', attrs=attrs)
        for d in data:
            name = re.sub('\\.dat', '', d.getText(), flags=re.IGNORECASE)
            urllib2.urlretrieve(self.base_file_path + d.get('href'),
                                '{}/{}.{}'.format(path, name.lower(), ext))


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

    def is_inside(self, x: float, y: float):
        if x < min(self.x) or x > max(self.x) or \
                y < min(self.y) or y > max(self.y):
            return False
        count = 0
        for (x1, y1), (x2, y2) in zip(self.coordinates, self.coordinates[1:]):
            condition_x = (x2 > x1 and x1 <= x <= x2) or \
                          (x1 > x2 and x2 <= x <= x1)
            condition_y = y <= y1 or y <= y2
            if not condition_x or not condition_y:
                continue
            k = (y2 - y1) / (x2 - x1) if x2 != x1 else 0.0
            b = y1 - k * x1
            y3 = k * x + b
            if y3 >= y:
                count += 1
        return count % 2 != 0

    @staticmethod
    def lin_space(start: float, stop: float,
                  num_points: int, endpoint: bool = True) -> np.array:
        assert num_points > 0
        return np.linspace(start, stop, num_points + 1, endpoint=endpoint)

    @property
    def coordinates(self):
        return np.array([(self.x[i], self.y[i])
                         for i in range(self.length)])

    @property
    def length(self):
        return len(self.x)

    @property
    def center(self):
        return sum(self.x) / self.length, \
               sum(self.y) / self.length

    @property
    def rect(self) -> tuple:
        """
        This method returns:
        x0: min x coordinate;
        y0: min y coordinate;
        a - figure length (Ox axis)
        b - figure width (Oy axis)
        """
        x0, y0 = min(self.x), min(self.y)
        dx = abs(max(self.x) - x0)
        dy = abs(max(self.y) - y0)
        return x0, y0, dx, dy


class Ellipse(Figure):
    """
    Ellipse figure:
    a - semi-major axis
    b - semi-minor axis
    """
    def __init__(self, a: float, b: float,
                 x0: float = 0, y0: float = 0,
                 num_points: int = 360):
        assert a > 0 and b > 0
        # X, Y coordinates of ellipse
        tetta = self.lin_space(2 * np.pi, 0.0, num_points)
        coord_x = a * np.cos(tetta) + x0
        coord_y = b * np.sin(tetta) + y0
        self.a, self.b = a, b
        super().__init__('Ellipse', coord_x, coord_y,
                         x0, y0, num_points)

    def is_inside(self, x: float, y: float):
        return (x - self.x0) ** 2 / self.a ** 2 + \
               (y - self.y0) ** 2 / self.b ** 2 <= 1.0


class Circle(Ellipse):
    """
    Circle figure:
    a - radius
    """
    def __init__(self, a: float,
                 x0: float = 0, y0: float = 0,
                 num_points: int = 360):
        super().__init__(a, a, x0, y0, num_points)


class Rectangle(Figure):
    """
    Rectangle figure:
    a - length (Ox axis)
    b - width (Oy axis)
    """
    def __init__(self, a: float, b: float,
                 x0: float = 0, y0: float = 0,
                 num_points: int = 400):
        assert a > 0 and b > 0
        self.a, self.b = a, b
        quarter_points = int(0.25 * num_points)
        # X, Y coordinates of square
        x1 = np.array([x0 + 0.5 * a] * (quarter_points + 1))
        y1 = self.lin_space(y0 + 0.5 * b, y0 - 0.5 * b,
                            quarter_points, False)

        x2 = self.lin_space(x0 + 0.5 * a, x0 - 0.5 * a,
                            quarter_points, False)
        y2 = np.array([y0 - 0.5 * b] * (quarter_points + 1))

        x3 = np.array([x0 - 0.5 * a] * (quarter_points + 1))
        y3 = self.lin_space(y0 - 0.5 * b, y0 + 0.5 * b,
                            quarter_points, False)

        x4 = self.lin_space(x0 - 0.5 * a, x0 + 0.5 * a,
                            quarter_points)
        y4 = np.array([y0 + 0.5 * b] * (quarter_points + 1))

        coord_x = np.concatenate([x1, x2, x3, x4])
        coord_y = np.concatenate([y1, y2, y3, y4])
        super().__init__('Square', coord_x, coord_y,
                         x0, y0, num_points)

    def is_inside(self, x: float, y: float):
        return (self.x0 + 0.5 * self.a) >= x >= (self.x0 - 0.5 * self.a) and \
               (self.y0 + 0.5 * self.b) >= y >= (self.y0 - 0.5 * self.b)


class Square(Rectangle):
    """
    Square figure:
    a - length (Ox and Oy axis)
    """
    def __init__(self, a: float,
                 x0: float = 0, y0: float = 0,
                 num_points: int = 400):
        super().__init__(a, a, x0, y0, num_points)


class Polygon(Figure):
    """
    Polygon figure:
    points - coordinate points,
    each length might be 2.
    """
    def make_side(self, p1: tuple, p2: tuple,
                  num_points: int, endpoint: bool = True) -> tuple:
        """
        This function creates line and divide it
        on points.
        """
        k = (p2[1] - p1[1]) / (p2[0] - p1[0]) \
            if p2[0] != p1[0] else 0
        b = p1[1] - k * p1[0]
        appendix = 1 if endpoint or k == 0 else 0

        x = self.lin_space(p1[0], p2[0], num_points, endpoint) \
            if k != 0 or p1[1] == p2[1] \
            else np.array([p1[0]] * (num_points + appendix))
        y = k * x + b if k != 0 \
            else self.lin_space(p1[1], p2[1],
                                num_points, endpoint)

        return x, y

    @staticmethod
    def atan(xc: float, yc: float, x: float, y: float):
        dx = x - xc
        dy = y - yc
        return np.arctan2(dy, dx)

    def __init__(self, name: str, points: list,
                 num_points: int = 15):
        assert len(points) > 0 and len(points[0]) == 2
        if not name:
            name = 'Polygon'
        length = len(points)
        # X, Y coordinates of triangle
        xc = sum(p[0] for p in points) / length
        yc = sum(p[1] for p in points) / length
        points.sort(key=lambda c: self.atan(xc, yc, c[0], c[1]),
                    reverse=True)
        coord_x, coord_y = np.empty(0), np.empty(0)
        endpoint = False
        for i in range(length):
            if i == (length - 1):
                p1, p2 = points[i], points[0]
                endpoint = True
            else:
                p1, p2 = points[i], points[i + 1]
            x, y = self.make_side(p1, p2,
                                  num_points, endpoint)
            coord_x = np.append(coord_x, x)
            coord_y = np.append(coord_y, y)

        super().__init__(name, coord_x, coord_y)


class Triangle(Polygon):
    """
    Triangle figure:
    p1, p2, p3 - coordinate points,
    they might be a tuple with length equals 2
    """
    def __init__(self, p1: tuple, p2: tuple, p3: tuple,
                 num_points: int = 15):
        assert len(p1) == len(p2) == len(p3) == 2
        assert p1 != p2 != p3
        super().__init__('Triangle', [p1, p2, p3], num_points)


class Airfoil(Figure):
    """
    Airfoil figure:
    Any airfoil you might want to have from the site
    https://m-selig.ae.illinois.edu/ads/coord_database.html
    or from the given path if you downloaded data before.
    Path is used only for offline mode (online = False).
    For online mode (online = True) name should be writen
    without '.dat' extension.
    For offline mode name should be writen fully,
    with extension.
    """
    def __init__(self, name: str, path: str = '',
                 online: bool = False):
        helper = DownloadHelper()
        if not online:
            coord_x, coord_y = helper.get_data(name, path)
        else:
            coord_x, coord_y = helper.get_online_data(name)
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
        bt = yt - kt * xt
        bc = yc - kc * xc
        x0 = (bc - bt) / (kt - kc)
        y0 = kt * x0 + bt
        h4 = abs(y0 - yc)
        gamma = 2.0 * np.arccos(h4 / r)
        return x0, y0, kt, bt, gamma

    def __init__(self, base_r: float, nose_r: float, length: float,
                 num_points: int = 25):
        assert length > base_r > nose_r > 0
        # X, Y coordinates of ogive (it look's like warhead)
        x0, y0, kt, bt, gamma = \
            self.tangent(0.0, length - nose_r, nose_r, -base_r, 0.0)
        gamma1 = 0.5 * (np.pi - gamma)
        gamma2 = gamma1 + gamma

        x1 = self.lin_space(-base_r, x0, num_points, False)
        y1 = kt * x1 + bt

        tetta = self.lin_space(gamma2, gamma1, num_points)
        x2 = nose_r * np.cos(tetta)
        y2 = nose_r * np.sin(tetta) + length - nose_r

        x3 = (-1.0 * x1[::-1])[:-1]
        y3 = (y1[::-1])[:-1]

        x4 = self.lin_space(base_r, -base_r, num_points)
        y4 = np.array([0] * (num_points + 1))

        coord_x = np.concatenate([x1, x2, x3, x4])
        coord_y = np.concatenate([y1, y2, y3, y4])
        super().__init__('Ogive', coord_x, coord_y)
