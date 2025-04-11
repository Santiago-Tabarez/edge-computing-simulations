import numpy as np
import plotly.graph_objects as go

# Constants
avg_load = 48530.0  # Average load
xi = 0.08
cpu_price = 0.5
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots

# Generating beta values
betas = np.linspace(1e-9, 1e-6, 100)

# Precompute optimal allocations and net utilities for each beta
optimal_allocations = np.array([np.log(cpu_price / (time_slots_in_horizon * beta * avg_load * xi)) / -xi for beta in betas])
net_utilities = np.zeros((100, 100))

# Calculate net utilities for each combination of beta and optimal allocation
for i, beta in enumerate(betas):
    for j, op_alloc in enumerate(optimal_allocations):
        gross_utility = beta * avg_load * (1 - np.exp(-xi * op_alloc)) * time_slots_in_horizon
        allocation_cost = cpu_price * op_alloc
        net_utilities[i, j] = gross_utility - allocation_cost

# Meshgrid for plotting
B, O = np.meshgrid(betas, optimal_allocations)

# Prepare 3D plot using Plotly
fig = go.Figure(data=[
    go.Surface(z=net_utilities, x=B, y=O, colorscale='Viridis', name='Net Utility Surface'),
    go.Scatter3d(
        x=betas,
        y=optimal_allocations,
        z=[beta * avg_load * (1 - np.exp(-xi * op_alloc)) * time_slots_in_horizon - cpu_price * op_alloc for beta, op_alloc in zip(betas, optimal_allocations)],
        mode='lines+markers',
        marker=dict(size=4, color='red'),
        line=dict(color='red', width=4),
        name='Optimal Net Utility Line'
    )
])

fig.update_layout(
    title='3D Plot of Net Utility as Function of Beta and Allocation',
    scene=dict(
        xaxis_title='Beta',
        yaxis_title='Allocation',
        zaxis_title='Net Utility'
    ),
    annotations=[
        dict(
            showarrow=False,
            text="Red line indicates the net utility for the optimal allocation for each beta.",
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

fig.show()
