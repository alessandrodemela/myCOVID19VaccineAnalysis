#!/Users/alessandrodemela/opt/anaconda3/bin/python

from Classes import Analysis, ReportBugs
from grafici import makePlot_Indicatori, Bonus
from datetime import datetime as dt

import streamlit as st
st.set_page_config(page_title='Vaccinazione COVID-19 Italia - Report', page_icon='logo.png')

st.title('Report vaccinazioni COVID-19')
st.markdown('***')
 

def GetReport(an):
    '''Manage report'''

    # Introduzione
    an.Header()

    # Somministrazioni
    an.Somministrazioni()

    # Anagrafica
    an.Anagrafica()

    # Regionale
    an.Regionale()

    # Bonus
    an.Bonus()

    # Footer
    an.Footer()

def Run():
    analysis = Analysis()
    GetReport(analysis)

Run()

