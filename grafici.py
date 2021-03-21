import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

anaVacSumLat = pd.read_csv('anagraficaVacciniSummaryLatest.csv')

#RADAR PLOT
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16,8))

for a,L,div in zip(ax,[1,25/100],[11,6]):

    x = [ L * np.cos(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['Totale'])]
    y = [ L * np.sin(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['Totale'])]

    Tx = [ i/100 * np.cos(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['% Seconda Dose Assoluta'])]
    Ty = [ i/100 * np.sin(n * 2*np.pi/len(anaVacSumLat)) for n,i in enumerate(anaVacSumLat['% Seconda Dose Assoluta'])]

    x.append(x[0]),y.append(y[0])
    Tx.append(Tx[0]),Ty.append(Ty[0])

    a.plot(x,y,lw=0)
    a.fill(Tx,Ty,fill=True,color='#d20060',alpha=.4)

    for n,i in enumerate(anaVacSumLat['Fascia Anagrafica']):
        a.text(x[n]+.1*x[n],
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
        
ax[1].annotate("% Vaccinati Italia",
               xy=(.05,.02),
               xytext=(.2, .1),
               arrowprops=dict(arrowstyle="->",
                               connectionstyle = "angle,angleA=50,angleB=-10,rad=70",
                               lw=1,
                               color='tab:gray'
                              ),
               font='Gill Sans',
               fontsize=18,
               va='center',
               color='dimgray'
            )

ax[1].annotate("% Vaccinati\nPer Anagrafica",
               xy=(.05,-.1),
               xytext=(.2, -.25),
               arrowprops=dict(arrowstyle="->",
                               connectionstyle = "angle,angleA=180,angleB=100,rad=70",
                               lw=1,
                               color='tab:gray'
                              ),
               font='Gill Sans',
               fontsize=18,
               va='center',
               color='dimgray'
            )

plt.show()

# SCATTER
fig, axs = plt.subplots(ncols=1,nrows=2,figsize=(40,25))

resize = 120

axs[0].scatter(x=anaVacSumLat['Fascia Anagrafica'],
            y=[1 for i in range(len(anaVacSumLat))],
            s=anaVacSumLat['Totale']/resize,
            alpha=.6,
            c='cornflowerblue',
            label='Somministrazioni'
           )
axs[0].scatter(x=anaVacSumLat['Fascia Anagrafica'],
            y=[1 for i in range(len(anaVacSumLat))],
            s=anaVacSumLat['Seconda Dose']/resize,
            c='Steelblue',
            label='Seconda Dose',
            alpha=.8
           )
axs[0].scatter(x=anaVacSumLat['Fascia Anagrafica'],
            y=[1 for i in range(len(anaVacSumLat))],
            s=anaVacSumLat['Platea']/resize,
            c='gray',
            label='Seconda Dose',
            alpha=.2
           )
for ax in axs:
    ax.set_ylim([0.98,1.04])
    ax.set_xlim([-1,10])
    ax.axis('off')

for n,i in enumerate(anaVacSumLat['Fascia Anagrafica']): 
    axs[0].text(x=i,y=0.975,s=i, fontsize=50, ha='center', va='top', fontfamily='Gill Sans', c='#156e45')

#for n,i in enumerate(anaVacSumLat['% Seconda Dose Sul Totale']):   
#    axs[1].text(x=n, y=1, s=str(round(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily='Gill Sans', c='navy')
#for n,i in enumerate(anaVacSumLat['% Seconda Dose Assoluta']):   
#    axs[1].text(x=n, y=1.013, s=str(round(i,2))+'%', ha='center', va='bottom', fontsize=60, fontfamily='Gill Sans', c='#d20060')
#for n,i in enumerate(anaVacSumLat['% Totale Assoluto']):   
#    axs[1].text(x=n, y=1.026, s=str(round(i,2))+'%', ha='center', va='bottom', fontsize=50, fontfamily='Gill Sans', c='#e39f1f')

    
axs[0].annotate("Totale\nSomministrazioni",
            xy=(7, 0.996),
            xytext=(8, 0.985),
            arrowprops=dict(arrowstyle="->",
                            connectionstyle = "angle,angleA=180,angleB=90,rad=60",
                            lw=3
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
axs[0].annotate("Platea",
            xy=(0, 0.997),
            xytext=(-1, 0.99),
            arrowprops=dict(arrowstyle="->",
                            connectionstyle = "angle,angleA=0,angleB=80,rad=50",
                            lw=3
                           ),
            font='Gill Sans',
            fontsize=45,
           )
axs[0].annotate("Seconda\nDose",
            xy=(5, 1),
            xytext=(6, 1.015),
            arrowprops=dict(arrowstyle="->",
                            connectionstyle = "angle,angleA=180,angleB=-100,rad=70",
                            lw=3
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
axs[0].text(x=4.,y=1.03,s='Vaccinazioni per fascia anagrafica',font='Gill Sans', fontsize=70, ha='center')

plt.show()
