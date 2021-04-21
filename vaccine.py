#!/Users/alessandrodemela/opt/anaconda3/bin/python

from Classes import Analysis, ReportBugs
from grafici import makePlot_Indicatori
from datetime import datetime as dt

import streamlit as st
st.set_page_config(page_title='Vaccinazione COVID-19 Italia - Report', page_icon='logo.png')

st.title('Report vaccinazioni COVID-19')
st.markdown('***')
 

def GetReport(an):
    '''Manage report'''

    # Introduzione
    an.Header()
    st.sidebar.write('Indicatori')
    st.sidebar.write(makePlot_Indicatori(an.KPI, an.auxiliaryMeas))
    st.sidebar.write('La percentuale di prime e seconde dosi somministrate è da intendersi sulla platea 16+.')

    # Somministrazioni
    an.Somministrazioni()

    # Anagrafica
    an.Anagrafica()

    # Regionale
    an.Regionale()

    # Bug/suggestions
    # elif sezione=='Segnalazioni':
    #     bug = ReportBugs()
    #     bug.Report()

def Run():
    analysis = Analysis()
    GetReport(analysis)

    st.markdown('***')
    st.markdown(
        f"Ultimo Aggiornamento {dt.today().strftime('%d/%m/%Y %T')}.    "
        '\nIl codice di analisi è disponibile [qui](https://github.com/alessandrodemela/myCOVID19VaccineAnalysis),  '
        ' i dati sono reperibili nel [repository ufficiale](https://github.com/italia/covid19-opendata-vaccini).<br>   '
        'Per suggerimenti e segnalazioni, [apri un issue su github](https://github.com/alessandrodemela/myCOVID19VaccineAnalysis/issues/new).<br>    ',
        unsafe_allow_html=True
    )
    #report = st.button('Vai alle segnalazioni')
    st.markdown('***')

Run()

