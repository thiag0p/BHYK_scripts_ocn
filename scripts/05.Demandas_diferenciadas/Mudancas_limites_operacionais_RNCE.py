'''
Rotina criada para realização de relatório referente à modificação dos limites
operacionais nas bacias de RN e CE.
'''
# _____________________________________________________________________________
#                               Modificar aqui
# _____________________________________________________________________________
# caminho onde devem ser salvos os dados
PATH = ("XXXXXXXXXXXXXXXX")

# UCDS de interesse
ucdmeteo = ['XXXXXXX']
ucdwave = ['XXXXXXXXXX']

# limites de vento e onda
limwind = 21.9
limwave = 2.5

# Definindo as datas iniciais e finais de busca de dados (HORA UTC)
DATEMIN = u"01/01/2013 03:00:00"
DATEMAX = u"31/12/2020 02:00:00"
# _____________________________________________________________________________

from datetime import timedelta
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from pandas import ExcelWriter, DataFrame, Grouper, concat
from sys import path
import locale
locale.setlocale(locale.LC_TIME, '')

pth1 = 'XXXXXXXXXXXXXXX'
dirs = ['data', 'graph', 'math']
for d in dirs:
    pth2 = pth1 + d
    path.append(pth2)
from custom import caxes, plot_custom
import OCNdb as ocn
plot_custom.temp_serie_config()
import statistic as st
from custom import caxes
# _____________________________________________________________________________
#                           Alguns ajustes
# _____________________________________________________________________________

# Definindo delta para ajusta de UTC para hora local
deltat = timedelta(hours=3)
# criando datetime do tempo final e incial para ajusta do eixo
dti = dt.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S') + deltat
dtf = dt.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S') + deltat

# _____________________________________________________________________________
#                           LENDO E PLOTANDO VENTO
# _____________________________________________________________________________

wd_data = ocn.get_BDs(ucdmeteo, [DATEMIN, DATEMAX], 'meteo')
wd_data.WSPD = wd_data.WSPD * 1.94384449
wdspd = wd_data.loc[ucdmeteo[0]].loc['YOUNG'].WSPD.to_frame()

excelfile = ExcelWriter(f'{PATH}\\vento_valores_estatistca.xlsx')
table1, table2 = DataFrame(), DataFrame()
# PLOTANDO
for y in set(wdspd.index.year):
    slc = wdspd[wdspd.index.year == y]
    fig, ax = plt.subplots(3, 1, figsize=[15, 10])
    fig.subplots_adjust(wspace=.35, hspace=.32)

    # Plota série temporal
    slc.plot(ax=ax[0], marker='o')
    ax[0].legend('')
    ax[0].grid('on')
    ylims = ax[0].get_ylim()
    ax[0].fill_between(slc.index, limwind, 50, color='r', alpha=.2)
    ax[0].plot(slc.index, [limwind] * slc.shape[0], color='r', linestyle='--')
    ax[0].set_ylim(ylims)
    ax[0].set_ylabel('Intensidade média do vento (nós)')
    caxes.fmt_time_axis(ax[0])

    # Plota percentual mensal
    perc = st.percentual(slc, [limwind], '.1f', 'Intensidade',
                         atype='mensal', signal=0)
    perc.plot.bar(ax=ax[1], legend='False')
    ax[1].grid('on')
    ax[1].set_ylabel(f'Percentual \u2265 {limwind} nós')
    ax[1].legend('')
    # Plota estatistica das diferenças
    df = slc[slc >= limwind] - limwind
    dfg = df.groupby(
        Grouper(freq='M')).agg(['max', 'mean', 'std'], axis='columns')
    dfg.index = [x.strftime('%b') for x in dfg.index]
    dfg.columns = ['Máxima', 'Média', 'Desv. Pad.']

    dfg.plot.bar(ax=ax[2])
    ax[2].grid('on')
    ax[2].set_ylabel(f'Diferença em nós dos resgistrados\nacima de {limwind}')

    fig.savefig(f'{PATH}\\{y}_wind.png',
                format='png',
                bbox_inches='tight',
                dpi=600)

    # Escrevendo no excel
    table1 = concat([
        table1, perc.rename(columns={f'\u2265 {limwind}': str(y)})], axis=1)
    table2 = table2.append(concat([dfg], keys=[y], names=['ANO']))
table1.to_excel(excelfile, sheet_name='percentual mensal')
table2.to_excel(excelfile, sheet_name='estatistica da diferenca')
excelfile.close()

# _____________________________________________________________________________
#                           LENDO E PLOTANDO ONDA
# _____________________________________________________________________________

wv_data = ocn.get_BDs(ucdmeteo, [DATEMIN, DATEMAX], 'wave')
wvhs = wv_data.loc[ucdmeteo[0]].loc['FSI3D'].VAVH.to_frame()

# PLOTANDO
for y in set(wvhs.index.year):
    slc = wvhs[wvhs.index.year == y]
    fig, ax = plt.subplots(2, 1, figsize=[15, 10])
    fig.subplots_adjust(wspace=.35, hspace=.32)

    # Plota série temporal
    slc.plot(ax=ax[0], marker='o')
    ax[0].legend('')
    ax[0].grid('on')
    ylims = ax[0].get_ylim()
    ax[0].fill_between(slc.index, limwave, 7, color='r', alpha=.2)
    ax[0].plot(slc.index, [limwave] * slc.shape[0], color='r', linestyle='--')
    ax[0].set_ylim(ylims)
    ax[0].set_ylabel('Altura significativa (m)')
    caxes.fmt_time_axis(ax[0])

    # Plota percentual mensal
    perc = st.percentual(slc, [limwave], '.1f', 'Hs',
                         atype='mensal', signal=0)
    perc.plot.bar(ax=ax[1], legend='False')
    ax[1].grid('on')
    ax[1].set_ylabel(f'Percentual \u2265 {limwave} m')
    ax[1].legend('')

    fig.savefig(f'{PATH}\\{y}_wave.png',
                format='png',
                bbox_inches='tight',
                dpi=600)
