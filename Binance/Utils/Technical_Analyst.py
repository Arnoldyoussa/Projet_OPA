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