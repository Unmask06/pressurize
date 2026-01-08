"""Dynamic Valve Pressurization Simulator.

A Dash web application for simulating gas flow through a valve into a vessel.
Provides real-time visualization of pressure and flow dynamics with multiple
valve opening modes and composition-based gas property calculations.
"""

import dash
import dash_bootstrap_components as dbc

from src.callbacks.callbacks import register_callbacks
from src.layouts.main_layout import create_layout

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.FLATLY],
    title="Valve Pressurization Simulator"
)

# Set the layout
app.layout = create_layout()

# Register callbacks
register_callbacks(app)

# Run server
if __name__ == "__main__":
    app.run(debug=True, port=8050)
