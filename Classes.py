import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import os
from datetime import datetime as dt
from grafici import *
from helper import *

plt.rcParams["font.family"] = "Sans Serif"
plt.rcParams.update({'font.size': 25})


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
    "Valle d'Aosta"             : 'Valle d\'Aosta / Vallée d\'Aoste',
    'Veneto'                    : 'Veneto'
}


class ReportBugs:
    '''This class is experimental'''

    def __init__(self):
        st.markdown('***')
        st.header('Suggerimenti e segnalazioni')

    def Report(self):
        st.markdown(
            'Per segnalazioni o suggerimenti: [github](https://github.com/alessandrodemela/myCOVID19VaccineAnalysis/issues/new), [email](about:blank)'
        )

        st.text_area("Testo:")
        if st.button('Invio'):
            st.write('SEND IT!')


class Analysis:

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
        self.readableDate = self.lastUpdateDataset.date().strftime('%d %B %Y')


        self.mapFornitore = {
            'Pfizer/BioNTech'           :   'Pfizer/BioNTech',
            'Moderna'                   :   'Moderna',
            'Vaxzevria (AstraZeneca)'   :   'Vaxzevria',
            'Janssen'                   :   'Janssen' 
        }

        self.ETL()
        self.getKPI()

    def createNameMappingDict(self,df):
        '''This function returns a dictionary which helps mapping columns names in a DataFrame'''
        nameMappingDict = {oldName : oldName.replace('_',' ').title().replace('Categoria', '').replace('Nome Area', 'Regione/P.A.').replace('Denominazione Regione', 'Regione/P.A.').replace('Seconda Dose', 'Persone Vaccinate') for oldName in df.columns}
        return nameMappingDict
    
    def ETL(self):
        '''ETL function to create clean tables'''

        # TABELLA DELLE SOMMINISTRAZIONI (fatti)
        self.tblSomministrazioni = self.tblSomministrazioni.rename(columns=self.createNameMappingDict(self.tblSomministrazioni))
        self.tblSomministrazioni['Totale'] = self.tblSomministrazioni[['Prima Dose','Persone Vaccinate']].sum(axis=1)
        self.tblSomministrazioni = self.tblSomministrazioni.drop(columns=['Codice Nuts1', 'Codice Nuts2', 'Codice Regione Istat', 'Area'])
        self.tblSomministrazioni['Data Somministrazione'] = pd.to_datetime(self.tblSomministrazioni['Data Somministrazione']).dt.date

        JanssenIndex = self.tblSomministrazioni[self.tblSomministrazioni['Fornitore']=='Janssen'].index.tolist()

        self.tblSomministrazioni.loc[JanssenIndex,'Persone Vaccinate'] = self.tblSomministrazioni.loc[JanssenIndex,'Prima Dose']
        self.tblSomministrazioni.loc[JanssenIndex,'Prima Dose'] = 0
        
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

        # TABELLA JOIN CONSEGNE SOMMINISTRAZIONI CON FORNITORE
        self.tblSomministrazioniTMP = self.tblSomministrazioni.groupby(['Fornitore','Data Somministrazione']).sum().unstack(level=0)['Totale']
        self.tblSomministrazioniTMP = self.tblSomministrazioniTMP.rename(columns = {i: 'Somministrazioni ' + i for i in self.tblSomministrazioniTMP.keys()} )

        self.tblConsegneTMP = self.tblConsegne.groupby(['Fornitore','Data Consegna']).sum().unstack(level=0)['Numero Dosi']
        self.tblConsegneTMP = self.tblConsegneTMP.rename(columns = {i: 'Consegne ' + i for i in self.tblConsegneTMP.keys()} )
        
        self.tblSomministrazioniConsegneFornitore = pd.concat([self.tblSomministrazioniTMP, self.tblConsegneTMP],axis=1).cumsum().fillna(method='ffill').fillna(0)

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
        self.tblFullRegioni['% Persone Vaccinate'] = round(self.tblFullRegioni['Persone Vaccinate']/self.tblFullRegioni['Totale Generale'] *100,2)
        self.tblFullRegioni['% Totale'] = round(self.tblFullRegioni['Totale']/self.tblFullRegioni['Totale Generale'] *100,2)
        self.tblFullRegioni['% Dosi Consegnate/Abitanti'] = round(self.tblFullRegioni['Numero Dosi Consegnate']/self.tblFullRegioni['Totale Generale']*100,2)

        self.tblAree = self.tblAree.join(self.tblFullRegioni)

    def getKPI(self):
        self.totSomministrate = self.tblSomministrazioni.Totale.sum()
        self.totPrime = self.tblSomministrazioni['Prima Dose'].sum()
        self.totSeconde = self.tblSomministrazioni['Persone Vaccinate'].sum()
        self.monodosi = int(self.tblSomministrazioni.where(self.tblSomministrazioni['Fornitore']=='Janssen')['Persone Vaccinate'].dropna().sum())
        self.platea = self.tblInfoAnagrafica['Totale Generale'].sum()
        self.percPrime = round(self.totPrime/self.platea,4)
        self.percSeconde = round(self.totSeconde/self.platea,4)

        self.totConsegne = self.tblConsegne['Numero Dosi'].sum()
        self.percConsegne = self.totSomministrate/self.totConsegne

        self.ultimeConsegne = self.tblConsegne.groupby(['Data Consegna','Fornitore']).sum()
        self.dataUltimaConsegna = self.ultimeConsegne.index.max()[0].strftime('%d %B %Y')
        self.qtaUltimaConsegna = int(self.ultimeConsegne.loc[self.ultimeConsegne.index.max()[0]].sum())
        self.ultimiFornitori = ', '.join(self.ultimeConsegne.loc[self.ultimeConsegne.index.max()[0]].index)

        self.ultimeSomministrazioni = self.tblSomministrazioni.groupby('Data Somministrazione').sum().reset_index().iloc[-7:,[0,-1]]
        self.dataUltimeSomministrazioni = self.ultimeSomministrazioni['Data Somministrazione'].iloc[-1].strftime('%d %B %Y')
        self.qtaUltimeSomministrazioni = self.ultimeSomministrazioni.iloc[-1,1]
        self.qtaUltimeSomministrazioniWeek = int(self.ultimeSomministrazioni['Totale'].mean())

        self.KPI = {
            'Dosi Somministrate Totali' : self.totSomministrate,
            'Ultime Somministrazioni'   : self.qtaUltimeSomministrazioni,
            'Dosi Consegnate Totali'    : self.totConsegne,
            'Ultime Consegne'           : self.qtaUltimaConsegna,
            'Prime Dosi'                : self.totPrime,
            'Persone Vaccinate'         : self.totSeconde,
        }
        self.auxiliaryMeas = {
            'Data Ultime Somministrazioni'  : self.dataUltimeSomministrazioni, 
            'Data Ultima Consegna'          : self.dataUltimaConsegna,
            'Percentuale Prime Dosi'        : self.percPrime, 
            'Percentuale Seconde Dosi'      : self.percSeconde
        }

    def Header(self):
        # st.warning('I dati sulle prime e seconde dosi potrebbero essere incorretti, a causa delle dosi somministrate con Janssen.')

        st.markdown('La somministrazione dei vaccini contro la COVID-19, è cominciata il 27 Dicembre 2020 [\[1\]]'
                    '(http://www.salute.gov.it/portale/news/p3_2_1_1_1.jsp?lingua=italiano&menu=notizie&p=dalministero&id=5242).'
                    )    

        st.markdown(
            f'Al {self.readableDate} sono state somministrate **{self.totSomministrate:,}** dosi di vaccino, suddivise in **{self.totPrime:,}** prime dosi'
            f' e **{self.totSeconde:,}** persone hanno completato il ciclo, di cui **{self.monodosi:,}** con vaccino monodose (Janssen). La percentuale di persone che ha ricevuto almeno una dose è '
            f' del **{self.percPrime:.2%}**, mentre il **{self.percSeconde:.2%}** della popolazione ha ricevuto entrambe le dosi.'
        )

        st.markdown(
            f'Sono state consegnate **{self.totConsegne:,}** dosi. La percentuale di dosi somministrate su quelle consegnate è pari al **{self.percConsegne:.2%}**.'
        )

        st.markdown(
            f"Il giorno **{self.dataUltimeSomministrazioni}** sono state somministrate **{self.qtaUltimeSomministrazioni:,}** dosi, mentre nell'"
            f"ultima settimana sono state somministrate in media **{self.qtaUltimeSomministrazioniWeek:,}** dosi."
        )
        st.markdown(
            f"L'ultima consegna è avvenuta il **{self.dataUltimaConsegna}** con **{self.qtaUltimaConsegna:,}** dosi complessive di vaccini " 
            f"**{self.ultimiFornitori}**."
        )

        st.subheader('Indicatori')
        st.plotly_chart(makePlot_Indicatori(self.KPI, self.auxiliaryMeas))
        st.write(f'La percentuale di prime dosi somministrate e persone vaccinate è da intendersi sulla platea 16+, pari a {self.platea:,.0f} abitanti su {59641488:,.0f}.')

        st.markdown('***')

        st.subheader('Dosi consegnate e somministrate per fornitore.')
        cDF = pd.DataFrame(self.tblConsegne.groupby('Fornitore').sum()).rename(columns={'Numero Dosi': 'Dosi Consegnate'})
        sDF = pd.DataFrame(self.tblSomministrazioni.groupby('Fornitore').sum()['Totale']).rename(columns={'Totale': 'Dosi Somministrate'})
        df = pd.concat([cDF,sDF],axis=1)
        df['% Somministrate/Consegnate'] = round(df['Dosi Somministrate'].astype(float)/df['Dosi Consegnate'],4).map('{:.2%}'.format)
        df.iloc[:,:2] = df.iloc[:,:2].applymap('{:,.0f}'.format)

        st.write(df)

        nBackWeeks = 4

        # Prepare DataFrame for plotting last weeks
        df = self.tblSomministrazioni[['Data Somministrazione','Totale']].groupby('Data Somministrazione').sum().reset_index()
        df['Settimana'] = pd.to_datetime(df['Data Somministrazione']).dt.isocalendar().week+1
        df['Giorno'] = pd.to_datetime(df['Data Somministrazione']).dt.isocalendar().day

        lastRows = -8
        lastDay = self.tblSomministrazioni['Data Somministrazione'].iloc[-1]
        lastWeek = lastRows-lastDay.isocalendar()[2]
        df = df.groupby(['Settimana', 'Giorno']).sum().iloc[lastWeek-nBackWeeks*7:lastRows]

        st.subheader(f'Dosi somministrate nelle ultime {nBackWeeks} settimane.')
        plot_LastWeeks = makePlot_SomministrazioniLastWeek(df, nBackWeeks)
        st.plotly_chart(plot_LastWeeks)
        
        st.write(
            'Il valore delle somministrazioni giornaliere, viene aggiornato più volte durante il giorno. ')
        st.write(
            'La stima proporzionale viene effettuata sommando le somministrazioni settimanali fino alla data odierna, rapportandole alla media d'
            f"dello stesso periodo nelle {nBackWeeks} settimane precedenti. La stima potrebbe non essere corretta fino all'ultimo aggiornamento del dato odierno." 
        )
        st.write(
            f'Un valore analogo della stima della settimana corrente è basato su un modello di regressione lineare sulle ultime {nBackWeeks} settimane.'
        )
   
    def Somministrazioni(self):

        def CreateViews_somministrazioni(self):
            '''Creating Views'''
            self.VwSomministrazioniGiorno = self.tblSomministrazioni.groupby('Data Somministrazione').sum()[['Prima Dose','Persone Vaccinate','Totale']]
            self.VwSomministrazioniGiornoFornitore = self.tblSomministrazioni.groupby(['Data Somministrazione', 'Fornitore']).sum().unstack(level=1)[['Totale']].fillna(0).astype(int)
            #self.VwSomministrazioniCategoria = self.tblSomministrazioni.iloc[:,[1,5,6,7,8,9,10,11,12,13,14]].groupby('Fornitore').sum()



        def Analisi_somministrazioni(self):
            st.header('Le Dosi Somministrate')
            st.subheader('Analisi Temporale')
            st.write(
                "Questa sezione contiene l'analisi delle dosi somministrate quotidianamente, la data odierna potrebbe contenere un dato parziale.    "
                "Inoltre, si riporta anche la distribuzione temporale delle somministrazioni divisa per fornitore di vaccino."
            )

            # Plot andamento giornaliero
            plt_somministrazioniGiorno = makePlot_SomministrazioniGiorno(self.VwSomministrazioniGiorno)
            st.write(plt_somministrazioniGiorno)

            # Plot andamento giornaliero per fornitore
            plt_somministrazioniGiornoFornitore = makePlot_SomministrazioniGiornoFornitore(self.VwSomministrazioniGiornoFornitore)
            st.write(plt_somministrazioniGiornoFornitore)

            # Plot consegne e somministrazioni
            st.markdown('### Le dosi consegnate e somministrate')
            plt_ConsegneSomministrazioni = makePlot_ConsegneSomministrazioni(self.tblSomministrazioniConsegne)
            st.write(plt_ConsegneSomministrazioni)

            # Plot consegne e somministrazioni per fornitore
            st.markdown('### Le dosi consegnate e somministrate per fornitore.')
            plt_ConsegneSomministrazioniFornitore = makePlot_ConsegneSomministrazioniFornitore(self.tblSomministrazioniConsegneFornitore)
            st.write(plt_ConsegneSomministrazioniFornitore)

            st.markdown(
                'Questi grafici mostrano l\'andamento per giorno delle somministrazioni e delle consegne di ciascun fornitore. '
            )

            st.subheader('Analisi sul tipo di vaccino somministrato')
            st.markdown(
                "L'analisi successiva mostra, in funzione dell'azienda fornitrice, quali e quanti vaccini vengano somministrati a quale categoria sociale e viceversa a chi sono somministrati i diversi vaccini."
            )
            # Plot somministrazioni per categoria
            #st.markdown('#### Le dosi di vaccino per categoria.')
            #plt_somministrazioniCategoria = makePlot_SomministrazioniCategoria(self.VwSomministrazioniCategoria)
            #st.write(plt_somministrazioniCategoria)

            #Plot somministrazioni per fornitore
            #st.markdown('#### Le dosi di vaccino per fornitore.')
            #plt_somministrazioniFornitori = makePlot_SomministrazioniFornitori(self.VwSomministrazioniCategoria.T)
            #st.write(plt_somministrazioniFornitori)

            #st.write(self.VwSomministrazioniCategoria.T.style.format('{:,}'))

        CreateViews_somministrazioni(self)
        Analisi_somministrazioni(self)

    def Anagrafica(self):
        def CreateViews_anagrafica(self):
            '''Creating Views'''

            self.VwTotaleFascia = self.tblSomministrazioni.groupby(
                ['Fascia Anagrafica']
                ).sum()[
                    ['Totale','Sesso Maschile','Sesso Femminile','Prima Dose', 'Persone Vaccinate']
                ].join(self.tblInfoAnagrafica.groupby('Range Eta').sum()[['Totale Generale', 'Totale Genere Maschile', 'Totale Genere Femminile']])
            self.VwFornitoreFascia = self.tblSomministrazioni.groupby(['Fascia Anagrafica','Fornitore']).sum().unstack(level=1)[['Totale']]


        def Analisi_anagrafica(self):
            st.header('Le somministrazioni per fascia anagrafica')
            # st.markdown(
            #     'I grafici seguenti, in funzione dell\'età anagrafica mostrano il numero di somministrazioni effettuate.<br>' 
            #     '1. Il primo mostra le somministrazioni totali per età;<br>   '
            #     '2. Il secondo è diviso per sesso;<br>   '
            #     '3. Il terzo è suddiviso per vaccino somministrato;<br>   '
            #     '4. Il quarto evidenzia il numero di dosi somministrate.   ',
            #     unsafe_allow_html=True
            # )

            # Plot anagrafica Totale
            plt_Anagrafica = makePlot_AnalisiAnagraficaTotale(self.VwTotaleFascia, self.VwFornitoreFascia)
            st.write(plt_Anagrafica)

        CreateViews_anagrafica(self)
        Analisi_anagrafica(self)
    
    def Regionale(self):

        def CreateViews_regioni(self):
            '''Creating Views'''
            self.VwSomministrazioniRegione = self.tblSomministrazioni.groupby(['Regione/P.A.', 'Fornitore']).sum()[['Totale']].unstack().fillna(0).rename(columns={'Totale': 'Numero Dosi'})
            self.VwConsegneRegione = self.tblConsegne.groupby(['Regione/P.A.', 'Fornitore']).sum().unstack(level=1)
            self.VwSomministrazioniConsegneRegione = self.VwSomministrazioniRegione.div(self.VwConsegneRegione,axis=1)*100


        def Analisi_regionale(self):
            st.markdown('***')
            st.header('L\'Analisi Regionale delle somministrazioni')
            st.markdown('Questa è un\'analisi delle dosi somministrate e consegnate in ogni regione divise per varie categorie di somministrazione')

            # 4 Plot sulle somministrazioni
            st.subheader('Dosi somministrate e consegnate')
            plt_Regioni = makePlot_Regioni(self.tblAree)
            st.write(plt_Regioni)

            # Bar Plot
            #st.write('Gli stessi dati, ma rappresentati in modo diverso.')
            #plt_percBar = makePlot_BarPercSomministrazioni(self.tblAree)
            #st.write(plt_percBar)

            # scatterplot
            st.subheader('Come si posiziona ciascuna regione')
            plt_Gartner = makePlot_MockGartner(self.tblAree)
            st.write(plt_Gartner)

            # consegne e somministrazioni
            st.subheader('La percentuale di somministrazione di ciascun vaccino per ciascuna regione')
            plt_consegneSomministrazioniRegione = makePlot_ConsegneSomministrazioniRegione(self.VwSomministrazioniConsegneRegione)
            st.write(plt_consegneSomministrazioniRegione)

        CreateViews_regioni(self)
        Analisi_regionale(self)
        st.markdown('***')

    def Footer(self):
        st.markdown('***')
        st.markdown(
            f"Ultimo Aggiornamento {dt.today().strftime('%d/%m/%Y %T %Z')}.    "
            '\nIl codice di analisi è disponibile [qui](https://github.com/alessandrodemela/myCOVID19VaccineAnalysis),  '
            ' i dati sono reperibili nel [repository ufficiale](https://github.com/italia/covid19-opendata-vaccini).<br>   '
            'Per suggerimenti e segnalazioni, [apri un issue su github](https://github.com/alessandrodemela/myCOVID19VaccineAnalysis/issues/new).<br>    ',
            unsafe_allow_html=True
        )
        #report = st.button('Vai alle segnalazioni')
        st.markdown('***')
