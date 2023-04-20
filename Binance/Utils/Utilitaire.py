import datetime
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd

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
    fig = go.Figure()
    # Ajout de la courbe de la colonne 'valeur_cours'
    fig.add_trace(go.Scatter(x=L_Dataframe.index, y=L_Dataframe['VALEUR_COURS'], mode='lines', name='Valeur du cours'))

    # Ajout des points verts pour les achats
    fig.add_trace(go.Scatter(x=L_Dataframe[L_Dataframe['DEC_ACHAT'] == 1].index, y=L_Dataframe[L_Dataframe['DEC_ACHAT'] == 1]['VALEUR_COURS'], mode='markers', marker=dict(color='green', symbol='circle'), name=' Decision Achat'))

    # Ajout des points rouges pour les ventes
    fig.add_trace(go.Scatter(x=L_Dataframe[L_Dataframe['DEC_VENTE'] == 1].index, y=L_Dataframe[L_Dataframe['DEC_VENTE'] == 1]['VALEUR_COURS'], mode='markers', marker=dict(color='red', symbol='circle'), name='Decision Vente'))
    # Configuration des titres et des axes
    fig.update_layout(title='Courbe de la paire par rapport au temps', xaxis_title='Temps', yaxis_title='Valeur de la paire')
    
    return fig

# --
def affiche_graphe_score(dfTest):
    # Créer une nouvelle figure vide
    fig = go.Figure()

    # Calculer les rendements mensuels en pourcentage
    monthly_returns = dfTest['wallet'].resample('M').last().pct_change() * 100

    # Créer un graphique en barres avec vert pour les rendements positifs et rouge pour les rendements négatifs
    fig = go.Figure(data=go.Bar(x=monthly_returns.index, y=monthly_returns.values, 
                                marker_color=monthly_returns.apply(lambda x: 'green' if x >= 0 else 'red'), name="Notre Bot de Trading"),
                    layout=go.Layout(title='Profits/Pertes de la stratégie par mois', 
                                    xaxis=dict(title=''), 
                                    yaxis=dict(title='Variation du portefeuille en %')))

    # Échantillonner le prix ETH/USDT à la fin de chaque mois
    
    monthly_prices = dfTest['VALEUR_COURS'].resample('M').last()

    # Calculer les rendements mensuels pour la stratégie Buy and Hold
    bh_monthly_returns = monthly_prices.pct_change() * 100

    # Créer un graphique en barres avec vert pour les rendements positifs et rouge pour les rendements négatifs pour la stratégie Buy and Hold
    bh_bar_colors = bh_monthly_returns.apply(lambda x: 'green' if x >= 0 else 'red')
    fig.add_trace(go.Bar(x=bh_monthly_returns.index, y=bh_monthly_returns.values, 
                        marker_color='black', opacity=0.2, name='Buy and Hold'))

    # Mettre à jour la mise en page pour afficher une légende
    fig.update_layout(title='Profits/Pertes de la stratégie par mois', 
                    xaxis=dict(title=''), 
                    yaxis=dict(title='Variation du portefeuille en %'),
                    barmode='overlay', legend=dict(x=0.7, y=1.1))

    return fig

# --
def Prediction_SQL_To_DF(ResultatSQL_Class) :
    
    L = list()
    for i in ResultatSQL_Class:
        (a, b, c, d, e, f) = i
        L.append({'ID_SIT_CRS' : a,
                 'IND_STOCH_RSI' : b, 
                 'IND_RSI' : c, 
                 'IND_TRIX' : d ,
                 'DEC_ACHAT' :e ,
                 'DEC_VENTE' : f
                 })

    return pd.DataFrame(L)