from Binance.Data import Binance_Histo as Histo
#from Binance.Data import Binance_Live as live
from Binance.Dao import Drivers_MongoDB as DAO_MB
from Binance.Dao import Drivers_SQlite as DAO_SQL
from Binance.Utils import Utilitaire as Util
from Binance.Utils import Technical_Analyst as Ta
import pandas as pd

X = Histo.Binance_Histo(['BTCUSDT'], ['15m'], Frequence= 'M')

X.get_ListeFichier()
X.TelechargeFichier()
#X.SupprimeFichier()

Y = DAO_MB.Drivers_MongoDB(['BTCUSDT-15m-2022-12.csv'])
Y.ChargeFichiers()

b=Y.get_ListeFichier('BTCUSDT')

A= DAO_SQL.Drivers_SQLite('DB_OPA.db')

G_Docs=Y.get_AllDocuments('BTCUSDT')
G_Symbole=G_Docs[0]['_id']
symbole=Y.get_AllCollection()
all_symbols_data = []
for i in symbole:
    symbol_data =Util.Recuperer_Info_Symbole(i)
    all_symbols_data.append(symbol_data)
q= A.Alim_DimSymbol(all_symbols_data)
print(q)
G_Noms_Colonnes = list(G_Docs[0]['Detail'][0].keys())
# Création d'un DataFrame Pandas en utilisant les noms de colonnes de l'array
G_DataFrame = pd.DataFrame(G_Docs[0]['Detail'], columns=G_Noms_Colonnes)
# Normalisation des données JSON pour créer un DataFrame avec une structure de données plus plate
G_DataFrame = pd.json_normalize(G_Docs, 'Detail')

TIME_DataFrame = Util.Convertir_Timestamp(G_DataFrame['Open_time'])
G_DataFrame['IND_TRIX']=Ta.Calculer_TRIX(G_DataFrame['Close'])
G_DataFrame['IND_SMA_20']=Ta.Calculer_SMA(G_DataFrame['Close'],20)
G_DataFrame['IND_SMA_30']=Ta.Calculer_SMA(G_DataFrame['Close'],30)
G_DataFrame['IND_RSI']=Ta.Calculer_RSI(G_DataFrame['Close'])
G_DataFrame['IND_STOCH_RSI']=Ta.Calculer_RSI_Stochastique(G_DataFrame['Close'])
G_DataFrame['IND_CHANGEPERCENT']=Ta.Calculer_Change_Percent(G_DataFrame[['Open','Close']])

print(G_DataFrame)
q=A.Alim_DimTemps(TIME_DataFrame)
print(q)
q=A.Alim_FaitSituation_Histo(G_DataFrame,'BTCUSDT')
#Z = live.Binance_Live()
#print(Z.klines("ETHBUSD", "15m", limit = 2))
"""
T = DAO_SQL.Drivers_SQLite('/home/arnold/ENV_VIRTUEL/ATU_FORMATION/REP_DEV/Projet_OPA/DataBase/SQLite/test.db')

print(T.ISValid_SQL('SELECT 1;'))

print(T.Select("SELECT 2, 5, ?;", ('hello!',)))
print(T.Select('select current_date +1 as "hi" union select current_date +2 as "ha"  ;'))

T.CloseConnection()
"""