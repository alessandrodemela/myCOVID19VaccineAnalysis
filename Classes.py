import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os, datetime
from grafici import SomministrazioniGiornoDose, ScatterAnagrafica, RadarAnagrafica, AnagraficaPlot, BarPercSomministrazioni



# from plotly.subplots import make_subplots
# import plotly.graph_objects as go

DWpath = 'DW'

somministrazioniAnagr = pd.read_csv(os.path.join(DWpath,'anagrafica.csv'))
somministrazioni = pd.read_csv(os.path.join(DWpath,'somministrazioniSummary.csv'))
consegne = pd.read_csv(os.path.join(DWpath,'consegne.csv'))

with open('lastupdate', 'r') as fin:
    lastupdate = fin.read().strip().split('/')
    lastupdate = datetime.date(day=int(lastupdate[0]), month=int(lastupdate[1]), year=int(lastupdate[2]))
    reformatLastUpdate = lastupdate.strftime('%d/%m/%Y')

def Header():
    st.title('Report vaccinazioni COVID-19')

    st.markdown('***')
    st.markdown(
        f'Ultimo Aggiornamento {reformatLastUpdate}.  '
        '\nIl codice di analisi è disponibile [qui](https://github.com/alessandrodemela/myCOVID19VaccineAnalysis).  '
        '\nMentre i dati sono reperibili nel [repository ufficiale](https://github.com/italia/covid19-opendata-vaccini).'
        )
    st.markdown('***')

    st.markdown('La somministrazione dei vaccini contro la COVID-19, è cominciata il 27/12/2020 [\[1\]]'
                '(http://www.salute.gov.it/portale/news/p3_2_1_1_1.jsp?lingua=italiano&menu=notizie&p=dalministero&id=5242).'
                #'\nNella tabella seguente si mostrano il numero di somministrazioni ordinato per data, nelle varie regioni'
                #' e suddiviso per sesso e categoria sociale, oltre che per tipo di sommnistrazione.'
                )

    totSomministrate = somministrazioniAnagr.Totale.sum()
    totPrime = somministrazioniAnagr['Prima Dose'].sum()
    totSeconde = somministrazioniAnagr['Seconda Dose'].sum()
    platea = somministrazioniAnagr.Platea.sum()
    percPrime = round(totPrime/platea,4)
    percSeconde = round(totSeconde/platea,4)
    totConsegne = consegne['Numero Dosi'].sum()
    percConsegne = totSomministrate/totConsegne
    #lastSomministrate = 
    st.markdown(
        f'Al {reformatLastUpdate} sono state distribuite **{totSomministrate:,}** dosi di vaccino, suddivise in **{totPrime:,}** prime dosi'
        f' e **{totSeconde:,}** seconde dosi. La percentuale di persone che ha ricevuto almeno una dose è '
        f' del **{percPrime:.2%}**, mentre il **{percSeconde:.2%}** della popolazione ha ricevuto entrambe le dosi.'
    )

    st.markdown(
        f'Sono state consegnate **{totConsegne:,}** dosi e la percentuale di somministrazione è pari al **{percConsegne:.2%}**.'
    )


class Somministrazioni:

    __somministrazioni = pd.read_csv(os.path.join(DWpath,'somministrazioniSummary.csv'))

    def __header(self):
        st.header('Dosi Somministrate per giorno')
        st.write(
            "Dosi somministrate quotidianamente, la data odierna potrebbe contenere un dato parziale."
        )

    def __getRelevantColumns(self):
        somministrazioniCol = self.__somministrazioni.loc[:,['Data Somministrazione','Prima Dose','Seconda Dose']].groupby('Data Somministrazione').sum()
        somministrazioniCol['Totale'] = somministrazioniCol.sum(axis=1)

        return somministrazioniCol

    def __DateRange(self,df):
        dateRange = pd.to_datetime(df.index).date
        start, end = st.select_slider(
            "Seleziona un intervallo temporale",
            value=[dateRange[0],dateRange[-1]],
            options=list(dateRange)
        )

        return start,end

    def Analisi(self,):
        self.__header()

        somministrazioniCol = self.__getRelevantColumns()

        startDate, endDate = self.__DateRange(somministrazioniCol)

        somministrazioniFilterData = somministrazioniCol[  
            (pd.to_datetime(somministrazioniCol.index).date >= startDate )
            & (pd.to_datetime(somministrazioniCol.index).date <= endDate)   
            ]

        fig = SomministrazioniGiornoDose(somministrazioniFilterData)

        st.write(fig)

def Anagrafica():

    anagrafica = pd.read_csv(os.path.join(DWpath,'anagrafica.csv'))

    anagrafica = anagrafica.drop(columns='Unnamed: 0')

    pltAnaDosi = ScatterAnagrafica(anagrafica)

    fig2 = RadarAnagrafica(anagrafica)

    fig3 = AnagraficaPlot(anagrafica)

    return pltAnaDosi, fig2, fig3

class AnalisiRegionale:

    __somministrazioni = pd.read_csv(os.path.join(DWpath,'somministrazioniSummary.csv'))

    def __header(self,):
        st.header('Analisi Regionale')
        st.write(
            "Vediamo ora la situazione vaccinale nelle regioni italiane. Il primo grafico mostra la percentuale di dosi somministrate da ciascuna regione."
        )

    def __getAbitanti(self,):
        abitantiRegioni = pd.read_csv('DCIS_POPRES1_25022021122609782.csv')
        abitantiRegioni = abitantiRegioni.iloc[:,[1,5,6,9,12]].sort_values(['Territorio','Sesso']
                                                            ).where((abitantiRegioni['Stato civile']=='totale') &
                                                            (abitantiRegioni.Sesso=='totale') &
                                                            (abitantiRegioni.ETA1=='TOTAL')
                                                            ).dropna().iloc[:,[0,-1]].set_index('Territorio')
        # Rename field and indexfor better naming
        abitantiRegioni = abitantiRegioni.rename(columns={'Value': 'Abitanti'}).rename_axis('Regione').astype(int)

        return abitantiRegioni

    def Analisi(self,):
        self.__header()

        abitantiRegioni = self.__getAbitanti()

        # Get Relevant Columns
        somministrazioniGiornoRegione = somministrazioni.loc[:,['Data Somministrazione','Prima Dose','Seconda Dose','Regione']].groupby(['Regione','Data Somministrazione']).sum()
        
        somministrazioniRegione = somministrazioniGiornoRegione.groupby('Regione').sum()
        somministrazioniRegione['Totale'] = somministrazioniRegione.sum(axis=1)
        somministrazioniRegione=somministrazioniRegione.join(abitantiRegioni)

        somministrazioniRegione['% Somministrazioni'] =  round(100 * somministrazioniRegione['Totale']/somministrazioniRegione['Abitanti'],2)
        somministrazioniRegione['% Prima Dose'] =  round(100 * somministrazioniRegione['Prima Dose']/somministrazioniRegione['Abitanti'],2)
        somministrazioniRegione['% Seconda Dose'] =  round(100 * somministrazioniRegione['Seconda Dose']/somministrazioniRegione['Abitanti'],2)

        st.write(somministrazioniRegione)

       # regione = st.multiselect('Seleziona una o più regioni per visualizzare il grafico.', options=somministrazioniRegione.index)

        st.write(BarPercSomministrazioni(somministrazioniRegione))

