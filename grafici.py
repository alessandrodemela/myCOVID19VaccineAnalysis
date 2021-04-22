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
from sklearn.linear_model import LinearRegression

import seaborn as sns
sns.set()

# Auxiliary objects
def getTicksLabels(a):
    formatData = '%d %b'
    labels = [datetime(day=d,month=m,year=2021).strftime(formatData) for m in range(1,datetime.today().month+1) for d in [1,15] ]
    labelsTMP = [i.strftime(formatData) for i in a]
    ticks=[labelsTMP.index(i) for i in labels]

    return labels, ticks

mapRegioni = {
    'Abruzzo'                               : 'ABR',
    'Basilicata'                            : 'BAS',
    'Provincia Autonoma Bolzano / Bozen'    : 'PAB',
    'Calabria'                              : 'CAL',
    'Campania'                              : 'CAM',
    'Emilia-Romagna'                        : 'EMR',
    'Friuli-Venezia Giulia'                 : 'FVG',
    'Lazio'                                 : 'LAZ',
    'Liguria'                               : 'LIG',
    'Lombardia'                             : 'LOM',
    'Marche'                                : 'MAR',
    'Molise'                                : 'MOL',
    'Piemonte'                              : 'PIE',
    'Puglia'                                : 'PUG',
    'Sardegna'                              : 'SAR',
    'Sicilia'                               : 'SIC',
    'Toscana'                               : 'TOS',
    'Provincia Autonoma Trento'             : 'PAT',
    'Umbria'                                : 'UMB',
    "Valle d'Aosta / Vallée d'Aoste"        : 'VDA',
    'Veneto'                                : 'VEN'
}

coloreFornitori = ['firebrick','royalblue','goldenrod','hotpink']


# Plotting Functions

def makePlot_Indicatori(KPI, aux):
    cols = 1
    rows = int(np.ceil(len(KPI.items())/cols))

    fig, axs = plt.subplots(nrows = rows, ncols = cols, figsize=(8,15), facecolor='#eceff4')
    axs = axs.ravel()

    colors = [
        'k',
        'k',
        'k',
        'k',
        sns.color_palette()[0],         # prime dosi
        sns.color_palette()[1]          # seconde dosi
    ]
    for ax,i,c in zip(axs,KPI.items(),colors):
        ax.set_facecolor('xkcd:white')
        ax.tick_params(axis='x', colors='w')
        ax.tick_params(axis='y', colors='w')
        ax.text(0.5, 0.9, i[0], font='Gill Sans', size=20, ha='center', va='center')
        ax.text(0.5, 0.5, '{:,}'.format(i[1]), font='Gill Sans', size=60, ha='center', va='center', color=c)
        ax.axis('off')

    axs[1].text(0.5, 0.2, aux['Data Ultime Somministrazioni'], font='Gill Sans', size=20, ha='center', va='center')
    axs[3].text(0.5, 0.2, aux['Data Ultima Consegna'], font='Gill Sans', size=20, ha='center', va='center')
    axs[4].text(0.5, 0.2, f'{aux["Percentuale Prime Dosi"]:.2%}', font='Gill Sans', size=20, ha='center', va='center')
    axs[5].text(0.5, 0.2, f'{aux["Percentuale Seconde Dosi"]:.2%}', font='Gill Sans', size=20, ha='center', va='center')
    

    plt.tight_layout()

    return fig


def makePlot_SomministrazioniLastWeek(df, n):
    def getDateRangeFromWeek(p_year,p_week):
        firstdayofweek = datetime.strptime(f'{p_year}-W{int(p_week )- 1}-1', "%Y-W%W-%w").date()
        lastdayofweek = firstdayofweek + timedelta(days=6.9)
        return firstdayofweek.strftime('%d/%m'), lastdayofweek.strftime('%d/%m')

    def predictCurrentWeek():
        '''Predict current week'''
        X=np.array(df.index)[:-1].reshape(-1,1)
        y=df.Totale[:-1]
        Xpred = [[np.array(df.index)[-1]]]

        return LinearRegression().fit(X,y).predict(Xpred)

    def makePlot(fig, ax):
        '''Make the actual Plot'''

        predicted = predictCurrentWeek()
        ax.bar(n-1, predicted, color='tab:gray',alpha=0.5,width=.5)

        df.plot.bar(legend=False, fontsize=18, ax=ax)

        for i in range(len(xlabels)):
            last = True if i==len(xlabels)-1 else False
            ax.text(
                x=i, y=df['Totale'].iloc[i]- [5e4 if last else 0], 
                s=f"{df['Totale'].iloc[i]:,}",
                fontsize=15,ha='center',
                va='bottom' if not last else 'top',
                color='k' if not last else 'white',
            )
        ax.text(x=i,y=predicted,s=f"{int(predicted):,}",fontsize=15,ha='center',va='bottom',color='k',alpha=.5)

        ax.set_xlabel('Settimana', fontsize=18)
        ax.set_ylabel('Somministrazioni', fontsize=18)
        ax.set_xticklabels(labels=xlabels, rotation=0)
        ax.set_ylim([0,predicted[0]*1.1])
        ax.grid(lw=.2)
        ax.legend(['Stima','Totale'], fontsize=15, loc='upper left')


    # Prepare DataFrame
    df = df[['Data Somministrazione','Totale']].groupby('Data Somministrazione').sum().reset_index()
    df['Settimana'] = pd.to_datetime(df['Data Somministrazione']).dt.isocalendar().week+1
    df = df.groupby('Settimana').sum()[:-2][-n:]

    # Convert week labels in interval range
    xlabels=[]
    for i in df.index: 
        print(*getDateRangeFromWeek(2021,i))
        xlabels.append(getDateRangeFromWeek(2021,i)[0]+'-'+getDateRangeFromWeek(2021,i)[1])

    # Now, plot
    fig, ax = plt.subplots(1,1,figsize=(15,5))
    makePlot(fig, ax)
    
    return fig


def makePlot_SomministrazioniGiorno(df):
    fig, ax = plt.subplots(1,1,figsize=(15,8))
    df.plot.bar(
        y=['Prima Dose', 'Seconda Dose'],
        stacked=True,
        fontsize=18,
        #color=['cornflowerblue','darksalmon'],
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
    labels, ticks = getTicksLabels(df.index)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=18)
    ax.grid(lw=.2)
    ax.set_xlabel(xlabel='Data', font='Gill Sans', fontsize=18)
    ax.set_ylabel(ylabel='Dosi Somministrate', font='Gill Sans', fontsize=18)
    ax.legend(fontsize=18)

    return fig


def makePlot_SomministrazioniGiornoFornitore(df):
    fig, ax = plt.subplots()
    df.plot.bar(
        stacked=True,
        figsize=(15,8),
        ax = ax,
        color=['firebrick','royalblue','goldenrod','tomato','skyblue','gold'],
        width=.9,
        ylabel='Somministrazioni',
        rot=0,
        fontsize=18,
    )
    labels, ticks = getTicksLabels(df.index)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=18)
    ax.grid(lw=.2)
    ax.set_xlabel(xlabel='Data', font='Gill Sans', fontsize=18)
    ax.set_ylabel(ylabel='Dosi Somministrate', font='Gill Sans', fontsize=18)

    ax.legend([j for i,j in df.keys()],loc='upper left', fontsize=18)

    return fig


def makePlot_ConsegneSomministrazioni(df):
    fig,ax=plt.subplots(1,1,figsize=(15,8))
    df.plot(
        y=['Dosi Somministrate','Dosi Consegnate'],
        color=['salmon','cornflowerblue'],
        lw=2,
        fontsize=18,
        xlabel='Data',
        ax=ax,
        legend=False,
    )
    ax.set_ylabel('Numero Dosi',fontsize=18)
    ax.set_xlabel('Data',fontsize=18)
    ax.grid(lw=.4)

    ax1=ax.twinx()
    df['% Somministrazioni/Consegne'].plot(
        color=['forestgreen'],
        lw=2,
        fontsize=15,
        xlabel='Data',
        label='% Somministrazioni/Consegne (media mobile 7gg)',
        ax=ax1,
        ylim=[0,100]
    )
    ax1.set_ylabel('% Dosi Somministrazioni/Dosi Consegna',fontsize=18)
    ax1.grid(False)

    labels = [datetime(day=d,month=m,year=2021).strftime('%d %b') for m in range(1,datetime.today().month+1) for d in [1,15] ]
    labelsTMP = [i.strftime('%d %b') for i in df.index]
    ticks_loc = ax.get_xticks().tolist()
    ax1.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
    ax1.set_xticklabels(labels, fontsize=18)

    handles,labels = [],[]
    for ax in fig.axes:
        for h,l in zip(*ax.get_legend_handles_labels()):
            handles.append(h)
            labels.append(l)
            
    plt.legend(handles,labels, loc='lower right',fontsize=15)

    return fig


def makePlot_ConsegneSomministrazioniFornitore(df):

    lista = [[i,j] for i,j in zip(df.keys()[:int(len(df.keys())/2)],df.keys()[int(len(df.keys())/2):])]
    color=[['firebrick','tomato'],['royalblue','skyblue'],['goldenrod','gold'],['lightpink','hotpink']]

    fig, axs = plt.subplots(ncols=2,nrows=int(round(len(lista) + .99)/2), figsize=(15,12))
    axs = axs.ravel()

    for ax,i,c in zip(axs,lista,color):
        df.plot(
            y=i,
            color=c,
            lw=2,
            ls='solid',
            ax=ax,
            label=[l.split()[0] for l in i],
            fontsize=18,
        )
        ax.grid(lw=.5)
        ax.set_title(i[0].split()[1],fontsize=18)
        ax.legend(fontsize=15)

        formatData='%B'
        labels = [datetime(day=1,month=m,year=2021).strftime(formatData) for m in range(1,datetime.today().month+1)]
        labelsTMP = [i.strftime(formatData) for i in df.index]
        ticks_loc = ax.get_xticks().tolist()
        ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc[::2]))
        ax.set_xticklabels(labels, fontsize=18)
        ax.set_xlabel('Data', fontsize=18)
        ax.set_ylabel('Numero Dosi', fontsize=18)

        ax.annotate(
            f'Somministrate: {df[i].iloc[-1][0]/df[i].iloc[-1][1]:.2%}', 
            fontsize=18,
            xy = (mdates.date2num(list(df.index)[0]), df[i].max().max()*0.8))
        
    if (len(lista)%2!=0):
        fig.delaxes(axs[-1])

    plt.tight_layout()  


    return fig


def makePlot_SomministrazioniCategoria(df):
    fig, axs = plt.subplots(nrows=4,ncols=3,figsize=(15,15))
    axs = axs.ravel()

    for i in range(df.keys().size):
        df.plot.pie(
            y=df.keys()[i],
            ax=axs[i] if i<=8 else axs[10],
            legend=False,
            colors=['firebrick','royalblue','goldenrod'],
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

    return fig


def makePlot_SomministrazioniFornitori(df):
    nrows = len(df.keys())+1
    fig, axs = plt.subplots(nrows=nrows,ncols=1,figsize=(15,6*nrows))
    axs = axs.ravel()

    maxScale = df.sum(axis=1).max()

    for i,c in zip(range(df.keys().size),coloreFornitori):
        df.plot.barh(
            y=df.keys()[i],
            ax=axs[i],
            legend=False,
            ylabel='Somministrazioni',
            width=.9,
            color=c,
            rot=0,
            fontsize=18
        )
        axs[i].set_ylabel(ylabel='Categoria', font='Gill Sans', fontsize=18)
        axs[i].grid(lw=.5)
        axs[i].set_xlim([0,maxScale*1.02])
        axs[i].set_title(label=df.keys()[i], fontsize=20)

    df.plot.barh(
        stacked=True,
        ax = axs[3],
        color=coloreFornitori,
        width=.9,
        fontsize=18
    )
    axs[-1].set_xlabel(xlabel='Somministrazioni', font='Gill Sans', fontsize=18)
    axs[-1].set_ylabel(ylabel='Categoria', font='Gill Sans', fontsize=18)
    axs[-1].set_xlim([0,maxScale*1.02])
    axs[-1].set_title(label='Tutti i fornitori', fontsize=20)
    axs[-1].legend(fontsize=18)
    axs[-1].grid(lw=.5)

    plt.tight_layout()                                                     

    return fig


def makePlot_AnalisiAnagraficaTotale(df, df_f):
    fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(15,12))
    axs = axs.ravel()  
    
    df['Totale'].plot.bar(
        legend=False,
        color='royalblue',
        width = .9,
        ax = axs[0],
        fontsize=15,
        rot=0
    )
    df[['Sesso Maschile', 'Sesso Femminile']].plot.bar(
        stacked=True,
        legend=False,
        color=['steelblue','coral'],
        width = .9,
        ax = axs[1],
        fontsize=15,
        rot=0
    )
    df_f.plot.bar(
        stacked=True,
        legend=False,
        color=coloreFornitori,
        width = .9,
        ax = axs[2],
        fontsize=15,
        rot=0
    )
    df['Totale Generale'].plot.bar( 
        alpha=.3,
        ax=axs[3],
        width=.9
     )
    df[['Prima Dose', 'Seconda Dose']].plot.bar(
        stacked=False,
        legend=False,
        color=['cornflowerblue','salmon'],
        width = .9,
        ax = axs[3],
        fontsize=15,
        rot=0
    )
    
    titles = [
        'Distribuzione vaccini per fascia anagrafica', 'Distribuzione vaccini per fascia anagrafica divisi per sesso',
        'Distribuzione vaccini per fascia anagrafica\ndivisi per fornitore', 'Distribuzione vaccini per fascia anagrafica divisi\n per dose somministrata'
    ]
    for i,t in zip(axs, titles): 
        i.grid(lw=.2)
        i.set_ylabel('Totale Somministrazioni',fontsize=18)
        i.set_xlabel('Fascia Anagrafica',fontsize=18)
        i.set_title(t, fontsize=18)
        i.legend(loc='best',fontsize=18)

    axs[-1].set_ylabel('Totale Somministrazioni - Generale',fontsize=18)
    axs[-1].set_ylim([0,df['Totale Generale'].max()*1.2])
    axs[2].legend([j for i,j in df_f.keys()],loc='upper left',fontsize=18)

    plt.tight_layout()
    

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
            shrink=0.5,
            label=i[0],
        )
        cbar.set_label(i[0],fontsize=20)

        ax.axis('off')
        df.boundary.plot(ax=ax, color='k', lw=1)
        ax.legend()
                    
    plt.tight_layout()

    return fig


def makePlot_BarPercSomministrazioni(df):
    fig, ax = plt.subplots(figsize=(15,8))

    x = np.arange(len(df.index)+1) 
    width = 0.45

    yPrimaIta = df['Prima Dose'].sum()/df['Totale Generale'].sum()*100
    yPrima = pd.concat([pd.Series({'Italia': yPrimaIta}),df['% Prima Dose']])

    ySecondaIta = df['Seconda Dose'].sum()/df['Totale Generale'].sum()*100
    ySeconda = pd.concat([pd.Series({'Italia': ySecondaIta}),df['% Seconda Dose']])

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
        label='% Seconda Dose'
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
    for a,yl in zip(fig.axes, ['% Somministrazioni/Abitanti', '% Dosi Somministrate/Dosi Consegnate']):
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
    ax.set_ylim([0,30])
    plt.legend(handles,labels, loc='best',fontsize=18, ncol=3)

    return fig


def makePlot_MockGartner(df):  
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,8))
    cmap = 'autumn_r'
    
    def scatter(ax,lx,ly):
        df.plot.scatter(
            ax=ax,
            x=lx, 
            y=ly,  
            c='% Dosi Somministrate/Dosi Consegnate',
            edgecolor='k',
            cmap=cmap,
            s=1000,
            lw=1,
            ylim=(df[ly].min()/1.05,df[ly].max()*1.05),
            xlim=(df[lx].min()/1.05,df[lx].max()*1.05),
            colorbar=False
        )  
        
    def colorbar(ax):
        norm = Normalize(vmin=df['% Dosi Somministrate/Dosi Consegnate'].min(),vmax=df['% Dosi Somministrate/Dosi Consegnate'].max())
        cbar = fig.colorbar(
                ScalarMappable(
                    norm=norm,
                    cmap=cmap,
                ),
                ax=ax, 
                shrink=0.9,
        )
        cbar.set_label('% Dosi Somministrate/Dosi Consegnate',fontsize=20)
        
    def attachLabels(ax,lx,ly):
        for i in df.index:
            ax.text(
                s=mapRegioni[i],
                x=df.loc[i,lx],
                y=df.loc[i,ly],
                ha='center',
                va='center',
                fontsize=15
            )

    scatter(ax,'% Seconda Dose','% Prima Dose')
    colorbar(ax)
    attachLabels(ax,'% Seconda Dose','% Prima Dose')
        
    ax.set_ylabel('% Prima Dose', fontsize=18)
    ax.set_xlabel('% Seconda Dose', fontsize=18)
    
    hline = df['Prima Dose'].sum()/df['Totale Generale'].sum()*100
    vline = df['Seconda Dose'].sum()/df['Totale Generale'].sum()*100
    ax.hlines(
        xmin=0, xmax=100,
        y=df['% Prima Dose'].mean(),
        ls='--',lw=2,color='tab:gray', alpha=.5
    )
    ax.vlines(
        ymin=0, ymax=100,
        x=vline,
        ls='--',lw=2,color='tab:gray', alpha=.5
    )
    ax.text(
        x=df['% Seconda Dose'].max(), y=hline-.1, s='% Prima Dose\nItalia', 
        c='tab:gray', fontsize=18, va='baseline', ha='center'
    )
    ax.text(
        y=df['% Prima Dose'].max()+1, x=vline, s='% Seconda Dose\nItalia', 
        c='tab:gray', fontsize=18, va='top', ha='left',rotation=-90
    )
    

    plt.tight_layout()

    return fig


## EXPERIMENTAL/UNUSED PLOTS


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
    #    axs[1].text(x=n, y=1, s=str(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily='Gill Sans', c='navy')
    #for n,i in enumerate(anaVacSumLat['% Seconda Dose Assoluta']):   
    #    axs[1].text(x=n, y=1.013, s=str(i,2))+'%', ha='center', va='bottom', fontsize=60, fontfamily='Gill Sans', c='#d20060')
    #for n,i in enumerate(anaVacSumLat['% Totale Assoluto']):   
    #    axs[1].text(x=n, y=1.026, s=str(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily='Gill Sans', c='#e39f1f')

        
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
        axs[i].set_xlabel(xlabel='Data', font='Gill Sans', fontsize=18)
        axs[i].set_ylabel(ylabel='Dosi Somministrate', font='Gill Sans', fontsize=18)
        axs[i].grid(lw=.5)

    plt.tight_layout()                                                  

    fig.delaxes(axs[7])

    return fig



