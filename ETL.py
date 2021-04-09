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
        anagrafica.to_csv(StagingPath+'anagrafica.csv',index=False)

        consegne = pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/consegne-vaccini-latest.csv')
        consegne.to_csv(StagingPath+'consegne.csv',index=False)

        pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-summary-latest.csv').to_csv(StagingPath+'somministrazioni_summary.csv',index=False)
        pd.read_csv('https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv').to_csv(StagingPath+'somministrazioni.csv',index=False)

        self.lastupdate(datetime.strptime(anagrafica.iloc[0,-1],"%Y-%m-%d").strftime("%d/%m/%Y"))

    # mapping columns names
    def createNameMappingDict(self,df):
        '''This function returns a dictionary which helps mapping columns names in a DataFrame'''
        nameMappingDict = {oldName : oldName.replace('_',' ').title() for oldName in df.columns}
        
        return nameMappingDict


    def lastupdate(self,date):
        print(date)
        with open('lastupdate','w') as fLastUpdate:
            fLastUpdate.write(date)
        
    def auxiliaryTables(self):
        # Abitanti Regioni
        abitantiRegioni = pd.read_csv('DCIS_POPRES1_25022021122609782.csv')
        abitantiRegioni = abitantiRegioni.iloc[:,[1,5,6,9,12]].sort_values(
            ['Territorio','Sesso']
            ).where((abitantiRegioni['Stato civile']=='totale') &
            (abitantiRegioni.Sesso=='totale') & (abitantiRegioni.ETA1=='TOTAL')
            ).dropna().iloc[:,[0,-1]].set_index('Territorio')
        # Rename field and indexfor better naming
        abitantiRegioni = abitantiRegioni.rename(columns={'Value': 'Abitanti'}).rename_axis('Regione').astype(int)

        # Coordinate Regioni
        coordinateRegioni = pd.read_csv('Staging/popolazione-istat-regione-range.csv',index_col=0)
        coordinateRegioni = pd.concat(
            [pd.DataFrame(coordinateRegioni['denominazione_regione'].unique(), columns=['Regione']),
            pd.DataFrame(coordinateRegioni['latitudine_regione'].unique(), columns=['lat']),
            pd.DataFrame(coordinateRegioni['longitudine_regione'].unique(), columns=['lon'])],
            axis=1,
        )
        mapRegioni={i : j for i,j in zip(coordinateRegioni['Regione'],abitantiRegioni.index)}
        coordinateRegioni['Regione'] = coordinateRegioni['Regione'].map(mapRegioni)
        coordinateRegioni = coordinateRegioni.set_index('Regione')

        regioniInfo = coordinateRegioni.join(abitantiRegioni)

        regioniInfo.to_csv(DWPath+'regioniInfo.csv')

    def transformData(self):
        logging.info('Transforming Data. Anagrafica...')

        anaVacSumLat = pd.read_csv(StagingPath+'anagrafica.csv')
        anaVacSumLat = anaVacSumLat.rename(columns=self.createNameMappingDict(anaVacSumLat))

        totaleRange = pd.read_csv('Staging/popolazione-istat-regione-range.csv')
        totaleRange = totaleRange.rename(columns=self.createNameMappingDict(totaleRange))
        totaleRange = totaleRange.rename(columns={'Range Eta': 'Fascia Anagrafica'})
        totaleRange = totaleRange.groupby('Fascia Anagrafica').sum()['Totale Generale'][1:]

        anaVacSumLat = anaVacSumLat.iloc[:,:-1]
        
        # -----NEW COLUMNS-----
        anaVacSumLat['% Seconda Dose Sul Totale'] = round(100 * anaVacSumLat['Seconda Dose']/anaVacSumLat['Totale'], 2)
        anaVacSumLat['Platea'] = [2298846,6084382,6854632,8937229,9414195,7364364,5968373,3628160,613523]
        anaVacSumLat['% Seconda Dose Assoluta'] = round(anaVacSumLat['Seconda Dose']/anaVacSumLat['Platea'] * 100,2)
        anaVacSumLat['% Totale Assoluto'] = round(anaVacSumLat['Totale']/anaVacSumLat['Platea'] * 100,2)
        # ---------------------
        
        #anaVacSumLat = anaVacSumLat.join(totaleRange)
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
        somVacciniSumLat = somVacciniSumLat.drop(columns=['index'])
        somVacciniSumLat.to_csv(DWPath+'somministrazioniSummary.csv')


        logging.info('Transforming Data. Done.')
