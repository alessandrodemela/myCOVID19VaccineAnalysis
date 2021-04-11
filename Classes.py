import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os, datetime
from grafici import SomministrazioniGiornoDose, ScatterAnagrafica, RadarAnagrafica, AnagraficaPlot, BarPercSomministrazioni

plt.rcParams["font.family"] = "Gill Sans"
plt.rcParams.update({'font.size': 25})

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
    platea = somministrazioniAnagr['Totale Generale'].sum()
    percPrime = round(totPrime/platea,4)
    percSeconde = round(totSeconde/platea,4)
    totConsegne = consegne['Numero Dosi'].sum()
    percConsegne = totSomministrate/totConsegne
    #lastSomministrate = 
    st.markdown(
        f'Al {reformatLastUpdate} sono state somministrate **{totSomministrate:,}** dosi di vaccino, suddivise in **{totPrime:,}** prime dosi'
        f' e **{totSeconde:,}** seconde dosi. La percentuale di persone che ha ricevuto almeno una dose è '
        f' del **{percPrime:.2%}**, mentre il **{percSeconde:.2%}** della popolazione ha ricevuto entrambe le dosi.'
    )

    st.markdown(
        f'Sono state consegnate **{totConsegne:,}** dosi e la percentuale di somministrazione è pari al **{percConsegne:.2%}**.'
    )


class Somministrazioni:

    __somministrazioni = pd.read_csv(os.path.join(DWpath,'somministrazioniSummary.csv')).drop(columns='Unnamed: 0')
    __somministrazioni['Fornitore'] = __somministrazioni['Fornitore'].map(
            {
                'Pfizer/BioNTech': 'Pfizer/BioNTech',
                'Moderna': 'Moderna',
                'Vaxzevria (AstraZeneca)' : 'Vaxzevria' 
                }
        )

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

        #######
        fig, ax = plt.subplots(1,1)
        somministrazioniFilterData.plot.bar(
            stacked=True,
            y=['Prima Dose', 'Seconda Dose'],
            title='Dose Somministrata',
            ylabel='Dosi giornaliere somministrate',
            color=['cornflowerblue','darksalmon'],
            width=.9,
            rot=0,
            ax=ax,
            fontsize=15,
            figsize=(15,8)
        )
        ax.plot( somministrazioniFilterData['Totale'].rolling(7).mean().fillna(somministrazioniFilterData['Totale'][:7].mean()),
            lw=3,
            color='forestgreen',
            label='Totale Somministrazioni Giornaliere (Media Mobile 7gg)'
        )

        ax.set_xticks(np.arange(0,(plt.xlim()[1]),12))
        ax.grid(lw=.2)
        ax.legend(fontsize=14)
        st.write(fig)

        ####

        st.markdown('Oltre alla divisione per dose, guardiamo anche la divisione per fornitore di vaccino.')

        somministrazioni_fornitore = self.__somministrazioni.loc[:,['Data Somministrazione','Fornitore','Prima Dose','Seconda Dose']].groupby(['Data Somministrazione', 'Fornitore']).sum().unstack(level=1).fillna(0).astype(int)

        fig, ax = plt.subplots()
        somministrazioni_fornitore.plot.bar(
            stacked=True,
            figsize=(15,8),
            ax = ax,
            color=['firebrick','royalblue','goldenrod','tomato','skyblue','gold'],
            width=.9,
            title = 'Distribuzione temporale somministrazioni',
            ylabel='Somministrazioni',
            rot=0
        )
        ax.legend([i + ' ' + j for i,j in somministrazioni_fornitore.keys()],loc='upper left',ncol=2)
        ax.grid(lw=.2)

        ax.set_xticks(np.arange(0,(ax.get_xlim()[1]),10))

        st.write(fig)

        ####
        st.write(self.__somministrazioni.groupby('Data Somministrazione').sum())
        somministrazioniVaccini_Categoria = self.__somministrazioni.iloc[:,[1,5,6,7,8,9,10,11]].groupby('Fornitore').sum()
        fig, axs = plt.subplots(4,2,figsize=(15,20))
        axs = axs.ravel()

        ###
        st.write('Questa analisi mostra in funzione dell\'azienda fornitrice quali e quanti vaccini vengano somministrati a quale categoria sociale e viceversa a chi sono somministrati i diversi vaccini.')

        for i in range(somministrazioniVaccini_Categoria.keys().size):
            somministrazioniVaccini_Categoria.plot.bar(
                y=somministrazioniVaccini_Categoria.keys()[i],
                ax=axs[i],
                legend=False,
                ylabel='Somministrazioni',
                title=somministrazioniVaccini_Categoria.keys()[i],
                width=.9,
                color=['tomato','cornflowerblue','gold'],
                logy=True,
                rot=0,
                fontsize=15
            )
        for i in axs: 
            i.grid(lw=.5)
        plt.tight_layout()                                                  

        fig.delaxes(axs[7])
        #fig.delaxes(axs[8])

        st.write(fig)

def Anagrafica():

    anagrafica = pd.read_csv(os.path.join(DWpath,'anagrafica.csv'))

    totaleRange=pd.read_csv('Staging/popolazione-istat-regione-range.csv')
    totaleRange = totaleRange.groupby('range_eta').sum().reset_index().loc[1:,['range_eta','totale_generale']]

    anagrafica.drop(columns='Unnamed: 0', inplace=True)
    #######
    fig, axs = plt.subplots(nrows=2,ncols=2, figsize=(15,15))
    axs = axs.ravel()

    anagrafica.plot.bar(
        x='Fascia Anagrafica', 
        y='Totale',  
        title='Distribuzione vaccini per fascia anagrafica',
        legend=False,
        color='royalblue',
        ax=axs[0],
        width=.9,
        fontsize=15
    )

    anagrafica.plot.bar(
        x='Fascia Anagrafica', 
        y=['Sesso Maschile', 'Sesso Femminile'],
        stacked=True,
        title='Distribuzione vaccini per fascia anagrafica\n e sesso',
        ax=axs[1],
        color=['steelblue','coral'],
        width=.9,
        fontsize=15
    )

    anagrafica.plot.bar(
        x='Fascia Anagrafica', 
        y= anagrafica.columns[4:11],
        stacked=True,
        title='Distribuzione vaccini per fascia anagrafica\n e categoria sociale',
        ax=axs[2],
        cmap='Dark2_r',
        width=.9,
        fontsize=15
    )

    axs[3].bar( 
        x=totaleRange['range_eta'],
        height=anagrafica['Totale Generale'],
        alpha=.3,
        label='Totale Generale'
    )
    anagrafica.plot.bar(
        x='Fascia Anagrafica', 
        y=['Prima Dose', 'Seconda Dose'],
        stacked=False,
        title='Distribuzione vaccini per fascia anagrafica\n e dose ricevuta',
        ax=axs[3],
        color=['cornflowerblue','salmon'],
        width=.9,
        fontsize=15
    )

    for i in axs: 
        i.grid(lw=.2)
        i.title.set_size(20)
        i.set_ylabel('Totale Somministrazioni')
        i.legend(loc='upper left', fontsize=15)
    plt.tight_layout()
    st.write(fig)
    st.write(anagrafica)
    st.markdown(
        'Il grafico in basso a sinistra, in particolare, mostra il numero di dosi somministrate, diviso per fascia anagrafica e categoria sociale'
        ' di appartenenza. La categoria "Over80" è però solo una parte delle fasce anagrafiche "80-89" e "90+", questo è corretto dal momento che'
        ' il grafico viene interpretato come *la ragione per la quale un appartenente ad una fascia anagrafica viene chiamato a vaccinarsi*.'
    )
    st.markdown(
        'Il grafico in basso a destra mostra anche la platea di riferimento (popolazione in una determinata fascia di età) oltre alla dose di vaccino somministrata'
    )
    #####

    #pltAnaDosi = ScatterAnagrafica(anagrafica)

    #fig2 = RadarAnagrafica(anagrafica)

    #fig3 = AnagraficaPlot(anagrafica)

    #return pltAnaDosi, fig2, fig3

class AnalisiRegionale:

    __somministrazioni = pd.read_csv(os.path.join(DWpath,'somministrazioniSummary.csv')).drop(columns='Unnamed: 0')
    __regioniInfo = pd.read_csv(os.path.join(DWpath,'regioniInfo.csv'))


    def __header(self,):
        st.header('Analisi Regionale')
        st.write(
            "Vediamo ora la situazione vaccinale nelle regioni italiane. Il primo grafico mostra la percentuale di dosi somministrate da ciascuna regione."
        )

    def Analisi(self,):
        self.__header()

        # Get Relevant Columns
        somministrazioniGiornoRegione = self.__somministrazioni.loc[:,['Data Somministrazione','Prima Dose','Seconda Dose','Regione']].groupby(['Regione','Data Somministrazione']).sum()
        
        somministrazioniRegione = somministrazioniGiornoRegione.groupby('Regione').sum()
        somministrazioniRegione['Totale'] = somministrazioniRegione.sum(axis=1)
        somministrazioniRegione=somministrazioniRegione.reset_index()

        somministrazioniRegione=somministrazioniRegione.merge(self.__regioniInfo).set_index('Regione')

        somministrazioniRegione['% Somministrazioni'] =  round(100 * somministrazioniRegione['Totale']/somministrazioniRegione['Abitanti'],2)
        somministrazioniRegione['% Prima Dose'] =  round(100 * somministrazioniRegione['Prima Dose']/somministrazioniRegione['Abitanti'],2)
        somministrazioniRegione['% Seconda Dose'] =  round(100 * somministrazioniRegione['Seconda Dose']/somministrazioniRegione['Abitanti'],2)

        st.write(somministrazioniRegione[['Totale','% Prima Dose','% Seconda Dose']])

       # regione = st.multiselect('Seleziona una o più regioni per visualizzare il grafico.', options=somministrazioniRegione.index)

        st.write(BarPercSomministrazioni(somministrazioniRegione))

        # mapData = pd.DataFrame(somministrazioniRegione[['lat','lon','% Prima Dose','% Seconda Dose']])
        # st.map(mapData)


