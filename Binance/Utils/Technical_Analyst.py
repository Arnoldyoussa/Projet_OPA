import pandas as pd
import numpy as np
import datetime

def calculate_trix(L_DataFrame, n=15):
    """
    Calcule l'indicateur TRIX pour un dataframe de données de cours.
    """
    # Calcul de la moyenne mobile exponentielle sur n périodes
    ema1 = L_DataFrame.ewm(span=n, adjust=False).mean()
    # Calcul de la moyenne mobile exponentielle sur n périodes de la première moyenne mobile exponentielle
    ema2 = ema1.ewm(span=n, adjust=False).mean()
    # Calcul de la moyenne mobile exponentielle sur n périodes de la deuxième moyenne mobile exponentielle
    ema3 = ema2.ewm(span=n, adjust=False).mean()
    # Calcul de l'indicateur TRIX comme la différence entre la troisième moyenne mobile exponentielle et sa moyenne mobile exponentielle sur n périodes
    trix = ema3.diff(n)
    return trix

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