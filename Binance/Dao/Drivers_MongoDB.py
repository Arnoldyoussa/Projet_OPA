

import json
import pandas as pd
from pymongo import MongoClient

class Drivers_MongoDB:
    """  
        Class Drivers_MongoDB : 
        Rôle : permet de gérer / interroger la base MongoDB

        Paramétres : 
            L_Fichier : 
        
        Méthodes :   
 """

    NomColumns = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume', 'Nb_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'ignore']

    def __init__(self, ListeFichier : list = [], Host : str = 'localhost', Port = 27017 , NomDB : str = 'OPA') :
        self.L_Fichier = ListeFichier
        self.ClientMongo = MongoClient(Host, Port)
        self.DBMongo = self.ClientMongo[NomDB]
    
    def DeleteCollection(self, Collections : list):
        for coll in Collections:
            self.DBMongo.drop_collection(coll)


    def ChargeFichiers(self):
        for nomFichier in self.L_Fichier:
            Symbol = nomFichier.split('-')[0]
            Intervalle = nomFichier.split('-')[1]
            collection = self.DBMongo[Symbol]

            # chargement fichier
            df = pd.read_csv(nomFichier , sep =',' )
            df = pd.DataFrame(df.values, columns=self.NomColumns) 

            # Transformation avant Import en MongoDB
            L = list()
            for i in df.index:
                L.append(json.loads(df.iloc[i].to_json()))

            # Création Collection Mongo
            if nomFichier not in self.get_ListeFichier(Symbol) :
                Document = {'_id': nomFichier ,'Symbol' : Symbol, 'Intervalle' : Intervalle, 'Detail' : L }
                collection.insert_one(Document)

    def get_AllCollection(self):
        return list(self.DBMongo.list_collection_names() )

    def get_ListeFichier(self, Symbol):
        L = list()
        collection = self.DBMongo[Symbol]
        
        for nomFichier in list(collection.find({}, {'_id' : 1})):
            L.append(nomFichier['_id'])

        return L

    def get_AllDocuments(self, Symbol):
        collection = self.DBMongo[Symbol]
        return list(collection.find({})) 