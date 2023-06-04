import dash_bootstrap_components as dbc
from dash import dcc, html

from Binance import Bot_Trading_OPA as Bot  
from Dash_Binance.Utilitaire import Dash_Fonction as Util_dash
from Dash_Binance.Utilitaire import Dash_DAO_Redis as DAO_redis

import datetime as dt
import pandas as pd

import plotly.graph_objs as go


# --> Entête
Header = dbc.Container( 
    [
        html.H1("Bienvenue sur le Projet OPA Cryptobot", className="display-4"),
        html.H2("Cours des paires de crypto-monnaies", className="display-5"),
        html.H3(id="date_Dash_Idx"),
    ],
    className="my-4",  # Ajoute une marge autour du conteneur
)

# --> Menu pour la sélection de la paire de cryptomonnaies
currency_pairs = DAO_redis.fetch_currency_pairs_redis()

if not currency_pairs:
    currency_pairs = Util_dash.fetch_currency_pairs_binance()

dropdown = dcc.Dropdown(  id="Menu_Idx", value="ETH_USDT", options =currency_pairs  )


# --> Section pour le prix actuel
price_section = html.Div(id="Price_Idx")

# --> Bouton de mise à jour
update_button = dbc.Button('Mise à jour', id='button_Idx', n_clicks=0)
loading_spinner = dcc.Loading(id="loading_Idx", children=[html.Div(id="content")], type="circle")

# --> Graphique pour l'historique des prix
price_graph = dcc.Graph(id="price_Graph_Idx")

# --> Assemblage du layout final
Accueil_Layout = dbc.Container(
    [
        dbc.Row(Header),
        dbc.Row(dropdown),
        dbc.Row(price_section),
        html.Br(),
        dbc.Row(html.Div([update_button, loading_spinner])),
        dbc.Row(price_graph),
    ]
)

# -->
def Graphique_accueil(selected_dropdown_value, start_date, end_date, frequence = '1h'):
    
    df = Bot.Get_Live_InfoPaire(selected_dropdown_value.replace("_",""), frequence, start_date, end_date)
    
    # Convert the 'OpenTime' column from a timestamp to a datetime object
    df['OpenTime'] = pd.to_datetime(df['OpenTime'], unit='ms')
    
    fig = go.Figure(data=go.Scatter(x=df['OpenTime'], y=df['OpenPrice'], mode='lines'))
    fig.update_layout(
        title='Cours du temps pour ' + selected_dropdown_value.replace("_","/"),
        xaxis_title='Temps',
        yaxis_title='Prix d\'ouverture',
        yaxis_type='log'  # Change l'échelle de l'axe des y en une échelle logarithmique
        )
    return fig