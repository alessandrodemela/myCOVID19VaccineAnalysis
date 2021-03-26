import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st


plt.rcParams["font.family"] = "Gill Sans"

def SomministrazioniGiornoDose(somministrazioniFilterData):
    fig, ax = plt.subplots(1,1,figsize=(20,8))
    somministrazioniFilterData.plot.bar(
        y=['Prima Dose', 'Seconda Dose'],
        stacked=True,
        fontsize=20,
        color=['cornflowerblue','darksalmon'],
        width=.9,
        rot=0,
        ax=ax,
    )
    ax.plot((somministrazioniFilterData['Totale']).rolling(window=7).mean(),
            lw=3,
            color='forestgreen',
            label='Totale Somministrazioni Giornaliere (Media Mobile 7gg)'
        )
    ax.set_xticks(np.arange(0,(plt.xlim()[1]),12))
    ax.grid(lw=.2)
    ax.set_xlabel(xlabel='Data', font='Gill Sans', fontsize=20)
    ax.set_ylabel(ylabel='Dosi Somministrate', font='Gill Sans', fontsize=20)
    ax.legend(fontsize=15)

    return fig

def RadarAnagrafica(anaVacSumLat):
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16,8))

    maxZoom = 1.1 * max(anaVacSumLat['% Seconda Dose Assoluta'])/100

    for a,L,div in zip(ax,[1,maxZoom],[11,6]):

        x = [ L * np.cos(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['Totale'])]
        y = [ L * np.sin(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['Totale'])]

        Tx = [ i/100 * np.cos(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['% Seconda Dose Assoluta'])]
        Ty = [ i/100 * np.sin(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['% Seconda Dose Assoluta'])]

        x.append(x[0]),y.append(y[0])
        Tx.append(Tx[0]),Ty.append(Ty[0])

        a.plot(x,y,lw=0)
        a.fill(Tx,Ty,fill=True,color='#d20060',alpha=.4)

        for n,i in enumerate(anaVacSumLat['Fascia Anagrafica']):
            a.text(
                x[n]+.1*x[n],
                y[n]+.1*y[n],
                s=i,
                ha='center',
                font='Gill Sans',
                fontsize='20'
                )
        a.axis('off')
        for i in np.linspace(0,L,div):
            a.add_patch(plt.Circle(xy=(0,0),radius=i, fill=None, color='gray', lw=.2))
            a.text(x=i*np.cos(4),y=i * np.sin(4),s=str(int(i*100))+'%',va='center',ha='center',font='Gill Sans', fontsize='10')

        totIta = anaVacSumLat['Seconda Dose'].sum() / anaVacSumLat['Platea'].sum()
        a.add_patch(plt.Circle(xy=(0,0), radius=totIta, fill=None, color='cornflowerblue', lw=3, ls='--'))

        for ix,iy in zip(x[:-1],y[:-1]):
            a.plot([0,ix],[0,iy], c='tab:gray', lw=.3)
            
    ax[1].annotate(
        "% Vaccinati Italia",
        xy=(.05,.02),
        xytext=(.2, .1),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle = "angle,angleA=50,angleB=-10,rad=70",
            lw=1,
            color='tab:gray'
        ),
        font='Gill Sans',
        fontsize=18,
        va='center',
        color='dimgray'
    )

    ax[1].annotate(
        "% Vaccinati\nPer Anagrafica",
        xy=(.05,-.1),
        xytext=(.2, -.35),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle = "angle,angleA=180,angleB=100,rad=70",
            lw=1,
            color='tab:gray'
        ),
        font='Gill Sans',
        fontsize=18,
        va='center',
        color='dimgray'
    )

    return fig

def ScatterAnagrafica(anaVacSumLat):
    fig, axs = plt.subplots(ncols=1,nrows=1,figsize=(40,14))

    resize = 120

    axs.scatter(x=anaVacSumLat['Fascia Anagrafica'],
                y=[1 for i in range(len(anaVacSumLat))],
                s=anaVacSumLat['Totale']/resize,
                alpha=.6,
                c='cornflowerblue',
                label='Somministrazioni'
            )
    axs.scatter(x=anaVacSumLat['Fascia Anagrafica'],
                y=[1 for i in range(len(anaVacSumLat))],
                s=anaVacSumLat['Seconda Dose']/resize,
                c='Steelblue',
                label='Seconda Dose',
                alpha=.8
            )
    axs.scatter(x=anaVacSumLat['Fascia Anagrafica'],
                y=[1 for i in range(len(anaVacSumLat))],
                s=anaVacSumLat['Platea']/resize,
                c='gray',
                label='Seconda Dose',
                alpha=.2
            )

    axs.set_ylim([0.98,1.04])
    axs.set_xlim([-1,10])
    axs.axis('off')

    for n,i in enumerate(anaVacSumLat['Fascia Anagrafica']): 
        axs.text(x=i,y=0.975,s=i, fontsize=50, ha='center', va='top', fontfamily='Gill Sans', c='#156e45')

    #for n,i in enumerate(anaVacSumLat['% Seconda Dose Sul Totale']):   
    #    axs[1].text(x=n, y=1, s=str(round(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily='Gill Sans', c='navy')
    #for n,i in enumerate(anaVacSumLat['% Seconda Dose Assoluta']):   
    #    axs[1].text(x=n, y=1.013, s=str(round(i,2))+'%', ha='center', va='bottom', fontsize=60, fontfamily='Gill Sans', c='#d20060')
    #for n,i in enumerate(anaVacSumLat['% Totale Assoluto']):   
    #    axs[1].text(x=n, y=1.026, s=str(round(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily='Gill Sans', c='#e39f1f')

        
    axs.annotate("Totale\nSomministrazioni",
                xy=(7, 0.9955),
                xytext=(8, 0.985),
                arrowprops=dict(arrowstyle="->",
                                connectionstyle = "angle,angleA=180,angleB=90,rad=120",
                                lw=3,
                                color='k'
                            ),
                font='Gill Sans',
                fontsize=45,
            )
    #axs[1].annotate("% Seconde Dosi\nSulla Platea",
    #            xy=(-.3, 1.016),
    #            xytext=(-2, 1),
    #            arrowprops=dict(arrowstyle="->",
    #                            connectionstyle = "angle,angleA=90,angleB=0,rad=50",
    #                            lw=3
    #                           ),
    #            font='Gill Sans',
    #            fontsize=45,
    #            )
    axs.annotate("Platea",
                xy=(0, 0.997),
                xytext=(-1, 0.99),
                arrowprops=dict(arrowstyle="->",
                                connectionstyle = "angle,angleA=0,angleB=80,rad=110",
                                lw=3,
                                color='k'
                            ),
                font='Gill Sans',
                fontsize=45,
            )
    axs.annotate(
        "Seconda\nDose",
        xy=(5, 1),
        xytext=(6, 1.015),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle = "angle,angleA=180,angleB=-100,rad=120",
            lw=3,
            color='k'
        ),
        ha='left',
        font='Gill Sans',
        fontsize=45,
    )
    #axs[1].annotate("% Dose Somministrate\nSul Totale Delle Dosi",
    #            xy=(8.3, 1.0285),
    #            xytext=(9, 1.005),
    #            arrowprops=dict(arrowstyle="->",
    #                            connectionstyle = "angle,angleA=90,angleB=0,rad=50",
    #                            lw=3
    #                           ),
    #            ha='left',
    #            font='Gill Sans',
    #            fontsize=45,
    #           )
    #axs[1].annotate("% Seconde Dosi\nSulla Platea",
    #            xy=(-.3, 1.02),
    #            xytext=(-1.5, 1.03),
    #            arrowprops=dict(arrowstyle="->",
    #                            connectionstyle = "angle,angleA=90,angleB=0,rad=40",
    #                            lw=3
    #                           ),
    #            font='Gill Sans',
    #            fontsize=45,
    #            ha='center'
    #            )
    axs.text(x=4.,y=1.03,s='Vaccinazioni per fascia anagrafica',font='Gill Sans', fontsize=70, ha='center')

    return fig

def AnagraficaPlot(anaVacSumLat):
    fig, axs = plt.subplots(nrows=2,ncols=1, figsize=(20,18))

    for ax,t,rg in zip(axs,['Sesso','Categoria Sociale'],[range(2,4),range(5,11)]):
        bottom = np.zeros(len(anaVacSumLat['Fascia Anagrafica']))  

        for i in rg:
            ax.bar(
                x=anaVacSumLat['Fascia Anagrafica'], 
                height=anaVacSumLat.iloc[:,i], 
                label=anaVacSumLat.columns[i],
                bottom=bottom,
                width=.9,
               # color=c
            )
            bottom=bottom+anaVacSumLat.iloc[:,i]
        ax.tick_params(labelsize=18)
        ax.set_xlabel('Fascia anagrafica', fontfamily='Gill Sans', fontsize=20)
        ax.set_ylabel('Somministrazioni', fontfamily='Gill Sans', fontsize=20)
        ax.set_title('Distribuzione vaccini per %s' %t, fontfamily='Gill Sans', fontsize=24)
        ax.legend(fontsize=15)
        ax.grid(lw=.2)

    return fig