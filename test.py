from plot import Plot
import figure
import flow
from circulation import Circulation

# Make grid for plot
grid = figure.Grid(-10, -10, 20, 20)

# Create flow
lift_flow = flow.LiftingCylinderFlow(vel=2, kappa=5, gamma=15)

# Calculate velocities in the given points of the grid
lift_flow.set_grid(grid)

# Init plot
plt = Plot(grid)

# Create figures
ellipse = figure.Ellipse(8.0, 1.0, 0.0, -7.0, num_points=360)
circle = figure.Ellipse(2.0, 2.0, num_points=360)
square = figure.Square(4.0, 4.0, 6.0, 5.0, num_points=360)
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
plt.plot_text(ellipse.x0, ellipse.y0, '{:.02f}'.format(el_gamma))
plt.plot_text(circle.x0, circle.y0, '{:.02f}'.format(ci_gamma))
plt.plot_text(square.x0, square.y0, '{:.02f}'.format(sq_gamma))
plt.plot_text(triangle.x0, triangle.y0, '{:.02f}'.format(tr_gamma))

# Show the plot
plt.show()
