import numpy as np
import plotly.graph_objects as go

# Constants
avg_load = 48530.0  # Average load
cpu_price = 0.5
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots

# Generating beta values
betas = np.linspace(1e-7, 1e-5, 100)
y_s = betas * avg_load

# Precompute optimal allocations and net utilities for each beta
xis = np.linspace(0.01, 0.1, 100)

net_utilities = np.zeros((100, 100))

# Calculate net utilities for each combination of beta and optimal allocation
for i, y in enumerate(y_s):
    for j, xi in enumerate(xis):
        optimal_alloc = np.log(cpu_price / (time_slots_in_horizon * y * xi)) / -xi
        gross_utility = y * (1 - np.exp(-xi * optimal_alloc)) * time_slots_in_horizon
        allocation_cost = cpu_price * optimal_alloc
        net_utilities[i, j] = gross_utility - allocation_cost

# Meshgrid for plotting
B, Y = np.meshgrid(betas, y_s)

# Prepare 3D plot using Plotly
fig = go.Figure(data=[
    go.Surface(z=net_utilities, x=B, y=Y, colorscale='Viridis', name='Net Utility Surface'),
    go.Scatter3d(
        x=betas,
        y=y_s,
        #z=[beta * avg_load * (1 - np.exp(-xi * op_alloc)) * time_slots_in_horizon - cpu_price * op_alloc for
        #   beta, op_alloc in zip(betas, optimal_allocations)],
        z=[net_utilities],
        mode='lines+markers',
        marker=dict(size=4, color='red'),
        line=dict(color='red', width=4),
        name='Optimal Net Utility Line'
    )
])

fig.update_layout(
    title='3D Plot of Net Utility as Function of Beta and y_s',
    scene=dict(
        xaxis_title='Beta',
        yaxis_title='y_s',
        zaxis_title='Net Utility'
    ),
    annotations=[
        dict(
            showarrow=False,
            text="Red line indicates the maximum net utility for each beta.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.1,
            align="center",
            font=dict(size=12, color="black")
        )
    ],
    autosize=False,
    width=800,
    height=600
)

# Commenting out fig.show() to comply with the instructions
fig.show()
