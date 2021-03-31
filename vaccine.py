import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()

import ETL
from Classes import Somministrazioni, Anagrafica

import datetime, os

DWpath = os.path.join('DW')

with open('lastupdate', 'r') as fin:
    lastupdate = fin.read().strip().split('/')
    lastupdate = datetime.date(day=int(lastupdate[0]), month=int(lastupdate[1]), year=int(lastupdate[2]))

#ETL
somministrazioniAnagr, newupdate = ETL.ETL_anagraficaVacciniSummaryLatest()
somministrazioni = ETL.ETL_somministrazioniVacciniSummaryLatest()
ETL.ETL_consegneVacciniLatest()

if(lastupdate < datetime.date.today()):
    with open('lastupdate', 'w') as fout:
        fout.write(newupdate)

###################TESTO INIZIALE##################

st.title('Report vaccinazioni COVID-19')
st.write('Ultimo Aggiornamento {}'.format(newupdate))

st.markdown('La somministrazione dei vaccini contro la patologia COVID-19, è cominciata il 27/12/2020 [\[1\]]'
            '(http://www.salute.gov.it/portale/news/p3_2_1_1_1.jsp?lingua=italiano&menu=notizie&p=dalministero&id=5242).'
            '\nNella tabella seguente si mostrano il numero di somministrazioni ordinato per data, nelle varie regioni'
            ' e suddiviso per sesso e categoria sociale, oltre che per tipo di sommnistrazione.'
            )

totSomministrate = somministrazioniAnagr.Totale.sum()
totPrime = somministrazioniAnagr['Prima Dose'].sum()
totSeconde = somministrazioniAnagr['Seconda Dose'].sum()
platea = somministrazioniAnagr.Platea.sum()
percPrime = round(totPrime/platea,4)
percSeconde = round(totSeconde/platea,4)
st.markdown(
    f'Al {newupdate} sono state distribuite **{totSomministrate:,}** dosi di vaccino, suddivise in **{totPrime:,}** prime dosi'
    f' e **{totSeconde:,}** seconde dosi. La percentuale di persone che ha ricevuto almeno una dose è '
    f' del **{percPrime:.2%}**, mentre il **{percSeconde:.2%}** della popolazione ha ricevuto entrambe le dosi.'


)
###################################################


################REPORT SOMMINISTRAZIONI############
st.header('Dosi Somministrate per giorno')
st.write(
    "Dosi somministrate quotidiananmente, la data odierna potrebbe contenere un dato parziale."
)
fig = Somministrazioni()
st.write(fig)
###################################################

################ANAGRAFICA############
st.header('Anagrafica Somministrazioni')
st.write(
    "Sguardo alla distribuzione dei vaccini per fascia di età."
    "Si nota la percentuale di vaccinati per anagrafica."
    )
pltAnaDosi, pltAnaPerc, altriPlot = Anagrafica()
st.write(pltAnaDosi)
st.write('Guardiamo inoltre come sono ripartiti in base al sesso e alla categoria sociale di appartenenza.')
st.write(altriPlot)
#st.write(pltAnaPerc)
###################################################

################ANALISI REGIONALE############
st.header('Analisi Regionale')
st.write(
    "*To be written*"
    )
###################################################

st.markdown('####################################################')

consegne = pd.read_csv(os.path.join(DWpath,'consegneVacciniLatest.csv'))


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

