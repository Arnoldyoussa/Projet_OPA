import sqlite3
import os
import time

class Drivers_SQLite:
    """
        Class Drivers_SQLite : 
        Rôle : permet de gérer / interroger la base SQLite

        Paramétres : 
        
        Méthodes : 
    """
    #--
    def __init__(self, PathDataBase) :
        self.PathDB = PathDataBase
        self.ClientSQLite = sqlite3.connect(PathDataBase)
        self.DBSQLite = self.ClientSQLite.cursor()

    #--
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

    #--
    def CloseConnection(self):
        self.ClientSQLite.close()

    #--
    def Commit(self):
        self.ClientSQLite.commit()

    #--
    def ISValid_SQL(self, SQL :str):
        return(sqlite3.complete_statement(SQL))

    #--
    def Select(self, SQL : str, Params = ()):
        if self.ISValid_SQL(SQL) == True:
            self.DBSQLite.execute(SQL, Params)
        else : 
            self.DBSQLite.execute("SELECT NULL")
        
        return self.DBSQLite.fetchall()

    #--
    def InsertMany(self, SQL:str, Data):
        self.DBSQLite.executemany(SQL, Data)   

    #--
    def Execute(self, CMDSQL):
        self.DBSQLite.execute(CMDSQL)
        self.Commit()
        return self.ClientSQLite.total_changes

    #--
    def Alim_DimTemps(self, Data):
        res = self.Select('select ID_TEMPS from DIM_TEMPS;')

        for i in res:
            (a,) = i
            Data = Data.drop(index = Data[Data['ID_TEMPS'] == a].index)

        self.InsertMany('INSERT INTO DIM_TEMPS VALUES (?,?, ?, ?, ?, ? ,?,?, current_date );', Data.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes
    


    #--
    def Alim_DimSymbol(self, Data):
        res = self.Select('select NOM_SYMBOL, INTERVALLE from DIM_SYMBOL;')

        for i in res:
            (a,b) = i
            Data = Data.drop(index = Data[(Data['NOM_SYMBOL'] == a) & (Data['INTERVALLE'] == b)].index)

        self.InsertMany('INSERT INTO DIM_SYMBOL VALUES (null, ?, ?, ?, ? , current_date );', Data.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes

    #--
    def Alim_FaitSituation_Histo(self, FaiCoursHisto):
        res = self.Select('select ID_TEMPS, ID_SYMBOL from FAIT_SIT_COURS_HIST;')

        for i in res:
            (a,b) = i
            FaiCoursHisto = FaiCoursHisto.drop(index = FaiCoursHisto[(FaiCoursHisto['ID_TEMPS'] == a) & (FaiCoursHisto['ID_SYMBOL'] == b)].index)

        self.InsertMany('INSERT INTO FAIT_SIT_COURS_HIST VALUES (null, ?, ?, ?, ?,?,?,?,?,?,? , current_date );', FaiCoursHisto.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes
    

    def Alim_DimTemps_Optimise(self, Data):
        try:
            start = time.time()

            data_values = Data.values.tolist()

            # Insertion par lots
            batch_size = 1000
            for i in range(0, len(data_values), batch_size):
                batch = data_values[i:i + batch_size]
                
                # Insertion uniquement des lignes qui n'existent pas déjà
                self.ClientSQLite.executemany("""
                    INSERT INTO DIM_TEMPS (ID_TEMPS, DATE_TEMPS, SECONDES, MINUTES, HEURE, JOUR, MOIS, ANNEE, DATE_CREATION)
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, current_date
                    WHERE NOT EXISTS (
                        SELECT 1 FROM DIM_TEMPS WHERE ID_TEMPS = ?
                    )
                    """, [(val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7], val[0]) for val in batch])

            self.Commit()

            end = time.time()

            print("Alim_DimTemps_Optimise took", end - start, "seconds.")

            return self.ClientSQLite.total_changes

        except Exception as e:
            print("An error occurred in Alim_DimTemps_Optimise: ", e)

    def clean_duplicates(self):
        # Démarrer une transaction
        self.ClientSQLite.execute("BEGIN TRANSACTION")

        # Supprimer les doublons basés sur les clés primaires
        self.ClientSQLite.execute("""
            DELETE FROM FAIT_SIT_COURS_HIST
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM FAIT_SIT_COURS_HIST
                GROUP BY ID_TEMPS, ID_SYMBOL
            )
            """)

        # Valider la transaction
        self.ClientSQLite.execute("COMMIT")




    def Alim_FaitSituation_Histo_Optimise(self, FaiCoursHisto):
        try:
            start = time.time()

            data_values = FaiCoursHisto.values.tolist()

            # Insertion par lots
            batch_size = 1000
            for i in range(0, len(data_values), batch_size):
                batch = data_values[i:i + batch_size]
                
                # Insertion ou remplacement des lignes existantes
                self.ClientSQLite.executemany("""
                    INSERT OR REPLACE INTO FAIT_SIT_COURS_HIST (ID_TEMPS, ID_SYMBOL, VALEUR_COURS, IND_SMA_20, IND_SMA_30, IND_QUOTEVOLUME, IND_CHANGEPERCENT, IND_STOCH_RSI, IND_RSI, IND_TRIX, DATE_CREATION)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, current_date)
                    """, [(val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7], val[8], val[9]) for val in batch])

            self.Commit()
            self.clean_duplicates()
            end = time.time()
            
            print("Alim_FaitSituation_Histo_Optimise took", end - start, "seconds.")

            return self.ClientSQLite.total_changes

        except Exception as e:
            print("An error occurred in Alim_FaitSituation_Histo_Optimise: ", e)




    #--
    def Alim_FaitDecision_Histo(self, FaitDec):
        
        self.InsertMany('REPLACE INTO FAIT_DEC_ML_CLASS (ID_SIT_CRS_HIS, ID_MLCLAS, IND_DEC) VALUES (?,?,? );', FaitDec.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes

    #--
    def Alim_FaitPrediction(self, FaitPred):
                
        self.InsertMany('REPLACE INTO FAIT_PREDICTION (ID_SIT_CRS , ID_MLCLAS , IND_PRED) VALUES (?,?,? );', FaitPred.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes
    
    #--
    def Alim_FaitSituation(self, FaitCours):
        res = self.Select('select ID_TEMPS, ID_SYMBOL from FAIT_SIT_COURS;')

        for i in res:
            (a,b) = i
            FaitCours = FaitCours.drop(index = FaitCours[(FaitCours['ID_TEMPS'] == a) & (FaitCours['ID_SYMBOL'] == b)].index)

        self.InsertMany('INSERT INTO FAIT_SIT_COURS VALUES (null, ?, ?, ?, ?,?,?,?,?,?,? , current_date );', FaitCours.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes
    
    
    