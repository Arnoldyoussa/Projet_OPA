import sqlite3
import os
import pandas as pd

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

        L = [{'ID_TEMPS' : i, 'VAL' : 0} for (i,) in res]
        df = pd.DataFrame(L, columns = ['ID_TEMPS', 'VAL'], dtype='int64')

        Data = Data.merge(df, on ='ID_TEMPS', how = 'left')
        Data = Data.drop(Data[Data['VAL'] == 0].index)
        Data = Data.drop(columns = 'VAL')

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

        L = [{'ID_TEMPS' : i, 'ID_SYMBOL' :j ,'VAL' : 0} for (i,j) in res]
        df = pd.DataFrame(L, columns = ['ID_TEMPS', 'ID_SYMBOL', 'VAL'], dtype='int64')

        FaiCoursHisto = FaiCoursHisto.merge(df, on =['ID_TEMPS','ID_SYMBOL'], how = 'left')
        FaiCoursHisto = FaiCoursHisto.drop(FaiCoursHisto[FaiCoursHisto['VAL'] == 0].index)
        FaiCoursHisto = FaiCoursHisto.drop(columns = 'VAL')

        self.InsertMany('INSERT INTO FAIT_SIT_COURS_HIST VALUES (null, ?, ?, ?, ?,?,?,?,?,?,? , current_date );', FaiCoursHisto.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes
    
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

        L = [{'ID_TEMPS' : i, 'ID_SYMBOL' :j ,'VAL' : 0} for (i,j) in res]
        df = pd.DataFrame(L, columns = ['ID_TEMPS', 'ID_SYMBOL', 'VAL'], dtype='int64')

        FaitCours = FaitCours.merge(df, on =['ID_TEMPS','ID_SYMBOL'], how = 'left')
        FaitCours = FaitCours.drop(FaitCours[FaitCours['VAL'] == 0].index)
        FaitCours = FaitCours.drop(columns = 'VAL')

        self.InsertMany('INSERT INTO FAIT_SIT_COURS VALUES (null, ?, ?, ?, ?,?,?,?,?,?,? , current_date );', FaitCours.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes
    
    
    