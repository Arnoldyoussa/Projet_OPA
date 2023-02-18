import json
import pandas as pd
import csv
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

    def __init__(self, ListeFichier : list = [], Host : str = 'localhost', Port = 27017 , NomDB : str = 'OPA2') :
        self.L_Fichier = ListeFichier
        self.myclient = MongoClient(Host, Port)
        self.mydb = self.myclient[NomDB]
        



    def upload_to_mongo(self):
        num_docs_inserted = 0
        for file in self.L_Fichier:
            symbol, interval = file.split("_")[0], file.split("_")[1]
            if f"{symbol}_{interval}" in self.mydb.list_collection_names():
                self.mydb[f"{symbol}_{interval}"].drop()
            mycol = self.mydb[f"{symbol}_{interval}"]
            with open(file, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                rows = list(reader)
            for row in rows:
                result = mycol.insert_one({header[0]: row[0], header[1]: row[1], header[2]: row[2], header[3]: row[3], header[4]: row[4], header[5]: row[5], header[6]: row[6], header[7]: row[7], header[8]: row[8], header[9]: row[9], header[10]: row[10], header[11]: row[11], header[12]: row[12]})
                if result.inserted_id:
                    num_docs_inserted += 1
        return num_docs_inserted
    
    def DeleteCollection(self, Collections : list):
        for coll in Collections:
            self.mydb.drop_collection(coll)

    def get_AllCollection(self):
        return list(self.mydb.list_collection_names() )

    def get_ListeFichier(self, Symbol):
        L = list()
        collection = self.mydb[Symbol]
        
        for nomFichier in list(collection.find({}, {'_id' : 1})):
            L.append(nomFichier['_id'])

        return L

    def get_AllDocuments(self, Symbol,Interval):
        
        collection = self.mydb[f"{Symbol}_{Interval}"]
        return list(collection.find({}))