import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime as dt
#from grafici import SomministrazioniGiornoDose, ScatterAnagrafica, RadarAnagrafica, AnagraficaPlot, BarPercSomministrazioni
from grafici import *

plt.rcParams["font.family"] = "Gill Sans"
plt.rcParams.update({'font.size': 25})

# from plotly.subplots import make_subplots
# import plotly.graph_objects as go


def Header():
    dm = DataModel()

    st.title('Report vaccinazioni COVID-19')

    st.markdown('***')
    st.markdown(
        f'Ultimo Aggiornamento {dm.readableDate}.  '
        '\nIl codice di analisi è disponibile [qui](https://github.com/alessandrodemela/myCOVID19VaccineAnalysis).  '
        '\nMentre i dati sono reperibili nel [repository ufficiale](https://github.com/italia/covid19-opendata-vaccini).'
        )
    st.markdown('***')

    st.markdown('La somministrazione dei vaccini contro la COVID-19, è cominciata il 27/12/2020 [\[1\]]'
                '(http://www.salute.gov.it/portale/news/p3_2_1_1_1.jsp?lingua=italiano&menu=notizie&p=dalministero&id=5242).'
                )

    totSomministrate = dm.tblSomministrazioni.Totale.sum()
    totPrime = dm.tblSomministrazioni['Prima Dose'].sum()
    totSeconde = dm.tblSomministrazioni['Seconda Dose'].sum()
    platea = dm.tblInfoAnagrafica['Totale Generale'].sum()
    percPrime = round(totPrime/platea,4)
    percSeconde = round(totSeconde/platea,4)

    totConsegne = dm.tblConsegne['Numero Dosi'].sum()
    percConsegne = totSomministrate/totConsegne

    ultimeConsegne = dm.tblConsegne.groupby('Data Consegna').sum()[-1:].reset_index()
    dataUltimaConsegna = ultimeConsegne.iloc[0,0].strftime('%d/%m/%Y')
    qtaUltimaConsegna = ultimeConsegne.iloc[0,1]

    ultimeSomministrazioni = dm.tblSomministrazioni.groupby('Data Somministrazione').sum().reset_index().iloc[-7:,[0,-1]]
    dataUltimeSomministrazioni = ultimeSomministrazioni['Data Somministrazione'].iloc[-1].strftime('%d/%m/%Y')
    qtaUltimeSomministrazioni = ultimeSomministrazioni.iloc[0,1]
    qtaUltimeSomministrazioniWeek = int(ultimeSomministrazioni['Totale'].mean())

    st.markdown(
        f'Al {dm.readableDate} sono state somministrate **{totSomministrate:,}** dosi di vaccino, suddivise in **{totPrime:,}** prime dosi'
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

    
    st.subheader('Dosi consegnate per fornitore.')
    st.write(dm.tblConsegne.groupby('Fornitore').sum().T.style.format('{:,}'))

    st.subheader('Dosi somministrate da ciascuna regione.')
    st.write(dm.tblSomministrazioni[['Regione/P.A.','Totale']].groupby('Regione/P.A.').sum().T.style.format('{:,}'))
    

class DataModel:
    def __init__(self):
        '''Load raw data from GitHub'''
        # somministrazioni
        self.tblSomministrazioni = pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv')
        # consegne
        self.tblConsegne = pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/consegne-vaccini-latest.csv')
        # anagrafica
        self.tblInfoAnagrafica = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-statistici-riferimento/popolazione-istat-regione-range.csv')


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
        nameMappingDict = {oldName : oldName.replace('_',' ').title().replace('Categoria', '').replace('Nome Area', 'Regione/P.A.') for oldName in df.columns}
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

        # TABELLA ANAGRAFICA
        self.tblInfoAnagrafica = self.tblInfoAnagrafica.rename(columns=self.createNameMappingDict(self.tblInfoAnagrafica))
        self.tblInfoAnagrafica = self.tblInfoAnagrafica.iloc[:,[4,6,7,8,9,10,11]]
        self.tblInfoAnagrafica = self.tblInfoAnagrafica.where(self.tblInfoAnagrafica['Range Eta']!='0-15').dropna()


class Somministrazioni(DataModel):

    def __init__(self):
        '''Creating Views'''
        super(Somministrazioni, self).__init__()

        self.VwSomministrazioniGiorno = self.tblSomministrazioni.groupby('Data Somministrazione').sum()[['Prima Dose','Seconda Dose','Totale']]
        self.VwSomministrazioniGiornoFornitore = self.tblSomministrazioni.groupby(['Data Somministrazione', 'Fornitore']).sum().unstack(level=1)[['Prima Dose','Seconda Dose']].fillna(0).astype(int)
        self.VwSomministrazioniCategoria = self.tblSomministrazioni.iloc[:,[1,5,6,7,8,9,10,11]].groupby('Fornitore').sum()

        print(self.tblSomministrazioni)

    def Analisi(self):
        st.header('Dosi Somministrate per giorno')
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
            'I grafici seguenti, in funzione dell\'età anagrafica mostrano il numero di somministrazioni effettuate.' 
            '1. Il primo mostra le somministrazioni totali per età   '
            '1. Il secondo è diviso per sesso   '
            '1. Il terzo è suddiviso per vaccino somministrato   '
            '1. Il quarto evidenzia il numero di dosi somministrate   '
    )

        # Plot anagrafica Totale
        plt_Anagrafica = makePlot_AnalisiAnagraficaTotale(self.VwTotaleFascia, self.VwFornitoreFascia)
        st.write(plt_Anagrafica)






# with open('lastupdate', 'r') as fin:
#     lastupdate = fin.read().strip().split('/')
#     lastupdate = datetime.date(day=int(lastupdate[0]), month=int(lastupdate[1]), year=int(lastupdate[2]))
#     dm.readableDate = lastupdate.strftime('%d/%m/%Y')




#




# def Anagrafica():

#     anagrafica = pd.read_csv(os.path.join(DWpath,'anagrafica.csv'))
#     somministrazioni = pd.read_csv(os.path.join(DWpath,'somministrazioni.csv'))

#     somministrazioni = somministrazioni.loc[:,['Fornitore','Fascia Anagrafica', 'Totale']]

#     somministrazioni['Fornitore'] = somministrazioni['Fornitore'].map({
#                 'Pfizer/BioNTech': 'Pfizer/BioNTech',
#                 'Moderna': 'Moderna',
#                 'Vaxzevria (AstraZeneca)' : 'Vaxzevria' 
#                 }
#         )

#     totaleRange=pd.read_csv('Staging/popolazione-istat-regione-range.csv')
#     totaleRange = totaleRange.groupby('range_eta').sum().reset_index().loc[1:,['range_eta','totale_generale']]

#     anagrafica.drop(columns='Unnamed: 0', inplace=True)
#     #######
#     fig, axs = plt.subplots(nrows=2,ncols=2, figsize=(15,15))
#     axs = axs.ravel()

#     anagrafica.plot.bar(
#         x='Fascia Anagrafica', 
#         y='Totale',  
#         title='Distribuzione vaccini per fascia anagrafica',
#         legend=False,
#         color='royalblue',
#         ax=axs[0],
#         width=.9,
#         fontsize=15,
#         rot=0
#     )

#     anagrafica.plot.bar(
#         x='Fascia Anagrafica', 
#         y=['Sesso Maschile', 'Sesso Femminile'],
#         stacked=True,
#         title='Distribuzione vaccini per fascia anagrafica\n e sesso',
#         ax=axs[1],
#         color=['steelblue','coral'],
#         width=.9,
#         fontsize=15,
#         rot=0
#     )

#     somministrazioni = somministrazioni.groupby(['Fascia Anagrafica','Fornitore']).sum()
#     somministrazioni = somministrazioni.unstack(level=1)
#     somministrazioni['Totale'].plot.bar(
#         stacked=True, 
#         ax=axs[2],
#         title='Distribuzione vaccini per fascia anagrafica\n e categoria sociale',
#         color=['tomato','cornflowerblue','gold'],
#         width=.9,
#         fontsize=15,
#         rot=0
#     )
#     axs[2].legend([i + ' ' + j for i,j in somministrazioni.keys()],loc='upper left')

#     axs[3].bar( 
#         x=totaleRange['range_eta'],
#         height=anagrafica['Totale Generale'],
#         alpha=.3,
#         label='Totale Generale'
#     )
#     anagrafica.plot.bar(
#         x='Fascia Anagrafica', 
#         y=['Prima Dose', 'Seconda Dose'],
#         stacked=False,
#         title='Distribuzione vaccini per fascia anagrafica\n e dose ricevuta',
#         ax=axs[3],
#         color=['cornflowerblue','salmon'],
#         width=.9,
#         fontsize=15,
#         rot=0
#     )

#     for i in axs: 
#         i.grid(lw=.2)
#         i.title.set_size(20)
#         i.set_ylabel('Totale Somministrazioni')
#         i.legend(loc='upper left', fontsize=15)
#     plt.tight_layout()
#     st.write(fig)
#     st.write(anagrafica)
#     st.markdown(
#         'Il grafico in basso a destra mostra anche la platea di riferimento (popolazione in una determinata fascia di età) oltre alla dose di vaccino somministrata'
#     )
#     #####

#     #pltAnaDosi = ScatterAnagrafica(anagrafica)

#     #fig2 = RadarAnagrafica(anagrafica)

#     #fig3 = AnagraficaPlot(anagrafica)

#     #return pltAnaDosi, fig2, fig3

# class AnalisiRegionale:

#     __somministrazioni = pd.read_csv(os.path.join(DWpath,'somministrazioniSummary.csv')).drop(columns='Unnamed: 0')
#     __regioniInfo = pd.read_csv(os.path.join(DWpath,'regioniInfo.csv'))


#     def __header(self,):
#         st.header('Analisi Regionale')
#         st.write(
#             "Vediamo ora la situazione vaccinale nelle regioni italiane. Il primo grafico mostra la percentuale di dosi somministrate da ciascuna regione."
#         )

#     def Analisi(self,):
#         self.__header()

#         # Get Relevant Columns
#         somministrazioniGiornoRegione = self.__somministrazioni.loc[:,['Data Somministrazione','Prima Dose','Seconda Dose','Regione']].groupby(['Regione','Data Somministrazione']).sum()
        
#         somministrazioniRegione = somministrazioniGiornoRegione.groupby('Regione').sum()
#         somministrazioniRegione['Totale'] = somministrazioniRegione.sum(axis=1)
#         somministrazioniRegione=somministrazioniRegione.reset_index()

#         somministrazioniRegione=somministrazioniRegione.merge(self.__regioniInfo).set_index('Regione')

#         somministrazioniRegione['% Somministrazioni'] =  round(100 * somministrazioniRegione['Totale']/somministrazioniRegione['Abitanti'],2)
#         somministrazioniRegione['% Prima Dose'] =  round(100 * somministrazioniRegione['Prima Dose']/somministrazioniRegione['Abitanti'],2)
#         somministrazioniRegione['% Seconda Dose'] =  round(100 * somministrazioniRegione['Seconda Dose']/somministrazioniRegione['Abitanti'],2)

#         st.write(somministrazioniRegione[['Totale','% Prima Dose','% Seconda Dose']])

#        # regione = st.multiselect('Seleziona una o più regioni per visualizzare il grafico.', options=somministrazioniRegione.index)

#         st.write(BarPercSomministrazioni(somministrazioniRegione))

#         # mapData = pd.DataFrame(somministrazioniRegione[['lat','lon','% Prima Dose','% Seconda Dose']])
#         # st.map(mapData)


