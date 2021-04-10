import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set()

import os, sys
from datetime import datetime
from ETL import ETL
from Classes import Header, Anagrafica

from Classes import AnalisiRegionale, Somministrazioni

DWpath = os.path.join('DW')

# Introduzione
Header()

# ETL
st.write('')
etl = ETL()
with open('lastupdate', 'r') as f:
    st.write(f.read())
    lastUpdate = datetime.strptime(f.read(), '%d/%m/%Y').date()

etl.getData()
etl.transformData()
etl.auxiliaryTables()

# Somministrazioni
somm = Somministrazioni()
somm.Analisi()

# # ################ANAGRAFICA############
st.header('Anagrafica Somministrazioni')
st.write(
    "Sguardo alla distribuzione dei vaccini per fascia di età."
    )
#pltAnaDosi, pltAnaPerc, altriPlot = 
Anagrafica()

# # Bubble plot
# st.pyplot(pltAnaDosi)

# st.markdown('***')
# # Add a checkbox to show/hide radar plot
# expander = st.beta_expander('Seleziona per vedere una visualizzazione alternativa.')
# expander.write(pltAnaPerc)
# expander.write(
#     'Questo grafico mostra la percentuale di vaccinati (seconda dose somministrata) in funzione della fascia anagrafica'
#     ' di appartenenza, oltre alla media italiana. Il grafico di destra è la versione ingrandita di quello a sinistra per maggior visibilità.'
# )

# st.markdown('***')

# st.write('Guardiamo inoltre come sono ripartiti in base al sesso e alla categoria sociale di appartenenza.')
# # Sex and social category
# st.write(altriPlot)

###################################################

# # Analisi Regionale
# anaReg = AnalisiRegionale()
# anaReg.Analisi()

###################################################

st.markdown('####################################################')


#dates  = pd.to_datetime(somministrazioni['Data Somministrazione']).dt.date.unique()



# somministrazioniFilterData = somministrazioni[  (pd.to_datetime(somministrazioni['Data Somministrazione']).dt.date >= startDate )
#                                                 & (pd.to_datetime(somministrazioni['Data Somministrazione']).dt.date <= endDate)   
#                                                 #& (somministrazioni['Regione']==somministrazioni.any)
#                 ]       

# st.write(somministrazioniFilterData)


# #####################BAR DOSI E TOTALE GIORNALIERO##################
# somministrazioniGiorno = somministrazioniFilterData.groupby('Data Somministrazione').sum()


# ####################ANALISI REGIONALE#################
# abitantiregioni = pd.read_csv('DCIS_POPRES1_25022021122609782.csv')
# abitantiregioni = abitantiregioni.iloc[:,[1,5,6,9,12]].sort_values(['Territorio',
#                                                     'Sesso']
#                                                   ).where((abitantiregioni['Stato civile']=='totale') &
#                                                           (abitantiregioni.Sesso=='totale') &
#                                                           (abitantiregioni.ETA1=='TOTAL')
#                                                          ).dropna().iloc[:,[0,-1]].set_index('Territorio')
# # Rename field and indexfor better naming
# abitantiregioni = abitantiregioni.rename(columns={'Value': 'Abitanti'}).rename_axis('Regione').astype(int)



# regione = st.multiselect('Seleziona una o più regioni per visualizzare il grafico.', options=somministrazioni.Regione.unique())

# regioniConfronto = make_subplots(specs=[[{"secondary_y": True}]])

# for i in regione:
#     regioneSelezionata = somministrazioniFilterData[somministrazioni.Regione==i]
#     regioniConfronto.add_trace(
#         go.Scatter(
#             name = 'Somministrazioni {}'.format(i),
#             x = regioneSelezionata['Data Somministrazione'],
#             y = regioneSelezionata['Totale'].cumsum()
#         )
#     )
# regioniConfronto.update_layout(legend=dict(
#     yanchor="top",
#     y=0.99,
#     xanchor="left",
#     x=0.01
# ))
# st.write(regioniConfronto, use_container_width=True)
# ######################################################

