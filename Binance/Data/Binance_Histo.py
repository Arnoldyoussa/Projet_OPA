from binance.client import Client
import pandas as pd
import requests

class Binance_Histo:
    def __init__(self,API_Key: str,API_PASS:str):
        self.G_Client = Client(API_Key, API_PASS)
 
    def get_data(self,L_Symbole,L_Intervalle,L_Start_Date):
        L_Symbole_Intervalle = []
        L_DF_Historical_Klines = self.G_Client.get_historical_klines(L_Symbole,L_Intervalle,L_Start_Date)
        for L_Lignes in L_DF_Historical_Klines:
            L_Symbole_Intervalle.append([L_Symbole,L_Intervalle] + L_Lignes)
        L_columns = ['Symbol', 'Interval', 'Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume', 'Nb_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'ignore']
        L_Resultat = pd.DataFrame(L_Symbole_Intervalle, columns=L_columns)
        return L_Resultat
 

    

 