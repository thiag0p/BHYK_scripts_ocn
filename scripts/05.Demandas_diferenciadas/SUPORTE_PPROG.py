'''
Rotina elaborada para consultoria de suporte pprog.

Edição:
    + 11/08/2020
        Ajustado o caso dos dias secos! A Rotina estava considerando os dias
        secos como dados NaN, quando na verdade os dados de dias de secos
        passaram a ser representados como 0.
    + 10/09/2020
        No momento de realizar a análise cruzada, agora só são considerados os
        meses e anos em que a operacionalidade foi acima de 80% para o tempo de
        coleta simultanea.

'''

# -*- coding: utf-8 -*-
import numpy as np
# _____________________________________________________________________________
#                             MODIFICAR AQUI
# _____________________________________________________________________________

# Unidade de interesse para sensor de vento
UCD_WIND = ["XXXXXXXXXXXX"]
# Unidade de interesse para sensor de onda
UCD_WAVE = ["XXXXXXXXXXXX"]
# Unidade de interesse para sensor de precipitação
UCD_PREC = ["XXXXXXXXXXXX"]

DATEMIN = "01/01/2015 00:00:00"
DATEMAX = "31/12/2019 23:00:00"

# Unidade de medida para o vento
UNID = "nós"

# diretorio onde serão salvos os resultados (substitui \ por \\)
PATH = ("XXXXXXXXXXXXXXXXXXXX")

# limites atenção e alerta de vento (nós)
WIND_LIM = [21.6, 24.8]
# limites atenção e alerta de altuma de onda (m)
WAVE_LIM = [2., 3.]
# Lista para alturas de operação (em m)
HOP = [20., 50, 100]
# Altura escolhida para ser plotada!
SHO = 20.

# Instrumento de onda
waveinst = 'MIROS'

# _____________________________________________________________________________
#                       Importando funções necessárias
# _____________________________________________________________________________

from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame, Panel, ExcelWriter, concat, datetime
import matplotlib.patheffects as PathEffects
from sys import path
from warnings import filterwarnings
import xarray
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from calendar import monthrange
# Desativação de alertas minimizando mensagens no console
filterwarnings("ignore")

pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'math', 'settings', 'graph']
for d in dirs:
    pth2 = pth1 + d
    path.append(pth2)

import statistic as stc
import OCNdb as ocn

# _____________________________________________________________________________
#                      Definições de labels e limites
# _____________________________________________________________________________

# Labels dos meses do ano
mes = ("Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
       "Jul", "Ago", "Set", "Out", "Nov", "Dez")

year = int(DATEMAX[6:10])  # ANO ATUAL  *******
years = np.arange(int(DATEMIN[6:10]), int(DATEMAX[6:10]) + 1, 1)

# _____________________________________________________________________________
#                             Carregando dados
# _____________________________________________________________________________
print('{:_<66}'.format('Carregando BD'))
print('{:<40} | {:26}'.format('Parâmetro', 'Status'))

print('{:<40} | {:26}'.format('Vento', 'Carregando...'))
Wind = ocn.get_BDs(UCD_WIND, [DATEMIN, DATEMAX], 'meteo').xs('YOUNG', level=1)
print('{:<40} | {:26}'.format('.', 'Ok.'))

print('{:<40} | {:26}'.format('Onda', 'Carregando...'))
Wave = ocn.get_BDs(UCD_WAVE, [DATEMIN, DATEMAX], 'wave').xs(waveinst, level=1)
print('{:<40} | {:26}'.format('.', 'Ok.'))

data = concat([Wind.droplevel([0]).WSPD, Wave.droplevel([0]).VAVH], axis=1)
if UNID == 'nós':
    data.WSPD = data.WSPD * 1.94384449
data.index = data.index.rename("DT_DATA")

# _____________________________________________________________________________
#                     Montando tabelas com estatística
# _____________________________________________________________________________
for xx, lv in enumerate(HOP):
    print('{:<40} | {:26}'.format('Realizando análise para altura de',
                                  str(lv) + ' m'))

    WND_LIM10 = (np.asarray(WIND_LIM) /
                 (1 + 0.137 * np.log(np.asarray(lv) / 10.)))

    wind_ = stc.percentual(data.WSPD, WND_LIM10, '.1f', 'int', atype='mensal')
    wave_ = stc.percentual(data.VAVH, WAVE_LIM, '.1f', 'Hs', atype='mensal')

    wind_years = stc.percentual(
        data.WSPD, WND_LIM10, '.1f', 'int', atype='anual').drop(
            ['Total'], level=1)
    wave_years = stc.percentual(
        data.VAVH, WAVE_LIM, '.1f', 'Hs', atype='anual').drop(
            ['Total'], level=1)

    crossdata = {}
    similar_time = data.dropna(how='any')

    both_params = DataFrame()
    # separando somente os anos com quantidade significativa dos dois dados
    for y in set(similar_time.index.year):
        yslc = similar_time[similar_time.index.year == y]
        for m in set(yslc.index.month):
            lentotal = monthrange(y, m)[1] * 24
            mslc = yslc[yslc.index.month == m]
            if mslc.count().min() / lentotal > .8:
                both_params = both_params.append(mslc)
    both_params = both_params.sort_index()

    if xx == 0:
        print('{:_<66}'.format('Informações da análise cruzada do parâmetros'))
        print('{:<40} | {:26}'.format('Mês', 'Anos contemplados'))
    for x, m in enumerate(mes):
        mslc = both_params[both_params.index.month == x + 1]
        if xx == 0:
            print('{:<40} | {:26}'.format(m, str(list(set(mslc.index.year)))))

        crosstable = stc.percentual_cruzado(
            mslc,
            WND_LIM10,
            WAVE_LIM,
            '.1f')
        crossdata[m] = [
            crosstable[
                crosstable.columns[0]].values[0] / mslc.count().min() * 100,
            crosstable[
                crosstable.columns[1]].values[1] / mslc.count().min() * 100]
    crossdata = DataFrame(data=crossdata, index=['Aten', 'Aler']).T.round(1)

    aten_table = concat([
        wind_[wind_.columns[0]],
        wave_[wave_.columns[0]],
        crossdata[crossdata.columns[0]],
        (wind_[wind_.columns[0]] +
        wave_[wave_.columns[0]] -
        crossdata[crossdata.columns[0]])], axis=1
    ).round(1)
    aten_table.columns = [
        'Vento (%)',
        'Onda (%)',
        'Ocorrência simultânea (%)',
        '% Tempo sob condições de atenção']
    w = ExcelWriter("{}\\atencao_{}m.xlsx".format(PATH, lv))
    aten_table.to_excel(w)
    w.close()

    aler_table = concat([
        wind_[wind_.columns[1]],
        wave_[wave_.columns[1]],
        crossdata[crossdata.columns[1]],
        (wind_[wind_.columns[1]] +
         wave_[wave_.columns[1]] -
         crossdata[crossdata.columns[1]])], axis=1
    ).round(1)
    aler_table.columns = [
        'Vento (%)',
        'Onda (%)',
        'Ocorrência simultânea (%)',
        '% Tempo sob condições de alerta']

    w = ExcelWriter("{}\\alerta_{}.xlsx".format(PATH, lv))
    aler_table.to_excel(w)
    w.close()

    if lv == SHO:
        ATEN = aten_table.copy()
        ALER = aler_table.copy()
        ywind = wind_years.copy()
        ywave = wave_years.copy()

# _____________________________________________________________________________
#                               Plotando
# _____________________________________________________________________________

print('{:_<66}'.format('Plotando histogramas'))
print('{:<40} | {:26}'.format(
    'Condição', 'Status'))

coloraten = ['#0070C0', '#385723', '#7F7F7F', '#FFC000']
coloraler = ['#0070C0', '#385723', '#7F7F7F', '#C00000']

for condition, df in zip(['aten', 'aler'], [ATEN, ALER]):

    fig = plt.figure()
    ax = df.plot.bar(
        figsize=(12, 9),
        legend=False,
        color=eval('color{}'.format(condition)))
    plt.xticks(rotation=45, fontsize=14)
    plt.yticks(fontsize=14)

    ax.set_ylabel('Registros (%)', fontsize=14)
    if condition == 'aten':
        ax.set_ylim(0, 70)
    else:
        ax.set_ylim(0, 50)
    ax.legend(
        prop={'size': 14},
        bbox_to_anchor=(
            0.5,
            -0.13),
        ncol=len(df.columns),
        loc='center')
    plt.title('Vento à {} m'.format(SHO), loc='right', fontsize=14)
    plt.savefig(
        '{}\\{}_{}_pprog.png'.format(PATH, condition, SHO),
        format='png',
        bbox_inches='tight',
        dpi=600)
    print('{:<40} | {:26}'.format(
        condition, 'Ok'))

# Plotando anexos _______________________________________________________
fig, ax = plt.subplots(3, 4, figsize=(12, 9))
fig.tight_layout()
plt.subplots_adjust(hspace=.32)
mc = 0
for l in range(3):
    for c in range(4):
        wanexp = ywind.xs(mes[mc], level=1) 
        wanexp.plot.bar(
            ax=ax[l][c],
            legend=False,
            color=['#FFC000', '#C00000'],
            width=.7)
        ax[l][c].tick_params(axis='x', labelrotation=45, size=6)
        ax[l][c].set_ylim(
            [0,
             ywind.max().max() + round(
                 ywind.max().max() / 10, 0) + 4])
        ax[l][c].text(.95, .9, mes[mc],
            horizontalalignment='right',
            transform=ax[l][c].transAxes,
            weight='bold')
        ax[l][c].grid(True)
        for xt in ax[l][c].get_xticks():
            ax[l][c].text(
                xt - .55,
                wanexp[wanexp.index == wanexp.index[xt]].values[0][0] + 1,
                '{:.1f}%'.format(
                    wanexp[wanexp.index == wanexp.index[xt]].values[0][0]),
                fontsize=7)
            ax[l][c].text(xt + .07, wanexp[
                wanexp.index == wanexp.index[xt]].values[0][1] + 1,
                '{:.1f}%'.format(
                    wanexp[wanexp.index == wanexp.index[xt]].values[0][1]),
                fontsize=7)
        mc += 1
plt.savefig(
    '{}\\wind_anexo.png'.format(PATH),
    format='png',
    bbox_inches='tight',
    dpi=600)

fig, ax = plt.subplots(3, 4, figsize=(12, 9))
fig.tight_layout()
plt.subplots_adjust(hspace=.32)
mc = 0
for l in range(3):
    for c in range(4):
        wanexp = ywave.xs(mes[mc], level=1) 
        wanexp.plot.bar(
            ax=ax[l][c],
            legend=False,
            color=['#FFC000', '#C00000'],
            width=.7)
        ax[l][c].tick_params(axis='x', labelrotation=45, size=6)
        ax[l][c].set_ylim(
            [0,
             ywave.max().max() + round(
                 ywave.max().max() / 10, 0) + 4])
        ax[l][c].text(.95, .9, mes[mc],
            horizontalalignment='right',
            transform=ax[l][c].transAxes,
            weight='bold')
        ax[l][c].grid(True)
        for xt in ax[l][c].get_xticks():
            ax[l][c].text(
                xt - .55,
                wanexp[wanexp.index == wanexp.index[xt]].values[0][0] + 1,
                '{:.1f}%'.format(
                    wanexp[wanexp.index == wanexp.index[xt]].values[0][0]),
                fontsize=7)
            ax[l][c].text(xt + .07, wanexp[
                wanexp.index == wanexp.index[xt]].values[0][1] + 1,
                '{:.1f}%'.format(
                    wanexp[wanexp.index == wanexp.index[xt]].values[0][1]),
                fontsize=7)
        mc += 1
plt.savefig(
    '{}\\wave_anexo.png'.format(PATH),
    format='png',
    bbox_inches='tight',
    dpi=600)
