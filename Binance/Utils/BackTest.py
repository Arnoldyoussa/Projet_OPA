import pandas as pd
import numpy as np
import datetime
import ta
import sqlite3
import plotly.graph_objects as go


def buyCondition(row,previousRow):
  if row['IND_TRIX_HISTO'] > 0 and row['IND_STOCH_RSI'] < 0.8 :
    return True
  else:
    return False

# -- Condition to SELL market --  
def sellCondition(row,previousRow):
  if row['IND_TRIX_HISTO'] < 0 and row['IND_STOCH_RSI'] > 0.2 :
    return True
  else:
    return False
  
def get_data_for_pair(PathDataBase, pair):
    conn = sqlite3.connect(PathDataBase)
    query = f"SELECT * FROM FAIT_SIT_COURS_HIST f JOIN DIM_SYMBOL s ON f.ID_SYMBOL = s.ID_SYMBOL WHERE s.NOM_SYMBOL = '{pair}'"
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

def Backtest_pair(usdt,makerFee,takerFee,pair,PathDataBase):

    # Récupération des données pour la paire dans la base de données
    df=get_data_for_pair(PathDataBase,pair)
    # Copie du dataframe pour les tests 
    dfTest = df.copy()
    # Conversion du timestamp en datetime et mise en index
    dfTest['timestamp_sec'] = dfTest['ID_TEMPS'] * 0.001
    dfTest['datetime'] = pd.to_datetime(dfTest['ID_TEMPS'], unit='ms')
    dfTest.set_index('datetime', inplace=True)
    # Initialisation du solde initial et courant
    initalWallet = usdt
    wallet = usdt
    # Initialisation des variables liées à la position
    coin = 0
    lastAth = 0
    previousRow = dfTest.iloc[0]
    stopLoss = 0
    takeProfit = 20
    buyReady = True
    sellReady = True
    # Initialisation du dataframe de suivi des trades
    dt = None
    dt = pd.DataFrame(columns = ['date','position', 'reason', 'price', 'frais' ,'fiat', 'coins', 'wallet', 'drawBack'])

    # Boucle de simulation des trades
    for index, row in dfTest.iterrows():

    # Achat en ordre de marché
        if buyCondition(row, previousRow) and usdt > 0 and buyReady == True:
            # Définition du prix d'achat
            buyPrice = row['VALEUR_COURS']

            # -- Define the price of you SL and TP or comment it if you don't want a SL or TP --
            # stopLoss = buyPrice - 0.02 * buyPrice
            # takeProfit = buyPrice + 0.04 * buyPrice

            # Calcul du nombre de coins achetés, avec prise en compte des frais
            coin = usdt / buyPrice
            fee = takerFee * coin
            coin = coin - fee
            usdt = 0
            wallet = coin * row['VALEUR_COURS']

            # Vérification de l'ATH atteint pour le calcul du drawdown
            if wallet > lastAth:
                lastAth = wallet
 

            # Ajout du trade au dataframe de suivi
            myrow = {'date': index, 'position': "Buy", 'reason':'Buy Market Order','price': buyPrice,'frais': fee * row['VALEUR_COURS'],'fiat': usdt,'coins': coin,'wallet': wallet,'drawBack':(wallet-lastAth)/lastAth}
            dt = pd.concat([dt, pd.DataFrame([myrow])], ignore_index=True)
        
        # Gestion de stop loss
        elif row['LOW'] < stopLoss and coin > 0:
            sellPrice = stopLoss
            usdt = coin * sellPrice
            fee = makerFee * usdt
            usdt = usdt - fee
            coin = 0
            buyReady = False
            wallet = usdt

            # Vérification de l'ATH atteint pour le calcul du drawdown
            if wallet > lastAth:
                lastAth = wallet
            


            # Ajout du trade au dataframe de suivi
            myrow = {'date': index,'position': "Sell", 'reason':'Sell Stop Loss','price': sellPrice,'frais': fee,'fiat': usdt,'coins': coin,'wallet': wallet,'drawBack':(wallet-lastAth)/lastAth}
            dt = pd.concat([dt, pd.DataFrame([myrow])], ignore_index=True)  

        # -- Sell Market Order --
        elif sellCondition(row, previousRow) and coin > 0 and sellReady == True:

            # Définition du prix d'achat de la vente
            sellPrice = row['VALEUR_COURS']
            usdt = coin * sellPrice
            fee = takerFee * usdt
            usdt = usdt - fee
            coin = 0
            buyReady = True
            wallet = usdt

            # Vérification de l'ATH atteint pour le calcul du drawdown
            if wallet > lastAth:
                lastAth = wallet
 

            # Ajout du trade au dataframe de suivi
            myrow = {'date': index,'position': "Sell", 'reason':'Sell Market Order','price': sellPrice,'frais': fee,'fiat': usdt,'coins': coin,'wallet': wallet,'drawBack':(wallet-lastAth)/lastAth}
            dt = pd.concat([dt, pd.DataFrame([myrow])], ignore_index=True)   
    
    previousRow = row
    dt = dt.set_index(dt['date'])
    dt.index = pd.to_datetime(dt.index)

    # Définition de la colonne "resultat" qui contiendra les gains/pertes en valeur absolue pour chaque transaction 
    # par rapport à la transaction précédente    
    dt['resultat'] = dt['wallet'].diff()
    # Définition de la colonne "resultat%" qui contiendra le pourcentage de gain/perte pour chaque transaction 
    # par rapport à la transaction précédente
    dt['resultat%'] = dt['wallet'].pct_change()*100
    # Mise à None des gains/pertes et des pourcentages de gain/perte pour les positions "Buy"
    dt.loc[dt['position']=='Buy','resultat'] = None
    dt.loc[dt['position']=='Buy','resultat%'] = None
    # Définition de la colonne "tradeIs" qui contiendra la qualité de chaque transaction (Good/Bad) 
    # en fonction du gain/perte réalisé
    dt['tradeIs'] = ''
    dt.loc[dt['resultat']>0,'tradeIs'] = 'Good'
    dt.loc[dt['resultat']<=0,'tradeIs'] = 'Bad'
    # Calcul du pourcentage de gain/perte pour un investissement "hold" sur toute la période de test
    iniClose = dfTest.iloc[0]['VALEUR_COURS']
    lastClose = dfTest.iloc[len(dfTest)-1]['VALEUR_COURS']
    holdPercentage = ((lastClose - iniClose)/iniClose) * 100
    # Calcul du pourcentage de gain/perte réalisé par l'algorithme pendant la période de test
    algoPercentage = ((wallet - initalWallet)/initalWallet) * 100
    # Calcul de la différence entre les pourcentages de gain/perte réalisés par l'algorithme et un investissement "hold"
    vsHoldPercentage = ((algoPercentage - holdPercentage)/holdPercentage) * 100
    # Calcul de la performance totale des trades positifs et négatifs
    try:
        tradesPerformance = round(dt.loc[(dt['tradeIs'] == 'Good') | (dt['tradeIs'] == 'Bad'), 'resultat%'].sum()
                / dt.loc[(dt['tradeIs'] == 'Good') | (dt['tradeIs'] == 'Bad'), 'resultat%'].count(), 2)
    except:
        tradesPerformance = 0
        print("/!\ There is no Good or Bad Trades in your BackTest, maybe a problem...")
# Calcul du nombre total de trades positifs
# Calcul de la performance moyenne des trades positifs
# Calcul de l'index du meilleur trade positif
# Calcul de la performance du meilleur trade positif

    try:
        totalGoodTrades = dt.groupby('tradeIs')['date'].nunique()['Good']
        AveragePercentagePositivTrades = round(dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].sum()
                                            / dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].count(), 2)
        idbest = dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].idxmax()
        bestTrade = str(
            round(dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].max(), 2))
    except:
        totalGoodTrades = 0
        AveragePercentagePositivTrades = 0
        idbest = ''
        bestTrade = 0
        print("/!\ There is no Good Trades in your BackTest, maybe a problem...")
# Calcul du nombre total de trades négatifs
# Calcul de la performance moyenne des trades négatifs
# Calcul de l'index du pire trade négatif
# Calcul de la performance du pire trade négatif
    try:
        totalBadTrades = dt.groupby('tradeIs')['date'].nunique()['Bad']
        AveragePercentageNegativTrades = round(dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].sum()
                                            / dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].count(), 2)
        idworst = dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].idxmin()
        worstTrade = round(dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].min(), 2)
    except:
        totalBadTrades = 0
        AveragePercentageNegativTrades = 0
        idworst = ''
        worstTrade = 0
        print("/!\ There is no Bad Trades in your BackTest, maybe a problem...")
    #Calcul du nombre total de trades et du taux de réussite
    totalTrades = totalBadTrades + totalGoodTrades
    winRateRatio = (totalGoodTrades/totalTrades) * 100
    #Extraction des raisons des trades
    reasons = dt['reason'].unique()
    #Initialisation de la variable de résultat sous forme de chaîne de caractères
    resultats_str = ""
    #Ajout des informations de performance à la variable de résultat
    resultats_str += "Symbole de la paire : " + pair + "\n"
    resultats_str += "Période : [" + str(dfTest.index[0]) + "] -> [" + str(dfTest.index[len(dfTest)-1]) + "]\n"
    resultats_str += "Solde initial : " + str(initalWallet) + " $\n\n"
    resultats_str += "Solde final : " + str(round(wallet, 2)) + " $\n"
    resultats_str += "Performance vs Dollar américain : " + str(round(algoPercentage, 2)) + " %\n"
    resultats_str += "Performance Buy and Hold : " + str(round(holdPercentage, 2)) + " %\n"
    resultats_str += "Performance vs Buy and Hold : " + str(round(vsHoldPercentage, 2)) + " %\n"
    resultats_str += "Meilleur trade : +" + str(bestTrade) + "%, le trade " + str(idbest) + "\n"
    resultats_str += "Pire trade : " + str(worstTrade) + "%, le trade " + str(idworst) + "\n"
    resultats_str += "Pire drawdown : " + str(100*round(dt['drawBack'].min(), 2)) + "%\n"
    resultats_str += "Frais totaux : " + str(round(dt['frais'].sum(), 2)) + " $\n\n"
    resultats_str += "Nombre total de trades : " + str(totalTrades) + "\n"
    resultats_str += "Nombre de trades positifs : " + str(totalGoodTrades) + "\n"
    resultats_str += "Nombre de trades négatifs : " + str(totalBadTrades) + "\n"
    resultats_str += "Taux de réussite des trades : " + str(round(winRateRatio, 2)) + "%\n"
    resultats_str += "Performance moyenne des trades : " + str(tradesPerformance) + "%\n"
    resultats_str += "Performance moyenne des trades positifs : " + str(AveragePercentagePositivTrades) + "%\n"
    resultats_str += "Performance moyenne des trades négatifs : " + str(AveragePercentageNegativTrades) + "%\n\n"
    #Ajout du nombre de trades pour chaque raison à la variable de résultat
    for r in reasons:
        resultats_str += "Nombre de trades pour la raison '" + r + "' : " + str(dt.groupby('reason')['date'].nunique()[r]) + "\n"

    #Retourne la chaîne de caractères contenant les résultats, le DataFrame original et le DataFrame des trades
    return resultats_str,dfTest,dt


def affiche_graphe_score(dt,dfTest):
    # Créer une nouvelle figure vide
    fig = go.Figure()

    # Calculer les rendements mensuels en pourcentage
    monthly_returns = dt['wallet'].resample('M').last().pct_change() * 100

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

    fig.show()
 