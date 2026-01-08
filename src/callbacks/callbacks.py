"""Dash callback functions for interactive application behavior."""

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, State, dash_table, html
from plotly.subplots import make_subplots

from src.core.properties import GasState
from src.core.simulation import run_simulation


def register_callbacks(app):
    """Register all Dash callbacks for the application."""
    @app.callback(
        [Output("graph-simulation", "figure"),
         Output("kpi-peak-flow", "children"),
         Output("kpi-final-pressure", "children"),
         Output("kpi-equil-time", "children"),
         Output("kpi-total-mass", "children"),
         Output("data-table", "children")],
        [Input("btn-run", "n_clicks")],
        [State("input-p-upstream", "value"),
         State("input-p-downstream", "value"),
         State("input-volume", "value"),
         State("input-valve-id", "value"),
         State("input-opening-mode", "value"),
         State("input-k-curve", "value"),
         State("input-opening-time", "value"),
         State("input-temp", "value"),
         State("input-molar-mass", "value"),
         State("input-z-factor", "value"),
         State("input-k-ratio", "value"),
         State("input-cd", "value"),
         State("input-property-mode", "value"),
         State("input-composition", "value")],
        prevent_initial_call=False
    )
    def update_simulation(n_clicks, p_up, p_down, volume, valve_id, opening_mode, k_curve,
                          opening_time, temp, molar_mass, z_factor, k_ratio, cd,
                          property_mode, composition):
        """Run simulation and update all outputs."""
        
        def use_default(value, default):
            return default if value is None else value

        # Default values (allow zero as a valid input)
        p_up = use_default(p_up, 2800)
        p_down = use_default(p_down, 800)
        volume = use_default(volume, 62)
        valve_id = use_default(valve_id, 3.7)
        opening_mode = use_default(opening_mode, 'linear')
        k_curve = use_default(k_curve, 4.0)
        opening_time = use_default(opening_time, 30)
        temp = use_default(temp, 55)
        molar_mass = use_default(molar_mass, 16.9)
        z_factor = use_default(z_factor, 0.771)
        k_ratio = use_default(k_ratio, 1.9)
        cd = use_default(cd, 0.9)
        property_mode = use_default(property_mode, 'manual')
        composition = use_default(composition, GasState.create_default_composition())
        
        # Run simulation
        df = run_simulation(
            P_up_psig=p_up,
            P_down_init_psig=p_down,
            volume_ft3=volume,
            valve_id_inch=valve_id,
            opening_time_s=opening_time,
            temp_f=temp,
            molar_mass=molar_mass,
            z_factor=z_factor,
            k_ratio=k_ratio,
            discharge_coeff=cd,
            opening_mode=opening_mode,
            k_curve=k_curve,
            property_mode=property_mode,
            composition=composition
        )
        
        # Create dual-axis figure
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Pressure trace
        fig.add_trace(
            go.Scatter(
                x=df['time'],
                y=df['pressure_psig'],
                name="Downstream Pressure",
                line=dict(color="#3498db", width=3)
            ),
            secondary_y=False
        )

        # Upstream Pressure trace
        fig.add_trace(
            go.Scatter(
                x=df['time'],
                y=df['upstream_pressure_psig'],
                name="Upstream Pressure",
                line=dict(color="#95a5a6", width=2, dash='dash'),
            ),
            secondary_y=False
        )
        
        # Flow rate trace
        fig.add_trace(
            go.Scatter(
                x=df['time'],
                y=df['flowrate_lb_hr'],
                name="Flow Rate",
                line=dict(color="#e74c3c", width=3, dash='dot'),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.1)'
            ),
            secondary_y=True
        )

        # Valve Opening Trace
        # We'll use a 3rd Y-axis for Valve Opening (%)
        fig.add_trace(
            go.Scatter(
                x=df['time'],
                y=df['valve_opening_pct'],
                name="Valve Opening (%)",
                line=dict(color="#27ae60", width=2),
                yaxis="y3"
            )
        )
        
        # Add vertical line for valve fully open
        fig.add_vline(
            x=opening_time,
            line_dash="dash",
            line_color="#27ae60",
            # annotation_text="Valve Fully Open",
            # annotation_position="top right"
        )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="<b>Pressure, Flow Rate & Valve Opening vs Time</b>",
                x=0.5,
                font=dict(size=18)
            ),
            xaxis_title="Time (seconds)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            hovermode="x unified",
            template="plotly_white",
            margin=dict(l=60, r=100, t=80, b=60), # Increased right margin for 3rd axis
            
            # Third Axis configuration
            yaxis3=dict(
                title=dict(
                    text="<b>Opening (%)</b>",
                    font=dict(color="#27ae60")
                ),
                tickfont=dict(color="#27ae60"),
                anchor="free",
                overlaying="y",
                side="right",
                position=1, # Move it further to the right
                range=[0, 105],
                gridcolor='rgba(0,0,0,0)' # Hide grid for 3rd axis
            )
        )
        
        fig.update_yaxes(
            title=dict(
                text="<b>Pressure (psig)</b>",
                font=dict(color="#3498db")
            ),
            secondary_y=False,
            tickfont=dict(color="#3498db"),
            gridcolor='rgba(0,0,0,0.1)'
        )
        
        fig.update_yaxes(
            title=dict(
                text="<b>Flow Rate (lb/hr)</b>",
                font=dict(color="#e74c3c")
            ),
            secondary_y=True,
            tickfont=dict(color="#e74c3c")
        )

        
        # Calculate KPIs
        peak_flow = df['flowrate_lb_hr'].max()
        final_pressure = df['pressure_psig'].iloc[-1]
        
        # Find equilibrium time - first time when downstream pressure >= upstream pressure
        equilibrium_mask = df['pressure_psig'] >= df['upstream_pressure_psig']
        if equilibrium_mask.any():
            equil_time = df.loc[equilibrium_mask, 'time'].iloc[0]
        else:
            equil_time = df['time'].iloc[-1]  # Fallback to total time if equilibrium not reached
        
        # Calculate total mass (integrate flow rate over time)
        # Flow rate is in lb/hr, time in seconds
        # Total mass = sum(flow_rate * dt) / 3600
        dt = 0.2
        total_mass = (df['flowrate_lb_hr'].sum() * dt) / 3600
        
        # Format KPIs
        peak_flow_str = f"{peak_flow:,.0f}"
        final_pressure_str = f"{final_pressure:,.1f}"
        equil_time_str = f"{equil_time:,.1f}"
        total_mass_str = f"{total_mass:,.1f}"
        
        # Create data table with pagination
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=15,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'inherit'
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'border': '1px solid #dee2e6'
            },
            style_data={
                'border': '1px solid #dee2e6'
            }
        )
        
        return fig, peak_flow_str, final_pressure_str, equil_time_str, total_mass_str, table
    
    @app.callback(
        Output("collapse-table", "is_open"),
        [Input("btn-toggle-table", "n_clicks")],
        [State("collapse-table", "is_open")],
        prevent_initial_call=True
    )
    def toggle_table(n_clicks, is_open):
        """Toggle the data table visibility."""
        return not is_open

    @app.callback(
        Output("container-k-curve", "style"),
        [Input("input-opening-mode", "value")]
    )
    def toggle_k_curve_input(opening_mode):
        if opening_mode == 'exponential' or opening_mode == 'quick_opening':
            return {'display': 'block'}
        return {'display': 'none'}

    @app.callback(
        [Output("container-composition", "style"),
         Output("input-molar-mass", "disabled"),
         Output("input-z-factor", "disabled"),
         Output("input-k-ratio", "disabled")],
        [Input("input-property-mode", "value")]
    )
    def toggle_property_mode_inputs(property_mode):
        """Toggle composition visibility and make manual props read-only in composition mode."""
        if property_mode == 'composition':
            return (
                {'display': 'block'},    # Show composition
                True,                    # Disable molar mass
                True,                    # Disable z-factor
                True                     # Disable k-ratio
            )
        else:
            return (
                {'display': 'none'},     # Hide composition
                False,                   # Enable molar mass
                False,                   # Enable z-factor
                False                    # Enable k-ratio
            )
    
    @app.callback(
        [Output("input-molar-mass", "value"),
         Output("input-z-factor", "value"),
         Output("input-k-ratio", "value")],
        [Input("input-property-mode", "value"),
         Input("input-composition", "value"),
         Input("input-temp", "value"),
         Input("input-p-downstream", "value")],
        prevent_initial_call=True
    )
    def update_computed_properties(property_mode, composition, temp, p_down):
        """Compute and update property fields when in composition mode."""
        if property_mode == 'composition' and composition:
            try:
                # Convert units
                from src.utils.converters import fahrenheit_to_kelvin, psig_to_pa
                T = fahrenheit_to_kelvin(temp if temp is not None else 55)
                P = psig_to_pa(p_down if p_down is not None else 800)
                
                # Get properties at downstream pressure and temperature
                gas = GasState(composition)
                props = gas.get_properties(P, T)
                
                return round(props.M, 2), round(props.Z, 4), round(props.k, 4)
            except Exception:
                # Return defaults if calculation fails
                return 16.9, 0.771, 1.9
        else:
            # In manual mode, don't update (return current values)
            from dash import no_update
            return no_update, no_update, no_update

    @app.callback(
        Output("modal-composition-editor", "is_open"),
        [Input("btn-open-composition-modal", "n_clicks"),
         Input("btn-apply-composition", "n_clicks"),
         Input("btn-cancel-composition", "n_clicks")],
        [State("modal-composition-editor", "is_open")],
        prevent_initial_call=True
    )
    def toggle_composition_modal(n_open, n_apply, n_cancel, is_open):
        """Toggle the composition editor modal."""
        return not is_open
    
    @app.callback(
        Output("selected-components-list", "children"),
        [Input("btn-open-composition-modal", "n_clicks"),
         Input("composition-preset-selector", "value"),
         Input({"type": "available-comp-btn", "index": dash.dependencies.ALL}, "n_clicks"),
         Input({"type": "remove-comp-btn", "index": dash.dependencies.ALL}, "n_clicks"),
         Input("btn-clear-composition", "n_clicks")],
        [State("selected-components-list", "children"),
         State("input-composition", "value")],
        prevent_initial_call=False
    )
    def update_selected_components(n_open, preset, add_clicks, remove_clicks, clear_clicks, 
                                   current_children, composition_str):
        """Update the selected components list based on user actions."""
        from dash import ctx, no_update
        from src.components.composition_selector import create_selected_component_row
        
        # Determine which input triggered the callback
        triggered_id = ctx.triggered_id
        
        # If modal is opening, populate from current composition
        if triggered_id == "btn-open-composition-modal":
            comp_dict = {}
            if composition_str:
                pairs = composition_str.split(",")
                for pair in pairs:
                    if "=" in pair:
                        name, val = pair.split("=", 1)
                        try:
                            comp_dict[name.strip()] = float(val.strip())
                        except ValueError:
                            pass
            
            # Create rows for non-zero components
            children = []
            for comp, val in comp_dict.items():
                if val > 0:
                    children.append(create_selected_component_row(comp, val))
            return children
        
        # If preset changed, load preset composition
        if triggered_id == "composition-preset-selector":
            if preset and preset != "custom":
                preset_comp = GasState.get_preset_composition(preset)
                children = []
                for comp, val in preset_comp.items():
                    if val > 0:
                        children.append(create_selected_component_row(comp, val))
                return children
        
        # If clear button clicked, clear all
        if triggered_id == "btn-clear-composition":
            return []
        
        # If add button clicked, add component
        if triggered_id and isinstance(triggered_id, dict) and triggered_id.get("type") == "available-comp-btn":
            comp_name = triggered_id["index"]
            # Check if already in selected
            if current_children:
                for child in current_children:
                    if child and "props" in child and "id" in child["props"]:
                        if child["props"]["id"]["index"] == comp_name:
                            return no_update  # Already selected
            
            # Add new component
            new_row = create_selected_component_row(comp_name, 0.0)
            if current_children is None:
                return [new_row]
            return current_children + [new_row]
        
        # If remove button clicked, remove component
        if triggered_id and isinstance(triggered_id, dict) and triggered_id.get("type") == "remove-comp-btn":
            comp_name = triggered_id["index"]
            if current_children:
                return [child for child in current_children 
                       if not (child and "props" in child and "id" in child["props"] 
                              and child["props"]["id"]["index"] == comp_name)]
        
        return no_update
    
    @app.callback(
        [Output("modal-comp-total", "children"),
         Output("modal-comp-validation-msg", "children"),
         Output("modal-comp-total-display", "style")],
        [Input({"type": "selected-comp-input", "index": dash.dependencies.ALL}, "value")],
        prevent_initial_call=False
    )
    def update_modal_total_and_validation(values):
        """Update the total sum display and validation in modal."""
        total = sum(v if v is not None and v > 0 else 0 for v in values)
        
        # Determine validation style
        if total == 0:
            color = "#6c757d"  # Gray
            msg = html.Div("⚠️ No components selected", className="text-muted", style={"fontSize": "12px"})
        elif 0.95 <= total <= 1.05:
            color = "#28a745"  # Green
            msg = html.Div("✓ Valid composition", className="text-success", style={"fontSize": "12px"})
        elif 0.5 <= total <= 1.5:
            color = "#ffc107"  # Yellow
            msg = html.Div("⚠️ Will be normalized to 1.0", className="text-warning", style={"fontSize": "12px"})
        else:
            color = "#dc3545"  # Red
            msg = html.Div("❌ Invalid composition", className="text-danger", style={"fontSize": "12px"})
        
        style = {"color": color}
        
        return f"{total:.4f}", msg, style
    
    @app.callback(
        Output("input-composition", "value"),
        [Input("btn-apply-composition", "n_clicks")],
        [State({"type": "selected-comp-input", "index": dash.dependencies.ALL}, "value"),
         State({"type": "selected-comp-input", "index": dash.dependencies.ALL}, "id")],
        prevent_initial_call=True
    )
    def apply_composition_from_modal(n_clicks, values, ids):
        """Build composition string from modal inputs and update textarea."""
        from dash import no_update
        
        if n_clicks is None:
            return no_update
        
        comp_parts = []
        
        for comp_id, val in zip(ids, values):
            comp_name = comp_id["index"]
            val = val if val is not None else 0.0
            if val > 0:  # Only include non-zero components
                comp_parts.append(f"{comp_name}={val:.4f}")
        
        if not comp_parts:
            return "Methane=1.0"  # Default to pure methane if empty
        
        return ", ".join(comp_parts)

