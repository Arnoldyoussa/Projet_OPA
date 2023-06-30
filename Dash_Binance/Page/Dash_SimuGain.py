import dash_bootstrap_components as dbc
from dash import dcc, html , dash_table


# --> Entête
Header = dbc.Container( 
    [
        html.Img(src="assets/logo_crypto_bot.png", alt="Logo", height="100px"),
        html.Div([
            html.H1("Analyse de performance du bot", className="display-5", style={'marginRight': '10px', 'marginLeft': '22px'}),
            html.Img(src="assets/bar-chart-line.svg", alt="Bar Chart Line Icon", height="30px"),
        ], style={'display': 'flex', 'alignItems': 'center'}),
        html.Div([
            html.Img(src="assets/clock.svg", alt="Clock Icon", height="15px", style={'marginBottom': '8px'}),
            html.H2(id="date_Dash_Simu", style={'display': 'inline-block', 'verticalAlign': 'middle'}),
        ], style={'display': 'flex', 'alignItems': 'center'}),
        dcc.Store(id="graph-update-trigger", data=None)
    ],
    className="my-4", 
)
"""
Header = dbc.Container( 
    [
        html.H1("Bienvenue sur le Projet OPA Cryptobot", className="display-4"),
        html.H2("Analyse de performance du bot", className="display-5"),
        html.H3(id="date_Dash_Simu"),
        dcc.Store(id="graph-update-trigger", data=None)
    ],
    className="my-4",  # Ajoute une marge autour du conteneur
)
"""

# --> Bloc de la sélection de la paire de devises
currency_pair_dropdown = dcc.Dropdown( id="currency-pair-dropdown", value="ETH_USDT"  )

# --> Bloc des options
case_option = dbc.RadioItems(
    id="methode-selection",
    options=[
        {"label": "Méthode 1", "value": "M1"},
        {"label": "Méthode 2", "value": "M2"},
    ],
    value="M1",
    inline=True,
) 

# --> Autres Blocs
output_notification = html.Div(id="output-notification")
output_container = html.Div(id="output-container")
loading_container3 = dcc.Loading(
    id="loading-container3",
    type="default",  # ou "cube", "circle", dépend de vos préférences
    children=[
        html.Br(),
        dbc.Row(
            dbc.Button("Lancement du Backtest", id="load-button3", n_clicks=0)
        )
    ]
)
# --> Assemblage du layout final
simuGain_layout = dbc.Container(
    [
        dbc.Row(Header),
        dcc.Store(id='output-store', storage_type='session'),
        currency_pair_dropdown,  # Placé au-dessus des entrées
        dbc.Row([case_option], style={'padding': '10px'}),  # Placé juste en dessous du sélecteur de devises
        dbc.Row(
            [
                dbc.Col([html.Label("Date de début (jj-mm-aaaa) :"), dcc.Input(id="date-debut-input", type="text", placeholder="JJ-MM-AAAA", value="01-10-2017")], width=3),
                dbc.Col([html.Label("Date de fin (jj-mm-aaaa) :"), dcc.Input(id="date-fin-input", type="text", placeholder="JJ-MM-AAAA", value="01-05-2023")], width=3),
                dbc.Col([html.Label("Capital en dollar :"), dcc.Input(id="capital-input", type="number", placeholder="10000", value=10000)], width=3)
																										 
            ],
            style={'padding': '10px'} 
        ),
        loading_container3,
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="fig_simulation"), width=6),
                dbc.Col(dcc.Graph(id="fig_prediction"), width=6),
                dbc.Col(dcc.Graph(id="fig_camembert"), width=6),
                dbc.Col(dcc.Graph(id="fig_wallet"), width=6)
            ],
            style={'padding': '10px'}
        ),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='Table_Rapport',
                    columns=[{"name": str(i), "id": str(i)} for i in ['Information', 'Valeur']],
                ),
                width={"size": 10, "offset": 1}  
            ),
            style={'padding': '10px'}
        ),
        dbc.Row([dbc.Col([html.Div(id="graph-container")], style={'padding': '10px'})]),
        dbc.Row([dbc.Col([output_notification, output_container], style={'padding': '10px'})])
    ],
    fluid=True  ,
    className="my-4"
) 