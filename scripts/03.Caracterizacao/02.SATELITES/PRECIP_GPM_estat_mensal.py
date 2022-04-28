#!/usr/bin/env python
'''

    Rotina de Leitura de dados de precipitação para relatório de suporte à
    PPROG. Nesta rotina, é considerado o banco Final_Run do GPM.

    ** BANCO DE DADOS
    title:          GPM - Global Precipitation Measurement
    institution:    NASA - National Aeronautics and Space Administration
    source:         Remote Sensing
    history:        2020-01-10T20:14:21Z: nasa_gpm_fix.py
    references:     https://www.nasa.gov/mission_pages/GPM/main/index.html
    conventions:    CF-1.7Global Precipitation Measurement

    Autor: Francisco Thiago Franca Parente (BHYK)
    Data de criação: 09/03/2020
    Versão: 1.0

    Edições:
        + 29/06/2020
            Ajustado dias secos. Rotina buscava NaN, onde na verdade os dias 
            secos são descritos como 0. 
            Inserido Loop para fazer para diferentes UCDs.
            Adicionada a escrita do percentual nas barras para valores acima
            de 5%.

'''
from sys import path
import xarray
from os.path import join, normpath
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame, Panel, ExcelWriter, date_range
from os import chdir as ch
import ocnpylib as ocn
import matplotlib.patheffects as PathEffects

# ==================== Campode de edição do usurário =======================

DATEMIN = u'01/01/2012 00:00:00'
DATEMAX = u'31/12/2018 00:00:00'

PATH = normpath(
    'XXXXXXXXXXXXXXX')

# UCD de interesse
UCDS = ['XXXXXXXXXXXXX']

# ======================= OPENDAP DO GPM =================================

opendap_link = ('http://XXXXXXXXXXXXXXXX')

# ========================================================================
# Criando arquivo de escrita excel

for ucd in UCDS:
    writer = ExcelWriter("{}\\{}_PorcMensalAcumChuva.xlsx".format(PATH, ucd))
    # Pegando posição da UCD
    lon, lat = ocn.SECRET(ocn.SECRET(ucd))
    # Criando variável de tempo para busca nos dados do opendap
    dti = datetime.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S')
    dtf = datetime.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S')
    # Definindo strings referentes aos meses do ano
    mes = ('Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez')
    # Definindo ranges de precimitação em mm
    PREC_LIM = ['Dias secos', 0, 2, 5, 10, 20, 50, 100]
    # Lendo dados do Opendap
    prec = xarray.open_dataset(opendap_link).sel(latitude=lat,
                                                 longitude=lon,
                                                 method='nearest')
    prec.load()
    data = prec.to_dataframe().reset_index().set_index('time')
    # Selecionando o período selecionado pelo usuário
    if dti in data.index and dtf in data.index:
        PRECIP = data[dti:dtf]
    else:
        raise RuntimeError('Não há dados no período solicitado!' +
                           'O período disponível vai de ' +
                           data.index[0].strftime('%d/%m/%Y') +
                           ' até ' + data.index[-1].strftime('%d/%m/%Y'))
    PRECIP = PRECIP.drop(['latitude', 'longitude'], axis=1)

    # Criando DataFrame com o percentual de dias secos e acumulados diários
    # de acordo com os range definido na linha 74
    HIST_PREC = DataFrame()
    for m in np.unique(PRECIP.index.month):

        slc = PRECIP.iloc[(PRECIP.index.month == m)]
        # slc = slc.reindex(time_reindex[time_reindex.month==m], fill_value=np.nan)

        perc = {}
        if not slc.empty:
            length = float(slc.count().sum())
            for xx, lim in enumerate(PREC_LIM):
                if xx == 0:
                    cases = slc.where(slc == 0).count().sum()
                    ind = lim
                elif xx == len(PREC_LIM) - 1:
                    cases = slc.where(slc > lim).count().sum()
                    ind = '> ' + str(lim) + ' mm'
                else:
                    cases = slc.where(
                        (slc > lim) & (slc <= PREC_LIM[xx + 1])).count().sum()
                    ind = str(lim) + ' - ' + str(PREC_LIM[xx + 1]) + 'mm'
                perc[ind] = np.round(100. * np.divide(cases, length), 1)
            HIST_PREC[mes[m - 1]] = perc.values()
        else:
            HIST_PREC[mes[m - 1]] = []
    HIST_PREC.index = perc.keys()

    # ====================== PLOTANDO ====================================

    barwidth = 1.
    PRECcolors = plt.cm.YlGnBu(np.linspace(0, 1, HIST_PREC.index.size))

    fig, ax = plt.subplots()

    PRECy_offset = np.zeros(HIST_PREC.columns.size)

    for i, lbl in enumerate(HIST_PREC.index):
        plota = HIST_PREC[HIST_PREC.index == lbl].values.flatten()
        rects = ax.bar(
            range(HIST_PREC.columns.size),
            plota, barwidth,
            bottom=PRECy_offset, color=PRECcolors[i],
            align='center', alpha=.5, label=lbl, edgecolor='#5d6d7e')

        texto = ['{:2.1f}%'.format(x) for x in plota]
        for xt, txt in enumerate(texto):
            if int(txt.split('.')[0]) > 5:
                txt = ax.text(
                    xt,
                    PRECy_offset[xt] + (int(txt.split('.')[0]) / 2),
                    txt,
                    horizontalalignment='center', fontsize=7)
                plt.setp(txt, path_effects=[
                    PathEffects.withStroke(linewidth=2, foreground="w")])
        PRECy_offset = PRECy_offset + plota

    plt.xticks(range(HIST_PREC.columns.size), mes, fontsize=12)

    ax.set_ylim(0, 100)
    ax.set_ylabel('Registros (%)', fontsize=12)
    ax.set_title(ucd, fontsize=12)
    ax.set_xlim([-0.5, 11.5])

    ax.legend(
        prop={'size': 8}, frameon=False, ncol=4,
        columnspacing=2, bbox_to_anchor=[0.5, -0.16],
        loc='center')

    fig.savefig(
        '{}\\{}_precPorcClasses.png'.format(PATH, ucd),
        bbox_inches='tight')

    HIST_PREC.T.to_excel(writer)
    writer.close()
    print('[Done]')
