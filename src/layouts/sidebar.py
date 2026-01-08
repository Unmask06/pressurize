import dash_bootstrap_components as dbc
from dash import dcc, html

from src.components.common import create_input_field


def get_sidebar():
    return html.Div([
        html.H4("⚙️ Simulation Parameters", className="sidebar-title"),
        
        html.Hr(style={"borderColor": "rgba(255,255,255,0.3)"}),
        
        html.H6("Pressure Settings", style={"color": "#ecf0f1", "marginTop": "15px"}),
        dbc.Row([
            dbc.Col(create_input_field("Upstream (psig)", "input-p-upstream", 2800), width=6),
            dbc.Col(create_input_field("Downstream (psig)", "input-p-downstream", 800), width=6),
        ]),
        
        html.Hr(style={"borderColor": "rgba(255,255,255,0.3)"}),
        
        html.H6("Vessel & Valve", style={"color": "#ecf0f1"}),
        create_input_field("Vessel Volume (ft³)", "input-volume", 62),
        create_input_field("Valve ID (inches)", "input-valve-id", 3.7),
        
        html.Div([
            html.Label("Valve Opening Mode", className="input-label"),
            dcc.Dropdown(
                id="input-opening-mode",
                options=[
                    {"label": "Linear", "value": "linear"},
                    {"label": "Exponential", "value": "exponential"},
                    {"label": "Fixed (Instant)", "value": "fixed"},
                    {"label": "Quick Opening", "value": "quick_opening"}
                ],
                value="linear",
                clearable=False,
                style={"color": "#2c3e50"}
            )
        ], className="input-group-custom"),

        # k_curve input - initially hidden, toggled via callback
        html.Div([
            create_input_field("Exponential Slope (k)", "input-k-curve", 4.0, step=0.1)
        ], id="container-k-curve", style={'display': 'none'}),

        create_input_field("Valve Opening Time (s)", "input-opening-time", 30),
        
        html.Hr(style={"borderColor": "rgba(255,255,255,0.3)"}),
        
        html.H6("Gas Properties", style={"color": "#ecf0f1"}),
        
        dbc.Row([
            dbc.Col(create_input_field("Temp (°F)", "input-temp", 55), width=6),
            dbc.Col(create_input_field("Mol Mass", "input-molar-mass", 16.9, step=0.01), width=6),
        ]),
        dbc.Row([
            dbc.Col(create_input_field("Z-Factor", "input-z-factor", 0.771, step=0.001), width=6),
            dbc.Col(create_input_field("k (Gamma)", "input-k-ratio", 1.9, step=0.01), width=6),
        ]),
        create_input_field("Discharge Coeff (Cd)", "input-cd", 0.9, step=0.01),
        
        dbc.Button(
            "🚀 Run Simulation",
            id="btn-run",
            color="success",
            className="run-button"
        ),
        
    ], className="sidebar")
