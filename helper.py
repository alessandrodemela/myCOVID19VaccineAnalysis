from datetime import datetime, timedelta
import streamlit as st
import numpy as np
from sklearn.linear_model import LinearRegression


###############################
# Auxiliary objects

def getTicksLabels(a):
    formatData = '%d %b'
    labels = [datetime(day=d,month=m,year=2021).strftime(formatData) for m in range(1,datetime.today().month+1) for d in [1,15] ]
    labelsTMP = [i.strftime(formatData) for i in a]
    ticks=[labelsTMP.index(i) for i in labels]

    return labels, ticks


# mapRegioni = {
#     'Abruzzo'                               : 'ABR',
#     'Basilicata'                            : 'BAS',
#     'Provincia Autonoma Bolzano / Bozen'    : 'PAB',
#     'Calabria'                              : 'CAL',
#     'Campania'                              : 'CAM',
#     'Emilia-Romagna'                        : 'EMR',
#     'Friuli-Venezia Giulia'                 : 'FVG',
#     'Lazio'                                 : 'LAZ',
#     'Liguria'                               : 'LIG',
#     'Lombardia'                             : 'LOM',
#     'Marche'                                : 'MAR',
#     'Molise'                                : 'MOL',
#     'Piemonte'                              : 'PIE',
#     'Puglia'                                : 'PUG',
#     'Sardegna'                              : 'SAR',
#     'Sicilia'                               : 'SIC',
#     'Toscana'                               : 'TOS',
#     'Provincia Autonoma Trento'             : 'PAT',
#     'Umbria'                                : 'UMB',
#     "Valle d'Aosta / Vallée d'Aoste"        : 'VDA',
#     'Veneto'                                : 'VEN'
# }

coloreFornitori = ['hotpink','firebrick','royalblue','goldenrod']

def predictCurrentWeek(df, regression=False):
    '''Predict current week'''
    if regression:
        df = df.groupby(level=0).sum()
        X=np.array(df.index)[:-1].reshape(-1,1)
        y=df.Totale[:-1]
        Xpred = [[np.array(df.index)[-1]]]

        return LinearRegression().fit(X,y).predict(Xpred)[0]

    else:
        dfAvgDay = (df.div(df.groupby(['Settimana']).sum()[:-1])).groupby('Giorno').mean()
        try:
            return (df.loc[datetime.today().isocalendar()[1]+1].cumsum() / dfAvgDay.cumsum()).dropna().values[-1][0]
        except Exception as e:
            return None


def getDateRangeFromWeek(p_year,p_week):
    firstdayofweek = datetime.strptime(f'{p_year}-W{int(p_week )- 1}-1', "%Y-W%W-%w").date()
    lastdayofweek = firstdayofweek + timedelta(days=6.9)
    return firstdayofweek.strftime('%d/%m'), lastdayofweek.strftime('%d/%m')