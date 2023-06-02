# Importation des bibliothèques nécessaires
 
import dash
from Binance import Bot_Trading_OPA as Bot 
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import datetime as dt
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import pandas as pd
from dash import dash_table
import threading
import redis
from Dash_Binance import Dash_Fonction as Util_dash
 
 

 
# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
 
# Définition du callback pour mettre à jour le contenu de la page en fonction de l'URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return Accueil_Layout
    elif pathname == '/Backtest':
        return Analyse_de_performance_layout
    elif pathname == '/LoadDatabase':
        return load_database_layout
    else:
        return '404'
 


####################################################################################################################################################################################
##############################################-------------------------------------PAGE ACCUEIL-------------------------------------------------#################################### 
####################################################################################################################################################################################
 

#############################################----------------------------------------LAYOUT-----------------------------------------------------#####################################
currency_pairs = Util_dash.fetch_currency_pairs_redis()
if not currency_pairs:
    currency_pairs = Util_dash.fetch_currency_pairs_binance()
# Titre et sous-titre
header = dbc.Container( 
    [
        html.H1("Bienvenue sur le Projet OPA Cryptobot", className="display-4"),
        html.H2("Cours des paires de crypto-monnaies", className="display-5"),
        html.H3(id="date-container-2"),
    ],
    className="my-4",  # Ajoute une marge autour du conteneur
)

# Dropdown pour la sélection de la paire de cryptomonnaies
dropdown = dbc.Container(
    [
        dcc.Dropdown(
            id="currency-pair-dropdown",
            options=currency_pairs,
            value="ETH_USDT",
            multi=False,
            clearable=False,
            searchable=True,
        ),
    ],
    className="my-4",  # Ajoute une marge autour du conteneur
)


# Section pour le prix actuel
price_section = html.Div(id="price-container")

# Bouton de mise à jour
update_button = html.Button('Mise à jour', id='update-button', n_clicks=0)
loading_spinner = dcc.Loading(id="loading", children=[html.Div(id="content")], type="circle")

# Graphique pour l'historique des prix
price_graph = dcc.Graph(id="price-graph")

# Intervalle de mise à jour
update_interval = dcc.Interval(
    id="interval-component",
    interval=30*1000,
    n_intervals=0
)

# Assemblage du layout final
Accueil_Layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            header,
            dropdown,
            price_section,
            html.Div([update_button, loading_spinner]),
            price_graph,
            update_interval,
        ])
    ])
])

 
 ############################################################-------------------------FONCTION----------------------####################################################################

currency_pairs = Util_dash.fetch_currency_pairs_redis()
if not currency_pairs:
    currency_pairs = Util_dash.fetch_currency_pairs_binance()
@app.callback(
    Output('content', 'children'),
    [Input('update-button', 'n_clicks')]
)
def update_output(n_clicks):
    if n_clicks > 0:  # pour ignorer le premier appel de rappel au chargement de l'application
        thread = threading.Thread(target=Util_dash.Maj_base_redis)
        thread.start()
    return ""
 
 
@app.callback(
    Output('price-graph', 'figure'),
    Input('currency-pair-dropdown', 'value')
)
def Graphique_accueil(selected_dropdown_value):
    now = dt.datetime.utcnow()
    start_date = int((now - dt.timedelta(days=60)).timestamp() * 1000)
    end_date = int(now.timestamp() * 1000)
    start_date=Util_dash.convert_timestamp(start_date)
    end_date=Util_dash.convert_timestamp(end_date)
    df = Bot.Get_Live_InfoPaire(selected_dropdown_value.replace("_",""), '1h', start_date, end_date)
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

####################################################################################################################################################################################
####################################################------------------------PAGE ANALYSE DE PERFORMANCE DU BOT-----------------------------######################################### 
####################################################################################################################################################################################

#############################################----------------------------------------LAYOUT-----------------------------------------------------#####################################


# Bloc des éléments statiques
titre_principal = html.H1("Bienvenue sur le Projet OPA Cryptobot")
titre_section = html.H2("Analyse de performance du bot")
date_container = html.H3(id="date-container-2")

# Bloc des intervalles de mise à jour
time_update = dcc.Interval(id="time-update-2", interval=1*1000, n_intervals=0)
interval_update = dcc.Interval(id='interval-update', interval=1000, n_intervals=0)
graph_update_trigger = dcc.Store(id="graph-update-trigger", data=None)


# Bloc de la sélection de la paire de devises
currency_pair_dropdown = dcc.Dropdown(
    id="currency-pair-dropdown",
    options=currency_pairs,
    value="ETH_USDT", 
    multi=False,
    clearable=False, 
    searchable=True,
)

# Bloc des options
case_option = dbc.RadioItems(
    id="methode-selection",
    options=[
        {"label": "Méthode 1", "value": "M1"},
        {"label": "Méthode 2", "value": "M2"},
    ],
    value="M1",
    inline=True,
) 

output_notification = html.Div(id="output-notification")
output_container = html.Div(id="output-container")

# Aggrégation des blocs dans le layout de la page 2
Analyse_de_performance_layout = dbc.Container(
    [
        dbc.Row([dbc.Col(titre_principal, className="text-center")]),
        dbc.Row([dbc.Col(titre_section, className="text-center")]),
        dbc.Row([dbc.Col(date_container, className="text-center")]),
        dbc.Row([dbc.Col(time_update, className="text-center")]),
        dbc.Row([dbc.Col(interval_update, className="text-center")]),
        currency_pair_dropdown,  # Placé au-dessus des entrées
        dbc.Row([dbc.Col([case_option], style={'padding': '10px'})]),  # Placé juste en dessous du sélecteur de devises
        dbc.Row(
            [
                dbc.Col([html.Label("Date de début (jj-mm-aaaa) :"), dcc.Input(id="date-debut-input", type="text", placeholder="JJ-MM-AAAA", value="01-10-2017")], width=3),
                dbc.Col([html.Label("Date de fin (jj-mm-aaaa) :"), dcc.Input(id="date-fin-input", type="text", placeholder="JJ-MM-AAAA", value="01-05-2023")], width=3),
                dbc.Col([html.Label("Capital en dollar :"), dcc.Input(id="capital-input", type="number", placeholder="10000", value=10000)], width=3),
                dbc.Col([dbc.Button("Lancement du Backtest", id="Bouton_Backtest", color="primary")], width=3)
            ],
            style={'padding': '10px'} 
        ),
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
    fluid=True
)


 ############################################################-------------------------FONCTION----------------------####################################################################
@app.callback( 
    [Output("output-store", "data"),
     Output("Bouton_Backtest", "n_clicks")], 
    [Input("Bouton_Backtest", "n_clicks")],
    [State("date-debut-input", "value"),
    State("date-fin-input", "value"),
    State("capital-input", "value"),
    State("currency-pair-dropdown", "value")],
    prevent_initial_call=True,
)
def on_button_click(n_clicks, date_debut, date_fin, capital, currency_pair): 
    if n_clicks: 
        currency_pair = currency_pair.replace("_", "") 
        dureeJr_Entrainement=100
        output = Util_dash.Get_Backtest(currency_pair, date_debut, date_fin, capital,dureeJr_Entrainement)
        
        return output, "Backtest lancé"
    else:
        return dash.no_update, dash.no_update

 
@app.callback(
    Output("fig_simulation","figure"),
    Output('fig_prediction', 'figure'),
    Output('fig_camembert', 'figure'),
    Output('fig_wallet','figure'),
    Output('Table_Rapport', 'data'),
    [Input("methode-selection", "value"),
     Input("output-store", "data")],  # Modifiez l'entrée pour pointer vers le stockage
)
def update_graph_containerv2(selected_method, output): 
    if output is None: 
        raise dash.exceptions.PreventUpdate 
    for methode, resultats in output.items():
        if methode == selected_method:
            Table_Rapport = resultats['rapport']
            fig_prediction = resultats['graph_prediction']
            fig_simulation = resultats['graph_simulation']
            fig_camembert=resultats['graph_good_bad_trade']
            fig_wallet=resultats['graph_wallet']
            return fig_prediction, fig_simulation,fig_camembert,fig_wallet, Table_Rapport


    raise dash.exceptions.PreventUpdate
 

# Définition de la structure de l'application, qui inclut des liens pour naviguer entre les pages
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='output-store', storage_type='session'),  
    html.Div([
        dcc.Link('Accueil', href='/'),
        html.Span(" | "),
        dcc.Link('Analyse de performance du bot', href='/Backtest'),
        html.Span(" | "),
        dcc.Link('Chargement des bases', href='/LoadDatabase'),
    ], style={'position': 'absolute', 'left': '0', 'top': '0', 'padding': '10px'}),
])
 
# Fonction de rappel pour afficher la page en fonction de l'URL

  

# Fonction de rappel pour actualiser l'horloge de la page 2
@app.callback(
    Output("date-container-2", "children"),
    [Input("time-update-2", "n_intervals")]
)
def update_time_2(n):
    current_time = dt.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    return f"Heure actuelle : {current_time}"

####################################################################################################################################################################################
####################################################------------------------------PAGE CHARGEMENT BASE-------------------------------------######################################### 
####################################################################################################################################################################################
 
load_database_layout = html.Div([
    html.H2("Chargement des bases"),
    html.Button('Chargement base', id='load-button', n_clicks=0),
    dash_table.DataTable(id='output-table') ,
    dropdown,
])



@app.callback(
    Output('output-table', 'data'),
    [Input('load-button', 'n_clicks'),
    Input('currency-pair-dropdown', 'value')],
)
def on_button_click(n,pair):
    if n > 0:
        pair = pair.replace("_", "") 
        Bot.Load_DB_Mongo(pair,Periode_Debut="2017-01-01",Periode_Fin="2023-04-01")
        print("fait")
        Bot.Load_DB_SQL_Histo(pair)
        print("faitou")
        # Convertir le DataFrame en une table Dash
        table = dbc.Table.from_dataframe()


        return table


# Exécute l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1')

