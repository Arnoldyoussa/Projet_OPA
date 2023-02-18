import pandas as pd
import numpy as np

def Calculer_trix(L_DataFrame, L_Periode_Jour=15):
    """
    Calcule l'indicateur TRIX pour un dataframe de données de cours.
    """
    # Calcul de la moyenne mobile exponentielle sur n périodes
    L_ema1 = L_DataFrame.ewm(span=L_Periode_Jour, adjust=False).mean()
    # Calcul de la moyenne mobile exponentielle sur n périodes de la première moyenne mobile exponentielle
    L_ema2 = L_ema1.ewm(span=L_Periode_Jour, adjust=False).mean()
    # Calcul de la moyenne mobile exponentielle sur n périodes de la deuxième moyenne mobile exponentielle
    L_ema3 = L_ema2.ewm(span=L_Periode_Jour, adjust=False).mean()
    # Calcul de l'indicateur TRIX comme la différence entre la troisième moyenne mobile exponentielle et sa moyenne mobile exponentielle sur n périodes
    L_Trix = L_ema3.diff(L_Periode_Jour)
    
    return L_Trix

 



def Calculer_Ema_200(L_DataFrame):
    window_size = 200
    col_name = 'SMA200'
    L_EMA_200 = L_DataFrame.rolling(window_size).mean()
    return L_EMA_200


def Calculer_Change_Percent(L_DataFrame):
    
    L_Dataframe = pd.DataFrame(L_DataFrame)
    # Calcul la différence de changement en %
    L_Dataframe['Before'] = L_Dataframe.shift(1)
    L_Change_Percent = ( L_Dataframe[L_Dataframe.columns[0]] - L_Dataframe[L_Dataframe.columns[1]]) / L_Dataframe[L_Dataframe.columns[0]] * 100
    return L_Change_Percent

def Calculer_SMA(L_DataFrame,L_indice):
    # Calculer la SMA à 20 périodes sur la colonne "Close"
    L_SMA = L_DataFrame.rolling(window=L_indice).mean()
    return L_SMA

def Calculer_RSI(L_DataFrame, n=14):
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
   # Calculer la moyenne mobile exponentielle de l'indicateur RSI sur k périodes
    L_RSI_K = L_RSI.ewm(span=k).mean()
    # Calculer la moyenne mobile exponentielle de l'indicateur RSI sur d périodes
    L_RSI_D = L_RSI_K.ewm(span=d).mean()
    # Calculer l'indicateur RSI Stochastique
    L_RSI_Stochastique = (L_RSI - L_RSI_D) / (100 - L_RSI_D)
    return L_RSI_Stochastique


def get_buy_sell_signal(df):
    # Calculer les seuils de signal
    trix_threshold = 0.0
    stoch_rsi_threshold = 0.2

    # Calculer les signaux d'achat/vente
    df['Signal'] = pd.Series('No Buy', index=df.index)
    buy_signals = (df['IND_TRIX'] > trix_threshold) & (df['IND_STOCH_RSI'] < stoch_rsi_threshold)
    df.loc[buy_signals, 'Signal'] = 'Buy'

    return df['Signal']
    
 
        
def verifier_decision_achat(df):
    decisions = []
    for i in range(1, len(df)):
        if df['Recommandation'][i-1] == 'Buy' and df['Close'][i] > df['Close'][i-1]:
            decisions.append('Bonne decision')
        elif df['Recommandation'][i-1] == 'No Buy' and df['Close'][i] < df['Close'][i-1]:
            decisions.append('Bonne decision')
        else:
            decisions.append('Mauvaise decision')
    #decisions.append("fin")
    df_decisions = df.copy().iloc[1:]
    df_decisions['Decision'] = decisions
 
    return df_decisions
def simulate_trading(df, initial_capital, stop_loss, take_profit):
    # Initialiser les variables de suivi du portefeuille
    cash = initial_capital
    positions = 0
    last_price = None
    realized_pnl = 0

    # Parcourir les signaux et exécuter les ordres d'achat/vente
    for index, row in df.iterrows():
        if row['Signal'] == 'Buy':
            if last_price is not None and row['Close'] > last_price:
                # Si le prix a augmenté depuis le dernier signal d'achat, acheter au prix actuel
                price = row['Close']
            else:
                # Sinon, acheter au prix d'ouverture du jour suivant
                if (index + 1) >= len(df):
                    # Si l'indice dépasse la plage d'indices du DataFrame, continuer à la ligne suivante
                    continue
                price = df.loc[index+1, 'Open']
            
            # Calculer la taille de la position en fonction du capital disponible
            position_size = cash // price
            if position_size == 0:
                continue # Si la position est trop petite, ne rien faire
            
            # Mettre en place les ordres d'achat
            positions += position_size
            cash -= position_size * price
            stop_loss_price = price * (1 - stop_loss)
            take_profit_price = price * (1 + take_profit)

        elif row['Signal'] == 'No Buy':
            if positions == 0:
                continue # Si aucune position n'est ouverte, ne rien faire
            
            # Calculer le prix de vente en fonction du prix d'ouverture du jour suivant
            if (index + 1) >= len(df):
                # Si l'indice dépasse la plage d'indices du DataFrame, continuer à la ligne suivante
                continue
            price = df.loc[index+1, 'Open']

            # Mettre en place les ordres de vente
            realized_pnl += positions * (price - last_price)
            cash += positions * price
            positions = 0

            # Vérifier les niveaux de stop loss et de take profit
            if price <= stop_loss_price or price >= take_profit_price:
                realized_pnl += cash
                cash = initial_capital

        last_price = price

    # Calculer le bénéfice ou la perte réalisé
    total_pnl = realized_pnl + cash - initial_capital

    return total_pnl
