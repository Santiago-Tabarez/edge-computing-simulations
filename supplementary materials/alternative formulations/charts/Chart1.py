# variant_optimal_curves_plotly_tabs.py
"""Interactive dashboard to compare several variants of the utility model

Baseline model (reference used throughout):
    U_base(h, X) = ρ * (1 - exp(-ξ(X) * e * h)) - d * h
    ξ(X) = d / (ρ * X)  (X > 0)
    h*_base(X) = (ρ / (e d X)) * (1 + ln X)  (valid for X > 1/e)

The script plots, for each variant, both curves in the same figure:
   • h*(X)   (left y‑axis, blue)
   • U(h*(X)) (right y‑axis, red)

Variants (modify cost term g(X) and/or add bonuses):
  1. Var 1     : g(X) = 1
  2. Var 1‑bis : g(X) = 1 and bonus +k ln(1+X)
  3. Var 2     : g(X) = 1/(1+βX)
  4. Var 3     : g(X) = e^{−βX}

General formulas used for each variant (excluding only regions with h* ≤ 0):
    expr = ρ ξ(X) / (d g(X))                 # interior‑optimum condition
    h*(X) = (1/ξ(X)) · ln(expr)             # if expr > 1; else undefined (NaN)
    U(h*) = ρ[1 - exp(-ξ(X)·h*) - f(X)] - d·h*·g(X)

All negative U(h*) values are displayed whenever the corresponding h*(X) is
positive; only points where h*(X) ≤ 0 are blanked.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    from ipywidgets import Tab, VBox
    USE_TABS = True
except ImportError:
    USE_TABS = False

# ---------------- Baseline parameters ----------------
rho   = 1.0   # benefit scale
# current marginal cost (can be changed interactively)
d     = 1.0
alpha = 0.6   # f(X) = e^{-αX}
beta  = 0.4   # parameter in g(X) for variants 2 & 3
k     = 0.7   # bonus strength for variant 1‑bis

# ---------------- Domain -----------------------------
# strictly positive X; up to 15 is enough to see asymptotics
X = np.linspace(0.01, 15, 1500)

# ---------------- Baseline helper functions ----------

def xi_base(X, rho=rho, d=d):
    """ξ(X) = d / (ρ X)."""
    return d / (rho * X)

def h_star_base(X, rho=rho, d=d):
    """h*_base(X) = (ρ / (e d X)) (1 + ln X)   valid for X > 1/e."""
    h = (rho / (np.e * d * X)) * (1 + np.log(X))
    return np.where(X > 1/np.e, h, 0.0)

def U_base(X, rho=rho, d=d):
    """Utility evaluated at h*_base."""
    xi = xi_base(X, rho, d)
    h  = h_star_base(X, rho, d)
    return rho * (1 - np.exp(-xi * np.e * h)) - d * h

# baseline curves (for information; not plotted inside the tab set)
h_base_curve = h_star_base(X)
U_base_curve = U_base(X)

# --------------- Shared building blocks --------------
xiX = xi_base(X)               # alias used later
fX  = np.exp(-alpha * X)

# Helper: build h* and U for any g(X)

def calc_h_U(g_val):
    expr = rho * xiX / (d * g_val)
    h_raw = np.where(expr > 1, (1/xiX) * np.log(expr), np.nan)
    U_raw = rho * (1 - np.exp(-xiX * h_raw) - fX) - d * h_raw * g_val
    U = np.where(np.isnan(h_raw), np.nan, U_raw)  # mask where h* invalid
    return h_raw, U

# ---------------- Variant 1 : g = 1 ------------------
g1  = 1.0
h1, U1 = calc_h_U(g1)

# ---------------- Variant 1‑bis : g = 1, +k ln(1+X) --
h1b = h1.copy()
U1b_raw = rho * (1 - np.exp(-xiX * h1b) - fX + k * np.log(1 + X)) - d * h1b
U1b = np.where(np.isnan(h1b), np.nan, U1b_raw)

# ---------------- Variant 2 : g = 1/(1+βX) -----------
g2 = 1 / (1 + beta * X)
h2, U2 = calc_h_U(g2)

# ---------------- Variant 3 : g = e^{−βX} ------------
g3 = np.exp(-beta * X)
h3, U3 = calc_h_U(g3)

# ---------------- Figure helper ----------------------

def dual_fig(title, h_vals, U_vals):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=X, y=h_vals, name="h*(X)",
                             line=dict(color="#1f77b4")), secondary_y=False)
    fig.add_trace(go.Scatter(x=X, y=U_vals, name="U(h*)",
                             line=dict(color="#d62728")), secondary_y=True)
    fig.update_layout(title=title, height=450,
                      legend=dict(x=0.02, y=0.95))
    fig.update_xaxes(title_text="X")
    fig.update_yaxes(title_text="h*", secondary_y=False, rangemode="tozero")
    fig.update_yaxes(title_text="Utility", secondary_y=True)
    return fig

figs = [
    dual_fig("Var 1 (g=1)",               h1,  U1 ),
    dual_fig("Var 1‑bis (+k ln(1+X))",     h1b, U1b),
    dual_fig("Var 2 (g=1/(1+βX))",        h2,  U2 ),
    dual_fig("Var 3 (g=e^{−βX})",         h3,  U3 )
]

# ---------------- Display ----------------------------
if USE_TABS:
    tabs = Tab(children=[go.FigureWidget(fig) for fig in figs])
    for i, name in enumerate(["Var 1", "Var 1‑bis", "Var 2", "Var 3"]):
        tabs.set_title(i, name)
    display(VBox([tabs]))
else:
    for fig in figs:
        fig.show()
