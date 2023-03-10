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

        
        if not os.path.exists(PathDataBase):
            # Database does not exist, create it
            script_path = os.path.join(os.path.dirname(__file__), "Create_DBSQLITE_OPA.sql")
            with open(script_path) as f:
                create_query = f.read()
            conn = sqlite3.connect(PathDataBase)
            cursor = conn.cursor()
            cursor.executescript(create_query)
            conn.commit()
            cursor.close()
            conn.close()
            print("Database created successfully!")
        else:
            print("Database already exists.")

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

        self.InsertMany('INSERT INTO FAIT_SIT_COURS_HIST VALUES (null, ?, ?, ?, ?,?,?,?,?,?,?,? , current_date );', FaiCoursHisto.values.tolist())
        self.Commit()

        self.Alim_FaitDecision_Histo()

        return self.ClientSQLite.total_changes

    def Alim_FaitDecision_Histo(self):
        sql_cript = """
        REPLACE INTO FAIT_DEC_ML_CLASS (ID_SIT_CRS_HIS, ID_MLCLAS, IND_DEC)
            SELECT 
            ID_SIT_CRS_HIS,
            ID_MLCLAS,
            CASE 
            WHEN ID_MLCLAS = 3 AND VALEUR_COURS <= MIN_JR AND MAX_JR >= (MOY_SEM + MAX_JR)/2   THEN 1 /* Décision ACHAT */
            WHEN ID_MLCLAS = 4 AND VALEUR_COURS >= MAX_JR AND MAX_JR >= (MOY_SEM + MAX_JR)/2   THEN 1 /* Décision VENTE */
            ELSE 0
            END as IND_DEC
            FROM 
            (
                select 
                ID_SIT_CRS_HIS,
                PER_JR,
                A.VALEUR_COURS,
                MAX(A.VALEUR_COURS) OVER (PARTITION BY ID_SYMBOL, PER_JR) as MAX_JR,
                MIN(A.VALEUR_COURS) OVER (PARTITION BY ID_SYMBOL, PER_JR) as MIN_JR,
                AVG(A.VALEUR_COURS) OVER (PARTITION BY ID_SYMBOL, PER_SEMAINE) as MOY_SEM
                from FAIT_SIT_COURS_HIST A
                inner join (select ID_TEMPS, 
                ANNEE||substr('00' || MOIS, -2, 2)||substr('00' || JOUR, -2, 2) as PER_JR, 
                ANNEE||strftime('%W',ANNEE||'-'||substr('00' || MOIS, -2, 2)||'-'||substr('00' || JOUR, -2, 2))   as PER_SEMAINE
                from DIM_TEMPS) B ON (A.ID_TEMPS = B.ID_TEMPS)
            )
            cross join ( select ID_MLCLAS from DIM_ML_CLAS  where ID_MLCLAS in (3,4))
            EXCEPT
            SELECT ID_SIT_CRS_HIS, ID_MLCLAS, IND_DEC  from FAIT_DEC_ML_CLASS
        """
        self.DBSQLite.execute(sql_cript)
        self.Commit()
        return self.ClientSQLite.total_changes