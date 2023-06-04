import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


# --> 
def	Get_Graphe_Prediction_Achat_Vente(Data):
    """
    Cette fonction retourne un graphe de prediction Achat ou Vente.
    """ 
    try: 
        Data = Data.sort_values(by='ID_TEMPS')

        Fig = go.Figure()

        # Ajout de la courbe de la colonne 'valeur_cours'
        Fig.add_trace(go.Scatter(x=Data.index, y=Data['VALEUR_COURS'], mode='lines', name='Valeur du cours'))


        # Ajout des points verts pour les achats
        Fig.add_trace(go.Scatter(x=Data[Data['DEC_ACHAT'] == 1].index, y=Data[Data['DEC_ACHAT'] == 1]['VALEUR_COURS'], mode='markers', marker=dict(color='green', symbol='circle'), name=' Decision Achat'))

        # Ajout des points rouges pour les ventes
        Fig.add_trace(go.Scatter(x=Data[Data['DEC_VENTE'] == 1].index, y=Data[Data['DEC_VENTE'] == 1]['VALEUR_COURS'], mode='markers', marker=dict(color='red', symbol='circle'), name='Decision Vente'))

        # Configuration des titres et des axes
        Fig.update_layout(title='Courbe de la paire par rapport au temps', xaxis_title='Temps', yaxis_title='Valeur de la paire')

    except:
        print("Une erreur est survenue lors de l'exécution de Get_Graphe_Prediction_Achat_Vente:")
        print(str(e))

    return Fig

# -->
def Get_Graphe_Wallet_Evolution(data):


    try:
        
        data = data.reset_index()
        data['DATE_TEMPS'] = pd.to_datetime(data['DATE_TEMPS'])
        start_value = data['wallet'].iloc[0]
        Fig = go.Figure()

        for i in range(1, len(data)):
            if data['wallet'].iloc[i] > start_value:
                # For wallet value greater than start value, color goes from yellow to green
                red = max(0, int(255 * (1 - ((data['wallet'].iloc[i] - start_value) / start_value))))
                green = 255
            else:
                # For wallet value less than start value, color goes from yellow to red
                red = 255
                green = min(255, int(255 * ((data['wallet'].iloc[i]) / start_value)))
            blue = 0

            Fig.add_trace(
                go.Scatter(
                    x=data['DATE_TEMPS'].iloc[i-1:i+1],
                    y=data['wallet'].iloc[i-1:i+1],
                    mode='lines',
                    showlegend=False,
                    hoverinfo='x+y',
                    line=dict(
                        color='rgb({},{},{})'.format(red, green, blue),
                    )
                )
            )
        Fig.update_layout(
            title='Evolution du Wallet',
            xaxis_title='Temps',
            yaxis_title='Montant du Wallet',
            
            showlegend=False
        )

    except Exception as e:
        print("Une erreur est survenue lors de l'exécution de Get_Graphe_Wallet_Evolution:")
        print(str(e))
        
    return (Fig)

# -->
def Get_Graphe_Good_Bad_Trade(data):
    
    try:
        # Compter les valeurs 'Good' et 'Bad'
        trade_counts = data['tradeIs'].value_counts()

        # Créer le dictionnaire de correspondance
        mapping_dict = {'Good': 'trades gagnants', 'Bad': 'trades perdants'}

        # Changer les noms en utilisant le dictionnaire
        trade_counts.index = trade_counts.index.map(mapping_dict)

        # Créer le diagramme circulaire
        Fig = px.pie(trade_counts, values=trade_counts.values, names=trade_counts.index, title='Pourcentage de bon et mauvais trades')

        # Modifier le tooltip
        Fig.update_traces(hovertemplate='Nombre de %{label} réalisés: %{value}')

    except Exception as e:
        print("Une erreur est survenue lors de l'exécution de Get_Graphe_Good_Bad_Trade:")
        print(str(e))

    return (Fig)

# -->
def Get_Graphe_SimulationGain(Data):
    """
    Cette fonction retourne un graphe de simulation de Gain 
    """
    try:
        df_temps = Data.copy()
        df_temps['timestamp_sec'] = df_temps['ID_TEMPS'] * 0.001
        df_temps['datetime'] = pd.to_datetime(df_temps['ID_TEMPS'], unit='ms')
        df_temps.set_index('datetime', inplace=True) 
        #df_temps.to_csv("data2.csv") 
    except Exception as e:
        print("Une erreur est survenue lors de l'exécution de Get_Graphe_SimulationGain:")
        print(str(e))
        df_temps = None 

    if df_temps is not None:
        # Créer une nouvelle figure vide
        fig = go.Figure()

        # Calculer le pourcentage mensuel
        monthly_wallet_change = df_temps.resample("M")["resultat%"].sum()

        # Échantillonner le prix ETH/USDT à la fin de chaque mois
        monthly_prices = df_temps['VALEUR_COURS'].resample('M').last()
        monthly_prices.iloc[0] = df_temps['VALEUR_COURS'].iloc[0]
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
    else:
        return None