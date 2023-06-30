import datetime
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# --
def Convertir_toTimestamp(DateIsoFormat):
    return int(datetime.datetime.fromisoformat(DateIsoFormat).timestamp() * 1000)

# --
def Convertir_Timestamp(X, formatDate = None):
    myDate = datetime.datetime.fromtimestamp(float(X)/1000)
    
    if formatDate == 'DD':
        return str(myDate.day).rjust(2,'0')
    elif formatDate == 'MM':
        return str(myDate.month).rjust(2,'0')
    elif formatDate == 'YYYY':
        return str(myDate.year)
    elif formatDate == 'HH':
        return str(myDate.hour).rjust(2,'0')
    elif formatDate == 'mm':
        return str(myDate.minute).rjust(2,'0')
    elif formatDate == 'ss':
        return str(myDate.second).rjust(2,'0')
    else :
        return str(myDate.year) + "-" + str(myDate.month).rjust(2,'0') + "-" + str(myDate.day).rjust(2,'0') + " " + str(myDate.hour).rjust(2,'0') + ":" + str(myDate.minute).rjust(2,'0') + ":" + str(myDate.second).rjust(2,'0')

# --
def Prediction_SQL_To_DF(ResultatSQL_Class) :
    
    L = list()
    for i in ResultatSQL_Class:
        (a, b, c, d, e, f, g, h) = i
        L.append({'ID_SIT_CRS' : a,
                 'IND_STOCH_RSI' : b, 
                 'IND_RSI' : c, 
                 'IND_TRIX' : d ,
                 'DEC_ACHAT' :e ,
                 'DEC_VENTE' : f,
                 'ID_TEMPS' : g,
                 'VALEUR_COURS' : h
                 })

    return pd.DataFrame(L)

# --
def supprimer_decisions_consecutives(df):

    prev_achat = None
    prev_vente = None
    to_drop = []
            # Ajout de la condition pour supprimer les lignes avec 0 dans les colonnes 'dec_achat' et 'dec_vente'
    for index, row in df.iterrows():
        if prev_achat == row['DEC_ACHAT'] and prev_vente == row['DEC_VENTE']:
            to_drop.append(index)
        else:
            prev_achat = row['DEC_ACHAT']
            prev_vente = row['DEC_VENTE']
    return df.drop(to_drop).reset_index(drop=True)

# --
def remove_duplicates(Data):
        # Identifier les lignes en double (gardez la première occurrence)
    duplicated_rows = Data.index.duplicated(keep='first')

        # Inverser les valeurs booléennes (True pour les lignes uniques, False pour les doublons)
    unique_rows = ~duplicated_rows

        # Filtrer les lignes uniques et créer un nouveau DataFrame sans doublons
    Data_unique = Data[unique_rows]

    return Data_unique