
import datetime as dt
import pandas as pd

from Binance import Bot_Trading_OPA as Bot
from Dash_Binance.Utilitaire import Dash_Graphe as Util_dash_graphe


# Convertit le timestamp en millisecondes en une chaîne formatée
def convert_timestamp(timestamp_en_millisecondes):
    timestamp_en_secondes = timestamp_en_millisecondes / 1000
    dt_object = dt.datetime.fromtimestamp(timestamp_en_secondes)
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")


# Récupère les paires de devises depuis l'API Binance
def fetch_currency_pairs_binance():
    X = Bot.Get_API_Binance().exchange_info()
    return [{'value' : symbol['symbol'], 'label' : symbol['baseAsset'] + '/'+ symbol['quoteAsset'] } for symbol in X['symbols'] ]

#
def converion_Dateformat(Periode, fmt_input, fmt_out):
    date_obj = dt.datetime.strptime(Periode, fmt_input)
    return date_obj.strftime(fmt_out)


def Get_Backtest(Paire,Periode_Debut,Periode_Fin,Capital_depart):

    #--> Step 1 : Initialisation de la période Début / Fin

    # Convertir la chaîne en objet datetime
    #date_obj = dt.datetime.strptime(Periode_Debut, "%d-%m-%Y")
    # Reformater l'objet datetime en chaîne de caractères
    #Periode_Debut = date_obj.strftime("%Y-%m-%d")
    #date_obj = dt.datetime.strptime(Periode_Fin, "%d-%m-%Y")
    # Reformater l'objet datetime en chaîne de caractères
    #Periode_Fin = date_obj.strftime("%Y-%m-%d")

    Periode_Debut = converion_Dateformat(Periode_Debut, "%d-%m-%Y", "%Y-%m-%d" )
    Periode_Fin = converion_Dateformat(Periode_Fin, "%d-%m-%Y", "%Y-%m-%d" )

    #-->  Step 2 : Chargement Live
    Bot.Load_DB_SQL_Live([Paire],Periode_Debut,Periode_Fin)

    #--> Step 3 : Prediction + Restitution Graphe
    
    output = {}  # Dictionnaire pour stocker les résultats
    for Methode in ['M1', 'M2']:
        print(Methode) 

        # --> Prediction :
        Bot.Load_DB_SQLPrediction(Paire,Methode, Periode_Debut,Periode_Fin)
        
        # --> Récupération Data
        data=Bot.Get_DataPaire([Paire],Periode_Debut,Periode_Fin,Methode)
        
        rapport,data_temp,wallet=Bot.Get_SimulationGain(data,Paire,Capital_depart)

        # --> Récupération Graphe
        L_Graph_simulation_gain=Util_dash_graphe.Get_Graphe_SimulationGain(data_temp)
        L_Graph_prediction_AV=Util_dash_graphe.Get_Graphe_Prediction_Achat_Vente(data)
        L_Graph_Good_bad_trade=Util_dash_graphe.Get_Graphe_Good_Bad_Trade(wallet)
        L_Wallet=Util_dash_graphe.Get_Graphe_Wallet_Evolution(wallet) 

        # --> Affichage Rapport : 
        L_Temp = rapport.to_dict('records') 
        L_Rapport_modifier = pd.DataFrame({ 'Information' : [i for i in L_Temp[0].keys()],   
        'Valeur' : [L_Temp[0][i] for i in L_Temp[0].keys()] 
        })
        
        output[Methode] = { 
           "rapport": L_Rapport_modifier.to_dict('records'), 
            "graph_prediction": L_Graph_prediction_AV.to_dict(), 
            "graph_simulation": L_Graph_simulation_gain.to_dict(),
            "graph_good_bad_trade":L_Graph_Good_bad_trade.to_dict(),
            "graph_wallet":L_Wallet.to_dict()
        }
    return output