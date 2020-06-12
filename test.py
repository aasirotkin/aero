from plot import Plot
import figure
import flow
from circulation import Circulation
from os import listdir
import numpy as np
from source_panel_method import SPMCircle, SourcePanelMethod, Geometry


def circulation_flow_figure_test() -> None:
    """
    This test shows example of how circulation
    can be calculated for different shapes and
    for given flow.
    """
    # Make grid for plot
    grid = figure.Grid(-10, -10, 20, 20)

    # Create flow
    lift_flow = flow.LiftingCylinderFlow(vel=2, kappa=5, gamma=15)

    # Calculate velocities in the given points of the grid
    lift_flow.set_grid(grid)

    # Init plot
    plt = Plot(grid)

    # Create figures
    ellipse = figure.Ellipse(8.0, 1.0, 0.0, -7.0)
    circle = figure.Circle(2.0)
    square = figure.Square(4.0, 6.0, 5.0, num_points=360)
    triangle = figure.Triangle((-3.0, 3.0), (-8.0, 3.0), (-5.5, 8.0))

    # Draw the flow's streamlines and the figures
    plt.plot_stream_line(lift_flow)
    plt.plot_figure(ellipse)
    plt.plot_figure(circle)
    plt.plot_figure(square)
    plt.plot_figure(triangle)

    # Calculate circulations inside the given figures
    el_gamma = Circulation.circulation(grid, lift_flow, ellipse)
    ci_gamma = Circulation.circulation(grid, lift_flow, circle)
    sq_gamma = Circulation.circulation(grid, lift_flow, square)
    tr_gamma = Circulation.circulation(grid, lift_flow, triangle)

    # Draw text
    plt.plot_text(ellipse.center, '{:.02f}'.format(el_gamma))
    plt.plot_text(circle.center, '{:.02f}'.format(ci_gamma))
    plt.plot_text(square.center, '{:.02f}'.format(sq_gamma))
    plt.plot_text(triangle.center, '{:.02f}'.format(tr_gamma))

    # Show the plot
    plt.show()


def download_all_airfoil_data() -> None:
    """
    This test downloads all airfoil data
    in the given directory, or in the current
    place if path is not denoted.
    For this test internet connection is required.
    This process might take a lot of time.
    """
    dh = figure.DownloadHelper()
    # Write your own path here
    path = r'C:\Users\User\Documents\python\aero\airfoils_data'
    dh.download_all_data(path)


def plot_airfoil_data() -> None:
    """
    This test plots airfoils by given name.
    """
    # Write your own path here
    path = r'C:\Users\User\Documents\python\aero\airfoils_data'
    # Airfoil name
    name = 'e636.txt'
    airfoil = figure.Airfoil(name, path)
    # name = 'e636'
    # airfoil = figure.Airfoil(name, online=True)

    # Create grid
    x0, y0, dx, dy = airfoil.rect
    grid = figure.Grid(x0, y0, dx, dy)

    # Plot
    plt = Plot(grid)
    plt.plot_figure(airfoil)
    plt.title(name)
    plt.show()


def spm_geometry_and_inside_outside_test():
    # # Write your own path here
    # path = r'C:\Users\User\Documents\python\aero\airfoils_data'
    # # Airfoil name
    # name = 'goe623.txt'
    # test_fig = figure.Airfoil(name, path)

    test_fig = figure.Circle(10, num_points=8)
    # test_fig = figure.Ellipse(10, 5, num_points=100)
    # test_fig = figure.Square(10, num_points=100)
    # test_fig = figure.Rectangle(10, 5, num_points=100)
    # test_fig = figure.Triangle((0, 0), (6, 0), (3, 3))
    # test_fig = figure.Triangle((0, 0), (0, 6), (3, 3))
    # test_fig = figure.Triangle((0, 0), (6, 3), (3, 4))
    # test_fig = figure.Polygon('Polygon',
    #                           [(1, 1), (2, 2), (3, 3),
    #                            (2, 3), (2, 4), (1, 4), (0, 3)])
    # test_fig = figure.Ogive(2, 1, 5)
    geometry = Geometry(test_fig, 1)
    x0, y0, dx, dy = test_fig.rect
    grid = figure.Grid(x0 - 0.1*dx, y0 - 0.1*dy,
                       dx + 0.2*dx, dy + 0.2*dy, 20)
    plt = Plot(grid)
    plt.plot_figure(test_fig)
    plt.plot_source_panel_method(geometry)

    for x in grid.x:
        for y in grid.y:
            res = test_fig.is_inside(x, y)
            if not res:
                plt.plot_point(x, y, '.y')

    plt.show()


def save_all_airfoil_spm_geometry_test():
    """
    This test saves all airfoil images to
    the given directory.
    """
    # Write your own path with airfoil data here
    airfoil_path = r'C:\Users\User\Documents\python\aero\airfoils_data'
    # Write your own path to save images here (Path must already exists)
    picture_path = r'C:\Users\User\Documents\python\aero\airfoils_picture'
    files = listdir(airfoil_path)
    for i, file in enumerate(files):
        airfoil = figure.Airfoil(file, airfoil_path)

        geometry = Geometry(airfoil, 1)

        # Create grid
        x0, y0, dx, dy = airfoil.rect
        grid = figure.Grid(x0 - 0.1*dx, y0 - 0.1*dy,
                           dx + 0.2*dx, dy + 0.2*dy)

        # Plot
        plt = Plot(grid)
        plt.plot_figure(airfoil)
        plt.plot_source_panel_method(geometry)
        plt.title(file)
        plt.save_image('{}\\{}.png'.format(picture_path, file))
        plt.close()
        print(i, file)


def circle_pressure_coef_spm_test():
    circle = figure.Circle(10, num_points=100)
    spm = SPMCircle(circle, 1.0)

    grid = figure.Grid(0.0, -3.0, 2.0 * np.pi, 4.0)
    plt = Plot(grid)
    tetta = np.linspace(0.0, 2.*np.pi, 360)
    cp = 1. - 4. * (np.sin(tetta) ** 2)
    analytic_coef = figure.Figure('Pressure coef', tetta, cp)
    plt.plot_figure(analytic_coef)

    spm_coef = figure.Figure('Spm coef', spm.geometry.angle_cp, spm.surface_cp)
    plt.plot_figure(spm_coef, '*b')

    plt.show()


def airfoil_pressure_coef_spm_test():
    # Write your own path here
    path = r'C:\Users\User\Documents\python\aero\airfoils_data'
    # Airfoil name
    name = 'naca2412.txt'
    test_fig = figure.Airfoil(name, path)
    spm = SourcePanelMethod(test_fig, 1, 0.0 * np.pi / 180.0)

    cp_upper = spm.surface_cp[spm.geometry.yc >= 0]
    x_upper = spm.geometry.xc[spm.geometry.yc >= 0]
    cp_lower = spm.surface_cp[spm.geometry.yc < 0]
    x_lower = spm.geometry.xc[spm.geometry.yc < 0]
    fgr_upper = figure.Figure('', x_upper, cp_upper)
    fgr_lower = figure.Figure('', x_lower, cp_lower)
    x01, y01, dx1, dy1 = fgr_upper.rect
    x02, y02, dx2, dy2 = fgr_lower.rect

    grid = figure.Grid(min(x01, x02), min(y01, y02),
                       max(dx1, dx2), max(dy1, dy2))
    plt = Plot(grid)
    plt.plot_figure(fgr_upper, '*b')
    plt.plot_figure(fgr_lower, '-r')
    plt.invert_y_axis()
    plt.show()


def grid_source_panel_method_test():
    fgr = figure.Circle(10, num_points=180)
    # fgr = figure.Ellipse(10, 5, num_points=100)
    # fgr = figure.Square(10, num_points=100)
    # fgr = figure.Rectangle(10, 5, num_points=100)
    # fgr = figure.Triangle((0, 0), (6, 0), (3, 3))
    # fgr = figure.Triangle((0, 0), (0, 6), (3, 3))
    # fgr = figure.Triangle((0, 0), (6, 3), (3, 4))
    # fgr = figure.Polygon('Polygon',
    #                           [(1, 1), (2, 2), (3, 3),
    #                            (2, 3), (2, 4), (1, 4), (0, 3)])
    # fgr = figure.Ogive(2, 1, 5)
    spm = SourcePanelMethod(fgr, 1)

    grid = figure.Grid(-15.0, -15.0, 30.0, 30.0, 30)
    plt = Plot(grid)

    spm.set_grid(grid)

    plt.plot_filled_figure(fgr)
    plt.plot_stream_line(spm)
    # plt.plot_flow(spm)
    # plt.plot_contour(spm)

    plt.show()


# circulation_flow_figure_test()
# download_all_airfoil_data()
# plot_airfoil_data()
# spm_geometry_and_inside_outside_test()
# save_all_airfoil_spm_geometry_test()
# circle_pressure_coef_spm_test()
# airfoil_pressure_coef_spm_test()
# grid_source_panel_method_test()
