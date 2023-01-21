import sqlite3

class Drivers_SQLite:
    """
        Class Drivers_SQLite : 
        Rôle : permet de gérer / interroger la base SQLite

        Paramétres : 
        
        Méthodes : 
    """

    def __init__(self, PathDataBase) :
        self.ClientSQLite = sqlite3.connect(PathDataBase)
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

    
    def Alim_DimTemps(self, SQL : str, Data):
        return 'nombre de lignes insérées'
    
    def Alim_DimSymbol(self, SQL : str, Data):
        return 'nombre de lignes insérées'

    def Alim_FaitSituation_Histo(self, SQL : str, Data):
        return 'nombre de lignes insérées'