import requests
import datetime as dt
import pandas as pd
import redis
import json
from Binance import Bot_Trading_OPA as Bot

BINANCE_API_URL = "https://api.binance.com/api/v3/exchangeInfo"
r = redis.Redis(host='localhost', port=6379, db=0)


# Convertit le timestamp en millisecondes en une chaîne formatée
def convert_timestamp(timestamp_en_millisecondes):
    timestamp_en_secondes = timestamp_en_millisecondes / 1000
    dt_object = dt.datetime.fromtimestamp(timestamp_en_secondes)
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")


# Récupère les données de l'API Binance et les stocke dans Redis
def Maj_base_redis():
    r = redis.Redis(host='localhost', port=6379, db=0)
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
        r = redis.Redis(host='localhost', port=6379, db=0)
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
