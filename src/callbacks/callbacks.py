import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, State, dash_table
from plotly.subplots import make_subplots

from src.core.simulation import run_simulation


def register_callbacks(app):
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
         State("input-cd", "value")],
        prevent_initial_call=False
    )
    def update_simulation(n_clicks, p_up, p_down, volume, valve_id, opening_mode, k_curve,
                          opening_time, temp, molar_mass, z_factor, k_ratio, cd):
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
            k_curve=k_curve
        )
        
        # Create dual-axis figure
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Pressure trace
        fig.add_trace(
            go.Scatter(
                x=df['time'],
                y=df['pressure_psig'],
                name="Downstream Pressure",
                line=dict(color="#3498db", width=3),
                fill='tozeroy',
                fillcolor='rgba(52, 152, 219, 0.1)'
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
                line=dict(color="#e74c3c", width=3, dash='dot')
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
        equil_time = df['time'].iloc[-1]
        
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

