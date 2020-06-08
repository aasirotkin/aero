from plot import Plot
import figure
import flow
from circulation import Circulation
from os import listdir
import numpy as np
from source_panel_method import SPMCircle, SourcePanelMethod


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


def save_airfoil_images():
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

        # Create grid
        x0, y0, dx, dy = airfoil.rect
        grid = figure.Grid(x0 - 0.1, y0 - 0.1,
                           dx + 0.2, dy + 0.2)

        # Plot
        plt = Plot(grid)
        plt.plot_figure(airfoil)
        plt.title(file)
        plt.save_image('{}\\{}.png'.format(picture_path, file))
        plt.close()
        print(i, file)


def pressure_coef_source_panel_method_test():
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


def grid_source_panel_method_test():
    fgr = figure.Circle(10, num_points=25)
    spm = SPMCircle(fgr, 1.0)

    # fgr = figure.Square(10)
    # spm = SourcePanelMethod(fgr, 1)

    grid = figure.Grid(-15.0, -15.0, 30.0, 30.0, 30)
    plt = Plot(grid)

    spm.set_grid(grid)

    plt.plot_figure(fgr)
    plt.plot_stream_line(spm)
    # plt.plot_flow(spm)

    plt.show()


# circulation_flow_figure_test()
# download_all_airfoil_data()
# plot_airfoil_data()
# save_airfoil_images()
# pressure_coef_source_panel_method_test()
# grid_source_panel_method_test()
