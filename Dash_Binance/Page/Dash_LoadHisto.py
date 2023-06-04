import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table

from Binance import Bot_Trading_OPA as Bot  
from Dash_Binance.Utilitaire import Dash_Fonction as Util_dash
from Dash_Binance.Utilitaire import Dash_DAO_Redis as DAO_redis

# --> Entête
Header = dbc.Container( 
    [
        html.H1("Bienvenue sur le Projet OPA Cryptobot", className="display-4"),
        html.H2("Chargement des Données Historiques", className="display-5"),
        html.H3(id="date_Dash_LoadH"),
    ],
    className="my-4",  # Ajoute une marge autour du conteneur
)

# init liste Symbol
currency_pairs = DAO_redis.fetch_currency_pairs_redis()
if not currency_pairs:
    currency_pairs = Util_dash.fetch_currency_pairs_binance()

# --> Bloc Symbol déjà chargé
Pave_Symbol_Loaded = dbc.Container(
    [
        dbc.Row(html.Div('Pavé : Liste des Symboles Existants ')),
        html.Br(),
        dbc.Row(dash_table.DataTable(
                    id='Table_HistoSymbol',
                    columns=[{"name": str(i), "id": str(i)} for i in ['Symbol', 'Periode Debut', 'Periode Fin']],
                )),
        html.Br(),
        dbc.Row(dbc.Button("Reset Base Historique", id="Bouton_Reset", n_clicks=0)),
        dbc.Alert(
            "Info : Fin Reset DataBase",
            id="alert-auto_reset",
            is_open=False,
            dismissable=True,
        )
    ]
)

# --> Bloc Symbol pouvant être chargé
Pave_Symbol_to_Load = dbc.Container(
    [
        dbc.Row(html.Div('Pavé : Liste des Symboles à Charger ')),
        html.Br(),
        dbc.Row(dcc.Dropdown( id="Menu_LoadH", value="ETHUSDT", options = currency_pairs)),
        html.Br(),
        dbc.Row(
                [
                    dbc.Col([html.Label("Date de début (jj-mm-aaaa) :"), dcc.Input(id="deb_input", type="text", placeholder="JJ-MM-AAAA", value="01-10-2017")]),
                    dbc.Col([html.Label("Date de fin (jj-mm-aaaa) :"), dcc.Input(id="dfin_input", type="text", placeholder="JJ-MM-AAAA", value="01-05-2023")]),
               ]
            ),
        html.Br(),
        dbc.Row(dbc.Button("Chargement Historique", id="load-button", n_clicks=0)),
        dbc.Alert(
            "Info : Fin Alimentation DataBase",
            id="alert-auto",
            is_open=False,
            dismissable=True,
        )
    ]
)

# --> Assemblage du layout final
Load_layout = dbc.Container(
    [
        dbc.Row(Header),
        dbc.Row([
            dbc.Col(html.Div(Pave_Symbol_Loaded)),
            dbc.Col(html.Div(Pave_Symbol_to_Load))
        ])
    ]
)