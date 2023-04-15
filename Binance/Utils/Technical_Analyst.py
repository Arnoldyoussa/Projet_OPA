import pandas as pd
import numpy as np
import datetime
import ta

def calculate_trix(L_DataFrame, trixLength = 9,trixSignal = 21):
    """
    Calcule l'indicateur TRIX pour un dataframe de données de cours.
    """
    trix = ta.trend.ema_indicator(ta.trend.ema_indicator(ta.trend.ema_indicator(close=L_DataFrame, window=trixLength), window=trixLength), window=trixLength)
    trix_pct = trix.pct_change()*100
    trix_signal = ta.trend.sma_indicator(trix_pct,trixSignal)
    trix_histo = trix_pct - trix_signal

    return trix_histo

def Calculer_Change_Percent(L_DataFrame):
    
    df = pd.DataFrame(L_DataFrame)
    # Calcul la différence de changement en %
    df['Before'] = df.shift(1)
    L_Change_Percent = ( df[df.columns[0]] - df[df.columns[1]]) / df[df.columns[0]] * 100
    return L_Change_Percent

def Calculer_SMA(L_DataFrame,L_indice):
    # Calculer la SMA à 20 périodes sur la colonne "Close"
    L_SMA = L_DataFrame.rolling(window=L_indice).mean()
    return L_SMA

def Calculer_RSI(L_DataFrame, n=14, k=3, d=3):
    # Calculer la différence entre le cours de clôture et le cours de clôture précédent
    L_Delta = L_DataFrame.diff()
    # Initialiser les séries L_Gain et perte avec des valeurs nulle
    L_Gain = pd.Series(0, L_Delta.index)
    L_Pertes = pd.Series(0, L_Delta.index)
    # Remplir les séries L_Gain et perte
    L_Gain[L_Delta > 0] = L_Delta[L_Delta > 0]
    L_Pertes[L_Delta < 0] = -L_Delta[L_Delta < 0]
    # Calculer la moyenne mobile exponentielle des gains et des pertes sur n périodes
    L_Gain_Moyen = L_Gain.rolling(n).mean()
    L_Pertes_Moyennes = L_Pertes.rolling(n).mean()
    # Calculer le ratio RS
    rs = L_Gain_Moyen / L_Pertes_Moyennes
    # Calculer l'indicateur RSI
    L_RSI = 100 - (100 / (1 + rs))
    return L_RSI

def Calculer_RSI_Stochastique(L_DataFrame, n=14, k=3, d=3):
    stoch_rsi=ta.momentum.stochrsi(close=L_DataFrame, window=n, smooth1=k, smooth2=d)
    return stoch_rsi

def buyCondition(row,previousRow):
  if row['IND_TRIX'] > 0 and row['IND_STOCH_RSI'] < 0.8 :
    return True
  else:
    return False

# -- Condition to SELL market --  
def sellCondition(row,previousRow):
  if row['IND_TRIX'] < 0 and row['IND_STOCH_RSI'] > 0.2 :
    return True
  else:
    return False
  
def boucle_trading(L_Dataframe_Cours, initial_usdt = 1000, takerFee = 0.0007):
    usdt = initial_usdt
    coin = 0
    L_Temps = L_Dataframe_Cours
    L_Temps['DEC_ACHAT'] = 0
    L_Temps['DEC_VENTE'] = 0
    previousRow = L_Temps.iloc[0]

    for index, row in L_Temps.iterrows():
        if buyCondition(row, previousRow) and usdt > 0:
            # Définition du prix d'achat
            buyPrice = row['VALEUR_COURS']
            # Calcul du nombre de coins achetés, avec prise en compte des frais
            coin = usdt / buyPrice
            fee = takerFee * coin
            coin = coin - fee
            usdt = 0
            # Mise à jour de la colonne 'achat' avec la valeur 1
            L_Temps.loc[index, 'DEC_ACHAT'] = 1

        elif sellCondition(row, previousRow) and coin > 0:
            # Définition du prix d'achat de la vente
            sellPrice = row['VALEUR_COURS']
            usdt = coin * sellPrice
            fee = takerFee * usdt
            usdt = usdt - fee
            coin = 0
            # Mise à jour de la colonne 'vente' avec la valeur 1
            L_Temps.loc[index, 'DEC_VENTE'] = 1

        previousRow = row
    # Utilisation de la fonction generate_report_v4 pour mettre à jour les valeurs du wallet
    # Filtrage des lignes du DataFrame pour ne garder que celles ayant une transaction d'achat ou de vente
    #L_Dataframe_Filtrer_Transactions = L_Dataframe_Cours.query('DEC_ACHAT == 1 or DEC_VENTE == 1')
    
    return L_Temps

def Generation_Rapport_Backtest(L_Dataframe_Filtrer_Transactions, L_Symbole, L_Capital_Depart = 1000, L_Frais_Transactions = 0.0007):
    # Ajout d'une colonne 'wallet' et initialisation avec la valeur initiale du portefeuille
    L_Dataframe_Filtrer_Transactions['wallet'] = L_Capital_Depart
    usdt = L_Capital_Depart
    coin = 0

    # Calcul des valeurs du wallet en fonction des transactions d'achat et de vente
    for index, row in L_Dataframe_Filtrer_Transactions.iterrows():
        if row['DEC_ACHAT'] == 1:
            buyPrice = row['VALEUR_COURS']
            coin = usdt / buyPrice
            fee = L_Frais_Transactions * coin
            coin = coin - fee
            usdt = 0
            wallet = coin * row['VALEUR_COURS']
            L_Dataframe_Filtrer_Transactions.loc[index, 'wallet'] = wallet
        elif row['DEC_VENTE'] == 1:
            sellPrice = row['VALEUR_COURS']
            usdt = coin * sellPrice
            fee = L_Frais_Transactions * usdt
            usdt = usdt - fee
            coin = 0
            L_Dataframe_Filtrer_Transactions.loc[index, 'wallet'] = usdt
        else:
            L_Dataframe_Filtrer_Transactions.loc[index, 'wallet'] = L_Dataframe_Filtrer_Transactions.loc[index-1, 'wallet']

    wallet = L_Dataframe_Filtrer_Transactions.iloc[-1]['wallet']
    totalGoodTrades = 0
    totalBadTrades = 0 
    L_Dataframe_Filtrer_Transactions['resultat'] = L_Dataframe_Filtrer_Transactions['wallet'].diff()
    L_Dataframe_Filtrer_Transactions['resultat%'] = L_Dataframe_Filtrer_Transactions['wallet'].pct_change()*100
    L_Dataframe_Filtrer_Transactions = L_Dataframe_Filtrer_Transactions.query('DEC_VENTE == 1')

    L_Dataframe_Filtrer_Transactions.loc[(L_Dataframe_Filtrer_Transactions['resultat'] > 0) & (L_Dataframe_Filtrer_Transactions['DEC_VENTE'].notnull()), 'tradeIs'] = 'Good'
    L_Dataframe_Filtrer_Transactions.loc[(L_Dataframe_Filtrer_Transactions['resultat'] <= 0) & (L_Dataframe_Filtrer_Transactions['DEC_VENTE'].notnull()), 'tradeIs'] = 'Bad'

    iniClose = L_Dataframe_Filtrer_Transactions.iloc[0]['VALEUR_COURS']
    lastClose = L_Dataframe_Filtrer_Transactions.iloc[len(L_Dataframe_Filtrer_Transactions)-1]['VALEUR_COURS']
    holdPercentage = ((lastClose - iniClose)/iniClose) * 100

    algoPercentage = ((wallet - L_Capital_Depart)/L_Capital_Depart) * 100

    vsHoldPercentage = ((algoPercentage - holdPercentage)/holdPercentage) * 100

 
    try:
        tradesPerformance = round(L_Dataframe_Filtrer_Transactions.loc[(L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Good') | (L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Bad'), 'resultat%'].sum()
                / L_Dataframe_Filtrer_Transactions.loc[(L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Good') | (L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Bad'), 'resultat%'].count(), 2)
    except:
        tradesPerformance = 0
        print("/!\ There is no Good or Bad Trades in your BackTest, maybe a problem...")
    try:
        totalGoodTrades = L_Dataframe_Filtrer_Transactions[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Good'].index.nunique()
        AveragePercentagePositivTrades = round(L_Dataframe_Filtrer_Transactions.loc[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Good', 'resultat%'].sum()
                                                / L_Dataframe_Filtrer_Transactions.loc[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Good', 'resultat%'].count(), 2)
        idbest = L_Dataframe_Filtrer_Transactions.loc[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Good', 'resultat%'].idxmax()
        bestTrade = str(
            round(L_Dataframe_Filtrer_Transactions.loc[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Good', 'resultat%'].max(), 2))
    except Exception as e:
        print("Error:", e)
        print("DataFrame head:", L_Dataframe_Filtrer_Transactions.head())
        print("DataFrame columns:", L_Dataframe_Filtrer_Transactions.columns)

        totalGoodTrades = 0
        AveragePercentagePositivTrades = 0
        idbest = ''
        bestTrade = 0
        print("/!\ There is no Good Trades in your BackTest, maybe a problem...")

    try:
        totalBadTrades = L_Dataframe_Filtrer_Transactions[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Bad'].index.nunique()
        AveragePercentageNegativTrades = round(L_Dataframe_Filtrer_Transactions.loc[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Bad', 'resultat%'].sum()
                                            / L_Dataframe_Filtrer_Transactions.loc[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Bad', 'resultat%'].count(), 2)
        idworst = L_Dataframe_Filtrer_Transactions.loc[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Bad', 'resultat%'].idxmin()
        worstTrade = round(L_Dataframe_Filtrer_Transactions.loc[L_Dataframe_Filtrer_Transactions['tradeIs'] == 'Bad', 'resultat%'].min(), 2)
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
    #Initialisation de la variable de résultat sous forme de chaîne de caractères
    L_Rapport = ""
    #Ajout des informations de performance à la variable de résultat
    L_Rapport += "Symbole de la L_Symbolee : " + L_Symbole + "\n"
    L_Rapport += "Période : [" + str(L_Dataframe_Filtrer_Transactions.index[0]) + "] -> [" + str(L_Dataframe_Filtrer_Transactions.index[len(L_Dataframe_Filtrer_Transactions)-1]) + "]\n"
    L_Rapport += "Solde initial : " + str(L_Capital_Depart) + " $\n\n"
    L_Rapport += "Solde final : " + str(round(wallet, 2)) + " $\n"
    L_Rapport += "Performance vs Dollar américain : " + str(round(algoPercentage, 2)) + " %\n"
    L_Rapport += "Performance Buy and Hold : " + str(round(holdPercentage, 2)) + " %\n"
    L_Rapport += "Performance vs Buy and Hold : " + str(round(vsHoldPercentage, 2)) + " %\n"
    L_Rapport += "Meilleur trade : +" + str(bestTrade) + "%, le trade " + str(idbest) + "\n"
    L_Rapport += "Pire trade : " + str(worstTrade) + "%, le trade " + str(idworst) + "\n"
    #L_Rapport += "Pire drawdown : " + str(100*round(L_Dataframe_Filtrer_Transactions['drawBack'].min(), 2)) + "%\n"
    #L_Rapport += "Frais totaux : " + str(round(L_Dataframe_Filtrer_Transactions['frais'].sum(), 2)) + " $\n\n"
    L_Rapport += "Nombre total de trades : " + str(totalTrades) + "\n"
    L_Rapport += "Nombre de trades positifs : " + str(totalGoodTrades) + "\n"
    L_Rapport += "Nombre de trades négatifs : " + str(totalBadTrades) + "\n"
    L_Rapport += "Taux de réussite des trades : " + str(round(winRateRatio, 2)) + "%\n"
    L_Rapport += "Performance moyenne des trades : " + str(tradesPerformance) + "%\n"
    L_Rapport += "Performance moyenne des trades positifs : " + str(AveragePercentagePositivTrades) + "%\n"
    L_Rapport += "Performance moyenne des trades négatifs : " + str(AveragePercentageNegativTrades) + "%\n\n"
    #Ajout du nombre de trades pour chaque raison à la variable de résultat

    return L_Rapport