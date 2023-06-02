import datetime as dt
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
     
    def __init__(self, Liste_Symbols : list= None, Liste_Intervals : list= None , DateDebut : str = None, DateFin : str = None, ProfondeurJr = 30, Frequence = 'M') :
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
            self.DateDebut = dt.date.today() - dt.timedelta(days = ProfondeurJr)
        else : 
            self.DateDebut = dt.date.fromisoformat(DateDebut)

        # Si pas de Date de fin alors on la date de la veille
        if DateFin is None:
            self.DateFin = dt.date.today()
        else : 
            self.DateFin = dt.date.fromisoformat(DateFin)

    
    def get_ListeFichier(self,fichier=None,premiere_date=None):
        """
            Retourne la liste des fichiers Historiques à télécharger en Local.
        """
        first_doc = None  # Variable pour stocker le premier document trouvé
        if fichier : 
            for i in fichier : 
                nomFichier = i.split(".")[0]
                temp = nomFichier.split("-")
                symbol = temp[0]
                interval = temp[1]
                date = temp[2]
                # Formatage de l'url de chargement des Fichiers
                url = self.Base_Url_Histo + symbol + "/" + interval + "/"+ nomFichier + ".zip"
                # Ckeck si existe 
                r= requests.get(url)
                if r.status_code == 200:
                    if first_doc is None:
                        first_doc = i
                        # Extraire la partie date du nom du fichier
                        date_str = first_doc.split('-')[2] + '-' + first_doc.split('-')[3].rsplit('.', 1)[0]
                        first_doc = dt.datetime.strptime(date_str, '%Y-%m')
                        first_doc = first_doc.strftime('%Y-%m')  # Convertir l'objet datetime en chaîne au format 'AAAA-MM'
                        if first_doc>premiere_date:
                            first_doc=premiere_date
                                          
                    self.L_Fichier.append({"Nom" : nomFichier + ".csv", "URL" : url})
                else:
                     
                    first_doc = i
                    # Extraire la partie date du nom du fichier
                    date_str = first_doc.split('-')[2] + '-' + first_doc.split('-')[3].rsplit('.', 1)[0]
                    first_doc = dt.datetime.strptime(date_str, '%Y-%m')
                    first_doc = first_doc.strftime('%Y-%m')  # Convertir l'objet datetime en chaîne au format 'AAAA-MM'
        else:
            
            self.L_Fichier = list()
            
            # Identification de la liste des Dates de Fichiers
            L_Date = list()
            DEB = self.DateDebut
            FIN = self.DateFin

            if FIN > DEB:
                for i in range(0, (FIN - DEB).days, 1 ):
                    MaDate = (DEB + dt.timedelta(days = i)).isoformat()

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
        return self.L_Fichier,first_doc
        
    def TelechargeFichier(self,fichier=None,premiere_date=None):
        """
            Téléchargement des Fichiers en Local
        """
        # Initialisation des fichiers à charger
        if fichier:
            temp,fd=self.get_ListeFichier(fichier,premiere_date)
        else:
            self.get_ListeFichier()
 
        for Monfichier in self.L_Fichier:
            nomZip = Monfichier['Nom'].split('.')[0] + ' .zip'
            try:
                if os.path.exists(Monfichier['Nom']): 
                    os.remove(Monfichier['Nom'])
            except OSError as e:
                print(f"Erreur: {e.strerror}")
                continue

            try:
                r = requests.get(Monfichier['URL'], stream=True)
                if r.status_code == 200:
                    try:
                        with open(nomZip , "wb") as f:
                            f.write(r.content)
                    except OSError as e:
                        print(f"Erreur d'écriture de fichier: {e.strerror}")
                        continue

                    try:
                        ZipFile(nomZip).extractall()
                    except Exception as e:
                        print(f"Erreur d'extraction de fichier zip: {str(e)}")
                        continue
                else:
                    print(f"Erreur de téléchargement: status code {r.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Erreur de requête: {str(e)}")
                continue

            try:
                os.remove(nomZip)
            except OSError as e:
                print(f"Erreur de suppression de fichier: {e.strerror}")
        return fd

    def SupprimeFichier(self):
        """
            Suppression des fichiers téléchargés
        """

        for Monfichier in self.L_Fichier:
            if os.path.exists(Monfichier['Nom']):
                os.remove(Monfichier['Nom'])