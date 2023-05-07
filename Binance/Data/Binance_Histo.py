from datetime import date
from datetime import timedelta
import requests
from zipfile import ZipFile
import os

class Binance_Histo:
    """
        Class Binance_Histo : 
            Rôle : Permet de récupérer toutes les données Historiques d'un Symbol(Paire) sur un interval donné

            Paramétres : 
                 L_Fichier :
                 L_Symbols : Liste des Symboles
                 L_Intervals : Liste des Intervalles
                 Freq :
                 DateDebut :
                 DateFin :
                 
            
            Méthodes : 
                get_ListeFichier()
                TelechargeFichier()
                SupprimeFichier()
                
    """
    Base_Url_Histo = 'https://data.binance.vision/data/spot/'
    TypeFichier = 'klines/'
    Base_Monthly = 'monthly/'
    Base_Daily = 'daily/'
    
    def __init__(self, Liste_Symbols : list, Liste_Intervals : list , DateDebut : str = None, DateFin : str = None, ProfondeurJr = 30, Frequence = 'M') :
        """
            Initialisation de la classe Binance_Histo, avec les valeurs par défaut : 
            - DateDebut = Date du Jour (Format Date YYYY-MM-JJ) - ProfondeurJr
            - DateFin = Date du Jour (Format Date YYYY-MM-JJ)
            - Fréquence = 'Q' (Q : Quotidien / M : Mensuel)
            - ProfondeurJr = 30
        """
        self.L_Fichier = list()
        self.L_Symbols = Liste_Symbols
        self.L_Intervals = Liste_Intervals
        self.Freq = Frequence

        if self.Freq == 'Q':
            self.Base_Url_Histo = self.Base_Url_Histo + self.Base_Daily + self.TypeFichier
        else :
            self.Base_Url_Histo = self.Base_Url_Histo + self.Base_Monthly + self.TypeFichier

        # Si pas de Date de Debut alors on le deduit à partir de la profondeur
        if DateDebut is None:
            self.DateDebut = date.today() - timedelta(days = ProfondeurJr)
        else : 
            self.DateDebut = date.fromisoformat(DateDebut)

        # Si pas de Date de fin alors on la date de la veille
        if DateFin is None:
            self.DateFin = date.today()
        else : 
            self.DateFin = date.fromisoformat(DateFin)

    
    def get_ListeFichier(self):
        """
            Retourne la liste des fichiers Historiques à télécharger en Local.
        """
        self.L_Fichier = list()
        
        # Identification de la liste des Dates de Fichiers
        L_Date = list()
        DEB = self.DateDebut
        FIN = self.DateFin

        if FIN > DEB:
            for i in range(0, (FIN - DEB).days, 1 ):
                MaDate = (DEB + timedelta(days = i)).isoformat()

                if self.Freq != 'Q':
                    MaDate = MaDate[0:7]
                
                if MaDate not in L_Date:
                    L_Date.append(MaDate)

            # Formatage de l'url de chargement des Fichiers
            for symbol in self.L_Symbols:
                for interval in self.L_Intervals:
                    for i in L_Date:
                        nomFichier = symbol + "-"+ interval +"-"+ i
                        url = self.Base_Url_Histo + symbol + "/" + interval + "/"+ nomFichier + ".zip"

                        # Ckeck si existe 
                        r= requests.get(url)
                        if r.status_code == 200:
                            self.L_Fichier.append({"Nom" : nomFichier + ".csv", "URL" : url})
                    
        return self.L_Fichier
        
    def TelechargeFichier(self):
        """
            Téléchargement des Fichiers en Local
        """
        # Initialisation des fichiers à charger
        self.get_ListeFichier()

        for Monfichier in self.L_Fichier:
            nomZip = Monfichier['Nom'].split('.')[0] + ' .zip'

            if os.path.exists(Monfichier['Nom']):
                os.remove(Monfichier['Nom'])
                
            r= requests.get(Monfichier['URL'], stream= True)
            with open(nomZip , "wb") as f:
                f.write(r.content)
            
            ZipFile(nomZip).extractall()
            os.remove(nomZip)
        

    def SupprimeFichier(self):
        """
            Suppression des fichiers téléchargés
        """

        for Monfichier in self.L_Fichier:
            if os.path.exists(Monfichier['Nom']):
                os.remove(Monfichier['Nom'])