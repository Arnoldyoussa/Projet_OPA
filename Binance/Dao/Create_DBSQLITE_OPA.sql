
/* STEP 02 : Création des Dimensions */
--> 
CREATE TABLE IF NOT EXISTS DIM_TEMPS  ( 
	ID_TEMPS VARCHAR(13) PRIMARY KEY,
	SECONDES VARCHAR(2), 	
	MINUTES VARCHAR(2), 	
	HEURE VARCHAR(2),	
	JOUR VARCHAR(2),	
	MOIS VARCHAR(2),	
	ANNEE VARCHAR(4),	
	DATE_CREATION DATE
);

--> 
CREATE TABLE IF NOT EXISTS DIM_SYMBOL  
(
	ID_SYMBOL NUMERIC(10) PRIMARY KEY AUTOINCREMENT,
	NOM_SYMBOL VARCHAR(10),
	INTERVALLE	VARCHAR(5),
	BASE_ASSET VARCHAR(10),
	QUOTE_ASSET VARCHAR(10),
	DATE_CREATION DATE

);

--> 
CREATE TABLE IF NOT EXISTS DIM_ML_CLAS 
(
	ID_MLCLAS NUMERIC(10) PRIMARY KEY AUTOINCREMENT,
	DESC_MLCLAS VARCHAR(250),
	DATE_CREATION DATE
);

--> 
INSERT INTO DIM_ML_CLAS (DESC_MLCLAS,DATE_CREATION) VALUES ( 'ML Classification Achat Paire', date('now') );
INSERT INTO DIM_ML_CLAS (DESC_MLCLAS,DATE_CREATION) VALUES ( 'ML Classification Vente Paire', date('now') );

/* STEP 03 : Création des Faits Histo */

--> 
CREATE TABLE IF NOT EXISTS FAIT_SIT_COURS_HIST  
(
	ID_SIT_CRS_HIS NUMERIC(20) PRIMARY KEY AUTOINCREMENT,
	ID_TEMPS VARCHAR(13), 
	ID_SYMBOL NUMERIC(10), 
	VALEUR_COURS NUMERIC(10), 
	IND_SMA_20 NUMERIC(10),
	IND_SMA_30 NUMERIC(10),
	IND_QUOTEVOLUME NUMERIC(10),
	IND_CHANGEPERCENT NUMERIC(10),
	IND_STOCH_RSI NUMERIC(10),
	IND_RSI NUMERIC(10),
	IND_TRIX NUMERIC(10),
	DATE_CREATION DATE,
	FOREIGN KEY(ID_TEMPS) REFERENCES DIM_TEMPS(ID_TEMPS),
	FOREIGN KEY(ID_SYMBOL) REFERENCES DIM_SYMBOL(ID_SYMBOL)

);

--> 
CREATE TABLE IF NOT EXISTS FAIT_DEC_ML_CLASS
(
	ID_DEC_ML_CL NUMERIC(20) PRIMARY KEY AUTOINCREMENT,
	ID_SIT_CRS_HIS NUMERIC(20),
	ID_MLCLAS NUMERIC(10),
	TOP_DECISION VARCHAR(1),
	DATE_CREATION DATE,
	FOREIGN KEY(ID_MLCLAS) REFERENCES DIM_ML_CLAS(ID_MLCLAS),
	FOREIGN KEY(ID_SIT_CRS_HIS) REFERENCES FAIT_SIT_COURS_HIST(ID_SIT_CRS_HIS)
);


/* STEP 04 : Création des Faits Temps Réels */

--> 
CREATE TABLE IF NOT EXISTS FAIT_SIT_COURS
(
	ID_SIT_CRS NUMERIC(20) PRIMARY KEY AUTOINCREMENT,
	ID_TEMPS VARCHAR(13), 
	ID_SYMBOL NUMERIC(10), 
	VALEUR_COURS NUMERIC(10), 
	IND_SMA_20 NUMERIC(10),
	IND_SMA_30 NUMERIC(10),
	IND_QUOTEVOLUME NUMERIC(10),
	IND_CHANGEPERCENT NUMERIC(10),
	IND_STOCH_RSI NUMERIC(10),
	IND_RSI NUMERIC(10),
	IND_TRIX NUMERIC(10),
	DATE_CREATION DATE,
	FOREIGN KEY(ID_TEMPS) REFERENCES DIM_TEMPS(ID_TEMPS),
	FOREIGN KEY(ID_SYMBOL) REFERENCES DIM_SYMBOL(ID_SYMBOL)

);

--> 
CREATE TABLE IF NOT EXISTS FAIT_PREDICTION
(
	ID_PREDICTION NUMERIC(20) PRIMARY KEY AUTOINCREMENT,
	ID_SIT_CRS NUMERIC(20),
	ID_MLCLAS NUMERIC(10),
	TOP_DECISION VARCHAR(1),
	DATE_CREATION DATE,
	FOREIGN KEY(ID_MLCLAS) REFERENCES DIM_ML_CLAS(ID_MLCLAS),
	FOREIGN KEY(ID_SIT_CRS) REFERENCES FAIT_SIT_COURS(ID_SIT_CRS)
);