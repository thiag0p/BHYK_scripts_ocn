# -*- coding: utf-8 -*-
'''
    Rotina para elaboração de gráfico da semana operacional

'''

from datetime import timedelta, date
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from pandas import ExcelWriter, concat
from sys import path

pth1 = 'XXXXXXXXXXXXXXXXXXXX'
dirs = ['data', 'graph', 'settings']
for d in dirs:
    pth2 = pth1 + d
    path.append(pth2)
import definitions as mopdef
from custom import caxes, plot_custom
import OCNdb as ocn
plot_custom.temp_serie_config()
from pyocnp import acronym2ext as acron

# _____________________________________________________________________________

# Definindo unidades de interesse
UCDS = mopdef.get_ucds_representativas()

# Definindo as datas iniciais e finais de busca de dados (HORA UTC)
today = date.today()
DATEMIN = (today - timedelta(days=8)).strftime('%d/%m/%Y 03:00:00')
DATEMAX = (today - timedelta(days=1)).strftime('%d/%m/%Y 02:00:00')

# caminho onde será salva imagem
PATH = ("XXXXXXXXXXXXXXXXXXXXXXX")

# _____________________________________________________________________________
#                           Alguns ajustes
# _____________________________________________________________________________

# Definindo delta para ajusta de UTC para hora local
deltat = timedelta(hours=3)

# _____________________________________________________________________________
#                           Carregando os dados
# _____________________________________________________________________________

data_dict = {}
print('{:80}'.format(80 * '#'))
for basin in ['Bacia de Santos', 'Bacia de Campos']:
    print('{}{:^76}{}'.format(2 * '#', 'Lendo dados da ' + basin, 2 * '#'))
    for prmdb, prm in zip(('meteo', 'wave'), ('VENTO', 'ONDA')):
        print('{}  {:<74}{}'.format(
            2 * '#', 'CARREGANDO ' + prm + '...', 2 * '#'))
        ucds_priori = UCDS.loc[basin].VENTO.values.tolist()
        ucds = [y for x in ucds_priori for y in x if y is not None]

        data = ocn.get_BDs(
            ucds=ucds,
            dates=[DATEMIN, DATEMAX],
            param=prmdb)
        print('{}  {:<74}{}'.format(2 * '#', prm + ' OK', 2 * '#'))
        data_dict['{} - {}'.format(basin, prm)] = data
    print('{}{}{}'.format(2 * '#', 76 * '-', 2 * '#'))

print('{:80}'.format(80 * '#'))
print('{}{:^76}{}'.format(
    2 * '#', '**** Carregamento dos dados finalizado ****', 2 * '#'))
print('{:80}'.format(80 * '#'))

# _____________________________________________________________________________
#               Definições gráficas para implementação no plot
# _____________________________________________________________________________
colors = [
    '#1C1C1C', '#1f77b4', '#008B8B', '#D62728', '#7F7F7F', '#9467BD',
    '#Ff7f0e', '#E377C2', '#8C564B', '#BCBD22', '#0000FF', '#2CA02C',
    '#FFA54F', '#B0E2FF', '#CDBA96', '#FF83FA', '#00688B', '#EED5D2',
    '#FF7F50', '#E6E6FA', '#8B7355', '#F0E68C', '#FF0000', '#FF00FF',
    '#2F4F4F', '#17BECF', '#FF6347', '#54FF9F', '#8B8B00', '#FFFF00',
    '#228B22', '#00FFFF', '#9B30FF', '#00FA9A']

# _____________________________________________________________________________
#                           PLOTANDO
# _____________________________________________________________________________

colm = {'VENTO': ['WSPD', 1.94384449], 'ONDA': ['VAVH', 1]}

for inf, dataplot in data_dict.items():
    print(
        '{}  {:<74}{}'.format(2 * '#', 'Plotando ' + inf, 2 * '#'))

    acr = colm[inf.split('- ')[1]][0]
    fat = colm[inf.split('- ')[1]][1]

    fig, ax = plt.subplots(1, 1, figsize=[15, 10])

    ixcolor = 0
    # Laço por UCD
    for ucd in set(dataplot.index.get_level_values(level=0)):
        udata = dataplot.loc[ucd].droplevel(0)

        plot = (udata[acr] * fat).to_frame()

        ax.plot(
            plot[acr].dropna().index - deltat,
            plot[acr].dropna(),
            marker='o',
            color=colors[ixcolor],
            linewidth=2,
            label=ucd)
        ixcolor += 1

    if acr == 'VAVH':
        ax.set_ylabel('{} ({})'.format(acron(acr)[0], acron(acr)[1]))
        ax.set_ylim(list(ax.get_ylim()))
        ax.fill_between(
            plot[acr].dropna().index - deltat,
            y1=2.5, y2=ax.get_ylim()[1] + 2,
            color='r', alpha=.4)

    if acr == 'WSPD':
        ax.set_ylabel(
            '{} ({})'.format(acron(acr)[0], acron(acr)[1]),
            fontsize=16)
        ax.set_ylim(list(ax.get_ylim()))
        ax.fill_between(
            plot[acr].dropna().index - deltat,
            y1=20, y2=28,
            color='#f4d03f', alpha=.6)
        ax.fill_between(
            plot[acr].dropna().index - deltat,
            y1=28, y2=ax.get_ylim()[1] + 10,
            color='r', alpha=.4)
    else:
        ax.set_ylabel(
            '{} (nós)'.format(acron(acr)[0]),
            fontsize=16)
    ax.grid('on')
    ax.set_xlim(
        [plot.index[0] - deltat, plot.index[-1] - deltat])
    caxes.fmt_time_axis(ax)
    ax.set_title(inf, fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=14)

    ax.legend(
        bbox_to_anchor=(0., -0.22, 1., .102),
        loc='center', ncol=6, mode="expand",
        borderaxespad=0., fontsize=12)

    fig.savefig(
        '{}\\{}.png'.format(PATH, inf.replace(' ', '_')),
        format='png',
        bbox_inches='tight',
        dpi=300)

print('{}{:^76}{}'.format(
    2 * '#', '**** Elaboração dos plots finalizada ****', 2 * '#'))
print('{:80}'.format(80 * '#'))
