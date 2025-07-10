# File: CMZ_data_explorer/Shocks.py
# -*- coding: utf-8 -*-

# Import necessary libraries
import dash
import pickle
from dash import dcc
from dash import html
from dash import dash_table
import plotly.express as px
import numpy as np
from functionality import format_molecule_HTML,ranges_cshock, mol_all_gas, mol_all_bulk, mol_all_surface
import datetime
from config import *

# Read the master dataframe from a pickle file
try:
    with open(cshock_pkl, 'rb') as file:
        cshock_df_pkl = pickle.load(file)
except FileNotFoundError:
    pass

# Find the position of the 'zeta' column
zeta_index = cshock_df_pkl.columns.get_loc('zeta')
# Insert 'zeta_scaled' right after the 'zeta' column - this way it is more intuitive to read
cshock_df_pkl.insert(zeta_index + 1, 'zeta_scaled', 1.310 * 1e-17 * cshock_df_pkl['zeta'])

# Divide the master DataFrame into segments - increases the speed of the application
shock_df = cshock_df_pkl[cshock_df_pkl['stage']=='shock'].reset_index(drop=True)
postshock_df = cshock_df_pkl[cshock_df_pkl['stage']=='post-shock'].reset_index(drop=True)

# Read the available values - for the dropdown and filtering purposes
zeta_available        = ranges_cshock["zeta"]
vel_available         = ranges_cshock["shock_vel"]
dens_available        = ranges_cshock["initialDens"]
rad_available         = ranges_cshock["radfield"]
initialTemp_available = ranges_cshock["initialTemp"]

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the Dash layout
app.layout = html.Div(
    [
        html.H1("Shock Data Explorer 🔎"),
        html.P("Welcome to the interactive shock data explorer! This tool provides access to the shock grid tailored to environments similar to the Galactic Center. " \
               "The models utilized the UCLCHEM gas-grain chemical code and are thoroughly described in Dutkowska et al. (submitted)."),
        html.Div([
            html.H3("What you can do with this tool:", style={"margin-top": "20px", "margin-bottom": "10px"}),
            html.Ul([
                html.Li("🔍 Explore shock and post-shock data interactively through visualizations and tables"),
                html.Li("📊 Create custom plots to analyze chemical evolution over time"),
                html.Li("🔽 Download filtered datasets as CSV files for your own analysis"),
                html.Li("⚙️ Filter by shock velocity, density, medium's temperature, cosmic ray rates, and FUV fields"),
                html.Li("💾 Save plots and visualizations for presentations or publications")
            ], style={"margin-bottom": "15px"})
        ]),
        html.P("This tool makes complex chemical models accessible and explorable. No prior experience with the UCLCHEM models is required!"),
        html.Hr(style={"margin": "20px 0"}),
        
        html.Div(
            [  # Start of the two-column layout
                # Left Column
                html.Div(
                    [
                        html.H2("Chemistry"),
                        # In your imports section, add these variables:
                        # from functionality import mol_all_gas, mol_all_surface, mol_all_bulk

                        # Replace your current "Species" section in the left column with:
                        html.H3("Species Selection"),
                        html.Div([
                            html.H4("Gas Phase Species"),
                            dcc.Dropdown(
                                id="df-dropdown-gas-species",
                                options=[
                                    {"label": species, "value": species}
                                    for species in mol_all_gas
                                ],
                                value=[],  # Start with empty selection
                                multi=True,
                                placeholder="Select gas phase species..."
                            ),
                        ], style={"margin-bottom": "10px"}),

                        html.Div([
                            html.H4("Surface Species"),
                            dcc.Dropdown(
                                id="df-dropdown-surface-species",
                                options=[
                                    {"label": species, "value": species}
                                    for species in mol_all_surface
                                ],
                                value=[],  # Start with empty selection
                                multi=True,
                                placeholder="Select surface species..."
                            ),
                        ], style={"margin-bottom": "10px"}),

                        html.Div([
                            html.H4("Bulk Species"),
                            dcc.Dropdown(
                                id="df-dropdown-bulk-species",
                                options=[
                                    {"label": species, "value": species}
                                    for species in mol_all_bulk
                                ],
                                value=[],  # Start with empty selection
                                multi=True,
                                placeholder="Select bulk species..."
                            ),
                        ], style={"margin-bottom": "15px"}),

                        html.Hr(style={"margin": "20px 0"}),  # Separator line

                        html.Div([
                            html.H3("Ratio Plot (Optional)"),
                            dcc.Checklist(
                                id="enable-ratio-plot",
                                options=[{"label": " Enable ratio plotting", "value": "enabled"}],
                                value=[],  # Start unchecked
                                style={"margin-bottom": "10px"}
                            ),
                            
                            # This div will show/hide based on the checkbox
                            html.Div(
                                id="ratio-controls",
                                children=[
                                    html.Div([
                                        html.Label("Numerator Species:", style={"font-weight": "bold"}),
                                        dcc.Dropdown(
                                            id="ratio-numerator-dropdown",
                                            options=[],  # Will be populated dynamically
                                            value=None,
                                            placeholder="Select numerator species...",
                                            style={"margin-bottom": "10px"}
                                        ),
                                    ]),
                                    html.Div([
                                        html.Label("Denominator Species:", style={"font-weight": "bold"}),
                                        dcc.Dropdown(
                                            id="ratio-denominator-dropdown",
                                            options=[],  # Will be populated dynamically
                                            value=None,
                                            placeholder="Select denominator species...",
                                            style={"margin-bottom": "10px"}
                                        ),
                                    ]),
                                    html.Div(id="ratio-validation-message", style={"color": "red", "margin-bottom": "10px"}),
                                ],
                                style={"display": "none"}  # Hidden by default
                            )
                        ]),

                        # Add validation message div
                        html.Div(id="species-validation-message", style={"color": "red", "margin-bottom": "10px"}),
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "vertical-align": "top",
                    },
                ),
                # Right Column
                html.Div(
                    [   
                        html.H2("Shock-data of interest"),
                        html.H3("Shock stage"),
                        dcc.Dropdown(
                            id="df-dropdown-type",
                            options=[
                                {"label": "Shock", "value": "shock"},
                                {"label": "Post-shock", "value": "postshock"},
                            ],
                            value="shock",
                        ),
                        html.H3("Shock velocity [km s⁻¹] "),
                        dcc.Dropdown(
                            id="df-dropdown-shockvel",
                            options=[
                                {"label": f"{shock_vel}", "value": shock_vel}
                                for shock_vel in vel_available
                            ],
                            value=[vel_available[0]],
                            multi=True,
                        ),
                        html.H2("Medium properties"),
                        html.H3("Density [cm⁻³]"),
                        dcc.Dropdown(
                            id="df-dropdown-dens",
                            options=[
                                {"label": f"{dens:.0e}", "value": dens}
                                for dens in dens_available
                            ],
                            value=[dens_available[0]],
                            multi=True,
                        ),
                        html.H3("Initial temperature [K]"),
                        dcc.Dropdown(
                            id="df-dropdown-initialtemp",
                            options=[
                                {"label": f"{temp:.0f}", "value": temp}
                                for temp in initialTemp_available
                            ],
                            value=[initialTemp_available[0]],
                            multi=True
                        ),

                        html.H3("Cosmic Ray Ionization Rate [s⁻¹]"),
                        dcc.Dropdown(
                            id="df-dropdown-zeta",
                            options=[
                                {"label": f"{1.310 * 1e-17 * zeta:.2e}", "value": zeta}
                                for zeta in zeta_available
                            ],
                            value=[zeta_available[0]],
                            multi=True,
                        ),
                        html.H3("FUV field [Habing]"),
                        dcc.Dropdown(
                            id="df-dropdown-rad",
                            options=[
                                {"label": f"{rad:.0e}", "value": rad}
                                for rad in rad_available
                            ],
                            value=[rad_available[0]],
                            multi=True,
                        ),
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "vertical-align": "top",
                    },
                ),
            ],
            style={"display": "flex", "justify-content": "space-between"},
        ),  # End of the two-column layout

                # Add plot controls section
        html.Div([
            html.H3("Plot Display Options", style={"margin-bottom": "10px"}),
            html.Div([
                html.Div([
                    html.Label("Y-axis scale:", style={"font-weight": "bold", "margin-right": "10px"}),
                    dcc.RadioItems(
                        id="y-axis-scale",
                        options=[
                            {"label": "Logarithmic", "value": "log"},
                            {"label": "Linear", "value": "linear"}
                        ],
                        value="log",
                        inline=True,
                        style={"margin-right": "20px"}
                    )
                ], style={"display": "inline-block", "margin-right": "30px"}),
                
                html.Div([
                    html.Label("Marker size:", style={"font-weight": "bold", "margin-right": "10px"}),
                    dcc.Slider(
                        id="marker-size-slider",
                        min=4,
                        max=20,
                        step=2,
                        value=DEFAULT_MARKER_SIZE,
                        marks={i: str(i) for i in range(4, 21, 4)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={"display": "inline-block", "width": "200px", "margin-right": "30px"}),
                
                html.Div([
                    html.Label("Show grid:", style={"font-weight": "bold", "margin-right": "10px"}),
                    dcc.Checklist(
                        id="show-grid",
                        options=[{"label": "Grid lines", "value": "grid"}],
                        value=["grid"],
                        inline=True
                    )
                ], style={"display": "inline-block"}),
            ]
            )]),
        html.Img(
            src="/assets/uclchem_transparent.png",
            style={
                "position": "absolute",
                "top": "10px",
                "right": "10px",
                "width": "50px",
            },
        ),
        dcc.Graph(id="df-graph"),
        html.Div(id="ratio-graph-container", style={"display": "none"}, children=[
        html.Hr(style={"margin": "20px 0"}),
        dcc.Graph(id="ratio-graph")
    ]),
        html.Div(id="df-summary"),
        html.Button("Download CSV", id="btn_csv"),
        dcc.Download(id="download-dataframe-csv"),
        html.Div(id='output-div')
    ]
)

@app.callback(
    [
        dash.Output("df-summary", "children"), 
        dash.Output("df-graph", "figure"), 
        dash.Output("download-dataframe-csv", "data"),
        dash.Output("species-validation-message", "children")
    ],
    [
        dash.Input("df-dropdown-type", "value"),
        dash.Input("df-dropdown-gas-species", "value"),
        dash.Input("df-dropdown-surface-species", "value"),
        dash.Input("df-dropdown-bulk-species", "value"),
        dash.Input("df-dropdown-zeta", "value"),
        dash.Input("df-dropdown-shockvel", "value"),
        dash.Input("df-dropdown-dens", "value"),
        dash.Input("df-dropdown-rad", "value"),
        dash.Input("df-dropdown-initialtemp", "value"),
        dash.Input("btn_csv", "n_clicks"),
        dash.Input("y-axis-scale", "value"),
        dash.Input("marker-size-slider", "value"),
        dash.Input("show-grid", "value"),
    ],
)

def update_output(
    selected_df,
    selected_gas_species,
    selected_surface_species,
    selected_bulk_species,
    selected_zeta,
    selected_velocity,
    selected_dens,
    selected_rad,
    selected_temp,
    n_clicks,
    y_scale, marker_size, show_grid
):
    # Combine all selected species
    selected_species = []
    if selected_gas_species:
        selected_species.extend(selected_gas_species)
    if selected_surface_species:
        selected_species.extend(selected_surface_species)
    if selected_bulk_species:
        selected_species.extend(selected_bulk_species)
    
    # Validation: Check if at least one species is selected
    if not selected_species:
        validation_message = "⚠️ Please select at least one species from any category."
        empty_fig = px.scatter(title="No species selected")
        empty_summary = html.Div("Please select species to view data.")
        return empty_summary, empty_fig, dash.no_update, validation_message
    
    # Clear validation message if species are selected
    validation_message = ""
    
    # Rest of your existing filtering logic remains the same
    if selected_df == "shock":
        df = shock_df[
            (shock_df["zeta"].isin(selected_zeta))
            & (shock_df["shock_vel"].isin(selected_velocity))
            & (shock_df["initialDens"].isin(selected_dens))
            & (shock_df["radfield"].isin(selected_rad))
            & (shock_df["initialTemp"].isin(selected_temp))
        ]
    else:
        df = postshock_df[
            (postshock_df["zeta"].isin(selected_zeta))
            & (postshock_df["shock_vel"].isin(selected_velocity))
            & (postshock_df["initialDens"].isin(selected_dens))
            & (postshock_df["radfield"].isin(selected_rad))
            & (postshock_df["initialTemp"].isin(selected_temp))
        ]

    # Filter columns to include only selected species
    df_filtered = df[
        [
            "age",
            "locDens",
            "locTemp",
            "Av",
            "run_id",
            "shock_vel",
            "initialDens",
            "initialTemp",
            "zeta_scaled",
            "radfield",
        ]
        + selected_species  # This now contains species from all three categories
    ]

    summary = html.Div(
        [
            html.H3(" Head of the chosen data"),
            dcc.Input(
                id="datatable-filter",
                type="text",
                placeholder="Filter table...",
                style={"margin-bottom": "10px"},
            ),
            dash_table.DataTable(
                id="datatable",
                columns=[{"name": i, "id": i} for i in df_filtered.columns],
                data=df.to_dict("records"),
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                page_current=0,
                page_size=10,
            ),
        ]
    )
    # Example plot (change columns as needed)
    fig = px.scatter(
        df, 
        x="age", 
        y=selected_species, 
        title=f"{selected_df.capitalize()}", 
        log_x=True,
        log_y=(y_scale == "log"),  # Add this line for logarithmic y-axis
        hover_data={
            'age': True, 
            'locDens': True, 
            'initialDens': True, 
            'locTemp': True, 
            'initialTemp': True, 
            'shock_vel': True, 
            'zeta_scaled': True, 
            'radfield': True
        },
        labels={
            'variable': 'Species', 
            'value': 'X(species)', 
            'age': 'Time', 
            'locDens': 'n<sub>H</sub>', 
            'initialDens': 'n<sub>H, initial</sub>', 
            'locTemp': 'T', 
            'initialTemp': 'T<sub>init</sub>', 
            'shock_vel': 'v<sub>s</sub>', 
            'zeta': 'CRIR', 
            'radfield': 'FUV'
        },
    )
    # Ensure you have enough traces for the number of species
    num_traces = len(fig.data)
    num_species = len(selected_species)

    for i in range(min(num_traces, num_species)):
        fig.data[i].name = format_molecule_HTML(selected_species[i].replace("log_", ""))

    # Set alpha for face and edge of scatter points and increase marker size
    fig.update_traces(
        marker=dict(
            size=marker_size,  # Adjust size of markers
            opacity=DEFAULT_OPACITY,  # Face color opacity
        ),
        hoverlabel=dict(
            font_size=16,  # Set the font size for hover labels
        ),
        hovertemplate=(
        'Abundance: %{y:.2e}<br>' +
        'Time: %{x:.2e} yr<br>' +
        'n<sub>H</sub>: %{customdata[0]:.2e}<br>' +
        'n<sub>H, initial</sub>: %{customdata[1]:.0e}<br>' +
        'T: %{customdata[2]:.2f}<br>' +
        'T<sub>init</sub>: %{customdata[3]}<br>' +
        'v<sub>s</sub>: %{customdata[4]}<br>' +
        'CRIR: %{customdata[5]:.2e}<br>' +
        'FUV: %{customdata[6]:.0e}<br>'
    ),
    )

    # Calculate y-axis range
    y_min = np.min([df[species].min() for species in selected_species])
    y_max = np.max([df[species].max() for species in selected_species])

    # Add horizontal line only if it is within the y-axis range
    if y_min <= 1E-14 <= y_max:
        fig.add_hline(y=1E-14,line_width=3)
        # Add annotation with more control

    fig.update_layout(
        template="seaborn",
        # xaxis_type="log",
        xaxis_title="Time (yr)",
        yaxis_title="X(species)",
        legend_title="Species",
        font=dict(
            size=16  # General font size for the plot
        ),
    )

    grid_style = {
        "showgrid": "grid" in show_grid,
        "gridcolor": "rgba(128, 128, 128, 0.3)",
        "gridwidth": 1,
        "showline": True,
        "linecolor": "Black",
        "linewidth": 2,
        "ticks": "outside",
        "ticklen": 8,
        "tickwidth": 1,
        "tickcolor": "black",
        "mirror": True,
        "exponentformat": "e",
        "showexponent": "all",
        "minor": dict(ticklen=4, tickwidth=1)
    }

    fig.update_xaxes(**grid_style)
    fig.update_yaxes(**grid_style)

    fig.update_traces(showlegend=False, selector=dict(type="box"))

    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    download_data = dcc.send_data_frame(df_filtered.to_csv, f"Shock_model_{current_time}.csv") if n_clicks else dash.no_update
    return summary, fig, download_data, validation_message

# Callback 1: Show/hide ratio controls based on checkbox
@app.callback(
    [
        dash.Output("ratio-controls", "style"),
        dash.Output("ratio-graph-container", "style")
    ],
    [dash.Input("enable-ratio-plot", "value")]
)
def toggle_ratio_controls(enabled):
    if "enabled" in enabled:
        return {"display": "block"}, {"display": "block"}
    else:
        return {"display": "none"}, {"display": "none"}

# Callback 2: Update dropdown options based on selected species
@app.callback(
    [
        dash.Output("ratio-numerator-dropdown", "options"),
        dash.Output("ratio-denominator-dropdown", "options")
    ],
    [
        dash.Input("df-dropdown-gas-species", "value"),
        dash.Input("df-dropdown-surface-species", "value"),
        dash.Input("df-dropdown-bulk-species", "value")
    ]
)
def update_ratio_dropdown_options(gas_species, surface_species, bulk_species):
    # Combine all selected species
    all_species = []
    if gas_species:
        all_species.extend(gas_species)
    if surface_species:
        all_species.extend(surface_species)
    if bulk_species:
        all_species.extend(bulk_species)
    
    # Create options for both dropdowns
    options = [{"label": species, "value": species} for species in all_species]
    
    return options, options

# Callback 3: Create ratio plot
@app.callback(
    [
        dash.Output("ratio-graph", "figure"),
        dash.Output("ratio-validation-message", "children")
    ],
    [
        dash.Input("df-dropdown-type", "value"),
        dash.Input("ratio-numerator-dropdown", "value"),
        dash.Input("ratio-denominator-dropdown", "value"),
        dash.Input("df-dropdown-zeta", "value"),
        dash.Input("df-dropdown-shockvel", "value"),
        dash.Input("df-dropdown-dens", "value"),
        dash.Input("df-dropdown-rad", "value"),
        dash.Input("df-dropdown-initialtemp", "value"),
        dash.Input("enable-ratio-plot", "value"),
        dash.Input("y-axis-scale", "value"),
        dash.Input("marker-size-slider", "value"),
        dash.Input("show-grid", "value"),
    ]
)
def update_ratio_plot(selected_df, numerator, denominator, selected_zeta, selected_velocity, 
                     selected_dens, selected_rad, selected_temp, ratio_enabled, y_scale, marker_size, show_grid):
    
    # If ratio plotting is not enabled, return empty figure
    if "enabled" not in ratio_enabled:
        return px.scatter(title="Ratio plotting disabled"), ""
    
    # Validation
    if not numerator or not denominator:
        validation_msg = "⚠️ Please select both numerator and denominator species for ratio plot."
        return px.scatter(title="Select species for ratio"), validation_msg
    
    if numerator == denominator:
        validation_msg = "⚠️ Numerator and denominator cannot be the same species."
        return px.scatter(title="Invalid ratio selection"), validation_msg
    
    # Clear validation message
    validation_msg = ""
    
    # Filter data (same logic as your main plot)
    if selected_df == "shock":
        df = shock_df[
            (shock_df["zeta"].isin(selected_zeta))
            & (shock_df["shock_vel"].isin(selected_velocity))
            & (shock_df["initialDens"].isin(selected_dens))
            & (shock_df["radfield"].isin(selected_rad))
            & (shock_df["initialTemp"].isin(selected_temp))
        ]
    else:
        df = postshock_df[
            (postshock_df["zeta"].isin(selected_zeta))
            & (postshock_df["shock_vel"].isin(selected_velocity))
            & (postshock_df["initialDens"].isin(selected_dens))
            & (postshock_df["radfield"].isin(selected_rad))
            & (postshock_df["initialTemp"].isin(selected_temp))
        ]
    
    # Calculate ratio
    df_ratio = df.copy()
    df_ratio['ratio'] = df_ratio[numerator] / df_ratio[denominator]
    
    # Create ratio plot
    fig = px.scatter(
        df_ratio,
        x="age",
        y="ratio",
        title=f"Ratio: {format_molecule_HTML(numerator)} / {format_molecule_HTML(denominator)} ({selected_df.capitalize()})",
        log_x=True,
        log_y=(y_scale == "log"),
        hover_data={
            'age': True, 
            'locDens': True, 
            'initialDens': True, 
            'locTemp': True, 
            'initialTemp': True, 
            'shock_vel': True, 
            'zeta_scaled': True, 
            'radfield': True,
            numerator: True,
            denominator: True
        },
        labels={
            'age': 'Time', 
            'ratio': f'{numerator}/{denominator}',
            'locDens': 'n<sub>local</sub>', 
            'initialDens': 'n<sub>initial</sub>', 
            'locTemp': 'T<sub>local</sub>', 
            'initialTemp': 'T<sub>init</sub>', 
            'shock_vel': 'v<sub>s</sub>', 
            'zeta': 'CRIR', 
            'radfield': 'FUV'
        }
    )
    
    # Apply same styling as your main plot
    fig.update_traces(
        marker=dict(size=marker_size, opacity=DEFAULT_OPACITY),
        hoverlabel=dict(font_size=16),
        hovertemplate=(
            f'{numerator}/{denominator}: %{{y:.2e}}<br>' +
            'Time: %{x:.2e} yr<br>' +
            f'{numerator}: %{{customdata[7]:.2e}}<br>' +
            f'{denominator}: %{{customdata[8]:.2e}}<br>' +
            'n<sub>local</sub>: %{customdata[0]:.2e}<br>' +
            'n<sub>initial</sub>: %{customdata[1]:.0e}<br>' +
            'T<sub>local</sub>: %{customdata[2]:.2f}<br>' +
            'T<sub>init</sub>: %{customdata[3]}<br>' +
            'v<sub>s</sub>: %{customdata[4]}<br>' +
            'CRIR: %{customdata[5]:.2e}<br>' +
            'FUV: %{customdata[6]:.0e}<br>'
        ),
    )
    

    # Enhanced axis styling
    grid_style = {
        "showgrid": "grid" in show_grid,
        "gridcolor": "rgba(128, 128, 128, 0.3)",
        "gridwidth": 1,
        "showline": True,
        "linecolor": "Black",
        "linewidth": 2,
        "ticks": "outside",
        "ticklen": 8,
        "tickwidth": 1,
        "tickcolor": "black",
        "mirror": True,
        "exponentformat": "e",
        "showexponent": "all",
        "minor": dict(ticklen=4, tickwidth=1)
    }

    fig.update_xaxes(**grid_style)
    fig.update_yaxes(**grid_style)
    
    fig.update_layout(
        template="seaborn",
        xaxis_title="Time (yr)",
        yaxis_title=f"X({numerator}) / X({denominator})",
        font=dict(size=16)
    )
    
    return fig, validation_msg

# Run the server
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', debug=True)
