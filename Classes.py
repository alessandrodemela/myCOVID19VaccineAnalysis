import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import os
from datetime import datetime as dt
#from grafici import SomministrazioniGiornoDose, ScatterAnagrafica, RadarAnagrafica, AnagraficaPlot, BarPercSomministrazioni
from grafici import *

plt.rcParams["font.family"] = "Gill Sans"
plt.rcParams.update({'font.size': 25})

# from plotly.subplots import make_subplots
# import plotly.graph_objects as go

mapRegioni = {
    'Abruzzo'                   : 'Abruzzo',
    'Basilicata'                : 'Basilicata',
    'Bolzano'                   : 'Provincia Autonoma Bolzano / Bozen',
    'Provincia autonoma Bolzano': 'Provincia Autonoma Bolzano / Bozen',
    'Calabria'                  : 'Calabria',
    'Campania'                  : 'Campania',
    'Emilia-Romagna'            : 'Emilia-Romagna',
    'Friuli Venezia Giulia'     : 'Friuli-Venezia Giulia',
    'Lazio'                     : 'Lazio',
    'Liguria'                   : 'Liguria',
    'Lombardia'                 : 'Lombardia',
    'Marche'                    : 'Marche',
    'Molise'                    : 'Molise',
    'Piemonte'                  : 'Piemonte',
    'Puglia'                    : 'Puglia',
    'Sardegna'                  : 'Sardegna',
    'Sicilia'                   : 'Sicilia',
    'Toscana'                   : 'Toscana',
    'Trento'                    : 'Provincia Autonoma Trento',
    'Provincia autonoma Trento' : 'Provincia Autonoma Trento',
    'Umbria'                    : 'Umbria',
    "Valle d'Aosta"             : "Valle d'Aosta / Vallée d'Aoste",
    'Veneto'                    : 'Veneto'
}


def Header(self):

    st.title('Report vaccinazioni COVID-19')

    st.markdown('***')
    st.markdown(
        f'Ultimo Aggiornamento {self.readableDate}.  '
        '\nIl codice di analisi è disponibile [qui](https://github.com/alessandrodemela/myCOVID19VaccineAnalysis).  '
        '\nMentre i dati sono reperibili nel [repository ufficiale](https://github.com/italia/covid19-opendata-vaccini).'
        )
    st.markdown('***')

    st.markdown('La somministrazione dei vaccini contro la COVID-19, è cominciata il 27/12/2020 [\[1\]]'
                '(http://www.salute.gov.it/portale/news/p3_2_1_1_1.jsp?lingua=italiano&menu=notizie&p=dalministero&id=5242).'
                )

    totSomministrate = self.tblSomministrazioni.Totale.sum()
    totPrime = self.tblSomministrazioni['Prima Dose'].sum()
    totSeconde = self.tblSomministrazioni['Seconda Dose'].sum()
    platea = self.tblInfoAnagrafica['Totale Generale'].sum()
    percPrime = round(totPrime/platea,4)
    percSeconde = round(totSeconde/platea,4)

    totConsegne = self.tblConsegne['Numero Dosi'].sum()
    percConsegne = totSomministrate/totConsegne

    ultimeConsegne = self.tblConsegne.groupby('Data Consegna').sum()[-1:].reset_index()
    dataUltimaConsegna = ultimeConsegne.iloc[0,0].strftime('%d/%m/%Y')
    qtaUltimaConsegna = ultimeConsegne.iloc[0,1]

    ultimeSomministrazioni = self.tblSomministrazioni.groupby('Data Somministrazione').sum().reset_index().iloc[-7:,[0,-1]]
    dataUltimeSomministrazioni = ultimeSomministrazioni['Data Somministrazione'].iloc[-1].strftime('%d/%m/%Y')
    qtaUltimeSomministrazioni = ultimeSomministrazioni.iloc[-1,1]
    qtaUltimeSomministrazioniWeek = int(ultimeSomministrazioni['Totale'].mean())

    st.markdown(
        f'Al {self.readableDate} sono state somministrate **{totSomministrate:,}** dosi di vaccino, suddivise in **{totPrime:,}** prime dosi'
        f' e **{totSeconde:,}** seconde dosi (ciclo completo). La percentuale di persone che ha ricevuto almeno una dose è '
        f' del **{percPrime:.2%}**, mentre il **{percSeconde:.2%}** della popolazione ha ricevuto entrambe le dosi.'
    )

    st.markdown(
        f'Sono state consegnate **{totConsegne:,}** dosi e la percentuale di somministrazione è pari al **{percConsegne:.2%}**.'
    )

    st.markdown(
        f"Il giorno **{dataUltimeSomministrazioni}** sono state somministrate **{qtaUltimeSomministrazioni:,}** dosi, mentre nell'"
        f"ultima settimana sono state somministrate in media **{qtaUltimeSomministrazioniWeek:,}** dosi."
    )
    st.markdown(f"L'ultima consegna è avvenuta il **{dataUltimaConsegna}** con **{qtaUltimaConsegna:,}** dosi.")

    st.subheader('Indicatori')
    fig, axs = plt.subplots(3,2, figsize=(15,7))
    KPI = {
            'Dosi Somministrate Totali' : totSomministrate,
            'Ultime Somministrazioni'   : qtaUltimeSomministrazioni,
            'Dosi Consegnate Totali'    : totConsegne,
            'Ultime Consegne'           : qtaUltimaConsegna,
            'Prime Dosi'                : totPrime,
            'Seconde Dosi'              : totSeconde,
    }
    for ax,i in zip(axs.ravel(),KPI.items()):
        ax.set_facecolor('xkcd:white')
        ax.tick_params(axis='x', colors='w')
        ax.tick_params(axis='y', colors='w')
        ax.text(0.5,0.9,i[0],font='Gill Sans',size=20,ha='center',va='center')
        ax.text(0.5,0.5,'{:,}'.format(i[1]),font='Gill Sans',size=50,ha='center',va='center')

    plt.tight_layout()

    st.write(fig)

    
    st.subheader('Dosi consegnate e somministrate per fornitore.')
    cDF = pd.DataFrame(self.tblConsegne.groupby('Fornitore').sum()).rename(columns={'Numero Dosi': 'Dosi Consegnate'})
    sDF = pd.DataFrame(self.tblSomministrazioni.groupby('Fornitore').sum()['Totale']).rename(columns={'Totale': 'Dosi Somministrate'})
    df = pd.concat([cDF,sDF],axis=1)
    df['% Somministrate/Consegnate'] = round(100 * df['Dosi Somministrate']/df['Dosi Consegnate'],2)
    st.write(df.T.style.format('{:,}'))

    st.subheader('Dosi somministrate da ciascuna regione.')
    st.write(self.tblSomministrazioni[['Regione/P.A.','Totale']].groupby('Regione/P.A.').sum().T.style.format('{:,}'))
    

class DataModel:
    def __init__(self):
        '''Load raw data from GitHub'''
        # somministrazioni
        self.tblSomministrazioni = pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv')
        # consegne
        self.tblConsegne = pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/consegne-vaccini-latest.csv')
        # anagrafica
        self.tblInfoAnagrafica = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-statistici-riferimento/popolazione-istat-regione-range.csv')
        # aree
        self.tblAree = gpd.read_file('aree/shp/dpc-covid-19-ita-aree-nuove-g.shp')

        # ultimo aggiornamento
        self.lastUpdateDataset = pd.read_json('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/last-update-dataset.json', typ='series')[0].to_pydatetime()
        self.readableDate = self.lastUpdateDataset.date().strftime('%d/%m/%Y')


        self.mapFornitore = {
            'Pfizer/BioNTech': 'Pfizer/BioNTech',
            'Moderna': 'Moderna',
            'Vaxzevria (AstraZeneca)' : 'Vaxzevria' 
        }

        self.ETL()

    def createNameMappingDict(self,df):
        '''This function returns a dictionary which helps mapping columns names in a DataFrame'''
        nameMappingDict = {oldName : oldName.replace('_',' ').title().replace('Categoria', '').replace('Nome Area', 'Regione/P.A.').replace('Denominazione Regione', 'Regione/P.A.') for oldName in df.columns}
        return nameMappingDict
    
    def ETL(self):
        '''ETL function to create clean tables'''

        # TABELLA DELLE SOMMINISTRAZIONI (fatti)
        self.tblSomministrazioni = self.tblSomministrazioni.rename(columns=self.createNameMappingDict(self.tblSomministrazioni))
        self.tblSomministrazioni['Totale'] = self.tblSomministrazioni[['Prima Dose','Seconda Dose']].sum(axis=1)
        self.tblSomministrazioni = self.tblSomministrazioni.drop(columns=['Codice Nuts1', 'Codice Nuts2', 'Codice Regione Istat', 'Area'])
        self.tblSomministrazioni['Data Somministrazione'] = pd.to_datetime(self.tblSomministrazioni['Data Somministrazione']).dt.date
        
        self.tblSomministrazioni['Fornitore'] = self.tblSomministrazioni['Fornitore'].map(self.mapFornitore)


        # TABELLA DELLE CONSEGNE
        self.tblConsegne = self.tblConsegne.rename(columns=self.createNameMappingDict(self.tblConsegne))   
        self.tblConsegne = self.tblConsegne.iloc[:,[1,2,3,7]]
        self.tblConsegne['Data Consegna'] = pd.to_datetime(self.tblConsegne['Data Consegna']).dt.date
        self.tblConsegne['Fornitore'] = self.tblConsegne['Fornitore'].map(self.mapFornitore)

        # TABELLA JOIN CONSEGNE SOMMINISTRAZIONI
        self.tblSomministrazioniConsegne = pd.DataFrame(
            self.tblSomministrazioni.groupby('Data Somministrazione').sum()['Totale']
            ).rename(
                columns={'Totale': 'Dosi Somministrate'}
                ).join(
                    self.tblConsegne.groupby('Data Consegna').sum().rename(columns={'Numero Dosi': 'Dosi Consegnate'})
                    ).cumsum().fillna(method='ffill')
        self.tblSomministrazioniConsegne['% Somministrazioni/Consegne'] = (self.tblSomministrazioniConsegne['Dosi Somministrate'] / self.tblSomministrazioniConsegne['Dosi Consegnate'] * 100).rolling(7).mean().fillna(method='bfill')

        # TABELLA ANAGRAFICA
        self.tblInfoAnagrafica = self.tblInfoAnagrafica.rename(columns=self.createNameMappingDict(self.tblInfoAnagrafica))
        self.tblInfoAnagrafica = self.tblInfoAnagrafica.iloc[:,[4,6,7,8,9,10,11]]
        self.tblInfoAnagrafica = self.tblInfoAnagrafica.where(self.tblInfoAnagrafica['Range Eta']!='0-15').dropna()
        self.tblInfoAnagrafica['Regione/P.A.'] = self.tblInfoAnagrafica['Regione/P.A.'].map(mapRegioni)
        

        # TABELLA AREE
        self.tblAree['nomeTesto'] = self.tblAree['nomeTesto'].map(mapRegioni)
        self.tblAree = self.tblAree[['nomeTesto','geometry']].set_index('nomeTesto')
        self.tblAree = self.tblAree[:21]

        # TABELLA COMPLESSIVA REGIONI
        self.tblFullRegioni = self.tblInfoAnagrafica.groupby('Regione/P.A.').sum().iloc[:,2:].join(self.tblSomministrazioni.groupby('Regione/P.A.').sum())
        self.tblFullRegioni = self.tblFullRegioni.join(self.tblConsegne.groupby('Regione/P.A.').sum()).rename(columns={'Numero Dosi': 'Numero Dosi Consegnate'})
        self.tblFullRegioni['% Dosi Somministrate/Dosi Consegnate'] = round(self.tblFullRegioni['Totale']/self.tblFullRegioni['Numero Dosi Consegnate'] *100,2)
        self.tblFullRegioni['% Prima Dose'] = round(self.tblFullRegioni['Prima Dose']/self.tblFullRegioni['Totale Generale'] *100,2)
        self.tblFullRegioni['% Seconda Dose'] = round(self.tblFullRegioni['Seconda Dose']/self.tblFullRegioni['Totale Generale'] *100,2)
        self.tblFullRegioni['% Totale'] = round(self.tblFullRegioni['Totale']/self.tblFullRegioni['Totale Generale'] *100,2)
        self.tblFullRegioni['% Dosi Consegnate/Abitanti'] = round(self.tblFullRegioni['Numero Dosi Consegnate']/self.tblFullRegioni['Totale Generale']*100,2)

        self.tblAree = self.tblAree.join(self.tblFullRegioni)


class Somministrazioni(DataModel):

    def __init__(self):
        '''Creating Views'''
        super(Somministrazioni, self).__init__()

        self.VwSomministrazioniGiorno = self.tblSomministrazioni.groupby('Data Somministrazione').sum()[['Prima Dose','Seconda Dose','Totale']]
        self.VwSomministrazioniGiornoFornitore = self.tblSomministrazioni.groupby(['Data Somministrazione', 'Fornitore']).sum().unstack(level=1)[['Prima Dose','Seconda Dose']].fillna(0).astype(int)
        self.VwSomministrazioniCategoria = self.tblSomministrazioni.iloc[:,[1,5,6,7,8,9,10,11]].groupby('Fornitore').sum()

        print(self.tblSomministrazioni)

    def Analisi(self):
        st.header('Analisi Dosi Somministrate')
        st.subheader('Analisi Temporale')
        st.write(
            "Questa sezione contiene l'analisi delle dosi somministrate quotidianamente, la data odierna potrebbe contenere un dato parziale. "
            "Inoltre, si riporta anche la distribuzione temporale delle somministrazioni divisa per fornitore di vaccino."
        )

        # Plot andamento giornaliero
        plt_somministrazioniGiorno = makePlot_SomministrazioniGiorno(self.VwSomministrazioniGiorno)
        st.write(plt_somministrazioniGiorno)

        # Plot andamento giornaliero per fornitore
        plt_somministrazioniGiornoFornitore = makePlot_SomministrazioniGiornoFornitore(self.VwSomministrazioniGiornoFornitore)
        st.write(plt_somministrazioniGiornoFornitore)

        # Plot consegne e somministrazioni
        plt_ConsegneSomministrazioni = makePlot_ConsegneSomministrazioni(self.tblSomministrazioniConsegne)
        st.write(plt_ConsegneSomministrazioni)

        st.subheader('Analisi sul tipo di vaccino somministrato')
        st.markdown(
            "L'analisi successiva mostra, in funzione dell'azienda fornitrice, quali e quanti vaccini vengano somministrati a quale categoria sociale e viceversa a chi sono somministrati i diversi vaccini."
            " La categoria `Over 80` non contiene tutta la popolazione di età superiore a 80 anni, ma rappresenta la popolazione chiamata al vaccino"
            " per il fatto di avere più di 80 anni. La platea over 80 rimanente potrebbe essere stata convocata per altre cause."
        )
        # Plot somministrazioni per categoria
        plt_somministrazioniCategoria = makePlot_SomministrazioniCategoria(self.VwSomministrazioniCategoria)
        st.write(plt_somministrazioniCategoria)

        #Plot somministrazioni per fornitore
        plt_somministrazioniFornitori = makePlot_SomministrazioniFornitori(self.VwSomministrazioniCategoria.T)
        st.write(plt_somministrazioniFornitori)


class Anagrafica(DataModel):
    def __init__(self):
        '''Creating Views'''
        super(Anagrafica, self).__init__()

        self.VwTotaleFascia = self.tblSomministrazioni.groupby(['Fascia Anagrafica']).sum()[['Totale','Sesso Maschile','Sesso Femminile','Prima Dose', 'Seconda Dose']].join(self.tblInfoAnagrafica.groupby('Range Eta').sum()['Totale Generale'])
        self.VwFornitoreFascia = self.tblSomministrazioni.groupby(['Fascia Anagrafica','Fornitore']).sum().unstack(level=1)[['Totale']]

    def Analisi(self):
        st.header('Analisi Anagrafica della somministrazione')
        st.markdown(
            'I grafici seguenti, in funzione dell\'età anagrafica mostrano il numero di somministrazioni effettuate.\n' 
            '1. Il primo mostra le somministrazioni totali per età   '
            '1. Il secondo è diviso per sesso   '
            '1. Il terzo è suddiviso per vaccino somministrato   '
            '1. Il quarto evidenzia il numero di dosi somministrate   '
    )

        # Plot anagrafica Totale
        plt_Anagrafica = makePlot_AnalisiAnagraficaTotale(self.VwTotaleFascia, self.VwFornitoreFascia)
        st.write(plt_Anagrafica)

        


class Regionale(DataModel):
    def __init__(self):
        '''Creating Views'''
        super(Regionale, self).__init__()


    def Analisi(self):
        st.markdown('***')
        st.header('Analisi Regionale delle somministrazioni')
        st.markdown(
            'Questa è un\'analisi delle dosi somministrate e consegnate in ogni regione.<br>  '
            'Il primo e il secondo grafico mostrano, rispettivamente, la percentuale di prime e seconde dosi somministrate sulla popolazione della regione.<br>  '
            'Il terzo mostra la percentuale di dose consegnate a ciascuna regione in base alla loro popolazione. <br>'
            'Il quarto mostra il rapporto percentuale fra dosi somministrate e dose consegnate a ciascuna regione.',
            unsafe_allow_html=True
        )

        # 4 Plot sulle somministrazioni
        plt_Regioni = makePlot_Regioni(self.tblAree)
        st.write(plt_Regioni)

        # 4 Plot sulle somministrazioni
        plt_Gartner = makePlot_MockGartner(self.tblAree)
       # st.write(plt_Gartner)

        st.write(self.tblFullRegioni.iloc[:,-4:])
