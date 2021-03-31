import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import os

if not os.path.isdir('DW'): os.mkdir('DW')
DWPath = 'DW/'
csvPath = 'covid19-opendata-vaccini/dati/'


# mapping columns names
def createNameMappingDict(df):
    '''This function returns a dictionary which helps mapping columns names in a DataFrame'''
    nameMappingDict = {oldName : oldName.replace('_',' ').title() for oldName in df.columns}
    
    return nameMappingDict

def ETL_anagraficaVacciniSummaryLatest():
    global anaVacSumLat 
    st.write(csvPath+'anagrafica-vaccini-summary-latest.csv')
    anaVacSumLat = pd.read_csv(csvPath+'anagrafica-vaccini-summary-latest.csv')
    anaVacSumLat = anaVacSumLat.rename(columns=createNameMappingDict(anaVacSumLat))
    
    vLastUpdate = datetime.strptime(anaVacSumLat.iloc[0,-1],"%Y-%m-%d").strftime("%d/%m/%Y")
    
    anaVacSumLat = anaVacSumLat.iloc[:,:-1]
    
    # -----NEW COLUMNS-----
    anaVacSumLat['% Seconda Dose Sul Totale'] = round(100 * anaVacSumLat['Seconda Dose']/anaVacSumLat['Totale'], 2)
    anaVacSumLat['Platea'] = [2298846,6084382,6854632,8937229,9414195,7364364,5968373,3628160,613523]
    anaVacSumLat['% Seconda Dose Assoluta'] = round(anaVacSumLat['Seconda Dose']/anaVacSumLat['Platea'] * 100,2)
    anaVacSumLat['% Totale Assoluto'] = round(anaVacSumLat['Totale']/anaVacSumLat['Platea'] * 100,2)
    # ---------------------
    
    anaVacSumLat.to_csv(DWPath+'anagraficaVacciniSummaryLatest.csv')

    return anaVacSumLat,vLastUpdate
    

def ETL_consegneVacciniLatest():
    global consVacciniLat 
    consVacciniLat = pd.read_csv(csvPath+'consegne-vaccini-latest.csv')
    consVacciniLat = consVacciniLat.rename(columns=createNameMappingDict(consVacciniLat)
                                          ).rename(columns={'Nome Area': 'Regione'} )   
    consVacciniLat = consVacciniLat.iloc[:,[1,2,3,7]]
    consVacciniLat['Data Consegna'] = pd.to_datetime(consVacciniLat['Data Consegna'])
    
    consVacciniLat.to_csv(DWPath+'consegneVacciniLatest.csv')

def ETL_somministrazioniVacciniSummaryLatest():
    global somVacciniSumLat
    somVacciniSumLat = pd.read_csv(csvPath+'somministrazioni-vaccini-summary-latest.csv')
    somVacciniSumLat = somVacciniSumLat.rename(columns=createNameMappingDict(somVacciniSumLat)
                                              ).rename(columns={'Nome Area': 'Regione'} )

    somVacciniSumLat.drop(columns=['Area', 'Codice Nuts1', 'Codice Nuts2', 'Codice Regione Istat'], inplace=True)

    somVacciniSumLat['Data Somministrazione'] = pd.to_datetime(somVacciniSumLat['Data Somministrazione']).dt.date
    
    # -----NEW COLUMNS-----
    somVacciniSumLat['Totale'] = somVacciniSumLat['Prima Dose'] + somVacciniSumLat['Seconda Dose']
    # ---------------------
    
    somVacciniSumLat = somVacciniSumLat.sort_values(['Data Somministrazione','Regione']).reset_index()
    somVacciniSumLat = somVacciniSumLat.drop(columns='index')
    somVacciniSumLat.to_csv(DWPath+'somministrazioniVacciniSummaryLatest.csv')

    return somVacciniSumLat