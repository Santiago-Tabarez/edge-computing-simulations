import numpy as np
from scipy.optimize import curve_fit

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Button, TextAreaInput, CustomJS
from bokeh.models.tools import PointDrawTool
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler

# ---- model definition ----
def model(t, *params):
    """
    Sum of K sinusoids plus a positive offset.
    params = [a1, phi1, a2, phi2, ..., aK, phiK, avg_load]
    Here phi_k = -2π * t_k / 86400 (phase per unit k)
    t in hours [0,24]
    """
    t_norm = t / 24.0
    K = (len(params) - 1) // 2
    avg = params[-1]
    y = np.full_like(t_norm, avg)
    for k in range(K):
        a = params[2*k]
        phi_unit = params[2*k + 1]
        # apply k+1 multiplier to phase
        phi = (k+1) * phi_unit
        y += a * np.sin(2 * np.pi * (k+1) * t_norm + phi)
    return y

# ---- Bokeh document factory ----
def modify_doc(doc):
    N = 24
    t = np.linspace(0, 24, N)

    # initial guess uses t_k offsets to phi_unit
    init_params = [
        25313, -47340/86400*2*np.pi,
        -8832, -49080/86400*2*np.pi,
        1757, -44520/86400*2*np.pi,
        -2873, -44880/86400*2*np.pi,
        48530
    ]

    y0 = np.clip(model(t, *init_params), 0, None)
    source = ColumnDataSource(data=dict(x=t, y=y0))

    p = figure(
        title="Drag points to sculpt the load curve",
        x_axis_label="Hour of Day", y_axis_label="Load",
        tools="pan,wheel_zoom,reset",
        width=1200, height=800
    )
    renderer = p.scatter('x', 'y', source=source, size=12)
    p.y_range.start = 0
    p.x_range.start = 0; p.x_range.end = 24

    drag_tool = PointDrawTool(renderers=[renderer])
    p.add_tools(drag_tool)
    p.toolbar.active_drag = drag_tool

    params_area = TextAreaInput(value="", rows=6, width=400)
    fit_button = Button(label="Submit & Fit Curve", button_type="primary")
    copy_button = Button(label="Copy parameters to clipboard", button_type="success")
    copy_button.js_on_click(CustomJS(args=dict(text=params_area), code="navigator.clipboard.writeText(text.value);"))

    def update_callback():
        data = source.data
        x = np.array(data['x'])
        y = np.clip(np.array(data['y']), 0, None)

        popt, _ = curve_fit(model, x, y, p0=init_params)
        y_fit = np.clip(model(t, *popt), 0, None)
        source.data = dict(x=t, y=y_fit)

        K = (len(popt) - 1) // 2
        a_k = [float(f"{popt[2*k]:.2f}") for k in range(K)]
        # invert phase back to t_k seconds: phi_unit = popt[2*k+1], so t_k = -phi_unit*86400/(2π)
        t_k = [float(f"{(-popt[2*k+1] * 86400/(2*np.pi)):.1f}") for k in range(K)]
        avg = float(f"{popt[-1]:.2f}")

        text = []
        text.append(f"avg_load: [{avg}]")
        text.append("a_k:")
        text.append(f"  - {a_k}")
        text.append("t_k:")
        text.append(f"  - {t_k}")
        params_area.value = "\n".join(text)

    fit_button.on_click(update_callback)

    controls = column(fit_button, copy_button, params_area)
    layout = row(p, controls)
    doc.add_root(layout)
    doc.title = "Interactive Load Hyperparameter Editor"

if __name__ == "__main__":
    apps = {'/': Application(FunctionHandler(modify_doc))}
    server = Server(apps, port=5006, allow_websocket_origin=["localhost:5006"])
    server.io_loop.add_callback(server.show, "/")
    server.start(); server.io_loop.start()
