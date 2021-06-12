import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import datetime, timedelta
import locale
locale.setlocale(locale.LC_TIME, "it_IT")
import time
import streamlit as st

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from helper import *

import seaborn as sns
sns.set()



############################################
# Plotting Functions

def makePlot_Indicatori(KPI, aux):

    colors = [
        '#000000',
        '#000000',
        '#000000',
        '#000000',
        '#3c5da0',         # prime dosi
        '#d37042'          # seconde dosi
    ]

    fig = go.Figure()

    xs = [0.25,0.75]
    ys = [0.9, 0.6, 0.3]

    for n,i in enumerate(KPI.items()):
        fig.add_annotation(
            x=xs[n%2], y=ys[int(n/2)],
            text=i[0],
            showarrow=False,
            font=dict(size=20),
        )
        fig.add_annotation(
            x=xs[n%2], y=ys[int(n/2)]-.1,
            text='{:,}'.format(i[1]),
            showarrow=False,
            font=dict(size=35),
        )  

    fig.add_annotation(
        x=xs[1], y=ys[0]-.18,
        text=aux['Data Ultime Somministrazioni'],
        showarrow=False,
        font=dict(size=15),
    )  
    fig.add_annotation(
        x=xs[1], y=ys[1]-.18,
        text=aux['Data Ultima Consegna'],
        showarrow=False,
        font=dict(size=15),
    )  
    fig.add_annotation(
        x=xs[0], y=ys[2]-.19,
        text=f'<b>{aux["Percentuale Prime Dosi"]:.2%}',
        showarrow=False,
        font=dict(size=22, color='#3c5da0'),
    )  
    fig.add_annotation(
        x=xs[1], y=ys[2]-.19,
        text=f'<b>{aux["Percentuale Seconde Dosi"]:.2%}',
        showarrow=False,
        font=dict(size=22,color='#d37042'),
    )  

    fig.update_layout(
        #width=730, height=130*3,
        margin=dict(l=5, r=5, t=20, b=20),
    )

    fig.update_yaxes(showgrid=False, zeroline=False, range=[0,1], showticklabels=False)
    fig.update_xaxes(showgrid=False, zeroline=False, range=[0,1], showticklabels=False)     

    return fig


def makePlot_SomministrazioniLastWeek(df, n):
    def makePlot(fig):
        dfweek = df.groupby(level=0).sum()
        #checkSunday = (datetime.today().isocalendar()[2]<7) and (datetime.today().isocalendar()[2]==1 or df.iloc[-1,0] != datetime.today().date())
        predicted = predictCurrentWeek(df)

        fig.add_trace(
            go.Bar(
                x=[df.index[-1][0]],
                y=[int(predictCurrentWeek(df,True))],
                marker_color='dimgray',
                texttemplate='%{y:,}',
                textposition='auto',
                hovertemplate='%{y}',
                name='Stima<br>Lineare',
                #opacity=.7,
                visible=True
            )
        )
        fig.add_trace(
            go.Bar(
                x=[df.index[-1][0]],
                y=[int(predicted)],
                marker_color='dimgray',
                texttemplate='%{y:,}',
                textposition='auto',
                hovertemplate='%{y}',
                name='Stima<br>Proporzionale',
                #opacity=.5,
                visible=False
            )
        )
        fig.add_trace(
            go.Bar(
                x=dfweek.index,
                y=dfweek['Totale'],
                marker_color='#3c5da0',
                texttemplate='%{y:,}',
                textposition='auto',
                hovertemplate='%{y}',
                name='Totale'
            )
        )

        fig.update_layout(barmode='overlay')
        fig.update_layout(
            barmode='overlay',
            width=730,
            legend=dict(
                yanchor="bottom",
                y=1,
                xanchor="left",
                x=.6
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    x=.535,
                    y=1.16,
                    showactive=True,
                    font= dict(color='gray'),
                    buttons=list(
                        [
                            dict(
                                label="Stima Lineare",
                                method="update",
                                args=[
                                    {"visible": [True, False, True]},
                                ],
                            ),
                            dict(
                                label="Stima Proporzionale",
                                method="update",
                                args=[
                                    {"visible": [False, True, True]},
                                ],
                            ),
                        ]
                    ),
                )
            ]
        )

        fig.update_yaxes(showgrid=False, zeroline=False, tickformat=',', title='Numero Dosi')
        fig.update_xaxes(showgrid=False, zeroline=False, title='Settimana', ticktext=xlabels, tickvals=dfweek.index)
    # Convert week labels in interval range
    xlabels=[]
    for i in df.groupby(level=0).sum().index:
        xlabels.append(getDateRangeFromWeek(2021,i)[0]+'-'+getDateRangeFromWeek(2021,i)[1])

    # Now, plot
    fig = go.Figure()
    makePlot(fig)
    
    return fig


def makePlot_SomministrazioniGiorno(df):
    fig = go.Figure()

    x=df.index
    fig.add_trace(
        go.Bar(
            x=x,
            y=df['Prima Dose'],
            name='Prima Dose',
            marker_color='#3c5da0',
            hovertemplate='%{y:,.0f}',
            marker_line_width=0
        )
    )
    fig.add_trace(
        go.Bar(
            x=x,
            y=df['Persone Vaccinate'],
            name='Persone Vaccinate',
            marker_color='#d37042',
            hovertemplate='%{y:,.0f}',
            marker_line_width=0
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x, 
            y=df['Totale'].rolling(7).mean(),
            mode='lines',
            name='Totale (media mobile 7gg)',
            line=dict(color='forestgreen', width=3),
            customdata=df['Totale'],
            hovertemplate='Totale (media mobile): <b>%{y:,.0f}</b><br>Totale giornaliero: <b> %{customdata:,.0f}</b>'
        )
    )

    fig.update_layout(
        barmode='stack',
        yaxis=dict(tickformat=".f"), 
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        font_size=15,
        margin=dict(l=5, r=5, t=20, b=20),
        hovermode="x",
    )

    fig.update_yaxes(showgrid=False, tickformat=',', title='Dosi Somministrate')
    fig.update_xaxes(showgrid=False, title='Data')

    return fig


def makePlot_SomministrazioniGiornoFornitore(df):
    fig = go.Figure()

    x=df.index

    for i,c in zip(df, coloreFornitori):
        fig.add_trace(
            go.Bar(
                x=x,
                y=df[i],
                name=i[1],
                marker_color=c,
                hovertemplate='%{y:,.0f}',
                marker_line_width=0
            )
        )

    fig.update_layout(
        barmode='stack',
        yaxis=dict(tickformat=".f"), 
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        font_size=15,
        margin=dict(l=5, r=5, t=20, b=20),
        hovermode="x"
    )

    fig.update_yaxes(showgrid=False, tickformat=',', title='Dosi Somministrate')
    fig.update_xaxes(showgrid=False, title='Data'),

    return fig


def makePlot_ConsegneSomministrazioni(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for i,c in zip(df.columns,['salmon','cornflowerblue']):
        fig.add_trace(
            go.Scatter(
                x = df.index,
                y = df[i],
                marker_color=c,
                line_width=2,
                name=i,
                hoverinfo='y',
                hovertemplate='%{y:,.0f}'
            )
        )
        
    fig.add_trace(
        go.Scatter(
            x = df.index,
            y = df['% Somministrazioni/Consegne'],
            marker_color='forestgreen',
            line_width=2,
            name='% Somministrazioni/Consegne',
            hoverinfo='y',
            hovertemplate='%{y:.2f}%'
        ),
        secondary_y=True,
    )
        
    fig.update_layout(
        yaxis=dict(tickformat=","), 
        legend=dict(
            yanchor="bottom",
            y=0.01,
            xanchor="right",
            x=0.92
        ),
        font_size=15,
        margin=dict(l=5, r=5, t=35, b=20),
        hovermode="x",
        width=730, height=500,
    )

    fig.update_yaxes(showgrid=False, zeroline=False, title_text="Numero Dosi", secondary_y=False, )
    fig.update_yaxes(showgrid=False, title_text="% Somministrazioni/Consegne", secondary_y=True, range=[5,100])
    fig.update_xaxes(showgrid=False, title='Data')
    return fig


def makePlot_ConsegneSomministrazioniFornitore(df):
    fig = make_subplots(
        rows=2, cols=2, start_cell="top-left",
        subplot_titles=('Janssen', 'Moderna', 'Pfizer/BioNTech', 'Vaxzevria')
    )

    vSomministrazioni = list(df.keys()[:int(len(df.keys())/2)])
        
    lista = [[i,j] for i,j in zip(vSomministrazioni,df.keys()[int(len(df.keys())/2):])]
    color=[['lightpink','hotpink'],['firebrick','tomato'],['royalblue','skyblue'],['goldenrod','gold']]
    text='somministrazioni %{y:,.0f}\n%somministrazioni %{}'


    for i,c,n in zip(lista,color, [[1,1],[1,2],[2,1],[2,2]]):
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[i[1]],
                marker_color=c[1],
                name=i[1],
                hovertemplate="%{y:,.0f}",
            ),
            row=n[0], col=n[1]
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[i[0]],
                marker_color=c[0],
                name=i[0],
                hovertemplate =
                    '%{y:,.0f}'+
                    '<br>% Somm. %{text:.2f}%',
                text = 100 * df[i[0]]/df[i[1]],
                
            ),
            row=n[0], col=n[1],
        )

    for i in range(2):
        fig.update_yaxes(title="Numero Dosi", row=i+1, col=1)
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False, title='Data')

    fig.update_layout(
        yaxis=dict(tickformat=","),
        legend=dict(
            yanchor="top",
            y=-0.3,
            xanchor="left",
            x=0.01,
            itemclick='toggle'
        ),
        showlegend=False,
        font_size=15,
        margin=dict(l=5, r=20, t=40, b=20),
        width=730, height=800,
        hovermode="x unified",
    )
    


    return fig


def makePlot_SomministrazioniCategoria(df, pie=False):

    if pie:
        fig, axs = plt.subplots(nrows=4,ncols=3,figsize=(15,15))
        axs = axs.ravel()

        for i in range(df.keys().size):
            df.plot.pie(
                y=df.keys()[i],
                ax=axs[i] if i<=8 else axs[10],
                legend=False,
                colors=coloreFornitori,
                fontsize=15,
                label='',
                startangle=50
            )
            axs[i].set_title(label=df.keys()[i], fontsize=18)
            axs[i].grid(lw=.5)

        axs[10].set_title(label=df.keys()[9], fontsize=18)
        plt.tight_layout()                                                  

        fig.delaxes(axs[9])
        fig.delaxes(axs[11])

    else:
        df = (100*df.div(df.sum())).T
        fig = go.Figure()

        for i,c in zip(range(len(df.keys())), coloreFornitori):
            fig.add_trace(
                go.Bar(
                    y=df.index, 
                    x=df.iloc[:,i],
                    marker_color=c,
                    orientation='h',
                    name=df.keys()[i],
                    hovertemplate='%{x:.2f}%'
                )
            )

        fig.update_yaxes(showgrid=False)
        fig.update_xaxes(showgrid=False, title='% Dosi Somministrate', range=[0,100], showline=False)
        fig.update_layout(barmode='stack')
        fig.update_layout(
            yaxis=dict(tickformat=","),
            legend=dict(
                yanchor="top",
                y=-0.3,
                xanchor="left",
                x=0.01,
                itemclick='toggle'
            ),
            font_size=15,
            margin=dict(l=5, r=20, t=30, b=20),
           # width=900, height=500,
            hovermode="y unified",
        )

    return fig


def makePlot_SomministrazioniFornitori(df):
    fig = make_subplots(
        rows=5, cols=1, start_cell="top-left",
        subplot_titles=('Janssen', 'Moderna', 'Pfizer/BioNTech', 'Vaxzevria', 'Tutti i vaccini'),
        vertical_spacing = 0.05
    )

    for i,c in zip(range(df.keys().size),coloreFornitori):
        fig.add_trace(
            go.Bar(
                y=df.index, 
                x=df.iloc[:,i],
                marker_color=c,
                orientation='h',
                name=df.keys()[i],
                hovertemplate='%{x:,.0f}',
                texttemplate='%{x:,}',
                textposition='auto'
            ),
            row=i+1, col=1
        )
        fig.add_trace(
            go.Bar(
                y=df.index, 
                x=df.iloc[:,i],
                marker_color=c,
                orientation='h',
                name=df.keys()[i],
                hovertemplate='%{x:,.0f}',
            ),
            row=5, col=1
        )

        fig.update_layout(
            barmode='stack',
            width=730, height=1600,
            hovermode="y",
            showlegend=False,
        )
        fig.update_xaxes(title="Numero Dosi")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False, title='Categoria')                                              

    return fig


def makePlot_AnalisiAnagraficaTotale(df, df_f):
    titles = [
            'Distribuzione vaccini<br>per fascia anagrafica totale', 'Distribuzione vaccini per fascia anagrafica<br>divisi per sesso',
            'Distribuzione vaccini per fascia<br>anagrafica e per fornitore', 'Distribuzione vaccini per fascia anagrafica<br> e per dose somministrata'
        ]

    fig = make_subplots(
        rows=2, cols=2, start_cell="top-left",
        subplot_titles=titles,
    )


    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Totale'],
            name='',
            marker_color='#3c5da0',
            text = 100 * df['Totale']/df['Totale Generale'],
            hovertemplate =
                '<b>%{y:,.0f}'+
                '<br><b>%{text:.2f}%</b> del totale',
        ),
        row=1, col=1
    )
    for i,c,s in zip(['Sesso Maschile', 'Sesso Femminile'], ['steelblue','coral'], ['Totale Genere Maschile', 'Totale Genere Femminile']):
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df[i],
                text = 100 * df[i]/df[s],
                hovertemplate =
                '<b>%{y:,.0f}</b> '+
                '<br><b>%{text:.2f}%</b> del totale',
                name=i,
                marker_color=c
            ),
            row=1, col=2
        )

    for n,v in enumerate(df_f):
        fig.add_trace(
            go.Bar(
                x=df_f.index,
                y=df_f[v],
                marker_color=coloreFornitori[n],
                name=v[1],
                hovertemplate ='<b>%{y:,.0f}</b> '
            ),
            row=2, col=1
        )
        
    df['Totale Generale']
    for i,c in zip(['Prima Dose', 'Persone Vaccinate'], ['cornflowerblue','salmon']):
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df[i],
                name=i,
                marker_color=c,
                text = 100 * df[i]/df['Totale Generale'],
                hovertemplate =
                    '<b>%{y:,.0f}</b> '+
                    '<br><b>%{text:.2f}%</b> del totale',
            ),
            row=2, col=2
        )
        
    fig.update_layout(barmode='stack', showlegend=False, width=750, height=800, font_size=15, hovermode='x')
    fig.update_yaxes(title='Dosi Somministrate', row=1, col=1)
    fig.update_yaxes(title='Dosi Somministrate', row=2, col=1)
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False, title='Fascia Anagrafica')
    

    return fig
 

def makePlot_Regioni(df):
    fig = go.Figure()

    fig.add_trace(
        go.Choroplethmapbox(
            locations=df.index,
            z=df["% Prima Dose"]/100,
            geojson = gpd.GeoSeries(df['geometry']).__geo_interface__,
            colorscale='blues',
            name='',
            autocolorscale=False,
            text = df["Prima Dose"],
            hovertemplate='Prime Dosi: <b>%{text:,}</b><br>pari al <b>%{z:.2%}</b> della platea',
            colorbar=dict(
                tickformat='.2%'
            ),
            visible=True,
        ),
    )
    fig.add_trace(
        go.Choroplethmapbox(
            locations=df.index,
            z=df["% Persone Vaccinate"]/100,
            geojson = gpd.GeoSeries(df['geometry']).__geo_interface__,
            colorscale='orrd',
            name='',
            autocolorscale=False,
            text = df["Persone Vaccinate"],
            hovertemplate='Persone Vaccinate: <b>%{text:,}</b><br>pari al <b>%{z:.2%}</b> della platea',
            colorbar=dict(
                tickformat='.2%'
            ),
            visible=False,
        ),
    )
    fig.add_trace(
        go.Choroplethmapbox(
            locations=df.index,
            z=df["% Dosi Consegnate/Abitanti"]/100,
            geojson = gpd.GeoSeries(df['geometry']).__geo_interface__,
            colorscale='blugrn',
            name='',
            autocolorscale=False,
            text = df['Numero Dosi Consegnate'],
            hovertemplate='Dosi Consegnate: <b>%{text:,}</b><br>pari al <b>%{z:.2%}</b> della platea',
            colorbar=dict(
                tickformat='.2%'
            ),
            visible=False,
        ),
    )
    fig.add_trace(
        go.Choroplethmapbox(
            locations=df.index,
            z=df['% Dosi Somministrate/Dosi Consegnate']/100,
            geojson = gpd.GeoSeries(df['geometry']).__geo_interface__,
            colorscale='redor',
            name='',
            autocolorscale=False,
            text = df["Totale"],
            hovertemplate='Dosi Somministrate: <b>%{text:,}</b><br>pari al <b>%{z:.2%}</b> delle dosi consegnate',
            colorbar=dict(
                tickformat='.2%'
            ),
            visible=False,
        ),
    )

    fig.update_layout(
        title='% Prima Dose',
        hovermode='closest',
        mapbox_style="carto-positron",
        mapbox=dict(
            center=go.layout.mapbox.Center(
                lat=42,
                lon=12
            ),
            zoom=4.5,
        ),
        width=730, height=700,
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=1,
                y=1.08,
                showactive=True,
                font= dict(color='gray'),
                buttons=list(
                    [
                        dict(
                            label="% Prima Dose",
                            method="update",
                            args=[
                                {"visible": [True, False, False, False]},
                                {"title": "% Prima Dose",},
                            ],
                        ),
                        dict(
                            label="% Persone Vaccinate",
                            method="update",
                            args=[
                                {"visible": [False, True, False, False]},
                                {"title": "% Persone Vaccinate",},
                            ],
                        ),
                        dict(
                            label="% Dosi Consegnate/<br>Abitanti",
                            method="update",
                            args=[
                                {"visible": [False, False, True, False]},
                                {"title": "% Dosi Consegnate/Abitanti",},
                            ],
                        ),
                        dict(
                            label="% Dosi Somministrate/<br>Dosi Consegnate",
                            method="update",
                            args=[
                                {"visible": [False, False, False, True]},
                                {"title": "% Dosi Somministrate/Dosi Consegnate",},
                            ],
                        ),
                    ]
                ),
            )
        ]
    )
    return fig


def makePlot_MockGartner(df):  
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df['% Persone Vaccinate']/100,
            y=df['% Prima Dose']/100,
            text=df.index,
            mode='markers+text',
            textposition='middle right',
            name='',
            customdata=df['% Dosi Somministrate/Dosi Consegnate']/100,
            hovertemplate='<b>'+df.index+
            '</b><br>% Persone Vaccinate <b>%{x:.2%}</b><br>% Prima Dose <b>%{y:.2%}</b>'
            '<br>% Dosi Somministrate/Dosi Consegnate <b> %{customdata:.2%}</b>',
            marker=dict(
                size=30,
                color=df['% Dosi Somministrate/Dosi Consegnate']/100,
                colorscale='redor',
                colorbar=dict(
                    title='% Dosi Somministrate/<br>Dosi Consegnate',
                    tickformat='%.2f'
                )
            ),
        ),
    )
    vline = df['Persone Vaccinate'].sum()/df['Totale Generale'].sum()
    fig.add_vline(
        x=vline, 
        line_width=1.3, 
        line_dash="dash", 
        line_color="slategray",
        annotation_text="% Persone Vaccinate Italia", 
        annotation_position="bottom right",
    )
    hline = df['Prima Dose'].sum()/df['Totale Generale'].sum()
    fig.add_hline(
        y=hline, 
        line_width=1.3, 
        line_dash="dash", 
        line_color="slategray",
        annotation_text="% Prima Dose Italia", 
        annotation_position="bottom right",
    )

    fig.update_yaxes(showgrid=False, title='% Prima Dose', tickformat='%.2f')
    fig.update_xaxes(showgrid=False, title='% Persone Vaccinate', tickformat='%.2f')
    fig.update_layout(
        margin=dict(l=5, r=5, t=20, b=20),
        width=730, height=500
    )

    return fig


def makePlot_ConsegneSomministrazioniRegione(df):
    fig = go.Figure()

    for i,c in zip(df['Numero Dosi'].columns, coloreFornitori):
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Numero Dosi'][i],
                #sc=9
                name=i,
                mode='markers',
                marker=dict(symbol='0', size=20, color=c),
                hovertemplate='<b>%{y:.2f}%</b>',
            )
        )
    fig.update_xaxes(
        range=[-.5,20.5],
        title='Regioni',
        showgrid=False,
        zeroline=False,
    )
    fig.update_yaxes(
        range=[-5,105],
        showgrid=False,
        title='% Somministrazioni'
    )
    fig.update_layout(
        hovermode="x unified",
        width=730, height=700,
        showlegend=False
    )

    return fig


def Bonus():
    st.header('Sezione Bonus')
    st.subheader('I colori delle regioni dal 6/11/2020, secondo il D.P.C.M. 4/11/2020.')

    aree = gpd.read_file('aree/shp/dpc-covid-19-ita-aree-nuove-g.shp')

    aree['datasetIni'] = pd.to_datetime(aree['datasetIni'], format='%d/%m/%Y').dt.date

    aree = aree.fillna(datetime.today().date())

    aree['legSpecRif'] = aree['legSpecRif'].map(
        {
            'art.1'              : 'GIALLO',
            'art.2'              : 'ARANCIONE',
            'art.3'              : 'ROSSO',
            'art.1 comma 11'     : 'BIANCO'
        }
    )
    aree['colorCode'] = aree['legSpecRif'].map(
        {
            'GIALLO' : 'gold',
            'ARANCIONE' : 'darkorange',
            'ROSSO' : 'firebrick',
            'BIANCO': 'white'
        }
    )

    aree = aree[['nomeTesto', 'datasetIni', 'legSpecRif', 'colorCode']]

    aree = aree.sort_values(['nomeTesto', 'datasetIni'])
    regioni = [i for i in aree.nomeTesto.unique() if i!='Intero territorio nazionale']

    fig=go.Figure()

    for reg in regioni:

        areaReg = aree[(aree['nomeTesto']==reg) | (aree['nomeTesto']=='Intero territorio nazionale')].sort_values('datasetIni').reset_index().drop(columns=['index'])
        
        if areaReg.loc[0,'datasetIni'] != datetime(2020, 11, 6):
            areaReg.loc[0,'datasetIni'] = datetime(2020, 11, 6).date()
        
        areaReg['permanenza'] =  [
                (areaReg['datasetIni'].iloc[i+1]-areaReg['datasetIni'].iloc[i]).days if i!=len(areaReg)-1 else (datetime.today().date() - areaReg['datasetIni'].iloc[i]).days
                for i in range(len(areaReg))
            ] 

        global areaRegPlot 
        areaRegPlot = areaReg[['datasetIni','permanenza','colorCode']]
        
        w = timedelta(0)
        init = datetime(2020,11,6)
        start = areaRegPlot['datasetIni'].min()

        for i in range(len(areaRegPlot)):
            fig.add_trace(
                go.Bar(
                    orientation='h',
                    x = [areaRegPlot.iloc[i,1]],
                    y = [reg],
                    marker=dict(
                        color= areaRegPlot.iloc[i,2],
                        line=dict(color=areaRegPlot.iloc[i,2], width=1)
                    ),
                    customdata = np.dstack(
                        [
                            ('Zona ROSSA' if areaRegPlot.iloc[i,2]=='firebrick' else 'Zona ARANCIONE' if areaRegPlot.iloc[i,2]=='darkorange' else 'Zona GIALLA' if areaRegPlot.iloc[i,2]=='gold' else 'Zona BIANCA',
                             areaRegPlot.iloc[i,0].strftime('%d %b %Y') + ' - ' + areaRegPlot.iloc[i+1,0].strftime('%d %b %Y') if i+1<len(areaRegPlot) else areaRegPlot.iloc[i,0].strftime('%d %b %Y') + ' - '
                            )
                        ]
                    ),
                    hovertemplate='<b> %{customdata[0]} </b><br> %{customdata[1]}',
                    name=reg
                )
            )

    delta = datetime.today().date() - datetime(2020,11,6).date()
    ticktext = [(datetime(2020,11,6).date() + timedelta(days=x)).strftime('%d %b') for x in range(delta.days)]

    tickvals = [i for i in range(len(ticktext))][::20]
    ticktext = ticktext[::20]

    fig.update_layout(
         margin=dict(l=5, r=5, t=25, b=20),
        height=500, width=730,
        barmode='stack',
        showlegend=False,
         xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
            tickmode = 'array',
            tickvals = tickvals,
            ticktext = ticktext
        ),
    )

    st.write(fig)

