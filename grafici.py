import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable 

import seaborn as sns
sns.set()



def makePlot_SomministrazioniGiorno(df):
    fig, ax = plt.subplots(1,1,figsize=(20,8))
    df.plot.bar(
        #x='Data Somministrazione',
        y=['Prima Dose', 'Seconda Dose'],
        stacked=True,
        fontsize=15,
        color=['cornflowerblue','darksalmon'],
        width=.9,
        rot=0,
        ax=ax,
    )
    dataPlot = (df.reset_index()['Totale'].rolling(window=7).mean()).fillna(df['Totale'][:7].mean())
    ax.plot(
        dataPlot,
        lw=3,
        color='forestgreen',
        label='Totale Somministrazioni Giornaliere (Media Mobile 7gg)'
    )
    ax.set_xticks(np.arange(0,(plt.xlim()[1]),10))
    ax.grid(lw=.2)
    ax.set_xlabel(xlabel='Data', font='Gill Sans', fontsize=15)
    ax.set_ylabel(ylabel='Dosi Somministrate', font='Gill Sans', fontsize=15)
    ax.legend(fontsize=15)

    return fig

def makePlot_SomministrazioniGiornoFornitore(df):
    fig, ax = plt.subplots()
    df.plot.bar(
        stacked=True,
        figsize=(20,8),
        ax = ax,
        color=['firebrick','royalblue','goldenrod','tomato','skyblue','gold'],
        width=.9,
        ylabel='Somministrazioni',
        rot=0,
        fontsize=15,
    )

    ax.set_xlabel(xlabel='Data', font='Gill Sans', fontsize=15)
    ax.set_ylabel(ylabel='Dosi Somministrate', font='Gill Sans', fontsize=15)
    ax.legend([i + ' ' + j for i,j in df.keys()],loc='upper left', ncol=2, fontsize=15)
    ax.grid(lw=.2)

    ax.set_xticks(np.arange(0,(ax.get_xlim()[1]),10))

    return fig

def makePlot_SomministrazioniCategoria(df):
    fig, axs = plt.subplots(nrows=4,ncols=2,figsize=(15,20))
    axs = axs.ravel()

    for i in range(df.keys().size):
        df.plot.bar(
            y=df.keys()[i],
            ax=axs[i],
            legend=False,
            ylabel='Somministrazioni',
            title=df.keys()[i],
            width=.9,
            color=['tomato','cornflowerblue','gold'],
            #logy=True,
            rot=0,
            fontsize=15
        )
        axs[i].set_xlabel(xlabel='Data', font='Gill Sans', fontsize=15)
        axs[i].set_ylabel(ylabel='Dosi Somministrate', font='Gill Sans', fontsize=15)
        axs[i].grid(lw=.5)

    plt.tight_layout()                                                  

    fig.delaxes(axs[7])

    return fig

def makePlot_SomministrazioniFornitori(df):
    fig, axs = plt.subplots(nrows=4,ncols=1,figsize=(15,20))
    axs = axs.ravel()
    
    maxScale = df.max().max()

    for i,c in zip(range(df.keys().size),['firebrick','royalblue','goldenrod']):
        df.plot.barh(
            y=df.keys()[i],
            ax=axs[i],
            legend=False,
            ylabel='Somministrazioni',
            title=df.keys()[i],
            width=.9,
            color=c,
            rot=0,
            fontsize=15
        )
        axs[i].set_ylabel(ylabel='Categoria', font='Gill Sans', fontsize=15)
        axs[i].grid(lw=.5)
        axs[i].set_xlim([0,maxScale*1.02])

    df.plot.barh(
        stacked=True,
        ax = axs[3],
        color=['firebrick','royalblue','goldenrod'],
        width=.9
    )
    axs[-1].set_xlabel(xlabel='Somministrazioni', font='Gill Sans', fontsize=15)
    axs[-1].set_ylabel(ylabel='Categoria', font='Gill Sans', fontsize=15)
    plt.tight_layout()                                                  

    return fig

def makePlot_AnalisiAnagraficaTotale(df, df_f):
    fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(15,12))
    axs = axs.ravel()  
    
    df['Totale'].plot.bar(
        title='Distribuzione vaccini per fascia anagrafica',
        legend=False,
        color='royalblue',
        width = .9,
        ax = axs[0],
        fontsize=15
    )
    df[['Sesso Maschile', 'Sesso Femminile']].plot.bar(
        stacked=True,
        title='Distribuzione vaccini per fascia anagrafica divisi per sesso',
        legend=False,
        color=['steelblue','coral'],
        width = .9,
        ax = axs[1],
        fontsize=15
    )
    df_f.plot.bar(
        stacked=True,
        title='Distribuzione vaccini per fascia anagrafica divisi per fornitore',
        legend=False,
        color=['firebrick','royalblue','goldenrod'],
        width = .9,
        ax = axs[2],
        fontsize=15
    )
    df['Totale Generale'].plot.bar( 
        alpha=.3,
        ax=axs[3],
        width=.9
     )
    df[['Prima Dose', 'Seconda Dose']].plot.bar(
        stacked=False,
        title='Distribuzione vaccini per fascia anagrafica divisi\n per dose somministrata',
        legend=False,
        color=['cornflowerblue','salmon'],
        width = .9,
        ax = axs[3],
        fontsize=15
    )
    
    for i in axs: 
        i.grid(lw=.2)
        i.set_ylabel('Totale Somministrazioni',fontsize=15)
        i.set_ylabel('Fascia Anagrafica',fontsize=15)
        i.legend(loc='upper left',fontsize=15)
    plt.tight_layout()
    axs[2].legend([i + ' ' + j for i,j in df_f.keys()],loc='upper left',fontsize=15)

    return fig
 
def makePlot_Regioni(df):
    fig, axs = plt.subplots(nrows=2,ncols=2, figsize=(15,20))
    axs = axs.ravel()

    iters = [
        ['% Prima Dose','Blues'],
        ['% Seconda Dose','Reds'],
        ['% Dosi Consegnate/Abitanti','Greens'],
        ['% Dosi Somministrate/Dosi Consegnate','Oranges']
    ]
    for i,ax in zip(iters,axs):
        df.plot(
            column=i[0],
            cmap=i[1],
            ax=ax
        )
        norm = Normalize(vmin=df[i[0]].min(),vmax=df[i[0]].max())
        cbar = fig.colorbar(
            ScalarMappable(
                norm=norm,
                cmap=i[1],
            ),
            ax=ax, 
            shrink=0.75,
            label=i[0],
        )
        cbar.set_label(i[0],fontsize=20)

        ax.axis('off')
        df.boundary.plot(ax=ax, color='k', lw=1)
                    
    plt.tight_layout()

    return fig

def makePlot_MockGartner(df):
    fig,ax=plt.subplots(nrows=2,ncols=1,figsize=(20,20),constrained_layout=True)
    ax=ax.ravel()

    df.plot.scatter(
        ax=ax[0],
        x='% Seconda Dose', 
        y='% Prima Dose',  
        c='% Dosi Somministrate/Dosi Consegnate',
        cmap='autumn',
        edgecolor='k',
        s=400,
        lw=1,
        ylim=(df['% Prima Dose'].min()/1.05,df['% Prima Dose'].max()*1.05),
        xlim=(df['% Seconda Dose'].min()/1.05,df['% Seconda Dose'].max()*1.05),
    )   
    ax[0].set_ylabel('% Prima Dose', fontsize=18)
    ax[0].set_xlabel('% Seconda Dose', fontsize=18)

    for i in df.index:
        ax[0].text(
            x=df.loc[i,'% Seconda Dose'],
            y=df.loc[i,'% Prima Dose']-.3,
            s=i.replace(
                "Valle d'Aosta / Vallée d'Aoste","Valle d'Aosta"
            ).replace(
                "Provincia Autonoma Bolzano / Bozen", 'P.A. Bolzano'
            ).replace(
                "Provincia Autonoma Trento", 'P.A. Trento'
            ),
            ha='left',
            va='center',
            fontsize = 15,
        )

    ax[0].axhline(
        y=sum(ax[0].get_ylim())/2,
        ls='--',
        c='tab:gray'
    )
    ax[0].axvline(
        x=sum(ax[0].get_xlim())/2,
        ls='--',
        c='tab:gray'
    )

    labels = [['Niche Players', 'Challengers'], ['Visionaries', 'Leaders']]
    #labels = [['Niche Players', 'Doses Giver'], ['Protectors', 'Leaders']]
    for yi in [0,1]:
        for xi in [0,1]:  
            ax[0].text(
                y=ax[0].get_ylim()[yi]+(0.3)*(-1)**yi,
                x=sum([ax[0].get_xlim()[xi],sum(ax[0].get_xlim())/2])/2,
                s=labels[xi][yi],
                size=20,
                c='tab:gray',
                va='center',
                ha='center'
            )

    plt.tight_layout()
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
        xy=(.12,-.2),
        xytext=(.35, -.12),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle = "angle,angleA=180,angleB=80,rad=70",
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

    axs.set_ylim([0.98,1.02])
    axs.set_xlim([-1,10])
    axs.axis('off')

    for n,i in enumerate(anaVacSumLat['Fascia Anagrafica']): 
        axs.text(x=i,y=0.975,s=i, fontsize=55, ha='center', va='top', fontfamily='Gill Sans', c='#156e45')

    #for n,i in enumerate(anaVacSumLat['% Seconda Dose Sul Totale']):   
    #    axs[1].text(x=n, y=1, s=str(round(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily='Gill Sans', c='navy')
    #for n,i in enumerate(anaVacSumLat['% Seconda Dose Assoluta']):   
    #    axs[1].text(x=n, y=1.013, s=str(round(i,2))+'%', ha='center', va='bottom', fontsize=60, fontfamily='Gill Sans', c='#d20060')
    #for n,i in enumerate(anaVacSumLat['% Totale Assoluto']):   
    #    axs[1].text(x=n, y=1.026, s=str(round(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily='Gill Sans', c='#e39f1f')

        
    axs.annotate("Totale\nSomministrazioni",
                xy=(7, 0.997),
                xytext=(7.2, 0.985),
                arrowprops=dict(arrowstyle="->",
                                connectionstyle = "angle,angleA=180,angleB=90,rad=120",
                                lw=3,
                                color='k'
                            ),
                font='Gill Sans',
                fontsize=60,
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
        font='Gill Sans',
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
        font='Gill Sans',
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
    #axs.text(x=4.,y=1.03,s='Vaccinazioni per fascia anagrafica',font='Gill Sans', fontsize=80, ha='center')
    plt.tight_layout()
    plt.subplots_adjust(left=.5,right=2.1)

    return fig


def BarPercSomministrazioni(sommRegio):
    fig, ax = plt.subplots(figsize=(15,8))

    x = np.arange(len(sommRegio.index)) 
    width = 0.45
    ax.bar(x - width/2, sommRegio['% Prima Dose'], width, color='cornflowerblue', label='% Prima Dose')
    ax.bar(x + width/2, sommRegio['% Seconda Dose'], width, color='salmon', label='% Seconda Dose')

    ax.legend()
    ax.set_xticks(x)
    ax.tick_params(labelsize=18)
    ax.legend(fontsize=18)
    ax.set_xticklabels(sommRegio.index, rotation=90, fontsize=18)
    ax.set_xlim([-1.5*width,len(sommRegio.index)-.5*width])
    ax.set_ylabel('% Somministrazioni/Abitanti', fontsize=18)

    ax.hlines(
        xmin=-1.5*width,
        xmax=len(sommRegio.index)-.5*width,
        y=sommRegio['Prima Dose'].sum()/sommRegio.Abitanti.sum() * 100,
        ls='--',lw=2,color='navy', label='% Prime Dosi Italia'
    )
    ax.hlines(
        xmin=-1.5*width,
        xmax=len(sommRegio.index)-.5*width,
        y=sommRegio['Seconda Dose'].sum()/sommRegio.Abitanti.sum() * 100,
        ls='--',lw=2,color='maroon', label='% Seconde Dosi Italia'
    )

    return fig




