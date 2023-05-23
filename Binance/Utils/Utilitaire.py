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
def visualiser_graphe_Moustache(Data):
    fig = go.Figure()

    fig.add_trace(go.Box( y=Data['data']))
    fig.update_layout(title='Graphe en Moustache', xaxis_title='Temps', yaxis_title='Valeur de la paire')

    return fig

# --
def visualiser_transactions(L_Dataframe):
    try :
        L_Dataframe = L_Dataframe.sort_values(by='ID_TEMPS')

        fig = go.Figure()
        # Ajout de la courbe de la colonne 'valeur_cours'
        fig.add_trace(go.Scatter(x=L_Dataframe.index, y=L_Dataframe['VALEUR_COURS'], mode='lines', name='Valeur du cours'))

        # Ajout des points verts pour les achats
        fig.add_trace(go.Scatter(x=L_Dataframe[L_Dataframe['DEC_ACHAT'] == 1].index, y=L_Dataframe[L_Dataframe['DEC_ACHAT'] == 1]['VALEUR_COURS'], mode='markers', marker=dict(color='green', symbol='circle'), name=' Decision Achat'))

        # Ajout des points rouges pour les ventes
        fig.add_trace(go.Scatter(x=L_Dataframe[L_Dataframe['DEC_VENTE'] == 1].index, y=L_Dataframe[L_Dataframe['DEC_VENTE'] == 1]['VALEUR_COURS'], mode='markers', marker=dict(color='red', symbol='circle'), name='Decision Vente'))
        # Configuration des titres et des axes
        fig.update_layout(title='Courbe de la paire par rapport au temps', xaxis_title='Temps', yaxis_title='Valeur de la paire')
    except Exception as e:
        print("Une erreur est survenue lors de l'exécution de visualiser_transactions:")
        print(str(e))
    return fig

# --
def affiche_graphe_score(dfTest):
    # Créer une nouvelle figure vide
    fig = go.Figure()

    # Calculer le pourcentage mensuel
    monthly_wallet_change = dfTest.resample("M")["resultat%"].sum()

    # Échantillonner le prix ETH/USDT à la fin de chaque mois
    monthly_prices = dfTest['VALEUR_COURS'].resample('M').last()
    monthly_prices.iloc[0] = dfTest['VALEUR_COURS'].iloc[0]
    bh_monthly_returns = monthly_prices.pct_change()
    bh_monthly_returns.iloc[0] = np.NaN
    bh_monthly_returns = bh_monthly_returns.fillna(0) * 100

    # Créer le graphique à barres pour l'évolution du wallet
    colors = ['green' if value >= 0 else 'red' for value in monthly_wallet_change]
    bar_chart_wallet = go.Bar(
        x=monthly_wallet_change.index, y=monthly_wallet_change.values,
        marker=dict(color=colors), name="Évolution du wallet en %"
    )

    # Créer le graphique à barres pour la stratégie buy and hold
    colors = ['green' if value >= 0 else 'red' for value in bh_monthly_returns]
    bar_chart_buy_and_hold = go.Bar(
        x=bh_monthly_returns.index, y=bh_monthly_returns.values,
        marker=dict(color=colors, opacity=0.5), name="Buy and hold",
        visible='legendonly'
    )

    # Créer une mise en page pour le graphique
    layout = go.Layout(
        title="Évolution du wallet en % par rapport au temps (avec stratégie Buy and Hold)",
        xaxis=dict(title="Mois", tickformat="%b %Y"), 
        yaxis=dict(title="Évolution du wallet en %"),
        barmode="overlay"
    )

    # Créer et afficher la figure
    fig = go.Figure(data=[bar_chart_wallet, bar_chart_buy_and_hold], layout=layout)

    # Générer les étiquettes de l'axe des x
    x_labels = bh_monthly_returns.index.strftime('%B %Y')

    # Mettre à jour l'axe des x avec les étiquettes générées
    fig.update_xaxes(type='category', tickvals=bh_monthly_returns.index, ticktext=x_labels)
    
    return fig

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