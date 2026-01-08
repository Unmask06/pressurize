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
                html.H6("Available", className="text-center mb-2", 
                       style={"fontWeight": "bold", "color": "#2c3e50"}),
                dbc.Input(
                    id="search-available-comps",
                    placeholder="Search...",
                    type="text",
                    size="sm",
                    className="mb-2"
                ),
                html.Div([
                    html.Div(
                        id="available-components-list",
                        children=[
                            dbc.Button(
                                comp,
                                id={"type": "available-comp-btn", "index": comp},
                                color="secondary",
                                outline=True,
                                size="sm",
                                className="mb-1 w-100 text-start available-comp-btn",
                                style={"fontSize": "13px", "fontWeight": "500", "color": "#495057", "borderColor": "#dee2e6"}
                            )
                            for comp in all_components
                        ],
                        className="composition-box",
                        style={
                            "maxHeight": "400px",
                            "overflowY": "auto",
                            "padding": "8px",
                            "border": "1px solid #ced4da",
                            "borderRadius": "8px",
                            "backgroundColor": "#f8f9fa"
                        }
                    )
                ])
            ], width=5, className="pe-1"),
            
            # Selected components column
            dbc.Col([
                html.H6("Selected", className="text-center mb-2",
                       style={"fontWeight": "bold", "color": "#2c3e50"}),
                dbc.Input(
                    id="search-selected-comps",
                    placeholder="Search selected...",
                    type="text",
                    size="sm",
                    className="mb-2"
                ),
                html.Div(
                    id="selected-components-list",
                    children=[],
                    className="composition-box",
                    style={
                        "minHeight": "400px",
                        "maxHeight": "400px",
                        "overflowY": "auto",
                        "padding": "8px",
                        "border": "1px solid #ced4da",
                        "borderRadius": "8px",
                        "backgroundColor": "#ffffff"
                    }
                )
            ], width=7, className="ps-1")
        ], className="mb-3"),
        
        html.Hr(),
        
        # Total and validation
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Strong("Total: "),
                    html.Span(id="modal-comp-total", children="0.0000", 
                             style={"marginLeft": "10px", "fontSize": "16px", "fontWeight": "bold"})
                ], id="modal-comp-total-display"),
                html.Div(id="modal-comp-validation-msg", className="mt-1")
            ], width=8),
            dbc.Col([
                dbc.Button(
                    "Normalize",
                    id="btn-normalize-composition",
                    color="primary",
                    size="sm",
                    outline=True,
                    className="w-100"
                )
            ], width=4, className="d-flex align-items-center")
        ], className="mb-2 align-items-center"),

        html.Small("Double-click items to move between lists.", className="text-muted d-block mb-1"),
        html.Small("Note: Values will be automatically normalized to sum to 1.0 when applied", 
                  className="text-muted")
    ])


def create_selected_component_row(component: str, value: float = 0.0, visible: bool = True):
    """Create a row for a selected component with input field and remove button.
    
    Args:
        component: Name of the component.
        value: Initial mole fraction value.
        visible: Whether the row should be visible (for filtering).
    
    Returns:
        A Dash component row with component name, input, and remove button.
    """
    comp_id = component.lower().replace('-', '').replace(' ', '')
    style = {"borderBottom": "1px solid #e9ecef"}
    if not visible:
        style["display"] = "none"
    
    return dbc.Row([
        dbc.Col([
            dbc.Button(
                component,
                id={"type": "remove-comp-btn", "index": component},
                color="link",
                style={
                    "textDecoration": "none", 
                    "color": "#2c3e50", 
                    "textAlign": "left", 
                    "fontWeight": "600",
                    "padding": "0",
                    "fontSize": "0.9rem"
                },
                className="text-start text-truncate w-100 remove-comp-btn"
            )
        ], width=7, className="d-flex align-items-center"),
        dbc.Col([
            dbc.Input(
                id={"type": "selected-comp-input", "index": component},
                type="number",
                step=0.0001,
                min=0,
                max=1,
                value=value,
                size="sm",
                placeholder="Frac",
                style={"borderColor": "#ced4da", "fontSize": "0.9rem", "padding": "0.2rem 0.4rem"}
            )
        ], width=5)
    ], id={"type": "selected-comp-row", "index": component}, 
       className="mb-1 pb-1 scale-in align-items-center g-1", 
       style=style)
