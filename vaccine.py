#!/Users/alessandrodemela/opt/anaconda3/bin/python

from Classes import Analysis
import streamlit as st
from datetime import datetime as dt

st.title('Report vaccinazioni COVID-19')

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

def Run():
    analysis = Analysis()
    analysis.GetReport()

Run()