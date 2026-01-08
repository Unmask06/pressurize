import dash_bootstrap_components as dbc
from dash import dcc, html

from src.components.common import create_kpi_card
from src.layouts.sidebar import get_sidebar


def get_main_content():
    return html.Div([
        # Header
        html.Div([
            html.H2("Dynamic Valve Pressurization Simulator", 
                    className="text-center mb-2", 
                    style={"color": "#2c3e50", "fontWeight": "bold"}),
            html.P("Real-gas flow simulation with choked and subsonic flow regimes",
                className="text-center text-muted mb-4")
        ]),
        
        # KPI Cards Row
        dbc.Row([
            dbc.Col([
                create_kpi_card("kpi-peak-flow", "Peak Flow Rate (lb/hr)", "📈", "#e74c3c")
            ], md=3),
            dbc.Col([
                create_kpi_card("kpi-final-pressure", "Final Pressure (psig)", "🎯", "#3498db")
            ], md=3),
            dbc.Col([
                create_kpi_card("kpi-equil-time", "Equilibrium Time (s)", "⏱️", "#27ae60")
            ], md=3),
            dbc.Col([
                create_kpi_card("kpi-total-mass", "Total Mass Flow (lb)", "⚖️", "#9b59b6")
            ], md=3),
        ], className="mb-4"),
        
        # Graph
        html.Div([
            dcc.Graph(id="graph-simulation", style={"height": "500px"})
        ], className="graph-container"),
        
        # Data table (collapsible)
        html.Div([
            dbc.Button(
                "📊 Show/Hide Data Table",
                id="btn-toggle-table",
                color="secondary",
                outline=True,
                className="mt-3"
            ),
            dbc.Collapse([
                html.Div(id="data-table", className="mt-3")
            ], id="collapse-table", is_open=False)
        ])
        
    ], style={"padding": "30px"})

def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(get_sidebar(), md=3, className="p-0"),
            dbc.Col(get_main_content(), md=9)
        ])
    ], fluid=True, className="p-0")
