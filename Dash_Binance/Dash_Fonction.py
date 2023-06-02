import requests
import datetime as dt
import pandas as pd
import redis
import json
from Binance import Bot_Trading_OPA as Bot
from datetime import  timedelta

BINANCE_API_URL = "https://api.binance.com/api/v3/exchangeInfo"
r = redis.Redis(host='localhost', port=6379, db=0)



# Convertit le timestamp en millisecondes en une chaîne formatée
def convert_timestamp(timestamp_en_millisecondes):
    timestamp_en_secondes = timestamp_en_millisecondes / 1000
    dt_object = dt.datetime.fromtimestamp(timestamp_en_secondes)
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")


# Récupère les données de l'API Binance et les stocke dans Redis
def Maj_base_redis():
    response = requests.get(BINANCE_API_URL)
    
    if response.status_code == 200:
        data = response.json()["symbols"]
        for index, item in enumerate(data):
            paire = item['baseAsset'] + item['quoteAsset']
            print(paire)
            donnees_paire = Bot.Get_Live_InfoPaire(paire, '1h', dt.date.today().isoformat(), dt.date.today().isoformat())
            if isinstance(donnees_paire, pd.DataFrame) and not donnees_paire.empty:
                paire_devises = {"label": f"{item['baseAsset']}/{item['quoteAsset']}", "value": f"{item['baseAsset']}_{item['quoteAsset']}"}
                restant = len(data) - (index + 1)  # Calcule le nombre de données restantes à traiter
                if not r.exists(paire_devises["value"]):  # Vérifie si la clé existe déjà
                    r.set(paire_devises["value"], json.dumps(donnees_paire.to_dict()))
                    print(f"Ajouté à Redis, {restant} restant(s)")
                else:
                    print(f"La clé existe déjà, {restant} restant(s)")


# Récupère les paires de devises depuis Redis
def fetch_currency_pairs_redis():
    try:
        cles = r.keys()  # Récupère toutes les clés de la base de données Redis
        paires_devises = []

        for cle in cles:
            donnees_paire_json = r.get(cle)  # Récupère la valeur de la clé
            donnees_paire = json.loads(donnees_paire_json)  # Convertit la chaîne JSON en objet Python
            # Nous supposons que la clé est au format "baseAsset_quoteAsset"
            baseAsset, quoteAsset = cle.decode('utf-8').split("_")  # Divise la clé sur le caractère '_'

            paire_devises = {
                "label": f"{baseAsset}/{quoteAsset}",
                "value": cle.decode('utf-8')
            }
            paires_devises.append(paire_devises)
        print("Telechargement des Paires depuis Redis réussi")
        return paires_devises
    except Exception as e:
        print(f"Erreur lors de la récupération des paires de devises depuis Redis : {str(e)}")
        return []


# Récupère les paires de devises depuis l'API Binance
def fetch_currency_pairs_binance():
    response = requests.get(BINANCE_API_URL)

    if response.status_code == 200:
        data = response.json()["symbols"]
        return [{"label": f"{item['baseAsset']}/{item['quoteAsset']}", "value": f"{item['baseAsset']}_{item['quoteAsset']}"} for item in data]
    else:
        return []
    

def Get_Backtest(Paire,Periode_Debut,Periode_Fin,Capital_depart,dureeJr_Entrainement):


    # Convertir la chaîne en objet datetime
    date_obj = dt.datetime.strptime(Periode_Debut, "%d-%m-%Y")
    # Reformater l'objet datetime en chaîne de caractères
    Periode_Debut = date_obj.strftime("%Y-%m-%d")
    date_obj = dt.datetime.strptime(Periode_Fin, "%d-%m-%Y")
    # Reformater l'objet datetime en chaîne de caractères
    Periode_Fin = date_obj.strftime("%Y-%m-%d")
    output = {}  # Dictionnaire pour stocker les résultats
    for Methode in ['M1', 'M2']: 
        if Methode =='M1':  
            data=Bot.Get_DataPaire([Paire],Periode_Debut,Periode_Fin,"M1")
            rapport,data_temp,wallet=Bot.Get_SimulationGain(data,Paire,Capital_depart)
            L_Graph_simulation_gain=Bot.Get_Graphe_SimulationGain(data_temp)
            L_Graph_prediction_AV=Bot.Get_Graphe_Prediction_Achat_Vente(data)
            L_Graph_Good_bad_trade=Bot.Get_Graphe_Good_Bad_Trade(wallet)
            L_Wallet=Bot.Get_Graphe_Wallet_Evolution(wallet) 
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
        else:
            StartTime = (dt.datetime.fromisoformat(Periode_Debut) - timedelta(days = dureeJr_Entrainement)).strftime('%Y-%m-%d')
            Bot.Load_DB_Mongo([Paire],StartTime,Periode_Debut)
            Bot.Load_DB_SQL_Histo([Paire],StartTime,Periode_Debut)
            Bot.Load_DB_SQLPrediction(Paire,"M2")
            data=Bot.Get_DataPaire([Paire],Periode_Debut,Periode_Fin,"M2")
            rapport,data_temp,wallet=Bot.Get_SimulationGain(data,Paire,Capital_depart)
            L_Graph_Good_bad_trade=Bot.Get_Graphe_Good_Bad_Trade(wallet)
            L_Wallet=Bot.Get_Graphe_Wallet_Evolution(wallet)
            L_Temp = rapport.to_dict('records')
            L_Rapport_modifier = pd.DataFrame({ 'Information' : [i for i in L_Temp[0].keys()],  
            'Valeur' : [L_Temp[0][i] for i in L_Temp[0].keys()] 
            })
            L_Graph_simulation_gain=Bot.Get_Graphe_SimulationGain(data_temp)
            L_Graph_prediction_AV=Bot.Get_Graphe_Prediction_Achat_Vente(data)
            output[Methode] = {
            "rapport": L_Rapport_modifier.to_dict('records'), 
            "graph_prediction": L_Graph_prediction_AV.to_dict(),  
            "graph_simulation": L_Graph_simulation_gain.to_dict(),
            "graph_good_bad_trade":L_Graph_Good_bad_trade.to_dict(),
            "graph_wallet":L_Wallet.to_dict()
            }   
    print("Fin du Backtest") 
    return output
