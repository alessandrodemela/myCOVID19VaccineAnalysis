import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import datetime

import os

DWpath = os.path.join('..','DW')

st.title('Report vaccinazioni COVID-19')


somministrazioni = pd.read_csv(os.path.join(DWpath,'somministrazioniVacciniSummaryLatest.csv'))
consegne = pd.read_csv(os.path.join(DWpath,'consegneVacciniLatest.csv'))

somministrazioni.drop(columns='Unnamed: 0', inplace=True)

###################TESTO INIZIALE##################
st.markdown('La somministrazione dei vaccini contro la patologia COVID-19, è cominciata il 27/12/2020 [\[1\]]'
            '(http://www.salute.gov.it/portale/news/p3_2_1_1_1.jsp?lingua=italiano&menu=notizie&p=dalministero&id=5242).'
            '\nNella tabella seguente si mostrano il numero di somministrazioni ordinato per data, nelle varie regioni'
            ' e suddiviso per sesso e categoria sociale, oltre che per tipo di sommnistrazione.'
            )
###################################################

dates  = pd.to_datetime(somministrazioni['Data Somministrazione']).dt.date.unique()

startDate, endDate = st.sidebar.slider("Seleziona un intervallo temporale",
                                min_value=dates[0],
                                max_value=dates[-1],
                                value=[dates[0],dates[-1]],
)

somministrazioniFilterData = somministrazioni[  (pd.to_datetime(somministrazioni['Data Somministrazione']).dt.date >= startDate )
                                                & (pd.to_datetime(somministrazioni['Data Somministrazione']).dt.date <= endDate)   
                                                #& (somministrazioni['Regione']==somministrazioni.any)
                ]       

st.write(somministrazioniFilterData)


#####################BAR DOSI E TOTALE GIORNALIERO##################
somministrazioniGiorno = somministrazioniFilterData.groupby('Data Somministrazione').sum()

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Bar(
        name='Prima Dose', 
        x = somministrazioniGiorno.index, 
        y = somministrazioniGiorno['Prima Dose'],
    )
)
fig.add_trace(
    go.Bar(
        name='Seconda Dose',
        x = somministrazioniGiorno.index,
        y = somministrazioniGiorno['Seconda Dose']
    )
)
fig.add_trace(
    go.Scatter(
        name = 'Totale',
        x = somministrazioniGiorno.index,
        y = somministrazioniGiorno['Totale'].cumsum(),
    ),
    secondary_y=True
)
fig.update_layout(barmode='stack')
# Set y-axes titles
fig.update_yaxes(title_text="Numero Dosi Somministrate", secondary_y=False)
fig.update_yaxes(title_text="Totale Dosi Somministrate", range=[0, 1.3*somministrazioniGiorno['Totale'].cumsum().max()],secondary_y=True)
fig.update_yaxes()
st.write(fig)

####################ANALISI REGIONALE#################
regione = st.multiselect('Seleziona una o più regioni per visualizzare il grafico.', options=somministrazioni.Regione.unique())

regioniConfronto = make_subplots(specs=[[{"secondary_y": True}]])
# regioniConfronto.add_trace(
#     go.Scatter(
#         name = 'Somministrazioni Totali Italia',
#         x = somministrazioniGiorno.index,
#         y = somministrazioniGiorno['Totale'].cumsum()
#     )
# )

for i in regione:
    regioneSelezionata = somministrazioniFilterData[somministrazioni.Regione==i]
    regioniConfronto.add_trace(
        go.Scatter(
            name = 'Somministrazioni {}'.format(i),
            x = regioneSelezionata['Data Somministrazione'],
            y = regioneSelezionata['Totale'].cumsum()
        )
    )
regioniConfronto.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))
st.write(regioniConfronto, use_container_width=True)
######################################################