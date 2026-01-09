"""Common UI components for the Dash application."""

import dash_bootstrap_components as dbc
from dash import html


def create_input_field(label, id, value, step=None, min_val=None):
    """Create a labeled numeric input field."""
    return html.Div([
        html.Label(label, className="input-label"),
        dbc.Input(
            id=id,
            type="number",
            value=value,
            step=step or "any",
            min=min_val,
            className="mb-2"
        )
    ], className="input-group-custom")

def create_kpi_card(id, title, icon, color):
    """Create a KPI (Key Performance Indicator) display card."""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={"fontSize": "2rem"}),
            ], style={"textAlign": "center"}),
            html.H3(id=id, className="kpi-value text-center", style={"color": color}),
            html.P(title, className="kpi-label text-center mb-0")
        ])
    ], className="kpi-card")
