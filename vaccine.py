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
    st.sidebar.header('Indicatori')
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

    # Footer
    an.Footer()

def Run():
    analysis = Analysis()
    GetReport(analysis)

Run()

