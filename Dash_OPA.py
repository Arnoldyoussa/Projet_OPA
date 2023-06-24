# Importation des bibliothèques nécessaires

from Binance import Bot_Trading_OPA as Bot  

from Dash_Binance.Utilitaire import Dash_Fonction as Util_dash
from Dash_Binance.Utilitaire import Dash_DAO_Redis as DAO_redis
from Dash_Binance.Page import Dash_Index as Page_Acceuil
from Dash_Binance.Page import Dash_LoadHisto as Page_LoadHisto
from Dash_Binance.Page import Dash_SimuGain as Page_SimuGain

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd
import threading
import datetime as dt
 
 
#########################################################
######## Initialisation de l'application Dash ###########
#########################################################

app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN], suppress_callback_exceptions=True)

# --> Intervalle de mise à jour
update_interval = dcc.Interval( id="interval-component", interval=30*1000, n_intervals=0 )

#########################################################
################### Fonctions Page Acceuil ##############
#########################################################

"""
 ------------- Actualisation de l'horloge
"""

@app.callback(
    Output("date_Dash_Idx", "children"),
    Input("interval-component", "n_intervals")
)
def update_time(n):
    current_time = dt.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    return f"Heure actuelle : {current_time}"


"""
 -------------  Mise à jour Base Redis
"""

@app.callback(
    Output('content', 'children'),
    [Input('button_Idx', 'n_clicks')]
)
def update_output(n_clicks):
    if n_clicks > 0:  # pour ignorer le premier appel de rappel au chargement de l'application
        thread = threading.Thread(target=DAO_redis.Maj_base_redis)
        thread.start()
    return ""

"""
 -------------  Mise à jour Graphe
"""
#--> 
# Définition du callback pour mettre à jour le graphe Acceuil de la Page D'acceuil

@app.callback(
    Output('price_Graph_Idx', 'figure'),
    Input('Menu_Idx', 'value')
)
def Graphique_accueil(value):
    if value is None:
        raise PreventUpdate

    # --
    now = dt.datetime.utcnow()
    
    # --
    start_date = int((now - dt.timedelta(days=60)).timestamp() * 1000)
    end_date = int(now.timestamp() * 1000)

    # --
    start_date=Util_dash.convert_timestamp(start_date)
    end_date=Util_dash.convert_timestamp(end_date)
    
    # --
    fig = Page_Acceuil.Graphique_accueil(value, start_date, end_date)

    return fig

#########################################################
################ Fonctions Page Load Histo ##############
#########################################################
"""
 -------------  Actualisation de l'horloge
"""

@app.callback(
    Output("date_Dash_LoadH", "children"),
    Input("interval-component", "n_intervals")
)
def update_time(n):
    current_time = dt.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    return f"Heure actuelle : {current_time}"

"""
 -------------  Récupération des Symboles Historiques chargés
"""


@app.callback(
    Output("Table_HistoSymbol", "data"),
    Input("interval-component", "n_intervals")
)
def get_HistoSymbol(n):
    return Bot.Get_ListeSymbolHisto().to_dict('records')

"""
 -------------  Reset de la base Historique
"""
@app.callback(
    Output('alert-auto_reset', 'is_open'),
    Input("Bouton_Reset", "n_clicks")
)
def Reset_DB_All(n_clicks):
    if n_clicks > 0:
        Bot.Reset_DB_All()
        return True

"""
 -------------  Load de la base Historique
""" 
@app.callback(
    Output('alert-auto', 'is_open'),
    Input('load-button2', 'n_clicks'),
    [
        State('Menu_LoadH', 'value'),
        State('deb_input', 'value'),
        State('dfin_input', 'value'),
    ]
)
def on_button_click(n,pair, deb_input,dfin_input ):
    
    dt_Debut = Util_dash.converion_Dateformat(deb_input, "%d-%m-%Y", "%Y-%m-%d" )
    dt_Fin = Util_dash.converion_Dateformat(dfin_input, "%d-%m-%Y", "%Y-%m-%d" )

    if n > 0:
        pair = pair.replace("_", "") 
        Bot.Load_DB_Mongo([pair], Periode_Debut=dt_Debut, Periode_Fin=dt_Fin)
        Bot.Load_DB_SQL_Histo([pair], Periode_Debut=dt_Debut, Periode_Fin=dt_Fin)
        
        return True

#########################################################
########### Fonctions Page Simulation Gain ##############
#########################################################
"""
 -------------  Actualisation de l'horloge
"""

@app.callback(
    Output("date_Dash_Simu", "children"),
    Input("interval-component", "n_intervals")
)
def update_time(n):
    current_time = dt.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    return f"Heure actuelle : {current_time}"


"""
 -------------  Actualisation du Menu
"""

@app.callback(
    Output("currency-pair-dropdown", "options"),
    Input("interval-component", "n_intervals")
)
def update_time(n):
    return  [{'value' : symbol, 'label' : symbol } for symbol in Bot.Get_ListeSymbolHisto()['Symbol'].values ]



"""
 -------------  Chargement Base Live
"""
@app.callback( 
    [Output("output-store", "data"),
     Output("load-button3", "n_clicks")], 
    [Input("load-button3", "n_clicks")],
    [State("date-debut-input", "value"),
    State("date-fin-input", "value"),
    State("capital-input", "value"),
    State("currency-pair-dropdown", "value")],
    prevent_initial_call=True,
)
def on_button_click(n_clicks, date_debut, date_fin, capital, currency_pair): 
    if n_clicks: 
        currency_pair = currency_pair.replace("_", "") 
        output = Util_dash.Get_Backtest(currency_pair, date_debut, date_fin, capital)
        
        return output, "Backtest lancé"

    else:
        return Dash.no_update, Dash.no_update

"""
 -------------  Simulation Gain
"""

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
        raise Dash.exceptions.PreventUpdate 
    for methode, resultats in output.items():
        if methode == selected_method:
            Table_Rapport = resultats['rapport']
            fig_prediction = resultats['graph_prediction']
            fig_simulation = resultats['graph_simulation']
            fig_camembert=resultats['graph_good_bad_trade']
            fig_wallet=resultats['graph_wallet']
            return fig_prediction, fig_simulation,fig_camembert,fig_wallet, Table_Rapport

    raise Dash.exceptions.PreventUpdate


#########################################################
################# Main : Lancement Dash #################
#########################################################

#--> Définition de la structure de l'application, qui inclut des liens pour naviguer entre les pages
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='store_ListHistoSymbol'),
    html.Div([
        dcc.Link('Accueil', href='/'),
        html.Span(" | "),
        dcc.Link('Chargement de la Base Historique', href='/LoadDatabase'),
        html.Span(" | "),
        dcc.Link('Analyse de performance du bot', href='/Backtest'),
       
    ], style={'position': 'absolute', 'left': '0', 'top': '0', 'padding': '10px'}),
    html.Br(),
    html.Div(id='page-content'),
    update_interval,
])


#--> Définition du callback pour mettre à jour le contenu de la page en fonction de l'URL
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))

def display_page(pathname):
    if pathname == '/':
        return Page_Acceuil.Accueil_Layout

    elif pathname == '/Backtest':
        return Page_SimuGain.simuGain_layout

    elif pathname == '/LoadDatabase':
        return Page_LoadHisto.Load_layout

    else:
        return '404'

# Exécute l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
