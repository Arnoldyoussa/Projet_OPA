import datetime

def Convertir_Timestamp(X, formatDate = None):
    myDate = datetime.datetime.fromtimestamp(float(X)/1000)
    
    if formatDate == 'DD':
        return myDate.day
    elif formatDate == 'MM':
        return myDate.month
    elif formatDate == 'YYYY':
        return myDate.year
    elif formatDate == 'HH':
        return myDate.hour
    elif formatDate == 'mm':
        return myDate.minute
    elif formatDate == 'ss':
        return myDate.second
    else :
        return myDate