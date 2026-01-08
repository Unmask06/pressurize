"""
Dynamic Valve Pressurization Simulator
A Python Dash web application that simulates the dynamic pressurization 
of a downstream vessel as a valve opens linearly over time.
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
