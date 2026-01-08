"""Component for dual-column composition selector."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.core.properties import GasState


def create_composition_selector():
    """Create a dual-column composition selector component.
    
    Returns:
        A Dash component with available and selected columns for composition entry.
    """
    all_components = GasState.get_default_components()
    
    return html.Div([
        # Preset selector
        html.Div([
            html.Label("Preset Compositions", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="composition-preset-selector",
                options=[
                    {"label": "Natural Gas (Pipeline)", "value": "natural_gas"},
                    {"label": "Pure Methane", "value": "pure_methane"},
                    {"label": "Rich Gas (High C2-C5)", "value": "rich_gas"},
                    {"label": "Sour Gas (with H2S)", "value": "sour_gas"},
                    {"label": "Lean Gas (Low C2+)", "value": "lean_gas"},
                    {"label": "Custom", "value": "custom"}
                ],
                value="natural_gas",
                clearable=False,
                style={"marginBottom": "15px"}
            )
        ], className="mb-3"),
        
        html.Hr(),
        
        # Dual column layout
        dbc.Row([
            # Available components column
            dbc.Col([
                html.H6("Available Components", className="text-center mb-3", 
                       style={"fontWeight": "bold", "color": "#2c3e50"}),
                html.Div([
                    html.Div(
                        id="available-components-list",
                        children=[
                            dbc.Button(
                                comp,
                                id={"type": "available-comp-btn", "index": comp},
                                color="light",
                                outline=True,
                                size="sm",
                                className="mb-2 w-100 text-start",
                                style={"fontSize": "13px"}
                            )
                            for comp in all_components
                        ],
                        style={
                            "maxHeight": "400px",
                            "overflowY": "auto",
                            "padding": "10px",
                            "border": "1px solid #dee2e6",
                            "borderRadius": "5px",
                            "backgroundColor": "#f8f9fa"
                        }
                    )
                ])
            ], md=6),
            
            # Selected components column
            dbc.Col([
                html.H6("Selected Components", className="text-center mb-3",
                       style={"fontWeight": "bold", "color": "#2c3e50"}),
                html.Div(
                    id="selected-components-list",
                    children=[],
                    style={
                        "minHeight": "400px",
                        "maxHeight": "400px",
                        "overflowY": "auto",
                        "padding": "10px",
                        "border": "1px solid #dee2e6",
                        "borderRadius": "5px",
                        "backgroundColor": "#fff"
                    }
                )
            ], md=6)
        ], className="mb-3"),
        
        html.Hr(),
        
        # Total and validation
        html.Div([
            html.Div([
                html.Strong("Total: "),
                html.Span(id="modal-comp-total", children="0.0000", 
                         style={"marginLeft": "10px", "fontSize": "16px", "fontWeight": "bold"})
            ], id="modal-comp-total-display", className="mb-2"),
            html.Div(id="modal-comp-validation-msg", className="mt-2")
        ]),
        
        html.Small("Note: Values will be automatically normalized to sum to 1.0 when applied", 
                  className="text-muted")
    ])


def create_selected_component_row(component: str, value: float = 0.0):
    """Create a row for a selected component with input field and remove button.
    
    Args:
        component: Name of the component.
        value: Initial mole fraction value.
    
    Returns:
        A Dash component row with component name, input, and remove button.
    """
    comp_id = component.lower().replace('-', '').replace(' ', '')
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label(component, style={"fontWeight": "500", "fontSize": "13px", "marginBottom": "5px"})
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    id={"type": "selected-comp-input", "index": component},
                    type="number",
                    step=0.0001,
                    min=0,
                    max=1,
                    value=value,
                    size="sm",
                    placeholder="Mole fraction"
                )
            ], width=8),
            dbc.Col([
                dbc.Button(
                    "×",
                    id={"type": "remove-comp-btn", "index": component},
                    color="danger",
                    outline=True,
                    size="sm",
                    style={"padding": "2px 8px", "fontWeight": "bold"}
                )
            ], width=4)
        ], className="mb-2")
    ], id={"type": "selected-comp-row", "index": component}, className="mb-2 pb-2", 
       style={"borderBottom": "1px solid #eee"})
