from binance import Client

class Binance_Live():
    """
        Class Binance_Live : 
            Rôle : Hérite de tous les propriétés de l'API Binance

            Paramétres : 
                ...
                 
            Méthodes : 
                       
    """
    def __init__(self, api_key=None, api_secret=None, **kwargs) :
        super().__init__( api_key, api_secret, **kwargs )