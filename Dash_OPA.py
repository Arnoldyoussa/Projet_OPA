# Importation des bibliothèques nécessaires

import os
import requests
import dash
from Binance import Bot_Trading_OPA as Bot
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime, timedelta
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import pandas as pd
from dash.exceptions import PreventUpdate
from dash import dash_table
import time
import threading



# Récupérez votre clé API CoinMarketCap
API_KEY = "c6d8798a-71de-4058-8774-54e33d5ef024"
fig2_M1_E = go.Figure()
fig2_M2_E = go.Figure()
fig_M1_E = go.Figure()
fig_M2_E = go.Figure()
rapport_M1_E = pd.DataFrame()
rapport_M2_E=pd.DataFrame()
is_thread_running = False


# Définition des URLs d'API de CoinMarketCap pour récupérer les données de marché
COINMARKETCAP_URL = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
COINMARKETCAP_HISTO_URL = f"https://web-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"
COINMARKETCAP_LISTINGS_URL = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
BINANCE_API_URL = "https://api.binance.com/api/v3/exchangeInfo"

def fetch_currency_pairs_binance():
    response = requests.get(BINANCE_API_URL)

    if response.status_code == 200:
        data = response.json()["symbols"]
        return [{"label": f"{item['baseAsset']}/{item['quoteAsset']}", "value": f"{item['baseAsset']}_{item['quoteAsset']}"} for item in data]
    else:
        return []

# Fonction pour récupérer les paires de cryptomonnaies disponibles sur CoinMarketCap
def fetch_currency_pairs():
    headers = {"X-CMC_PRO_API_KEY": API_KEY}
    params = {"limit": 5000}  # Récupérer les 5000 premières paires
    response = requests.get(COINMARKETCAP_LISTINGS_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()["data"]
        # Renvoie une liste d'options pour le menu déroulant de la page d'accueil
        return [{"label": f"{item['symbol']}/USDT", "value": item["id"]} for item in data]
    else:
        # Si la requête échoue, renvoie une liste vide
        return []

# Appelle la fonction fetch_currency_pairs() pour récupérer les paires de cryptomonnaies
currency_pairs = fetch_currency_pairs_binance()

# Page d'accueil
home_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            # Titre principal de la page d'accueil
            html.H1("Bienvenue sur le Projet OPA Cryptobot"),
            # Sous-titre pour le menu déroulant
            html.H2("Cours des paires de crypto-monnaies"),
            # Horloge en temps réel pour afficher l'heure actuelle
            html.H3(id="date-container-2"),
            # Intervalle de mise à jour pour actualiser les données de la page 2
            dcc.Interval(
                id="time-update-2",
                interval=1*1000,  # Mise à jour toutes les secondes
                n_intervals=0),
            # Menu déroulant pour sélectionner une paire de cryptomonnaies
            dcc.Dropdown(
                id="currency-pair-dropdown",
                options=currency_pairs,
                value="1027",  # Valeur par défaut : ETH
                multi=False,
                clearable=False,
                searchable=True
            ),
            # Section pour afficher le prix actuel de la paire sélectionnée
            html.Div(id="price-container"),
            # Graphique pour afficher l'historique des prix de la paire sélectionnée
            dcc.Graph(id="price-graph"),
            # Intervalle de mise à jour pour actualiser les données
            dcc.Interval(
                id="interval-component",
                interval=30*1000,  # Mise à jour toutes les 30 secondes
                n_intervals=0
            )
        ])
    ])
])

# Deuxième page
button = html.Div([
    dbc.Button("Lancement du Backtest", id="Bouton_Backtest", color="primary")
], style={'position': 'absolute', 'right': '167px', 'top': '200px', 'z-index': 1000}) 
case_option = dbc.RadioItems(
    id="methode-selection",
    options=[
        {"label": "Méthode 1", "value": "M1"},
        {"label": "Méthode 2", "value": "M2"},
    ],
    value="M1",
    inline=True,
)

page_2_layout = dbc.Container([
    # Titre principal de la page 2
    html.H1("Bienvenue sur le Projet OPA Cryptobot"),
    # Titre de la section de la page pour la simulation de la stratégie de trading
    html.H2("Analyse de performance du bot"),
    # Horloge en temps réel pour afficher l'heure actuelle
    html.H3(id="date-container-2"),
    # Intervalle de mise à jour pour actualiser les données de la page 2
    dcc.Interval(
        id="time-update-2",
        interval=1*1000,  # Mise à jour toutes les secondes
        n_intervals=0
    ),
    dcc.Interval(id='interval-update', interval=1000, n_intervals=0), 
    dcc.Store(id="graph-update-trigger", data=None),
    dcc.Dropdown(
    id="currency-pair-dropdown",
    options=currency_pairs,
    value="ETH/USDT",  # Valeur par défaut : ETH/USDT
    multi=False,
    clearable=False,
    searchable=True,
),
    # Ajoutez une nouvelle ligne pour inclure le bouton et le conteneur de sortie

    dbc.Row([dbc.Col([case_option])]),
    dbc.Row([dbc.Col([html.Div(id="graph-container")])]),
    dbc.Row([
        dbc.Col([
            html.Label("Date de début (aaaa-mm-jj) :"),
            dcc.Input(id="date-debut-input", type="text", placeholder="2017-08-01")
        ]),
        dbc.Col([
            html.Label("Date de fin (aaaa-mm-jj) :"),
            dcc.Input(id="date-fin-input", type="text", placeholder="2023-05-01")
        ]),
        dbc.Col([
            html.Label("Capital en dollar :"),
            dcc.Input(id="capital-input", type="number", placeholder="10000"),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            button,
            # Ajoutez un élément HTML pour afficher le résultat de la fonction
            html.Div(id="output-container"),
        ])
    ])
])
def execute_in_parallel(currency_pair, date_debut, date_fin, capital, selected_method):
    global fig2_M1_E, fig2_M2_E, fig_M1_E, fig_M2_E, rapport_M1_E, rapport_M2_E,is_thread_running 
    is_thread_running = True
    Bot.Reset_DB_All()
    #base reinitialisé
    Bot.Load_DB_Mongo([currency_pair], date_debut, date_fin)
    #paire télécharger en mongo
    Bot.Load_DB_SQL_Histo([currency_pair], date_debut, date_fin)
    #paire telecharger en sql
    X_M1_E = Bot.Get_DataPaire([currency_pair],  date_debut, date_fin, 'M1')
    X_M2_E = Bot.Get_DataPaire([currency_pair],  date_debut, date_fin, 'M2')
    #graph 1 pret
    fig_M1_E = Bot.Get_Graphe_Prediction_Achat_Vente(X_M1_E)
    fig_M2_E = Bot.Get_Graphe_Prediction_Achat_Vente(X_M2_E)
    #graph 2 pret
    (rapport_M1_E, Data_M1_E) = Bot.Get_SimulationGain(X_M1_E, currency_pair,capital)
    (rapport_M2_E, Data_M2_E) = Bot.Get_SimulationGain(X_M2_E, currency_pair,capital)
    fig2_M1_E = Bot.Get_Graphe_SimulationGain(Data_M1_E)
    fig2_M2_E = Bot.Get_Graphe_SimulationGain(Data_M2_E)
    # Créez un objet Figure avec des subplots
    is_thread_running = False
    
@app.callback(
    [Output("output-container", "children"),
     Output("graph-update-trigger", "data"),
     Output("Bouton_Backtest", "disabled")],  # Ajouter un nouvel Output pour modifier la propriété 'disabled' du bouton
    [Input("Bouton_Backtest", "n_clicks"),
     Input('interval-update', 'n_intervals')],
    State("date-debut-input", "value"),
    State("date-fin-input", "value"),
    State("capital-input", "value"),
    State("currency-pair-dropdown", "value"),  # Ajouter l'état du menu déroulant
    State("methode-selection", "value"),
    prevent_initial_call=True,
)
def on_button_click(n_clicks,n_intervals, date_debut, date_fin, capital, currency_pair, selected_method): 
    global is_thread_running
    if not n_clicks:
        return dash.no_update, dash.no_update, False
    ctx = dash.callback_context
    currency_pair = currency_pair.replace("_", "")  # Supprimez la barre oblique de la valeur récupérée
    if not ctx.triggered:
        raise PreventUpdate
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if input_id  == "Bouton_Backtest" and n_clicks: 
        # Lancer la fonction 'execute_in_parallel()' dans un deuxième thread
        threading.Thread(target=execute_in_parallel, args=(currency_pair, date_debut, date_fin, capital, selected_method)).start()
        
        return None, time.time(), is_thread_running
    elif input_id == 'interval-update':
        return dash.no_update, dash.no_update, is_thread_running
    else:
        raise PreventUpdate
    
@app.callback(
    Output("graph-container", "children"),
    [Input("methode-selection", "value"),
     Input("graph-update-trigger", "data")], 
)
def update_graph_container(selected_method,_):
    global fig2_M1_E, fig2_M2_E, fig_M1_E, fig_M2_E, rapport_M1_E, rapport_M2_E

    if not fig2_M1_E or not fig2_M2_E or not fig_M1_E or not fig_M2_E or rapport_M1_E.empty or rapport_M2_E.empty:
        raise PreventUpdate
    if selected_method == "M1":
        rapport_transpose = rapport_M1_E.T
    elif selected_method == "M2":
        rapport_transpose = rapport_M2_E.T

    rapport_dict_list = rapport_transpose.to_dict().values()

    rapport_paragraphs = [html.P(f"{key}: {value}") for item in rapport_dict_list for key, value in item.items()]

    if selected_method == "M1":
        return [
            html.Div(rapport_paragraphs, style={'position': 'absolute', 'left': '0', 'width': '25%', 'padding': '10px'}),
            html.Div([
                dcc.Graph(figure=fig2_M1_E, id="fig2_M1_E"),
            ], style={'position': 'absolute', 'left': '20%','top':'300px', 'width': '37.5%', 'padding': '10px'}),
            html.Div([
                dcc.Graph(figure=fig_M1_E, id="fig_M1_E"),
            ], style={'position': 'absolute', 'left': '62.5%','top':'300px', 'width': '37.5%', 'padding': '10px'}),
        ]
    elif selected_method == "M2":
        return [
            html.Div(rapport_paragraphs, style={'position': 'absolute', 'left': '0', 'width': '25%', 'padding': '10px'}),
            html.Div([
                dcc.Graph(figure=fig2_M2_E, id="fig2_M2_E"),
            ], style={'position': 'absolute', 'left': '20%','top':'300px', 'width': '37.5%', 'padding': '10px'}),
            html.Div([
                dcc.Graph(figure=fig_M2_E, id="fig_M2_E"),
            ], style={'position': 'absolute', 'left': '62.5%','top':'300px', 'width': '37.5%', 'padding': '10px'}),
        ]

def generate_graph_container(selected_method):
    global fig2_M1_E, fig2_M2_E, fig_M1_E, fig_M2_E, rapport_M1_E, rapport_M2_E

    if not fig2_M1_E or not fig2_M2_E or not fig_M1_E or not fig_M2_E or rapport_M1_E.empty or rapport_M2_E.empty:
        raise PreventUpdate
    if selected_method == "M1":
        rapport_transpose = rapport_M1_E.T
    elif selected_method == "M2":
        rapport_transpose = rapport_M2_E.T

    rapport_dict_list = rapport_transpose.to_dict().values()

    rapport_paragraphs = [html.P(f"{key}: {value}") for item in rapport_dict_list for key, value in item.items()]

    if selected_method == "M1":
        return [
            html.Div(rapport_paragraphs, style={'position': 'absolute', 'left': '0', 'width': '25%', 'padding': '10px'}),
            html.Div([
                dcc.Graph(figure=fig2_M1_E, id="fig2_M1_E"),
            ], style={'position': 'absolute', 'left': '20%','top':'300px', 'width': '37.5%', 'padding': '10px'}),
            html.Div([
                dcc.Graph(figure=fig_M1_E, id="fig_M1_E"),
            ], style={'position': 'absolute', 'left': '62.5%','top':'300px', 'width': '37.5%', 'padding': '10px'}),
        ]
    elif selected_method == "M2":
        return [
            html.Div(rapport_paragraphs, style={'position': 'absolute', 'left': '0', 'width': '25%', 'padding': '10px'}),
            html.Div([
                dcc.Graph(figure=fig2_M2_E, id="fig2_M2_E"),
            ], style={'position': 'absolute', 'left': '20%','top':'300px', 'width': '37.5%', 'padding': '10px'}),
            html.Div([
                dcc.Graph(figure=fig_M2_E, id="fig_M2_E"),
            ], style={'position': 'absolute', 'left': '62.5%','top':'300px', 'width': '37.5%', 'padding': '10px'}),
        ]
# Définition de la structure de l'application, qui inclut des liens pour naviguer entre les pages
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div([
        dcc.Link('Accueil', href='/'),
        html.Span(" | "),
        dcc.Link('Analyse de performance du bot', href='/page-2'),
    ], style={'position': 'absolute', 'left': '0', 'top': '0', 'padding': '10px'}),
])

# Fonction de rappel pour afficher la page en fonction de l'URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-2':
        # Si l'URL contient '/page-2', affiche la page 2
        return page_2_layout
    else:
        # Sinon, affiche la page d'accueil
        return home_layout

# Fonction de rappel pour actualiser le prix affiché en fonction de la paire sélectionnée
@app.callback(
    Output("price-container", "children"),
    [Input("interval-component", "n_intervals"),
     Input("currency-pair-dropdown", "value")]
)
def update_price(n, currency_pair_id):
    headers = {"X-CMC_PRO_API_KEY": API_KEY}
    params = {"id": currency_pair_id, "convert": "USDT"}
    response = requests.get(COINMARKETCAP_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        currency_pair_id = str(currency_pair_id)
        # Récupération du prix actuel de la paire sélectionnée
        current_price = data["data"][currency_pair_id]["quote"]["USDT"]["price"]
        currency_pair_symbol = data["data"][currency_pair_id]["symbol"]
        # Texte à afficher dans la section "price-container" sur la page d'accueil
        price_text = f"Le cours actuel de la paire {currency_pair_symbol}/USDT est : ${current_price:.2f}"
    else:
        # Si la requête échoue, affiche un message d'erreur
        price_text = "Erreur lors de la récupération du cours."

    return price_text


# Fonction de rappel pour actualiser le graphique des prix en fonction de la paire sélectionnée
@app.callback(
    Output("price-graph", "figure"),
    [Input("interval-component", "n_intervals"),
     Input("currency-pair-dropdown", "value")]
)
def update_graph(n, currency_pair_id):
    timestamps, prices, currency_pair_symbol = fetch_historical_data(currency_pair_id)
    if timestamps and prices:
        # Crée un graphique avec les données historiques de la paire sélectionnée
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=prices, mode='lines', name=f'{currency_pair_symbol}/USDT'))
        fig.update_layout(
            title=f"Graphique du cours de la paire {currency_pair_symbol}/USDT (30 jours)",
            xaxis_title="Date",
            yaxis_title="Prix (USDT)"
        )
    else:
        # Si la récupération des données échoue, affiche un message d'erreur
        fig = go.Figure()
        fig.update_layout(title="Erreur lors de la récupération des données historiques.")

    return fig

# Fonction de rappel pour actualiser l'horloge de la page 2
@app.callback(
    Output("date-container-2", "children"),
    [Input("time-update-2", "n_intervals")]
)
def update_time_2(n):
    current_time = datetime.now().strftime("%H:%M:%S - %Y/%m/%d")
    return f"Heure actuelle : {current_time}"

# Fonction pour récupérer les données historiques d'une paire de cryptomonnaies
def fetch_historical_data(currency_pair_id):
    now = datetime.utcnow()
    start_date = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
    end_date = now.strftime("%Y-%m-%dT%H:%M:%S")
    params = {
        "id": currency_pair_id,
        "convert": "USDT",
        "time_start": start_date,
        "time_end": end_date
    }
    headers = {"X-CMC_PRO_API_KEY": API_KEY}
    response = requests.get(COINMARKETCAP_HISTO_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()["data"]["quotes"]
        currency_pair_symbol = response.json()["data"]["symbol"]
        # Récupération des données historiques de la paire sélectionnée
        timestamps = [entry["time_close"] for entry in data]
        prices = [entry["quote"]["USDT"]["close"] for entry in data]
        return timestamps, prices, currency_pair_symbol
    else:
        # Si la récupération des données échoue, renvoie des listes vides
        return [], [], ""

# Exécute l'application Dash
if __name__ == "__main__":
    app.run_server(debug=True)
