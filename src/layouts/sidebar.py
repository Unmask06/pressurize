"""Sidebar layout component for simulation parameters.

This module creates the left sidebar interface containing all user-adjustable
simulation parameters including pressure, vessel, valve, and gas property settings.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.components.common import create_input_field
from src.core.properties import GasState


def get_sidebar():
    """Create the sidebar layout with all simulation parameter inputs.
    
    Returns:
        dash.html.Div: A Div containing the complete sidebar interface with:
            - Pressure settings (upstream and downstream)
            - Vessel and valve parameters
            - Valve opening mode selection
            - Gas property inputs (manual or composition-based)
            - Discharge coefficient
            - Run simulation button
    
    Notes:
        The sidebar includes:
        - Grouped sections for related parameters
        - Dynamic visibility (e.g., composition editor only shown in composition mode)
        - Default values appropriate for typical natural gas applications
        - Tooltips and helper text for user guidance
    
    Examples:
        >>> sidebar = get_sidebar()
        >>> # Returns a styled sidebar Div ready to be placed in the layout
    """
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
        dbc.Row([
            dbc.Col(create_input_field("Vessel Volume (ft³)", "input-volume", 62), width=6),
            dbc.Col(create_input_field("Valve ID (inches)", "input-valve-id", 3.7), width=6),
        ]),
        
        dbc.Row([
            dbc.Col(html.Div([
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
            ], className="input-group-custom"), width=6),
            dbc.Col(html.Div([
                create_input_field("Exponential Slope (k)", "input-k-curve", 4.0, step=0.1)
            ], id="container-k-curve", style={'display': 'none'}), width=6),
        ]),
        
        create_input_field("Valve Opening Time (s)", "input-opening-time", 30),
        
        html.Hr(style={"borderColor": "rgba(255,255,255,0.3)"}),
        
        html.H6("Gas Properties", style={"color": "#ecf0f1"}),
        
        # Property Mode Toggle
        html.Div([
            html.Label("Property Mode", className="input-label"),
            dcc.Dropdown(
                id="input-property-mode",
                options=[
                    {"label": "Manual", "value": "manual"},
                    {"label": "Composition (Derived)", "value": "composition"}
                ],
                value="manual",
                clearable=False,
                style={"color": "#2c3e50"}
            )
        ], className="input-group-custom"),
        
        # Composition Input - only visible in composition mode
        html.Div([
            html.Div([
                html.Label("Gas Composition", className="input-label", style={"display": "inline-block"}),
                dbc.Button(
                    "✏️ Edit",
                    id="btn-open-composition-modal",
                    size="sm",
                    color="info",
                    outline=True,
                    style={"marginLeft": "10px", "fontSize": "11px", "padding": "2px 8px"}
                ),
            ]),
            dbc.Textarea(
                id="input-composition",
                placeholder="e.g., Methane=0.85, Ethane=0.10, CO2=0.05",
                value=GasState.create_default_composition(),
                style={"minHeight": "75px", "fontSize": "13px"}
            ),
            html.Small(
                "Supported: " + ", ".join(GasState.get_default_components()),
                style={"color": "#95a5a6", "fontSize": "10px"}
            )
        ], id="container-composition", className="input-group-custom", style={'display': 'none'}),
        
        # Manual property inputs - always visible, read-only in composition mode
        html.Div([
            dbc.Row([
                dbc.Col(create_input_field("Temp (°F)", "input-temp", 55), width=12),
            ]),
            dbc.Row([
                dbc.Col(create_input_field("Mol Mass", "input-molar-mass", 16.9, step=0.01), width=4),
                dbc.Col(create_input_field("Z-Factor", "input-z-factor", 0.771, step=0.001), width=4),
                dbc.Col(create_input_field("k (Gamma)", "input-k-ratio", 1.9, step=0.01), width=4),
            ]),
        ], id="container-manual-props"),
        
        create_input_field("Discharge Coeff (Cd)", "input-cd", 0.9, step=0.01),
        
        dbc.Button(
            "🚀 Run Simulation",
            id="btn-run",
            color="success",
            className="run-button"
        ),
        
    ], className="sidebar")
