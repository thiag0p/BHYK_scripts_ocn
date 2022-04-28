'''
    Autor: Francisco Thiago Franca Parente
    Data de Criação: 03/01/2022

    Rotina que calcula o percentual de dados horários acima de um limite de
    vento e onda para cada mês.

    Output: Dataframe com o percentual mensal (linhas) para todos os horários
    (colunas) acima do(s) limite(s) de interesse (abas do excel).

'''

# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________

# Diretório onde serão salvos os resultados
PATH = ('XXXXXXXXXXXXXXXXXX')

# Data inical e final da análise dos dados
datemin = u"01/01/2020 00:00:00"
datemax = u"30/04/2020 23:00:00"

# UCD de interesse
ucdmeteo = ['XXXXXXX']
ucdwave = ['XXXXXXXXXXX']

# Limites considerados (*Atenção! Devem ser listas. Ex.: [1, 2, 3])
limites_meteo = [10, 15, 20]
limites_wave = [1., 2., 3.]

# Unidade de medida para vento e corrente
unid = 'nós'

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________

import matplotlib.pyplot as plt
from seaborn import heatmap
from sys import path as syspath
from os import path
from pandas import ExcelWriter, DataFrame, to_datetime, datetime, concat
from collections import namedtuple
import matplotlib.patheffects as PathEffects
import locale
import calendar
locale.setlocale(locale.LC_TIME, '')

pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data']
for d in dirs:
    pth2 = pth1 + d
    syspath.append(pth2)
import OCNdb as ocn

# _____________________________________________________________________________
#                       Carregando dados
# _____________________________________________________________________________
if ucdmeteo:
    wind = ocn.get_BDs(ucdmeteo, [datemin, datemax], 'meteo')
    if unid.lower() == 'nós':
        wind.WSPD = wind.WSPD * 1.94384449
if ucdwave:
    wave = ocn.get_BDs(ucdwave, [datemin, datemax], 'wave')

# _____________________________________________________________________________
#                   Calculando os percentuais de vento
# _____________________________________________________________________________
if ucdmeteo:
    wind_ = wind.reset_index().set_index('DT_DATA')

    excel_wind = ExcelWriter(f'{PATH}\\vento_percentual_horario.xlsx')
    month = wind_.groupby([wind_.index.month]).WSPD
    wind_analysis = DataFrame()
    for lim in limites_meteo:
        df = DataFrame()
        for bloco, data in month:
            hour = data.groupby([data.index.hour])
            hlist = {}
            for bloco2, data2 in hour:
                hlist[bloco2] = (
                    data2[data2 >= lim].count() / data2.count()) * 100
            df = df.append(
                DataFrame(hlist, index=[calendar.month_abbr[bloco]]))
        wind_analysis = wind_analysis.append(concat(
            [df], keys=[f'\u2265 {lim} {unid.lower()}'], names=['Limites']))
        df.round(1).to_excel(
            excel_wind, sheet_name=f'\u2265 {lim} {unid.lower()}')
    excel_wind.close()

# _____________________________________________________________________________
#                   Calculando os percentuais de onda
# _____________________________________________________________________________
if ucdwave:
    wave_ = wave.reset_index().set_index('DT_DATA')

    excel_wave = ExcelWriter(f'{PATH}\\onda_percentual_horario.xlsx')
    month = wave_.groupby([wave_.index.month]).VAVH
    wave_analysis = DataFrame()
    for lim in limites_wave:
        df = DataFrame()
        for bloco, data in month:
            hour = data.groupby([data.index.hour])
            hlist = {}
            for bloco2, data2 in hour:
                hlist[bloco2] = (
                    data2[data2 >= lim].count() / data2.count()) * 100
            df = df.append(
                DataFrame(hlist, index=[calendar.month_abbr[bloco]]))
        wave_analysis = wave_analysis.append(concat(
            [df], keys=[f'\u2265 {lim} m'], names=['Limites']))
        df.round(1).to_excel(
            excel_wave, sheet_name=f'\u2265 {lim} m')
    excel_wave.close()

# _____________________________________________________________________________
#                   Plotando heatmap
# _____________________________________________________________________________

if ucdmeteo:
    for lim in set(wind_analysis.index.get_level_values(0)):
        plot = wind_analysis.loc[lim]

        fig, ax = plt.subplots(figsize=(15, 10))
        axx = heatmap(
            plot, cmap='RdYlGn_r', annot=True, ax=ax,
            cbar=True, linewidths=.5,
            annot_kws={"size": 11, "color": 'black', "fontfamily": 'arial'},
            cbar_kws={'label': 'Percentual (%)'},
            fmt='.1f', vmax=100, vmin=0)
        axx.figure.axes[-1].yaxis.label.set_size(16)
        # configurando ticks e labels
        ax.tick_params(
            axis='x', labelsize=16, pad=12, length=0,
            labeltop=False, labelbottom=True)

        ax.tick_params(
            axis='y', labelsize=16, pad=12,
            length=0, labelleft=True, labelrotation=0)

        bottom, top = ax.get_ylim()

        ax.set_ylim(bottom + 0.5, top - 0.5)
        ax.set_xlabel('horas', fontsize=16)
        # formatando as ticklabels
        plt.xticks(weight='bold', family='arial')
        plt.yticks(weight='bold', family='arial')

        ax.set_title(
            f'Percentual de dados de intensidade média\ndo vento {lim}',
            fontsize=16)
        fig.savefig(f'{PATH}\\vento_{lim}.png', format='png')

    plt.close('all')


if ucdwave:
    for lim in set(wave_analysis.index.get_level_values(0)):
        plot = wave_analysis.loc[lim]

        fig, ax = plt.subplots(figsize=(15, 10))
        axx = heatmap(
            plot, cmap='RdYlGn_r', annot=True, ax=ax,
            cbar=True, linewidths=.5,
            annot_kws={"size": 11, "color": 'black', "fontfamily": 'arial'},
            cbar_kws={'label': 'Percentual (%)'},
            fmt='.1f', vmax=100, vmin=0)
        axx.figure.axes[-1].yaxis.label.set_size(16)
        # configurando ticks e labels
        ax.tick_params(
            axis='x', labelsize=16, pad=12, length=0,
            labeltop=False, labelbottom=True)

        ax.tick_params(
            axis='y', labelsize=16, pad=12,
            length=0, labelleft=True, labelrotation=0)

        bottom, top = ax.get_ylim()

        ax.set_ylim(bottom + 0.5, top - 0.5)
        ax.set_xlabel('horas', fontsize=16)
        # formatando as ticklabels
        plt.xticks(weight='bold', family='arial')
        plt.yticks(weight='bold', family='arial')

        ax.set_title(
            f'Percentual de dados de altura significativa\nde onda {lim}',
            fontsize=16)
        fig.savefig(f'{PATH}\\onda_{lim}.png', format='png')

    plt.close('all')
