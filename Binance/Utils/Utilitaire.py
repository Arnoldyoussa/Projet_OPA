import datetime
from binance import Client
from math import *

G_api_key= "7D2zP6PkcRVmrP3KiYfePPrCeJmio8zHZKNeEtwFbHtgK6DNbWse4auahLHglgwf"       #on crée une variable avec la valeur de la clef de l'api qui à été generer en amont
G_api_secret= "0vZzdRUXlnoZLWYfeFi4nqFkszxnEIgw18qYlSKbEW9izxDnqKHKqugX6T5Yv129"    #on crée une variable avec la valeur du code de la clef de l'api.

def Convertir_Timestamp(L_Series):
    L_DataFrame = L_Series.to_frame()
    L_DataFrame.columns=['Open_time']
    L_DataFrame['ID_TEMPS']=L_DataFrame['Open_time']
    #Convert timestamp to datetime object
    L_DataFrame['Open_time'] = L_DataFrame["Open_time"].apply(lambda x: datetime.datetime.fromtimestamp(x/1000))
    #Create new columns with desired date and time information
    L_DataFrame["JOUR"] = L_DataFrame["Open_time"].apply(lambda x: x.day)
    L_DataFrame["MOIS"] = L_DataFrame["Open_time"].apply(lambda x: x.month)
    L_DataFrame["ANNEE"] = L_DataFrame["Open_time"].apply(lambda x: x.year)
    L_DataFrame["HEURE"] = L_DataFrame["Open_time"].apply(lambda x: x.hour)
    L_DataFrame["MINUTES"] = L_DataFrame["Open_time"].apply(lambda x: x.minute)
    L_DataFrame["SECONDES"] = L_DataFrame["Open_time"].apply(lambda x: x.second)
    # Formater les objets datetime en format "jj/mm/aaaa hh/mm/ss"
    L_DataFrame['DATE_CREATION'] = L_DataFrame['Open_time'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S"))
    return(L_DataFrame)


def Recuperer_Info_Symbole(L_pair):
   client = Client(api_key=G_api_key,api_secret=G_api_secret) #On instancie la classe avec nos variables 
   L_Requette=client.get_symbol_info(L_pair)
   #renvoie un dictionnaire
   return(L_Requette)
