# -*- coding: utf-8 -*-
'''
    Autor: Francisco Thiago Franca Parente
    Data de Criação: 27/04/2020

    Rotina que calcula o percentual de dados dentro de N intervalos
    de interesse do usuário, acima ou abaixo. A rotina salva uma imagem
    de histograma, caso N>1, e exporta uma tabela em excel com o percentual
    de dados.

'''
import numpy as np
# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________

# Diretório onde serão salvos os resultados
upath = ('XXXXXXXXXXX')

# Data inical e final da análise dos dados
datemin = u"01/01/2019 00:00:00"
datemax = u"31/12/2019 23:00:00"

# Bacia de exploração de interesse, caso não tenha, colocar None
# Deve estar entre chaves, ex.: ['Bacia de Campos', 'Bacia de Santos']
bacias = None
# Campo de previsão de interesse, caso não tenha, colocar None
# Deve estar entre chaves, ex: ['Profunda Central', 'Polo Sul']
campos = None

# UCD(s) de interesse
ucdmeteo = None
ucdwave = None
ucdcurr = ['XXXXXXXXXXXX']

# Para o caso da onda, aqui você escolhe se o parâmetro a ser avaliado será
# altura significativa ('hs') ou período de pico primário ('tp') 
waveopt = 'tp'

# Limites considerados (*Atenção! Devem ser listas. Ex.: [1, 2, 3])
limites_wind = [15]
limites_wave = [8.5]
limites_curr = [.0, 1.]

# Aqui o usuário define se quer o percentual de dados maior que ou menor que
# o limite operacional escolhido ( 0 para maior que e 1 para menor que)
sinal = 0

# Unidade de medida para vento e corrente
unid = 'nós'

# Instrumentos para cada parâmetro! Se não ouver um específico,
# deixar esta variável como None (Ex.: inst = None)
meteoinst = None
waveinst = None
currinst = None

# Caso queiram avaliar rajada, utilize True, caso contrário False
gust = False

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________

import matplotlib.pyplot as plt
from sys import path as syspath
from os import path
from pandas import ExcelWriter, concat, DataFrame
from collections import namedtuple
import matplotlib.patheffects as PathEffects

normpath = path.normpath(upath)
pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'graph', 'settings', 'math']
for d in dirs:
    pth2 = pth1 + d
    syspath.append(pth2)
import histograma as hist
import definitions as mopdef
from custom import plot_custom
import statistic as st
import OCNdb as ocn
from calendar import monthrange
plot_custom.temp_serie_config()

# _____________________________________________________________________________
#  Lendo quais as UCDS serão avaliada para o caso de busca por campo ou bacia
# _____________________________________________________________________________

if bacias is not None:
    ucdmeteo, ucdwave = [], []
    inf = mopdef.get_ucds_representativas()
    for bacia in bacias:
        uwd = list(filter(
            None,
            [item for ucd in inf.loc[bacia].VENTO.values
             for item in ucd]))
        uwv = list(
            filter(
                None,
                [item for ucd in inf.loc[bacia].ONDA.values for item in ucd])
        )
        ucdmeteo.append((bacia, uwd))
        ucdwave.append((bacia, uwv))
        ucdcurr = None

if campos is not None:
    ucdmeteo, ucdwave = [], []
    inf = mopdef.get_ucds_representativas().droplevel(0)
    for campo in campos:
        uwd = list(filter(
            None,
            [ucd for ucd in inf.loc[campo].VENTO]))
        uwv = list(
            filter(
                None,
                [ucd for ucd in inf.loc[campo].ONDA])
        )
        ucdmeteo.append((campo, uwd))
        ucdwave.append((campo, uwv))
        ucdcurr = None

if campos is None and bacias is None:
    if ucdmeteo is not None:
        ucdmeteo = [(ucd, [ucd]) for ucd in ucdmeteo]
    if ucdwave is not None:
        ucdwave = [(ucd, [ucd]) for ucd in ucdwave]
    if ucdcurr is not None:
        ucdcurr = [(ucd, [ucd]) for ucd in ucdcurr]

# _____________________________________________________________________________
#           Definindo variavel de acesso aos parametros de interesse
# _____________________________________________________________________________

sets = namedtuple('Settings', 'column limites frmt label')
if waveopt == 'hs':
    acrwave = 'VAVH'
elif waveopt == 'tp':
    acrwave = 'VTPK1'

param = {
    'meteo': sets('WSPD', limites_wind, '.1f', 'int'),
    'wave': sets(acrwave, limites_wave, '.1f', 'Hs'),
    'curr': sets('HCSP', limites_curr, '.2f', 'int')}

# _____________________________________________________________________________
#                       Carrengado os dados de interesse
# _____________________________________________________________________________

ocndata = DataFrame()
# laço para parâmetros de interesse
for prm in param.keys():
    data = DataFrame()
    if eval("ucd{}".format(prm)) is not None:
        # Laço para região de interesse
        for n in range(len(eval("ucd{}".format(prm)))):
            place = eval("ucd{}".format(prm))[n][0]
            ucds_ = eval("ucd{}".format(prm))[n][1]
            print('[Carregando {} | {}...]'.format(place, prm))
            # Carrega os dados
            _raw = ocn.get_BDs(
                ucds_,
                [datemin, datemax],
                prm,
                eval("{}inst".format(prm))).round(
                    int(param[prm].frmt.split('.')[1].split('f')[0]))
            if _raw.shape[0] > 1:
                if param[prm].column in ['WSPD', 'HCSP']:
                    if unid == 'nós':
                        _data = _raw.droplevel([0, 1])[
                            param[prm].column] * 1.94384449
                else:
                    _data = _raw.droplevel([0, 1])[param[prm].column]
                data = data.append(
                    concat([_data.to_frame()], keys=[place], names=['Região']))
        ocndata = ocndata.append(
            concat([data], keys=[prm], names=['Parâmetro']))

# _____________________________________________________________________________
#                  Calculando o percentual para cada região
# _____________________________________________________________________________

place_perc = DataFrame()
percent = []
# Laço por parâmetro
for prm in ocndata.index.levels[0]:
    _prmdata = ocndata.loc[prm]
    # Laço por região
    for place in np.unique(_prmdata.index.get_level_values(level=0)):
        exam = _prmdata.loc[place][param[prm].column].to_frame()
        if prm == 'curr':
            exam = exam.droplevel(0)
        exam.index = exam.index.rename('DT_DATA')
        perc = st.percentual(
            exam,
            param[prm].limites,
            param[prm].frmt,
            param[prm].label,
            atype='mensal',
            signal=sinal)
        place_perc = place_perc.append(
            concat([perc], keys=[place], names=['Região']))
    percent.append((prm, place_perc))

# _____________________________________________________________________________
#                      Exportando Excel
# _____________________________________________________________________________
w = ExcelWriter("{}\\tabela.xlsx".format(upath))
place_perc.to_excel(w)
w.close()

# _____________________________________________________________________________
#                               Plotando
# _____________________________________________________________________________

for prm in range(len(ocndata.index.levels[0])):

    dataplot = percent[prm][1]
    ylim = dataplot.max().max()

    fig, ax = plt.subplots(len(dataplot.index.levels[0]), 1, figsize=(12, 9))

    for x, place in enumerate(dataplot.index.levels[0]):

        plot = dataplot.loc[place]
        xtik = list(range(len(plot.index)))

        if len(plot.columns) > 1:
            dx = - 1 / (len(plot.columns) + 1) * xtik[1] - xtik[0]
        else:
            dx = 0
        sm = dx
        for categoria in plot.columns:
            if len(dataplot.index.levels[0]) > 1:
                axx = ax[x]
            else:
                axx = ax
            bars = axx.bar(
                [x + dx for x in xtik],
                plot[categoria].values,
                width=1 / (len(plot.columns) + 1),
                align='center',
                alpha=.7,
                edgecolor='k',
                label=categoria)

            # Escrevendo valores nas barras
            texto1 = [
                '{:.1f}%'.format(round(x, 1))
                for x in plot[categoria].values]
            for tx in range(len(xtik)):
                if plot[categoria].values[tx] > 0:
                    txt = axx.text(
                        [x + dx for x in xtik][tx],
                        plot[categoria].values[tx] + .5,
                        texto1[tx],
                        horizontalalignment='center',
                        fontsize=8)
                    plt.setp(
                        txt,
                        path_effects=[
                            PathEffects.withStroke(
                                linewidth=2,
                                foreground="w")])
            dx += abs(sm)

        plt.sca(axx)
        plt.xticks(xtik, plot.index, fontsize=14)
        axx.set_ylabel('Registros (%)', fontsize=14)
        if ylim < 40:
            axx.set_ylim(0, 50)
        else:
            axx.set_ylim(0, 100)
        if len(dataplot.index.levels[0]) > 1:
            axx.set_title(place, loc='left')
        if x == len(dataplot.index.levels[0]) - 1:
            if len(dataplot.columns) > 1:
                fig.add_axes([
                    axx.get_position().get_points()[0, 0] / 2 + .25,
                    axx.get_position().get_points()[0, 1] -
                    axx.get_position().get_points()[0, 1],
                    .2,
                    .2], frameon=False, axisbelow=True, xticks=[], yticks=[])

                dy = (1 / axx.get_ylim()[1]) * 25
                axx.legend(
                    prop={'size': 14},
                    bbox_to_anchor=(
                        fig.axes[-1].get_position().get_points()[1, 0],
                        fig.axes[-1].get_position().get_points()[0, 1] - dy),
                    ncol=len(plot.columns),
                    loc='center')
    fig.savefig(
        '{}\\{}_histograma.png'.format(upath, percent[prm][0]),
        format='png',
        bbox_inches='tight',
        dpi=600)
