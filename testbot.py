
from Binance import Bot_Trading_OPA as Bot
import plotly.graph_objs as go
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import pandas as pd
import time
import threading
import plotly.express as px
date_debut="2023-01-01"
date_fin="2023-05-01"
capital=10000
currency_pair="ETHUSDT"
StartTime = (datetime.fromisoformat(date_debut) - timedelta(days = 90)).strftime('%Y-%m-%d')
EndTime = date_debut 
Bot.Reset_DB_All()
#base reinitialisé
Bot.Load_DB_Mongo([currency_pair], StartTime, EndTime)
#paire télécharger en mongo
Bot.Load_DB_SQL_Histo([currency_pair], StartTime, EndTime)
Bot.Load_DB_SQL_Live([currency_pair], EndTime, date_fin)
#paire telecharger en sql


L = list()
for Methode in ['M1', 'M2']:
    print('#######Etape Methode : {} #######'.format(Methode))
    
    #--
    print('#######Calcul Prediction Vente Achat #######')
    Bot.Load_DB_SQLPrediction(currency_pair, Methode)
    X = Bot.Get_DataPaire([currency_pair], date_debut, date_fin, Methode )           
    X.to_csv("x.csv")
    
    #--
    print('#######Generation Graphe Prediction Vente Achat #######')
    fig_DEC = Bot.Get_Graphe_Prediction_Achat_Vente(X)
    #--
    print('#######Generation Graphe Simulation #######')
    (rapport, Data) = Bot.Get_SimulationGain(X, currency_pair,capital)
    fig_GAIN = Bot.Get_Graphe_SimulationGain(Data)
    
    
    #--
    X = rapport.to_dict('records')
    
    X_temps = pd.DataFrame({ 'Information' : [i for i in X[0].keys()], 
                        'Value' : [X[0][i] for i in X[0].keys()] 
                        })
    L.append({'Methode' : Methode,
                'Resultat' : {'rapport' : X_temps.to_dict('records'), 
                            'fig_Graphe_Decision' : fig_DEC,
                            'fig_Graphe_SimiGain' : fig_GAIN}
                })
Data=L
fig_decision = Data[0]['Resultat']['fig_Graphe_Decision']
fig_gain = Data[0]['Resultat']['fig_Graphe_SimiGain']

fig_decision.show()
fig_gain.show()
fig_decision = Data[1]['Resultat']['fig_Graphe_Decision']
fig_gain = Data[1]['Resultat']['fig_Graphe_SimiGain']

fig_decision.show()
fig_gain.show()

# Affichage du rapport
rapport = Data[0]['Resultat']['rapport']
for item in rapport:
    print(f"{item['Information']}: {item['Value']}")

rapport = Data[1]['Resultat']['rapport']
for item in rapport:
    print(f"{item['Information']}: {item['Value']}")

