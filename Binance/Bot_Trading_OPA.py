from Binance.Data import Binance_Histo as Histo
from Binance.Data import Binance_Live as live
from Binance.Dao import Drivers_MongoDB as DAO_MB
from Binance.Dao import Drivers_SQlite as DAO_SQL
from Binance.Utils import Utilitaire as util
from Binance.Utils import Technical_Analyst as util_TA
from Binance.Utils import ML_Classification as ML

import pandas as pd
import sys
import datetime

# Paramétrage Générique
PathDatabase = 'test.db'
PathCreateTable = 'Binance/Dao/Create_DBSQLITE_OPA.sql'

Host_DBMongo = 'localhost' 
Port_DBMongo = 27017
Nom_DBMongo  = 'OPA'

"""
########################################################################
#############Bloc 1 : Reinitialisation DataBase ########################
########################################################################
"""

# -->
def Reset_DB_All():
    """
        Cette Fonction réinitialise les Bases Mongo & SQLlite
    """
    try:
        # Step 1 : suppression de la base SQLlite
        print('Step 1 : suppression de la base SQLlite')
        DB_SQL = DAO_SQL.Drivers_SQLite(PathDatabase)
        DB_SQL.Re_InitDB(PathCreateTable)
        DB_SQL.CloseConnection()

        # Step 2 : suppression des Collections Mongo
        print('Step 2 : suppression des Collections  dans la Base Mongo')
        DB_MB = DAO_MB.Drivers_MongoDB(Host = Host_DBMongo, Port = Port_DBMongo, NomDB = Nom_DBMongo)
        DB_MB.DeleteCollection(DB_MB.get_AllCollection())

    except:
        return "KO"
    
    return "OK"

# -->
def Reset_DB_Live():

    try:
        DB_SQL = DAO_SQL.Drivers_SQLite(PathDatabase)
        
        # --
        print('Suppression des Tables SQL Live')
        DB_SQL.Execute("""DELETE FROM FAIT_PREDICTION;""")
        DB_SQL.Execute("""DELETE FROM FAIT_SIT_COURS;""")

        # -- 
        DB_SQL.CloseConnection()
    
    except : 
        return "KO"
    
    return "OK"

"""
########################################################################
#############Bloc 2 :  Chargement Database #############################
########################################################################
"""

# --> Base Mongo
def Load_DB_Mongo(ListePaire : list, Periode_Debut, Periode_Fin):
    """
        Cette Fonction charge la base Mongo à partir des Fichiers Historiques
    """
    try:
          
        L_Symbol = ListePaire

        # Téléchargement des Fichiers à charger
        DataHisto = Histo.Binance_Histo(L_Symbol, ['1h'], DateDebut = Periode_Debut, DateFin = Periode_Fin)
        DataHisto.TelechargeFichier()
        print('Téléchargement des Fichiers à charger')

        #Chargement Base Mongo
        L = list()
    
        for NomFichier in DataHisto.L_Fichier:
            L.append(NomFichier['Nom'])
            
        DB_MB = DAO_MB.Drivers_MongoDB(L,Host = Host_DBMongo, Port = Port_DBMongo, NomDB = Nom_DBMongo)
        DB_MB.ChargeFichiers()
        print('Chargement Base MongoDB')

        #Suppression fichiers Chargés
        DataHisto.SupprimeFichier()

    except:
         return "KO"
        
    return "OK"

# --> Base SQL Histo
def Load_DB_SQL_Histo(ListePaire : list, Periode_Debut, Periode_Fin) :
    """
        Cette Fonction charge la base SQLite à partir de la base Mongo
    """
    try:
        L_Symbol = ListePaire

        # Connection aux Bases
        DB_SQL = DAO_SQL.Drivers_SQLite(PathDatabase)
        DB_MB = DAO_MB.Drivers_MongoDB(Host = Host_DBMongo, Port = Port_DBMongo, NomDB = Nom_DBMongo)
        DataLive = live.Binance_Live()

        print('Connexion aux DataBases')

        # Step 1 : Récupération des info Temps / Symbols / Cours
        
        # --
        L_TEMPS = list()
        L_SYMBOLS = list()
        L_INFOSYMBOLS = list()
        L_COURS= list()

        # --
        for Paire in L_Symbol:
            Liste_Temps = list(DB_MB.DBMongo[Paire].find({}, { 'Detail.Close_time': 1}))
            Liste_Symboles = list(DB_MB.DBMongo[Paire].find({}, {"Symbol" : 1, "Intervalle" : 1, "_id" : 0}))
            Liste_Cours = list(DB_MB.DBMongo[Paire].find({}))

            # --
            for i in Liste_Temps :
                for y in i['Detail']:
                    if y['Close_time'] not in L_TEMPS:
                        L_TEMPS.append(y['Close_time'])

            # --
            for i in Liste_Symboles:
                a = {"NOM_SYMBOL" : i['Symbol'], "INTERVALLE" : i['Intervalle']} 
                if a not in L_SYMBOLS:
                    L_SYMBOLS.append(a)

            # --
            Info_symbol = DataLive.exchange_info(Paire)
            i = {'NOM_SYMBOL' : Info_symbol['symbols'][0]['symbol'],
                                    'BaseAsset' : Info_symbol['symbols'][0]['baseAsset'],
                                    'QuoteAsset' : Info_symbol['symbols'][0]['quoteAsset']}
            if i not in L_INFOSYMBOLS:
                    L_INFOSYMBOLS.append(i)

            # --
            for doc in Liste_Cours:
                for detail in doc['Detail']:
                    L_COURS.append({'ID_TEMPS' :detail['Close_time'], 
                            'NOM_SYMBOL' : doc['Symbol'], 
                            'INTERVALLE' : doc['Intervalle'], 
                            'VALEUR_COURS' : detail['Close'] ,
                            'IND_QUOTEVOLUME' : detail['Quote_asset_volume'] 
                            })

        # Step 2 : Transformation des Données puis Stockage en Base

        # --
        DimTemps = pd.DataFrame(L_TEMPS, columns = ['ID_TEMPS'] , dtype='int64')
        DimTemps['DATE_TEMPS'] =  DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp)
        DimTemps['SECONDES'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('ss'))
        DimTemps['MINUTES'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('mm'))
        DimTemps['HEURE'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('HH'))
        DimTemps['JOUR'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('DD'))
        DimTemps['MOIS'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('MM'))
        DimTemps['ANNEE'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('YYYY'))
        
        DB_SQL.Alim_DimTemps(DimTemps)
        print('Chargement Dimension Temps')

        # --
        DimSymbol = pd.DataFrame(L_SYMBOLS)
        df = pd.DataFrame(L_INFOSYMBOLS)
        DimSymbol = DimSymbol.merge(df, on = 'NOM_SYMBOL' )
        
        DB_SQL.Alim_DimSymbol(DimSymbol)
        print('Chargement Dimension Symbol')

        # --
        FaiCoursHisto = pd.DataFrame(L_COURS)
        FaiCoursHisto['ID_TEMPS'] = FaiCoursHisto['ID_TEMPS'].astype('int64')
        FaiCoursHisto['IND_QUOTEVOLUME'] = FaiCoursHisto['IND_QUOTEVOLUME'].astype(int)


        L = list()
        res = DB_SQL.Select('select ID_SYMBOL,NOM_SYMBOL,INTERVALLE  from DIM_SYMBOL;')
        for i in res:
            (a,b,c) = i
            L.append({'ID_SYMBOL' : a, 'NOM_SYMBOL' : b, 'INTERVALLE' : c})
        df = pd.DataFrame(L)

        FaiCoursHisto = FaiCoursHisto.merge(df, how = 'inner')

        FaiCoursHisto['IND_SMA_20'] = util_TA.Calculer_SMA(FaiCoursHisto['VALEUR_COURS'], 20)
        FaiCoursHisto['IND_SMA_30'] = util_TA.Calculer_SMA(FaiCoursHisto['VALEUR_COURS'], 30)
        FaiCoursHisto['IND_CHANGEPERCENT'] = util_TA.Calculer_Change_Percent(FaiCoursHisto['VALEUR_COURS'])
        FaiCoursHisto['IND_STOCH_RSI'] = util_TA.Calculer_RSI_Stochastique(FaiCoursHisto['VALEUR_COURS'])
        FaiCoursHisto['IND_RSI'] =  util_TA.Calculer_RSI(FaiCoursHisto['VALEUR_COURS'])
        FaiCoursHisto['IND_TRIX'] = util_TA.calculate_trix(FaiCoursHisto['VALEUR_COURS'])

        FaiCoursHisto = FaiCoursHisto[['ID_TEMPS',  'ID_SYMBOL','VALEUR_COURS', 'IND_SMA_20', 'IND_SMA_30', 'IND_QUOTEVOLUME', 'IND_CHANGEPERCENT', 'IND_STOCH_RSI', 'IND_RSI', 'IND_TRIX']]
        
        DB_SQL.Alim_FaitSituation_Histo(FaiCoursHisto)  
        print('Chargement Fait Cours Historique')      

        # Step 3 : Apprentissage Décision Achat / Vente Méthode 1
        
        # --
        df_temp= Get_DataPaire(ListePaire, Periode_Debut, Periode_Fin, 'M1')
        Alim_Data_M1(df_temp, 'H')

        # Step 4 : Apprentissage Décision Achat / Vente Méthode 2
        sql_cript = """
        REPLACE INTO FAIT_DEC_ML_CLASS (ID_SIT_CRS_HIS, ID_MLCLAS, IND_DEC)
            SELECT 
            A.ID_SIT_CRS_HIS,
            ID_MLCLAS,
            CASE 
                WHEN ID_MLCLAS = 3 AND A.VALEUR_COURS <= MIN_JR    THEN 1 /* Décision ACHAT */
                WHEN ID_MLCLAS = 4 AND A.VALEUR_COURS >= MAX_JR    THEN 1 /* Décision VENTE */
                ELSE 0
            END as IND_DEC
            FROM 
            (
                select 
                ID_SIT_CRS_HIS,
                PER_JR,
                A.VALEUR_COURS,
                MAX(A.VALEUR_COURS) OVER (PARTITION BY ID_SYMBOL, PER_JR) as MAX_JR,
                MIN(A.VALEUR_COURS) OVER (PARTITION BY ID_SYMBOL, PER_JR) as MIN_JR
                from FAIT_SIT_COURS_HIST A
                inner join (select ID_TEMPS, 
                ANNEE||MOIS||JOUR as PER_JR, 
                ANNEE||strftime('%W',ANNEE||MOIS||JOUR)   as PER_SEMAINE
                from DIM_TEMPS) B ON (A.ID_TEMPS = B.ID_TEMPS)
            ) A
            cross join ( select ID_MLCLAS from DIM_ML_CLAS  where ID_MLCLAS in (3,4)) B
            EXCEPT
            SELECT ID_SIT_CRS_HIS, ID_MLCLAS, IND_DEC  from FAIT_DEC_ML_CLASS
        """
        DB_SQL.Execute(sql_cript)
        print('Chargement Decision Histo Achat Vente M2')

        # Fin Connection
        DB_SQL.CloseConnection()

    except:
        return "KO"
    
    return "OK"

# --> Base SQL Live
def Load_DB_SQL_Live(ListePaire : list, Periode_Debut = None, Periode_Fin = datetime.date.today().isoformat()):
    """
    Cette fonction charge en temps réel les données Paires présentes dans la base Historique
    """
    try:
        #Connexion
        DataLive = live.Binance_Live()
        DB_SQL = DAO_SQL.Drivers_SQLite(PathDatabase)
        L_Symbol = ListePaire

        # Step 1 : Pour chaque Paire, on alimente la base SQL Live
        
        # --
        if Periode_Debut is None:
            today = datetime.datetime.now()
            DebutMois = str(today.year)+ "-" +str(today.month).rjust(2,'0') + "-01"        
        else :
            DebutMois = Periode_Debut
        
        # --
        for symbol in L_Symbol:
            # --
            df = Get_Live_InfoPaire(symbol, Periode_Debut = DebutMois, Periode_Fin = Periode_Fin )

            # --
            DimTemps = pd.DataFrame(df)
            DimTemps['ID_TEMPS'] = DimTemps['CloseTime']
            DimTemps = pd.DataFrame(DimTemps['ID_TEMPS'])
            
            DimTemps['DATE_TEMPS'] =  DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp)
            DimTemps['SECONDES'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('ss'))
            DimTemps['MINUTES'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('mm'))
            DimTemps['HEURE'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('HH'))
            DimTemps['JOUR'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('DD'))
            DimTemps['MOIS'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('MM'))
            DimTemps['ANNEE'] = DimTemps['ID_TEMPS'].apply(util.Convertir_Timestamp, formatDate=('YYYY'))
            
            DB_SQL.Alim_DimTemps(DimTemps)
            print('Chargement Dimension Temps')
            
            # --
            Info_symbol = DataLive.exchange_info(symbol)
            i = {'NOM_SYMBOL' : Info_symbol['symbols'][0]['symbol'],
                 "INTERVALLE" : df['INTERVALLE'].unique()[0],
                 'BaseAsset' : Info_symbol['symbols'][0]['baseAsset'],
                 'QuoteAsset' : Info_symbol['symbols'][0]['quoteAsset']
                }
            DimSymbol = pd.DataFrame([i])
            DB_SQL.Alim_DimSymbol(DimSymbol)

            print('Chargement Dimension Symbol')

            # --
            L = list()
            res = DB_SQL.Select('select ID_SYMBOL,NOM_SYMBOL,INTERVALLE  from DIM_SYMBOL;')
            for i in res:
                (a,b,c) = i
                L.append({'ID_SYMBOL' : a, 'NOM_SYMBOL' : b, 'INTERVALLE' : c})
            DimSymbol = pd.DataFrame(L)

            FaitCours = pd.DataFrame(df)
            FaitCours = FaitCours.merge(DimSymbol, how = 'inner')

            FaitCours['ID_TEMPS'] = FaitCours['CloseTime'].astype('int64')
            FaitCours['VALEUR_COURS'] = FaitCours['ClosePrice'].astype(float)
            FaitCours['IND_QUOTEVOLUME'] = FaitCours['QuoteAssetVolume'].astype(float)

            FaitCours['IND_SMA_20'] = util_TA.Calculer_SMA(FaitCours['VALEUR_COURS'], 20)
            FaitCours['IND_SMA_30'] = util_TA.Calculer_SMA(FaitCours['VALEUR_COURS'], 30)

            FaitCours['IND_CHANGEPERCENT'] = util_TA.Calculer_Change_Percent(FaitCours['VALEUR_COURS'])
            FaitCours['IND_STOCH_RSI'] = util_TA.Calculer_RSI_Stochastique(FaitCours['VALEUR_COURS'])
            FaitCours['IND_RSI'] =  util_TA.Calculer_RSI(FaitCours['VALEUR_COURS'])
            FaitCours['IND_TRIX'] = util_TA.calculate_trix(FaitCours['VALEUR_COURS'])
            
            FaitCours = FaitCours[['ID_TEMPS',  'ID_SYMBOL','VALEUR_COURS', 'IND_SMA_20', 'IND_SMA_30', 'IND_QUOTEVOLUME', 'IND_CHANGEPERCENT', 'IND_STOCH_RSI', 'IND_RSI', 'IND_TRIX']]
            
            DB_SQL.Alim_FaitSituation(FaitCours) 
            print('Chargement Fait Cours')

        # -- 
        DB_SQL.CloseConnection()

    except:
        return "KO"
    
    return "OK"

# --> Base SQL Live Prediction
def Load_DB_SQLPrediction(Paire, MethodeCalcul, Periode_Debut = None, Periode_Fin = None, LimiteML = 50000):

    def max_df(df, id_temps, decision):
        df_2 = df[( (df['DEC_VENTE'] == 1) | (df['DEC_ACHAT'] == 1)) & ( df['ID_TEMPS'] < id_temps) ][['ID_TEMPS','DEC_ACHAT', 'DEC_VENTE']]
        return df_2.iloc[df_2.shape[0] - 1][decision]

    try:
        DB_SQL = DAO_SQL.Drivers_SQLite(PathDatabase)

        if MethodeCalcul == "M2":

            # Step 1 : Phase Entrainement sur les N derniers cours
            sql_train = """
                select A.ID_SIT_CRS_HIS, 
                    IND_STOCH_RSI,
                    IND_RSI,
                    IND_TRIX,
                    B_A.IND_DEC, 
                    B_V.IND_DEC,
                    A.ID_TEMPS,
                    A.VALEUR_COURS
                from FAIT_SIT_COURS_HIST A
                inner join FAIT_DEC_ML_CLASS B_A ON (B_A.ID_SIT_CRS_HIS = A.ID_SIT_CRS_HIS and B_A.ID_MLCLAS = 3)
                inner join FAIT_DEC_ML_CLASS B_V ON (B_V.ID_SIT_CRS_HIS = A.ID_SIT_CRS_HIS and B_V.ID_MLCLAS = 4)
                inner join DIM_TEMPS C ON (C.ID_TEMPS = A.ID_TEMPS)
                inner join DIM_SYMBOL D ON (D.ID_SYMBOL = A.ID_SYMBOL)
                inner join ( SELECT MIN(ID_TEMPS) as Id_TEMPS FROM FAIT_SIT_COURS A
						inner join DIM_SYMBOL B ON (A.ID_SYMBOL = B.ID_SYMBOL) WHERE NOM_SYMBOL = '{NomSymbol}' ) E ON ( E.Id_TEMPS > A.Id_TEMPS)
                where IND_STOCH_RSI is not null and IND_RSI is not null and IND_TRIX is not null
                AND NOM_SYMBOL = '{NomSymbol}'
                order by A.Id_TEMPS desc
                limit {Limite};
            """.format(NomSymbol = Paire, 
                       Limite = LimiteML)

            resultat = DB_SQL.Select(sql_train)
            df_train = util.Prediction_SQL_To_DF(resultat)
            ML_Class = ML.ML_CLassification(df_train)
            print('Entrainement sur les 6 Derniers Mois')

            # Step 2 : Phase Prediction
            
            sql_Test = """select ID_SIT_CRS, 
                        IND_STOCH_RSI, 
                        IND_RSI, 
                        IND_TRIX,
                        NULL, 
                        NULL,
                        A.ID_TEMPS,
                        A.VALEUR_COURS
                        from FAIT_SIT_COURS A
                        inner join DIM_SYMBOL B ON (B.ID_SYMBOL = A.ID_SYMBOL)
                        where IND_STOCH_RSI is not null and IND_RSI is not null and IND_TRIX is not null
                        AND NOM_SYMBOL = '{NomSymbol}'
                        order by A.Id_TEMPS desc; 
                    """.format(NomSymbol = Paire)
            
            resultat = DB_SQL.Select(sql_Test)
            df_test = util.Prediction_SQL_To_DF(resultat)
            df_test = ML_Class.predict(df_test)
            print('Prediction sur les données Lives')
            

            # Optimisation résultat Prediction
            df_temp = df_test[(df_test['DEC_VENTE'] == 1) | (df_test['DEC_ACHAT'] == 1)][['ID_TEMPS','DEC_ACHAT', 'DEC_VENTE', 'ID_SIT_CRS']]
            df_temp = df_temp.sort_values(by = 'ID_TEMPS')

            for i in range(0, df_temp.shape[0]):
                if i > 0 :
                    #cas Décision Achat
                    DEC_ACHAT = df_temp.iloc[i]['DEC_ACHAT']
                    DEC_VENTE_1 = max_df(df_temp, df_temp.iloc[i]['ID_TEMPS'], 'DEC_VENTE')
                    if (DEC_ACHAT == 1) & ( DEC_VENTE_1 == 0):
                        df_temp.iat[i, 1] = 0

                    #cas Décision Vente
                    DEC_VENTE = df_temp.iloc[i]['DEC_VENTE']
                    DEC_ACHAT_1 = max_df(df_temp, df_temp.iloc[i]['ID_TEMPS'], 'DEC_ACHAT')
                    if (DEC_VENTE == 1) & ( DEC_ACHAT_1 == 0):
                        df_temp.iat[i, 2] = 0

            print('Optimisation Prediction Resultat')

            # Stockage resultat Prediction
            # --
            Fait_Dec_A = pd.DataFrame(df_temp['ID_SIT_CRS'])
            Fait_Dec_A['ID_MLCLAS'] = 3
            Fait_Dec_A['DEC_ACHAT'] = df_temp['DEC_ACHAT']
            DB_SQL.Alim_FaitPrediction(Fait_Dec_A)

            # --
            Fait_Dec_V = pd.DataFrame(df_temp['ID_SIT_CRS'])
            Fait_Dec_V['ID_MLCLAS'] = 4
            Fait_Dec_V['DEC_VENTE'] = df_temp['DEC_VENTE']
            DB_SQL.Alim_FaitPrediction(Fait_Dec_V)

            print('Chargement Prédiction Live Achat Vente M2')

        elif MethodeCalcul == "M1":

            df_test=Get_DataPaire([Paire],Periode_Debut,Periode_Fin,"M1")
            Alim_Data_M1(df_test, 'L')

        # -- 
        DB_SQL.CloseConnection()

    except : 
        return "KO"
    return "OK"

"""
########################################################################
#############Bloc 3 : Extraction Data Base #############################
########################################################################
"""
# -->
def Get_DataPaire(ListePaire :list, Periode_Debut, Periode_Fin, MethodeCalcul) :
    """
    Cette fonction retourne les informations du cours d'une Paire sur une période donnée.
    seleon une méthode de Calcul
    """
    
    try:
        # --
        MesSymbols =""

        for paire in ListePaire:
            MesSymbols = MesSymbols + "'" + str(paire) + "',"

        MesSymbols = MesSymbols.strip(",")
        
        # -- 
        if MethodeCalcul == 'M1':
            achat = 1
            vente = 2
        elif MethodeCalcul == 'M2': 
            achat = 3
            vente = 4

        # -- 
        script_sql = """
        SELECT A.ID_SIT_CRS_HIS, A.ID_TEMPS, C.DATE_TEMPS, NOM_SYMBOL, 
                VALEUR_COURS, IND_STOCH_RSI, IND_RSI, IND_TRIX,
                D_ACHAT.IND_DEC,D_VENTE.IND_DEC

        FROM FAIT_SIT_COURS_HIST A
        INNER JOIN DIM_SYMBOL B ON (A.ID_SYMBOL = B.ID_SYMBOL)
        INNER JOIN DIM_TEMPS C ON (A.ID_TEMPS = C.ID_TEMPS)
        LEFT OUTER JOIN FAIT_DEC_ML_CLASS D_ACHAT ON (D_ACHAT.ID_SIT_CRS_HIS = A.ID_SIT_CRS_HIS AND D_ACHAT.ID_MLCLAS = {Achat})
        LEFT OUTER JOIN FAIT_DEC_ML_CLASS D_VENTE ON (D_VENTE.ID_SIT_CRS_HIS = A.ID_SIT_CRS_HIS AND D_VENTE.ID_MLCLAS = {Vente})
        WHERE NOM_SYMBOL IN ({Liste_Symbol})
        AND A.ID_TEMPS NOT IN (SELECT ID_TEMPS FROM FAIT_SIT_COURS)
        AND ANNEE||'-'||MOIS||'-'||JOUR BETWEEN '{Periode_Debut}' AND '{Periode_Fin}'

        UNION

        SELECT A.ID_SIT_CRS, A.ID_TEMPS, C.DATE_TEMPS, NOM_SYMBOL, 
                VALEUR_COURS, IND_STOCH_RSI, IND_RSI, IND_TRIX,
                D_ACHAT.IND_PRED, D_VENTE.IND_PRED

        FROM FAIT_SIT_COURS A
        INNER JOIN DIM_SYMBOL B ON (A.ID_SYMBOL = B.ID_SYMBOL)
        INNER JOIN DIM_TEMPS C ON (A.ID_TEMPS = C.ID_TEMPS)
        LEFT OUTER JOIN FAIT_PREDICTION D_ACHAT ON (D_ACHAT.ID_SIT_CRS = A.ID_SIT_CRS AND D_ACHAT.ID_MLCLAS = {Achat})
        LEFT OUTER JOIN FAIT_PREDICTION D_VENTE ON (D_VENTE.ID_SIT_CRS = A.ID_SIT_CRS AND D_VENTE.ID_MLCLAS = {Vente})
        WHERE NOM_SYMBOL IN ({Liste_Symbol})
        AND ANNEE||'-'||MOIS||'-'||JOUR BETWEEN '{Periode_Debut}' AND '{Periode_Fin}';
        """.format(Liste_Symbol = MesSymbols, 
                Periode_Debut = Periode_Debut, 
                Periode_Fin = Periode_Fin,
                Achat = achat,
                Vente = vente)
        
        # -- 
        DB_SQL = DAO_SQL.Drivers_SQLite(PathDatabase)
        res = DB_SQL.Select(script_sql) 
        print('Récupération des Données des Paires [{}] sur la période du {} au {}'.format(MesSymbols, Periode_Debut,Periode_Fin ) )

        # -- 
        L = []
        for i in res:
            (ID_SIT_CRS, ID_TEMPS, DATE_TEMPS, NOM_SYMBOL, VALEUR_COURS, IND_STOCH_RSI, 
             IND_RSI, IND_TRIX,DEC_ACHAT, DEC_VENTE) = i

            L.append({ 'ID_SIT_CRS' : ID_SIT_CRS,
                      'ID_TEMPS': ID_TEMPS, 
                      'DATE_TEMPS' : DATE_TEMPS, 
                      'NOM_SYMBOL' : NOM_SYMBOL, 
                      'VALEUR_COURS': VALEUR_COURS, 
                      'IND_STOCH_RSI': IND_STOCH_RSI, 
                      'IND_RSI': IND_RSI, 
                      'IND_TRIX' : IND_TRIX,
                      'DEC_ACHAT':DEC_ACHAT, 
                      'DEC_VENTE': DEC_VENTE}
                      )
            
        df_resultat = pd.DataFrame(L)
        df_resultat.set_index('DATE_TEMPS', inplace=True)


        # -- 
        DB_SQL.CloseConnection()

    except:
        print("KO")
        return pd.DataFrame(columns=['ID_TEMPS', 'DATE_TEMPS', 'NOM_SYMBOL', 'VALEUR_COURS', 'IND_STOCH_RSI', 'IND_RSI', 'IND_TRIX','DEC_ACHAT', 'DEC_VENTE'])
    
    return df_resultat.sort_values(by='ID_TEMPS')

# -->
def	Get_Graphe_Prediction_Achat_Vente(Data):
    """
    Cette fonction retourne un graphe de prediction Achat ou Vente.
    """
    try:
        Fig = util.visualiser_transactions(Data)
    except:
        print("KO")

    return Fig

# -->
def Get_SimulationGain(Data, Symbol,Capital_depart = 1000):
    """
    Cette fonction effectue une simulation de gain sur une période donnée
    """
    try:
        Data = Data.copy()
        Data = Data[(Data['DEC_ACHAT'] == 1) | (Data['DEC_VENTE'] == 1)]
                                                                   
        prev_achat = None
        prev_vente = None
        to_drop = []

        for index, row in Data.iterrows():
            if prev_achat == row['DEC_ACHAT'] and prev_vente == row['DEC_VENTE']:
                to_drop.append(index)
            else:
                prev_achat = row['DEC_ACHAT']
                prev_vente = row['DEC_VENTE']

        Data = Data.drop(to_drop)
        if Data.iloc[0]['DEC_VENTE'] == 1:
            Data = Data.drop(Data.index[0])
        # ... les autres opérations sur Data

        rapport = util_TA.Generation_Rapport_Backtest(Data, Symbol,Capital_depart)
        
    except Exception as e:
        print("Une erreur est survenue lors de l'exécution de Get_SimulationGain:")
        print(str(e))
        #print("Traceback de l'erreur :")
        #traceback.print_exc()
        rapport = None
        Data = None

    return (rapport, Data)

# -->
def Get_Graphe_SimulationGain(Data):
    """
    Cette fonction retourne un graphe de simulation de Gain 
    """
    try:
        df_temps = Data.copy()
        df_temps['timestamp_sec'] = df_temps['ID_TEMPS'] * 0.001
        df_temps['datetime'] = pd.to_datetime(df_temps['ID_TEMPS'], unit='ms')
        df_temps.set_index('datetime', inplace=True) 
        #df_temps.to_csv("data2.csv") 
    except Exception as e:
        print("Une erreur est survenue lors de l'exécution de Get_Graphe_SimulationGain:")
        print(str(e))
        df_temps = None

    if df_temps is not None:
        return util.affiche_graphe_score(df_temps)
    else:
        return None

"""
########################################################################
#############Bloc 4 : Extraction Data Binance ##########################
########################################################################
"""
# -->
def	Get_Live_InfoPaire(Paire, Interval = '1h', Periode_Debut = datetime.date.today().isoformat(), Periode_Fin = datetime.date.today().isoformat()):
    """
    Cette fonction retourne les infos d'une Paire sur une Période de 24h
    """

    try:
        columns = ['OpenTime', 'OpenPrice','HighPrice','LowPrice','ClosePrice','Volume','CloseTime','QuoteAssetVolume','NumberTrade','BuyAssetVol','BuyQuoteVol','Ignore' ]

        API_Live = live.Binance_Live()
        startTime = util.Convertir_toTimestamp(Periode_Debut)
        endTime = util.Convertir_toTimestamp(Periode_Fin)

        # --> initialisation Boucle
        X= API_Live.klines(Paire, Interval, startTime = startTime, endTime = endTime )
        df = pd.DataFrame(X, columns= columns)
        startTime = df['CloseTime'].max()

        # --> Lancement de la boucle pour récupérer tous les cours de la période
        while endTime >= startTime:
            X= API_Live.klines(Paire, Interval, startTime = startTime, endTime = endTime )
            df_temps = pd.DataFrame(X, columns= columns)
            df = pd.concat([df, df_temps], axis = 0)
            startTime = df_temps['CloseTime'].max()
        
        # --> suppression des doublons
        df = df.drop_duplicates(keep='first')

        print('Récuparation de la Paire {} à partir du {} jusqu''au {} '.format(Paire, Periode_Debut, Periode_Fin ))

        df['INTERVALLE'] = Interval
        df['NOM_SYMBOL'] = Paire
        df['datetime'] = df['CloseTime'].apply(util.Convertir_Timestamp)

        df.set_index('datetime', inplace=True)

    except:
        print("KO")
        return pd.DataFrame([], columns=columns)
    
    return df

# --> 
def Get_API_Binance():
    """
    Cette fonction retourne la liste des Paires existantes sur Binance
    """
    try:
        DataLive = live.Binance_Live()
        return DataLive
    except:
        return 'KO'

# --> 
def Alim_Data_M1(Data, TypeDate):
    """
    Cette fonction permet d'alimenter les tables Prédictions / Decision avec la méthode 1
    """
    
    try:

        DB_SQL = DAO_SQL.Drivers_SQLite(PathDatabase)

        # --
        df_temp = util_TA.boucle_trading(Data[['ID_SIT_CRS','VALEUR_COURS', 'IND_STOCH_RSI', 'IND_RSI', 'IND_TRIX']])
        print('Lancement Fonction Boucle Trading M1')      
        
        # --
        Fait_Dec_A = pd.DataFrame(df_temp['ID_SIT_CRS'])
        Fait_Dec_A['ID_MLCLAS'] = 1
        Fait_Dec_A['DEC_ACHAT'] = df_temp['DEC_ACHAT']

        # --
        Fait_Dec_V = pd.DataFrame(df_temp['ID_SIT_CRS'])
        Fait_Dec_V['ID_MLCLAS'] = 2
        Fait_Dec_V['DEC_VENTE'] = df_temp['DEC_VENTE']

        if TypeDate == 'L':
            DB_SQL.Alim_FaitPrediction(Fait_Dec_A)
            DB_SQL.Alim_FaitPrediction(Fait_Dec_V)
            print('Chargement Prediction Live Achat Vente M1')

        elif TypeDate == 'H':
            DB_SQL.Alim_FaitDecision_Histo(Fait_Dec_A)
            DB_SQL.Alim_FaitDecision_Histo(Fait_Dec_V)
            print('Chargement Desision Histo Achat Vente M1')

    except :
        return "KO"

    return "OK"