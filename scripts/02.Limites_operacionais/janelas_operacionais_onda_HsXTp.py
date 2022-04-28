# -*- coding: utf-8 -*-
'''
    Autor: Francisco Thiago Franca Parente
    Data de Criação: 02/07/2020

    Rotina que calcula o número de janelas operacionais mensais para dados de
    onda de uma UCD específica. Nesta rotina, são considerados limites
    operacionais de Tp e Hs. São calculadas as janelas para cada parâmetro de
    forma separada e depois de forma cruzada.

    Output: Planilha em excel com o número de janelas operacionais.

'''
from os import path
import numpy as np
# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________

# Diretório onde serão salvos os resultados
diretorio = path.normpath('XXXXXXXXXXXXXXX')

# Data inical e final da análise dos dados
datemin = u"01/01/2010 00:00:00"
datemax = u"30/07/2020 23:00:00"

# UCD de interesse, deve estar entre chaves. Ex: ['P-19']
ucds = ['XXXXXXXXXXXXXXXXXXXXX']

# Limites operacionais de Hs (m) e Período de pico primário (s)
lim_hs = tuple(np.arange(1, 3.6, .5))
lim_tp = tuple(np.arange(6, 14, 1))

# Duração da janela em horas
janela = np.arange(1, 13, 1)

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________

from warnings import filterwarnings
filterwarnings("ignore")
import matplotlib.pyplot as plt
from sys import path as syspath
from pandas import ExcelWriter, concat, DataFrame, date_range
from datetime import timedelta, datetime
from collections import namedtuple
from itertools import islice

pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'graph', 'settings', 'math']
for d in dirs:
    pth2 = pth1 + d
    syspath.append(pth2)
import OCNdb as ocn
import statistic as st
plt.style.use('seaborn-whitegrid')

# _____________________________________________________________________________
#            Definição dos labels dos meses
# _____________________________________________________________________________

meses = [
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# _____________________________________________________________________________
#           Carrengado os dados de interesse
# _____________________________________________________________________________

print('[Carregando dados de onda...]')
data = ocn.get_BDs(ucds, [datemin, datemax], 'wave')

head = namedtuple('conditions', 'period hs')
condition = head(lim_tp, lim_hs)

# _____________________________________________________________________________
#       Calculando o número de janelas de diferentes durações para período
# _____________________________________________________________________________
for ucd in np.unique(data.index.get_level_values(level=0)):
    sldata = data.drop(['VPED1', 'VPEDM'], axis=1).loc[ucd].droplevel([0])
    notnul = sldata.dropna()

    print('Avaliando a unidade {}'.format(ucd))
    print('[Calculando janelas de período de onda]')

    per_windows = DataFrame()
    for m in range(meses.__len__()):

        mdata = sldata[sldata.index.month == m + 1]
        per_windows = per_windows.append(concat(
            [st.janelas_operacionais(
                df=mdata.VTPK1.to_frame(),
                limites=list(condition.period),
                janelas=janela,
                op='igual')],
            keys=[meses[m]],
            names=['Mês']))

    # ________________________________________________________________________
    #       Calculando o número de janelas de diferentes durações para Hs
    # ________________________________________________________________________
    print('[Calculando janelas de Hs de onda]')

    hs_windows = DataFrame()
    for m in range(meses.__len__()):

        mdata = sldata[sldata.index.month == m + 1]
        print(mdata)
        hs_windows = hs_windows.append(concat(
            [st.janelas_operacionais(
                df=mdata.VAVH.to_frame(),
                limites=list(condition.hs),
                janelas=janela,
                op='menor')],
            keys=[meses[m]],
            names=['Mês']))

    # _________________________________________________________________________
    #     Calculando o número de janelas de diferentes durações para Hs X Per
    # _________________________________________________________________________

    print('[Calculando janelas de Hs X Período de onda]')

    cross_windows = DataFrame()
    for m in range(meses.__len__()):

        mdata = notnul[notnul.index.month == m + 1]

        wd = DataFrame()
        for i in range(lim_hs.__len__()):

            check = mdata[(mdata.VAVH < condition.hs[i])]

            pw = DataFrame()
            for j in range(lim_tp.__len__()):
                check2 = check[
                    (check.VTPK1 > condition.period[j] - .6) &
                    (check.VTPK1 < condition.period[j] + .5)]

                n_windows = st.janela_tempo(
                    time=check2.index,
                    janelas=janela)

                df = DataFrame(
                    n_windows,
                    columns=[condition.period[j]],
                    index=['< 1 h'] + ["{} h".format(x) for x in janela])
                pw = concat([pw, df], axis=1)

            wd = wd.append(
                concat([pw],
                       keys=['< {}m'.format(condition.hs[i])],
                       names=['Hs']))
        cross_windows = cross_windows.append(
            concat([wd], keys=[meses[m]], names=['Mês']))

    # _____________________________________________________________________________
    #                       Escrevendo Tabela Excel
    # _____________________________________________________________________________
    print('[Escrevendo tabela excel]')

    writer = ExcelWriter("{}\\janelas_operacionais_{}.xlsx".format(
        diretorio, ucd))

    per_windows.to_excel(writer, sheet_name='Período')
    hs_windows.to_excel(writer, sheet_name='Hs')
    cross_windows.to_excel(writer, sheet_name='Hs Vs Período')

    writer.close()

    print('[Done]')

    # _____________________________________________________________________________
    #                       Anotações sobre a série de dados
    # _____________________________________________________________________________

    log = open("{}\\log_data_{}.txt".format(diretorio, ucd), 'w')
    log.write("Dados coletados em {}\n".format(ucd))
    log.write("Período solicitado: {} até {}\n\n".format(datemin, datemax))
    log.write("Número total de dados esperado para a busca: {}\n".format(
        len(date_range(
            datetime.strptime(datemin, '%d/%m/%Y %H:%M:%S'),
            datetime.strptime(datemax, '%d/%m/%Y %H:%M:%S'),
            freq='H'))
    ))
    log.write("Período avaliado: {} até {}\n\n".format(
        sldata.index[0], sldata.index[-1]))
    log.write("Número total de dados esperado do avaliado: {}\n".format(
        len(date_range(sldata.index[0], sldata.index[-1], freq='H'))
    ))
    log.write("Número total de dados encontrados: {}\n".format(
        sldata.shape[0]
    ))
    log.write("Número total de dados de período: {}\n".format(
        sldata.VTPK1.dropna().shape[0]
    ))
    log.write("Número total de dados de Hs: {}\n".format(
        sldata.VAVH.dropna().shape[0]
    ))
    log.write("Número total de dados com ambos parâmetros: {}\n".format(
        notnul.shape[0]
    ))
    log.close()

    # # _______________________________________________________________________
    # #                               Plotando
    # # _______________________________________________________________________

    # fig, ax = plt.subplots(4, 3,figsize=(15, 10))
    # cl, line = 0, 0 
    # for x, c in enumerate(
    #   hs_windows.loc[hs_windows.index.levels[0][0]].index[1:]):
    #     axs = hs_windows.xs(c, level=1).plot(
    #         kind='bar',
    #         ax=ax[line][cl],
    #         legend=False,
    #         ylim=[0, 50],
    #         sharex=True,
    #         fontsize=14,
    #         rot=45)
    #     plt.subplots_adjust(hspace=.2)
    #     if cl == 2:
    #         cl = 0
    #         line += 1
    #     else:
    #         cl += 1
    #     axs.set_xlabel('')
    #     axs.set_title('Janela de {}'.format(c), fontsize=14)
    # axs.legend(
    #     prop={'size': 14},
    #     bbox_to_anchor=(-0.6, -0.5),
    #     ncol=6,
    #     loc='center')

