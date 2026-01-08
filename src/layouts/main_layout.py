"""Main application layout structure."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.components.common import create_kpi_card
from src.core.properties import GasState
from src.layouts.sidebar import get_sidebar


def get_main_content():
    """Create the main content area layout with KPIs, graphs, and data tables."""
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
            dcc.Loading(
                id="loading-graph",
                type="default",
                children=[dcc.Graph(id="graph-simulation", style={"height": "500px"})]
            )
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
    """Create the complete application layout."""
    # Create composition editor modal
    composition_modal = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Gas Composition Editor")),
        dbc.ModalBody([
            html.P("Enter mole fractions for each component (values will be auto-normalized):", 
                   className="mb-3"),
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Label(comp, style={"fontWeight": "500"}),
                        dbc.Input(
                            id=f"modal-comp-{comp.lower().replace('-', '')}",
                            type="number",
                            step=0.0001,
                            min=0,
                            max=1,
                            value=0,
                            size="sm"
                        )
                    ], md=6, className="mb-2")
                    for comp in GasState.get_default_components()
                ][i:i+2])
                for i in range(0, len(GasState.get_default_components()), 2)
            ]),
            html.Hr(),
            html.Div([
                html.Strong("Total: "),
                html.Span(id="modal-comp-total", children="0.0000", style={"marginLeft": "10px"})
            ], className="mb-2"),
            html.Small("Note: Values will be automatically normalized to sum to 1.0", 
                      className="text-muted")
        ]),
        dbc.ModalFooter([
            dbc.Button("Apply", id="btn-apply-composition", color="success", className="me-2"),
            dbc.Button("Cancel", id="btn-cancel-composition", color="secondary")
        ])
    ], id="modal-composition-editor", size="lg", is_open=False)
    
    return dbc.Container([
        composition_modal,
        dbc.Row([
            dbc.Col(get_sidebar(), md=3, className="p-0"),
            dbc.Col(get_main_content(), md=9)
        ])
    ], fluid=True, className="p-0")
