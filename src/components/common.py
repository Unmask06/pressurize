"""Common UI components for the Dash application.

This module provides reusable component builders for creating consistent
UI elements across the application interface.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_input_field(label, id, value, step=None, min_val=None):
    """Create a labeled numeric input field.
    
    Args:
        label (str): Display label for the input field.
        id (str): Unique identifier for the Dash component.
        value (float or int): Default value for the input.
        step (float or str, optional): Increment step for the input.
            Use "any" for unrestricted decimal input. Defaults to "any".
        min_val (float, optional): Minimum allowed value. Defaults to None.
    
    Returns:
        dash.html.Div: A Div containing a label and numeric input field.
    
    Examples:
        >>> create_input_field("Temperature (°F)", "input-temp", 70)
        # Creates a temperature input with default value 70
        
        >>> create_input_field("Pressure (psig)", "input-pressure", 100, step=0.1, min_val=0)
        # Creates a pressure input with step 0.1 and minimum 0
    """
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
    """Create a KPI (Key Performance Indicator) display card.
    
    Args:
        id (str): Unique identifier for the value display element.
        title (str): Descriptive title for the KPI metric.
        icon (str): Emoji or icon character to display.
        color (str): CSS color code for the value text (e.g., "#e74c3c").
    
    Returns:
        dash_bootstrap_components.Card: A styled card component displaying
            an icon, value, and label.
    
    Notes:
        The card includes three elements:
        - Icon at the top center
        - Large colored value (populated by callback)
        - Descriptive label at the bottom
    
    Examples:
        >>> create_kpi_card("kpi-flow", "Peak Flow Rate (lb/hr)", "📈", "#e74c3c")
        # Creates a red KPI card for flow rate with chart emoji
        
        >>> create_kpi_card("kpi-pressure", "Final Pressure (psig)", "🎯", "#3498db")
        # Creates a blue KPI card for pressure with target emoji
    """
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={"fontSize": "2rem"}),
            ], style={"textAlign": "center"}),
            html.H3(id=id, className="kpi-value text-center", style={"color": color}),
            html.P(title, className="kpi-label text-center mb-0")
        ])
    ], className="kpi-card")
