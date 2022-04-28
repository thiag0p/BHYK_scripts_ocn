'''

    Rotina que lê dados de vento da UCD de interesse e
    o número de dias com vento abaixo ou igual a um ou mais valores de
    intensidade por pelo menos X horas de duração.
    Calcula também a média, o mínimo e o máximo de janelas contabilizadas

    Autora: Patrícia Baldasso (BWQ7)
    Criação: 25/03/2021

    Edição  ___________________________________________________________________
            |   + 31/03/2021 (bhyk)
            |       Inclusão da criação da planilha excel e plot

'''

# _____________________________________________________________________________
#                               Modificar aqui
# _____________________________________________________________________________
# Diretório onde serão salvos os outputs
PATH = "XXXXXXXXXXXXXXXXXX"

# Intervalo de data para busca no banco de dados
DATEMIN = u"01/01/2014 03:00:00"
DATEMAX = u"01/01/2021 02:00:00"

# UCD de interesse, deve estar entre chaves. Ex: ['P-19']
UCD = ['XXXXXXXXXXXXXXXXX']

# Duração da janela em horas
janela = 4

# Definindo os limites de vento
wind_lim = [3., 10.]

# Unidade de medida para vento SEM ACENTO
unit = 'nos'

# _____________________________________________________________________________
import numpy as np
from warnings import filterwarnings
# Desativação de alertas minimizando mensagens no console
filterwarnings("ignore")
import time
import matplotlib.pyplot as plt
from pandas import ExcelWriter, concat, DataFrame, date_range
from datetime import timedelta
import calendar
import locale
locale.setlocale(locale.LC_TIME, '')

from sys import path
pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'math', 'settings', 'graph']
for d in dirs:
    pth2 = pth1 + d
    path.append(pth2)
import OCNdb as ocn

#_____________________________________________________________________________
#           Carrengado os dados de interesse
# _____________________________________________________________________________

print('{}'.format(60 * '#'))
print('## {:<54} ##'.format('Carregando dados de vento'))
docn = ocn.get_BDs(UCD, [DATEMIN, DATEMAX], 'meteo')
data = docn[['WSPD']].droplevel([0, 1]).dropna()
# Conferindo unidade de medida
if unit.lower() == 'nos':
    data.WSPD = data.WSPD * 1.94384449
print('## {:<54} ##'.format('OK.'))

# Colocando em hora local
data.index = data.index - timedelta(hours=3)

wex = ExcelWriter('{}\\NumJanelas_{}.xlsx'.format(PATH, UCD[0]))
for lim in wind_lim:
    print('## {} ##'.format(54 * '-'))
    print('## {:<54} ##'.format('Vento menor que {} {}'.format(lim, unit )))
    print('## {:<54} ##'.format('Busca de instantes de interesse'))
    
    # Encontrando os valores menores que cada limite
    slc = data[data['WSPD'] <= lim]

    # Intervalo de tempo entre os registros
    diftime = slc.index[1:] - slc.index[:-1]
    slc['DeltaT'] = np.append(diftime.to_list(), None)

    print('## {:<54} ##'.format('Agrupamento de janelas de interesse'))
    # Agrupando janelas de interesse
    windows = slc[slc['DeltaT'] == timedelta(hours=1)].groupby(
        (slc['DeltaT'] != timedelta(hours=1)).cumsum())
    pack = DataFrame()
    for k, v in windows:
        if v.shape[0] >= janela:
            pack = pack.append(v.WSPD.to_frame())

    print('## {:<54} ##'.format('Conta número de dias'))
    # Contando o número de dias em cada mês de cada ano.
    ympack = pack.groupby([pack.index.year, pack.index.month])
    colect = {}
    for x in set(pack.index.year):
        colect[x] = []
    for idx, unpack in ympack:
        colect[idx[0]].append(
            (idx[1], len(set(unpack.index.day))))

    exportdata = DataFrame()
    for key in colect.keys():
        exportdata = exportdata.append(
            DataFrame(dict(colect[key]), index=[key]))

    # Ordenando indices
    exportdata = exportdata.sort_index()
    # Escrevendo os meses
    exportdata.columns = [calendar.month_abbr[x] for x in exportdata.columns]
    # Calculando média, moda, mínimo, máx e total
    exportdata['Total'] = exportdata.T.sum()
    nidx = [x for x in exportdata.index]
    nidx.extend(['Média', 'Mínimo', 'Máximo'])
    exportdata = exportdata.append(
        exportdata.mean().to_frame().T, ignore_index=True)
    exportdata = exportdata.append(
        exportdata.min().to_frame().T, ignore_index=True)
    exportdata = exportdata.append(
        exportdata.max().to_frame().T, ignore_index=True)
    exportdata = exportdata.set_index([nidx])
    exportdata = exportdata.round(1)
    print('## {:<54} ##'.format('Exporta arquivo excel'))
    exportdata.to_excel(
        wex, sheet_name='Menor e igual que {} {}'.format(lim, unit))

    print('## {:<54} ##'.format('Plot gráfico de barras'))

    # Plotando os valores estatísticos
    fig, ax = plt.subplots(figsize=(15, 10))
    exportdata.T[['Mínimo', 'Máximo', 'Média']][:-1].plot.bar(
        ax=ax,
        linewidth=2,
        fontsize=18)
    ax.set_ylabel(
        '{} {} {}'.format(
            'Número de dias de Vento abaixo de',
            lim, unit.replace('o', 'ó'), janela),
        fontsize=16)
    ax.legend(fontsize=16)
    plt.xticks(rotation=0)

    fig.savefig(
        '{}\\NumJanelas_{}_MenorQue_{}{}.png'.format(
            PATH, UCD[0], lim, unit),
        format='png',
        bbox_inches='tight',
        dpi=600)
wex.close()

print('## {:<54} ##'.format('Finalizado.'))
print('{}'.format(60 * '#'))
