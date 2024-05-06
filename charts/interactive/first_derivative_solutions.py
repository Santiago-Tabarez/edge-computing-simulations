import numpy as np
import plotly.graph_objects as go

# Parameters
h = 1.0  # fixed value for h

# Define xi and y ranges
xi = np.linspace(0.1, 2, 100)
y = np.linspace(0.1, 2, 100)

# Create meshgrid for xi and y
Xi, Y = np.meshgrid(xi, y)

# Calculate the function values
Z = Y * (Xi * np.exp(-h * Xi))

# Create the 3D surface plot
fig = go.Figure(data=[go.Surface(z=Z, x=Xi, y=Y)])
fig.update_layout(title='Interactive 3D Surface Plot of f(xi, y) = y * (xi * exp(-h * xi))',
                  scene=dict(
                      xaxis_title='xi',
                      yaxis_title='y',
                      zaxis_title='f(xi, y)'),
                  autosize=False,
                  width=800,
                  height=800)

# Show the plot
fig.show()
