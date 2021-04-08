import pandas as pd
import numpy as np
from datetime import datetime
import os
from shutil import copyfile

import logging
logging.basicConfig(level=logging.INFO, format="ETL\t ::\t%(levelname)s\t\t%(message)s")

DWPath = 'DW/'
StagingPath = 'Staging/'


class ETL:
    
    def getData(self):
        logging.info('Retrieving Data...')
        anagrafica = pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/anagrafica-vaccini-summary-latest.csv')
        anagrafica.to_csv(StagingPath+'anagrafica.csv')

        pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/consegne-vaccini-latest.csv').to_csv(StagingPath+'consegne.csv')
        pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-summary-latest.csv').to_csv(StagingPath+'somministrazioni_summary.csv')
        pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv').to_csv(StagingPath+'somministrazioni.csv')

        self.lastupdate(datetime.strptime(anagrafica.iloc[0,-1],"%Y-%m-%d").strftime("%d/%m/%Y"))

    # mapping columns names
    def createNameMappingDict(self,df):
        '''This function returns a dictionary which helps mapping columns names in a DataFrame'''
        nameMappingDict = {oldName : oldName.replace('_',' ').title() for oldName in df.columns}
        
        return nameMappingDict

    # def writeDf(df,dir,name):

    def lastupdate(self,date):
        with open('lastupdate','w') as fLastUpdate:
            fLastUpdate.write(date)
        
    def transformData(self):
        logging.info('Transforming Data. Anagrafica...')

        anaVacSumLat = pd.read_csv(StagingPath+'anagrafica.csv')
        anaVacSumLat = anaVacSumLat.rename(columns=self.createNameMappingDict(anaVacSumLat))

        anaVacSumLat = anaVacSumLat.iloc[:,:-1]
        
        # -----NEW COLUMNS-----
        anaVacSumLat['% Seconda Dose Sul Totale'] = round(100 * anaVacSumLat['Seconda Dose']/anaVacSumLat['Totale'], 2)
        anaVacSumLat['Platea'] = [2298846,6084382,6854632,8937229,9414195,7364364,5968373,3628160,613523]
        anaVacSumLat['% Seconda Dose Assoluta'] = round(anaVacSumLat['Seconda Dose']/anaVacSumLat['Platea'] * 100,2)
        anaVacSumLat['% Totale Assoluto'] = round(anaVacSumLat['Totale']/anaVacSumLat['Platea'] * 100,2)
        # ---------------------
        
        anaVacSumLat.to_csv(DWPath+'anagrafica.csv')
    

        logging.info('Transforming Data. Consegne...')

        consVacciniLat = pd.read_csv(StagingPath+'consegne.csv')
        consVacciniLat = consVacciniLat.rename(columns=self.createNameMappingDict(consVacciniLat)
                                            ).rename(columns={'Nome Area': 'Regione'} )   
        consVacciniLat = consVacciniLat.iloc[:,[1,2,3,4,7]]
        consVacciniLat['Data Consegna'] = pd.to_datetime(consVacciniLat['Data Consegna'])
        
        consVacciniLat.to_csv(DWPath+'consegne.csv')


        logging.info('Transforming Data. Somminstrazioni (summary)...')

        somVacciniSumLat = pd.read_csv(StagingPath+'somministrazioni_summary.csv')
        somVacciniSumLat = somVacciniSumLat.rename(
            columns=self.createNameMappingDict(somVacciniSumLat)
        ).rename(columns={'Nome Area': 'Regione'} )

        somVacciniSumLat.drop(columns=['Area', 'Codice Nuts1', 'Codice Nuts2', 'Codice Regione Istat'], inplace=True)

        somVacciniSumLat['Data Somministrazione'] = pd.to_datetime(somVacciniSumLat['Data Somministrazione']).dt.date
        
        # -----NEW COLUMNS-----
        somVacciniSumLat['Totale'] = somVacciniSumLat['Prima Dose'] + somVacciniSumLat['Seconda Dose']
        # ---------------------
        
        somVacciniSumLat = somVacciniSumLat.sort_values(['Data Somministrazione','Regione']).reset_index()
        somVacciniSumLat = somVacciniSumLat.drop(columns='index')
        somVacciniSumLat.to_csv(DWPath+'somministrazioniSummary.csv')


        logging.info('Transforming Data. Done.')