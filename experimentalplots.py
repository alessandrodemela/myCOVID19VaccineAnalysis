## EXPERIMENTAL/UNUSED PLOTS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import locale
locale.setlocale(locale.LC_TIME, "it_IT")
import time
import matplotlib.pyplot as plt
import streamlit as st
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable 
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

from helper import *

import seaborn as sns
sns.set()


def makePlot_BarPercSomministrazioni(df):
    fig, ax = plt.subplots(figsize=(15,8))

    x = np.arange(len(df.index)+1) 
    width = 0.45

    yPrimaIta = df['Prima Dose'].sum()/df['Totale Generale'].sum()*100
    yPrima = pd.concat([pd.Series({'Italia': yPrimaIta}),df['% Prima Dose']])

    ySecondaIta = df['Persone Vaccinate'].sum()/df['Totale Generale'].sum()*100
    ySeconda = pd.concat([pd.Series({'Italia': ySecondaIta}),df['% Persone Vaccinate']])

    ySommConsegneITa = df['Totale'].sum()/df['Numero Dosi Consegnate'].sum()*100
    ySommConsegne = pd.concat([pd.Series({'Italia': ySommConsegneITa}),df['% Dosi Somministrate/Dosi Consegnate']])

    ax.bar(
        x=x - width/2, 
        height=yPrima, 
        width=width, 
        color='cornflowerblue', 
        label='% Prima Dose'
    )
    ax.bar(
        x=x + width/2, 
        height=ySeconda, 
        width=width, 
        color='salmon', 
        label='% Persone Vaccinate'
    )
    ax1=ax.twinx()
    ax1.scatter(
        x=x, 
        y=ySommConsegne, 
        s=100, 
        color='maroon', 
        marker='s',
        label='% Dosi Somministrate/Dosi Consegnate')

    xlabels = ['Italia'] + [mapRegioni[i] for i in df.index]
    for a,yl in zip(fig.axes, ['% Dosi Somministrate', '% Dosi Somministrate/Dosi Consegnate']):
        a.set_xticks(x)
        a.tick_params(labelsize=18)
        a.set_xticklabels(
            xlabels, 
            rotation=90, fontsize=18, ha='center'
        )
        a.set_xlim([-1.5*width,len(xlabels)-.5*width])
        a.set_ylabel(yl, fontsize=18)


    handles,labels = [],[]
    for a in [ax1,ax]:
        for h,l in zip(*a.get_legend_handles_labels()):
            handles.append(h)
            labels.append(l)

    ax.grid(lw=.2)
    ax1.grid(False)
    ax1.set_ylim([60,100])
    ax.set_ylim([0,35])
    plt.legend(handles,labels, loc='best',fontsize=18, ncol=2)

    return fig

def RadarAnagrafica(anaVacSumLat):
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16,8))

    maxZoom = 1.1 * max(anaVacSumLat['% Persone Vaccinate Assoluta'])/100

    for a,L,div in zip(ax,[1,maxZoom],[11,6]):

        x = [ L * np.cos(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['Totale'])]
        y = [ L * np.sin(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['Totale'])]

        Tx = [ i/100 * np.cos(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['% Persone Vaccinate Assoluta'])]
        Ty = [ i/100 * np.sin(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['% Persone Vaccinate Assoluta'])]

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
        
                fontsize='20'
                )
        a.axis('off')
        for i in np.linspace(0,L,div):
            a.add_patch(plt.Circle(xy=(0,0),radius=i, fill=None, color='gray', lw=.2))
            a.text(x=i*np.cos(4),y=i * np.sin(4),s=str(int(i*100))+'%',va='center',ha='center', fontsize='10')

        totIta = anaVacSumLat['Persone Vaccinate'].sum() / anaVacSumLat['Platea'].sum()
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
        fontsize=18,
        va='center',
        color='dimgray'
    )

    ax[1].annotate(
        "% Vaccinati\nPer Anagrafica",
        xy=(.12,-.2),
        xytext=(.35, -.12),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle = "angle,angleA=180,angleB=80,rad=70",
            lw=1,
            color='tab:gray'
        ),
        fontsize=18,
        va='center',
        color='dimgray'
    )

    return fig

def ScatterAnagrafica(anaVacSumLat):
    fig, axs = plt.subplots(ncols=1,nrows=1,figsize=(20,14))

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
                s=anaVacSumLat['Persone Vaccinate']/resize,
                c='Steelblue',
                label='Persone Vaccinate',
                alpha=.8
            )
    axs.scatter(x=anaVacSumLat['Fascia Anagrafica'],
                y=[1 for i in range(len(anaVacSumLat))],
                s=anaVacSumLat['Platea']/resize,
                c='gray',
                label='Persone Vaccinate',
                alpha=.2
            )

    axs.set_ylim([0.98,1.02])
    axs.set_xlim([-1,10])
    axs.axis('off')

    for n,i in enumerate(anaVacSumLat['Fascia Anagrafica']): 
        axs.text(x=i,y=0.975,s=i, fontsize=55, ha='center', va='top', fontfamily=' Gill Sans MT', c='#156e45')

    #for n,i in enumerate(anaVacSumLat['% Persone Vaccinate Sul Totale']):   
    #    axs[1].text(x=n, y=1, s=str(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily=' Gill Sans MT', c='navy')
    #for n,i in enumerate(anaVacSumLat['% Persone Vaccinate Assoluta']):   
    #    axs[1].text(x=n, y=1.013, s=str(i,2))+'%', ha='center', va='bottom', fontsize=60, fontfamily=' Gill Sans MT', c='#d20060')
    #for n,i in enumerate(anaVacSumLat['% Totale Assoluto']):   
    #    axs[1].text(x=n, y=1.026, s=str(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily=' Gill Sans MT', c='#e39f1f')

        
    axs.annotate("Totale\nSomministrazioni",
                xy=(7, 0.997),
                xytext=(7.2, 0.985),
                arrowprops=dict(arrowstyle="->",
                                connectionstyle = "angle,angleA=180,angleB=90,rad=120",
                                lw=3,
                                color='k'
                            ),
                fontsize=60,
            )
    #axs[1].annotate("% Seconde Dosi\nSulla Platea",
    #            xy=(-.3, 1.016),
    #            xytext=(-2, 1),
    #            arrowprops=dict(arrowstyle="->",
    #                            connectionstyle = "angle,angleA=90,angleB=0,rad=50",
    #                            lw=3
    #                           ),
    #          ,
    #            fontsize=45,
    #            )
    axs.annotate(
        "Platea",
        xy=(0, 0.997),
        xytext=(-1, 0.99),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle = "angle,angleA=0,angleB=80,rad=110",
            lw=3,
            color='k'
            ),
        fontsize=60,
    )
    axs.annotate(
        "Seconda\nDose",
        xy=(5, 1),
        xytext=(5.3, 1.01),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle = "angle,angleA=180,angleB=-100,rad=120",
            lw=3,
            color='k'
        ),
        ha='left',
        fontsize=60,
    )
    #axs[1].annotate("% Dose Somministrate\nSul Totale Delle Dosi",
    #            xy=(8.3, 1.0285),
    #            xytext=(9, 1.005),
    #            arrowprops=dict(arrowstyle="->",
    #                            connectionstyle = "angle,angleA=90,angleB=0,rad=50",
    #                            lw=3
    #                           ),
    #            ha='left',
    #          ,
    #            fontsize=45,
    #           )
    #axs[1].annotate("% Seconde Dosi\nSulla Platea",
    #            xy=(-.3, 1.02),
    #            xytext=(-1.5, 1.03),
    #            arrowprops=dict(arrowstyle="->",
    #                            connectionstyle = "angle,angleA=90,angleB=0,rad=40",
    #                            lw=3
    #                           ),
    #          ,
    #            fontsize=45,
    #            ha='center'
    #            )
    #axs.text(x=4.,y=1.03,s='Vaccinazioni per fascia anagrafica, fontsize=80, ha='center')
    plt.tight_layout()
    plt.subplots_adjust(left=.5,right=2.1)

    return fig

def makePlot_SomministrazioniCategoriaOLD(df):
    fig, axs = plt.subplots(nrows=4,ncols=2,figsize=(15,20))
    axs = axs.ravel()

    for i in range(df.keys().size):
        df.plot.bar(
            y=df.keys()[i],
            ax=axs[i],
            legend=False,
            width=.9,
            color=['firebrick','royalblue','goldenrod'],
            rot=0,
            fontsize=15
        )
        axs[i].set_title(label=df.keys()[i], fontsize=18)
        axs[i].set_xlabel(xlabel='Data', fontsize=18)
        axs[i].set_ylabel(ylabel='Dosi Somministrate', fontsize=18)
        axs[i].grid(lw=.5)

    plt.tight_layout()                                                  

    fig.delaxes(axs[7])

    return fig

