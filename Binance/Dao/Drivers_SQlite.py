import sqlite3
import os
import pandas as pd

class Drivers_SQLite:
 

    def __init__(self, PathDataBase) :
        self.PathDB = PathDataBase

        # Vérification de l'existence de la base de données
        if not os.path.exists(self.PathDB):
            # Création de la base de données en utilisant le fichier "Create_DBSQLITE_OPA.sql"
            path_create_table = "Binance\Dao\Create_DBSQLITE_OPA.sql"
            if os.path.exists(path_create_table):
                f = open(path_create_table, "r")
                cmdSQL = f.read()
                f.close()
                self.ClientSQLite = sqlite3.connect(self.PathDB)
                self.DBSQLite = self.ClientSQLite.cursor()
                self.DBSQLite.executescript(cmdSQL)
                self.Commit()
            else:
                raise Exception(f"Le fichier '{path_create_table}' pour créer la base de données n'existe pas.")
        else:
            # Connexion à la base de données existante
            self.ClientSQLite = sqlite3.connect(self.PathDB)
            self.DBSQLite = self.ClientSQLite.cursor()


    def Re_InitDB(self, PathCreateTable ):
        self.CloseConnection()

        if os.path.exists(PathCreateTable):

            if os.path.exists(self.PathDB):
                os.remove(self.PathDB)

            f = open(PathCreateTable, "r")
            cmdSQL = f.read()
            f.close()
            #print(cmdSQL)
            self.ClientSQLite = sqlite3.connect(self.PathDB)
            self.DBSQLite = self.ClientSQLite.cursor()
            self.DBSQLite.executescript(cmdSQL)
            self.Commit()


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

 


    def Alim_FaitSituation_Histo(self, FaiCoursHisto):
        self.InsertMany('INSERT OR REPLACE INTO FAIT_SIT_COURS_HIST (OPEN_TIME, SYMBOL, INTERVALLE, OPEN_VALUE,CLOSE_VALUE, IND_SMA_20, IND_SMA_30, IND_QUOTEVOLUME, IND_CHANGEPERCENT, IND_STOCH_RSI, IND_RSI, IND_TRIX, IND_TRIX_HISTO, IND_EMA, DATE_CREATION) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, date(\'now\'))', FaiCoursHisto.values.tolist())
        self.Commit()
        
        return self.ClientSQLite.total_changes