import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
from grafici import SomministrazioniGiornoDose, ScatterAnagrafica, RadarAnagrafica, AnagraficaPlot

DWpath = 'DW'

def Somministrazioni():
    somministrazioni = pd.read_csv(os.path.join(DWpath,'somministrazioniVacciniSummaryLatest.csv'))

    # Get Relevant Columns
    somministrazioni = somministrazioni.loc[:,['Data Somministrazione','Prima Dose','Seconda Dose']].groupby('Data Somministrazione').sum()
    somministrazioni['Totale'] = somministrazioni.sum(axis=1)
    somministrazioni
    
    # Filter
    dateRange = pd.to_datetime(somministrazioni.index).date
    startDate, endDate = st.select_slider(
        "Seleziona un intervallo temporale",
        value=[dateRange[0],dateRange[-1]],
        options=list(dateRange)
    )
    somministrazioniFilterData = somministrazioni[  (pd.to_datetime(somministrazioni.index).date >= startDate )
                                                    & (pd.to_datetime(somministrazioni.index).date <= endDate)   ]

    fig = SomministrazioniGiornoDose(somministrazioniFilterData)
    return fig

def Anagrafica():
    anagrafica = pd.read_csv(os.path.join(DWpath,'anagraficaVacciniSummaryLatest.csv'))

    anagrafica = anagrafica.drop(columns='Unnamed: 0')

    fig = ScatterAnagrafica(anagrafica)

    fig2 = RadarAnagrafica(anagrafica)

    fig3 = AnagraficaPlot(anagrafica)

    return fig, fig2, fig3