from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import pandas as pd

class ML_CLassification:
    def __init__(self, Data):
        self.DataTrain = Data[['ID_SIT_CRS','IND_STOCH_RSI','IND_RSI','IND_TRIX','TOP_ACHAT','TOP_VENTE']]
        self.ML_Class_Achat = self.fit('ACHAT')
        self.ML_Class_Vente = self.fit('VENTE')

    def fit(self, TypeDecision, test_size = 0.2, random_state = 42 ):
        
        if TypeDecision == 'ACHAT':
            X = self.DataTrain.drop(columns = ['TOP_ACHAT','ID_SIT_CRS','TOP_VENTE'])
            y = self.DataTrain['TOP_ACHAT']

        elif TypeDecision == 'VENTE':
            X = self.DataTrain.drop(columns = ['TOP_VENTE','ID_SIT_CRS','TOP_ACHAT'])
            y = self.DataTrain['TOP_VENTE']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = test_size, random_state = random_state)
        MLClass = DecisionTreeClassifier(random_state=random_state)
        MLClass.fit(X_train, y_train)

        return MLClass
    
    def predict(self,  Data):
        DataTest = Data[['ID_SIT_CRS','IND_STOCH_RSI','IND_RSI','IND_TRIX']]
        y_predA = self.ML_Class_Achat.predict(DataTest.drop(columns = ['ID_SIT_CRS']))
        y_predV = self.ML_Class_Vente.predict(DataTest.drop(columns = ['ID_SIT_CRS']))

        return pd.concat([Data['ID_SIT_CRS'], pd.DataFrame(y_predV, columns = ['TOP_VENTE']), pd.DataFrame(y_predA, columns = ['TOP_ACHAT'])], axis = 1)

        
    
