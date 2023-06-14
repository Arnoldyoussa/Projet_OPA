from Binance import Bot_Trading_OPA as Bot
import redis
import json
import requests
import datetime as dt
import pandas as pd

r = redis.Redis(host='localhost', port=6379, db=0)

# Récupère les données de l'API Binance et les stocke dans Redis
def Maj_base_redis(Periode_Debut= dt.date.today().isoformat(), Periode_Fin = dt.date.today().isoformat() ):
    
    # -->    
    X = Bot.Get_API_Binance().exchange_info()
    data = [{'symbol' : symbol['symbol'], 'baseAsset' : symbol['baseAsset'], 'quoteAsset' : symbol['quoteAsset']  } for symbol in X['symbols'] ]

    # -->
    for index, item in enumerate(data):
        paire = item['symbol']
        donnees_paire = Bot.Get_Live_InfoPaire(paire, '1h', Periode_Debut, Periode_Fin)
        if isinstance(donnees_paire, pd.DataFrame) and not donnees_paire.empty:
            paire_devises = {"label": f"{item['baseAsset']}/{item['quoteAsset']}", "value": f"{item['baseAsset']}_{item['quoteAsset']}"}
            restant = len(data) - (index + 1)  # Calcule le nombre de données restantes à traiter
            if not r.exists(paire_devises["value"]):  # Vérifie si la clé existe déjà
                r.set(paire_devises["value"], json.dumps(donnees_paire.to_dict()))

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
