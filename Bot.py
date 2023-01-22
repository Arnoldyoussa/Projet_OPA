
from Binance.Data import Binance_Histo as Histo
from Binance.Data import Binance_Live as live
from Binance.Dao import Drivers_MongoDB as DAO_MB
from Binance.Dao import Drivers_SQlite as DAO_SQL

#X = Histo.Binance_Histo(['ETHBUSD'], ['15m'], Frequence= 'M')

#X.get_ListeFichier()
#X.TelechargeFichier()
#X.SupprimeFichier()

#Y = DAO_MB.Drivers_MongoDB(['ETHBUSD-15m-2022-12.csv'])
#Y.ChargeFichiers()

#Z = live.Binance_Live()
#print(Z.klines("ETHBUSD", "15m", limit = 2))

T = DAO_SQL.Drivers_SQLite('/home/arnold/ENV_VIRTUEL/ATU_FORMATION/REP_DEV/Projet_OPA/DataBase/SQLite/test.db')

print(T.ISValid_SQL('SELECT 1;'))

print(T.Select("SELECT 2, 5, ?;", ('hello!',)))
print(T.Select('select current_date +1 as "hi" union select current_date +2 as "ha"  ;'))

T.CloseConnection()