import sqlite3
import os

class Drivers_SQLite:
    """
        Class Drivers_SQLite : 
        Rôle : permet de gérer / interroger la base SQLite

        Paramétres : 
        
        Méthodes : 
    """

    def __init__(self, PathDataBase) :
        self.PathDB = PathDataBase
        self.ClientSQLite = sqlite3.connect(PathDataBase)
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

    
    def Alim_DimTemps(self, Data):
        res = self.Select('select ID_TEMPS from DIM_TEMPS;')

        for i in res:
            (a,) = i
            Data = Data.drop(index = Data[Data['ID_TEMPS'] == a].index)

        self.InsertMany('INSERT INTO DIM_TEMPS VALUES (?, ?, ?, ?, ? ,?,?, current_date );', Data.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes
    
    def Alim_DimSymbol(self, Data):
        res = self.Select('select NOM_SYMBOL, INTERVALLE from DIM_SYMBOL;')

        for i in res:
            (a,b) = i
            Data = Data.drop(index = Data[(Data['NOM_SYMBOL'] == a) & (Data['INTERVALLE'] == b)].index)

        self.InsertMany('INSERT INTO DIM_SYMBOL VALUES (null, ?, ?, ?, ? , current_date );', Data.values.tolist())
        self.Commit()

        return self.ClientSQLite.total_changes

    def Alim_FaitSituation_Histo(self, FaiCoursHisto):
        res = self.Select('select ID_TEMPS, ID_SYMBOL from FAIT_SIT_COURS_HIST;')

        for i in res:
            (a,b) = i
            FaiCoursHisto = FaiCoursHisto.drop(index = FaiCoursHisto[(FaiCoursHisto['ID_TEMPS'] == a) & (FaiCoursHisto['ID_SYMBOL'] == b)].index)

        self.InsertMany('INSERT INTO FAIT_SIT_COURS_HIST VALUES (null, ?, ?, ?, ?,?,?,?,?,?,? , current_date );', FaiCoursHisto.values.tolist())
        self.Commit()
        
        return self.ClientSQLite.total_changes