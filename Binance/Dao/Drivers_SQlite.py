import sqlite3
from datetime import datetime
import pandas as pd

class Drivers_SQLite:
    """
        Class Drivers_SQLite : 
        Rôle : permet de gérer / interroger la base SQLite

        Paramétres : 
        
        Méthodes : 
    """

    def __init__(self, PathDataBase) :
        self.ClientSQLite = sqlite3.connect(PathDataBase)
        with open('C:/Users/wari/Documents/Projet_OPA/Projet_OPA/Binance/Dao/Create_DBSQLITE_OPA.sql', 'r') as f:
        # Read the contents of the file
            sql = f.read()
        # Execute the SQL commands
            self.ClientSQLite.executescript(sql)

# Commit the changes and close the connection
        self.ClientSQLite.commit()
        self.DBSQLite = self.ClientSQLite.cursor()

    def CloseConnection(self):
        self.ClientSQLite.close()

    def Commit(self):
        self.ClientSQLite.commit()

    def ISValid_SQL(self, SQL :str):
        return(sqlite3.complete_statement(SQL))

    def Select(self, SQL : str, Params = ()):
        if self.ISValid_SQL(SQL) == True:
            self.DBSQLite.execute(SQL, Params)
        else : 
            self.DBSQLite.execute("SELECT NULL")
        
        return self.DBSQLite.fetchall()

    def InsertMany(self, SQL:str, Data):
        self.DBSQLite.executemany(SQL, Data)

    
    def Alim_DimTemps(self,Data):
        L_Nombre_Lignes = Data.shape[0]
        Data[["ID_TEMPS","JOUR","MOIS","ANNEE","HEURE","MINUTES","SECONDES","DATE_CREATION"]].to_sql('DIM_TEMPS', self.ClientSQLite,if_exists='replace', index=False)
        self.Commit()
        return L_Nombre_Lignes
    
    def Alim_DimSymbol(self,L_Liste_Symbole):
        #insert data into the table
        L_Compteur=0
        for symbol_data in L_Liste_Symbole:
            NOM_SYMBOL = symbol_data['symbol']
            BASE_ASSET = symbol_data['baseAsset']
            QUOTE_ASSET=symbol_data['quoteAsset']
            DATE_CREATION=datetime.now().strftime('%d/%m/%Y')
            self.DBSQLite.execute("INSERT INTO DIM_SYMBOL(NOM_SYMBOL,BASE_ASSET,QUOTE_ASSET,DATE_CREATION) \
SELECT ?,?,?,? \
WHERE NOT EXISTS (SELECT 1 FROM DIM_SYMBOL \
WHERE NOM_SYMBOL=? AND BASE_ASSET=? AND QUOTE_ASSET=?)",
(NOM_SYMBOL, BASE_ASSET, QUOTE_ASSET, DATE_CREATION, NOM_SYMBOL, BASE_ASSET, QUOTE_ASSET))
            self.Commit()
            L_Compteur+=1
            self.Commit()
        return L_Compteur

    def Alim_FaitSituation_Histo(self, L_DataFrame,L_Symbole):
        dim_symbol = pd.read_sql_query("SELECT * FROM DIM_SYMBOL where NOM_SYMBOL = '{}'".format(L_Symbole) , self.ClientSQLite)
    #ajout de la ligne qui correspond a l'id de la Paire 
        for i, row in L_DataFrame.iterrows():
            L_DataFrame.at[i, 'ID_SYMBOL'] = dim_symbol['ID_SYMBOL'][0]
    # Insertion des données combinées dans la table cible
        L_DataFrame['ID_TEMPS']=L_DataFrame['Open_time']
        L_DataFrame["VALEUR_COURS"]=L_DataFrame["Close"]
        L_DataFrame["IND_QUOTEVOLUME"]=L_DataFrame["Quote_asset_volume"]
        L_DataFrame['DATE_CREATION'] = L_DataFrame["Open_time"].apply(lambda x: datetime.fromtimestamp(x/1000))
        L_DataFrame['DATE_CREATION'] = L_DataFrame['DATE_CREATION'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S"))
        L_DataFrame[["ID_TEMPS","ID_SYMBOL","VALEUR_COURS","IND_SMA_20","IND_SMA_30","IND_QUOTEVOLUME","IND_STOCH_RSI","IND_CHANGEPERCENT","IND_RSI","IND_TRIX","DATE_CREATION"]].to_sql('FAIT_SIT_COURS_HIST', self.ClientSQLite, if_exists='append', index=False)
        self.Commit()
        return 'nombre de lignes insérées'