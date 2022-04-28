# -*- coding: utf-8 -*-
'''
    Autor: Francisco Thiago Franca Parente
    Data de Criação: 21/06/2020

    Rotina que calcula o percentual de dados dentro de N intervalos
    de interesse do usuário, acima ou abaixo, para dois parâmetros.
    No final, tem-se o resultado do percentual desses parâmetros
    isolados e ocorrendo simultaneamente nos N intervalos.

'''
import numpy as np
# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________

# Diretório onde serão salvos os resultados
PATH = ('XXXXXXXX')

# Data inical e final da análise dos dados
datemin = u"01/01/2018 00:00:00"
datemax = u"31/12/2018 23:00:00"

# UCD de interesse
ucdmeteo = ['XXXXXXX']
ucdwave = ['XXXXXXX']
ucdcurr = None

# # Bacia de exploração de interesse, caso não tenha, colocar None
# # Deve estar entre chaves, ex.: ['Bacia de Campos', 'Bacia de Santos']
# bacias = None

# # Campo de previsão de interesse, caso não tenha, colocar None
# # Deve estar entre chaves, ex: ['Profunda Central', 'Polo Sul']
# campos = ['Profunda Central', 'Lula']

# Limites considerados (*Atenção! Devem ser listas. Ex.: [1, 2, 3])
limites_meteo = [10, 15, 20]
limites_wave = [1., 2., 3.]
limites_curr = [.8]

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
from pandas import ExcelWriter, concat, DataFrame, date_range, datetime
from collections import namedtuple
import matplotlib.patheffects as PathEffects

normpath = path.normpath(PATH)
pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'graph', 'settings', 'math']
for d in dirs:
    pth2 = pth1 + d
    syspath.append(pth2)
import histograma as hist
import definitions as mopdef
from custom import plot_custom
import statistic as stc
import OCNdb as ocn
plot_custom.temp_serie_config()

# _____________________________________________________________________________
#  Lendo quais as UCDS serão avaliada para o caso de busca por campo ou bacia
# _____________________________________________________________________________

# if bacias is not None:
#     ucdmeteo, ucdwave = [], []
#     inf = mopdef.get_ucds_representativas()
#     for bacia in bacias:
#         uwd = list(filter(
#             None,
#             [item for ucd in inf.loc[bacia].VENTO.values
#              for item in ucd]))
#         uwv = list(
#             filter(
#                 None,
#                 [item for ucd in inf.loc[bacia].ONDA.values for item in ucd])
#         )
#         ucdmeteo.append((bacia, uwd))
#         ucdwave.append((bacia, uwv))
#         ucdcurr = None

# if campos is not None:
#     ucdmeteo, ucdwave = [], []
#     inf = mopdef.get_ucds_representativas().droplevel(0)
#     for campo in campos:
#         uwd = list(filter(
#             None,
#             [ucd for ucd in inf.loc[campo].VENTO]))
#         uwv = list(
#             filter(
#                 None,
#                 [ucd for ucd in inf.loc[campo].ONDA])
#         )
#         ucdmeteo.append((campo, uwd))
#         ucdwave.append((campo, uwv))
#         ucdcurr = None

# if campos is None and bacias is None:
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
param = {
    'meteo': sets('WSPD', limites_meteo, '.1f', 'int'),
    'wave': sets('VAVH', limites_wave, '.1f', 'Hs'),
    'curr': sets('HCSP', limites_curr, '.2f', 'int')}

mes = ("Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
       "Jul", "Ago", "Set", "Out", "Nov", "Dez")

timesize = len(date_range(
    datetime.strptime(datemin, '%d/%m/%Y %H:%M:%S'),
    datetime.strptime(datemax, '%d/%m/%Y %H:%M:%S'),
    freq='H'))

# _____________________________________________________________________________
#                       Carrengado os dados de interesse
# _____________________________________________________________________________

ocndata = []
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
        ocndata.append((prm, data))

# _____________________________________________________________________________
#                  Calculando o percentual para cada região
# _____________________________________________________________________________

# if campos is None and bacias is None:
data = concat(
    [ocndata[0][1].droplevel([0]), ocndata[1][1].droplevel([0])],
    axis=1
)
data = concat([data], keys=['ucd'], names=['Regiao'])

# if campos is not None or bacias is not None:
#     for local in ocndata[0][1].index.levels[0]:
#         if local in ocndata[1][1].index.levels[0]:
#             data = concat(
#                 [ocndata[0][1].loc[place], ocndata[1][1].loc[place]],
#                 axis=1)
#             data = concat([data], keys=[place], names=['Regiao'])

#         else:
#             print('[{} não possui ambos parâmetros.]'.format(place))


for place in data.index.levels[0]:
    df = data.loc[place].copy()
    crossdata = {}
    similar_time = df.dropna(how='any')

    compare = stc.percentual_cruzado(
        similar_time,
        eval('limites_{}'.format(ocndata[0][0])),
        eval('limites_{}'.format(ocndata[1][0])),
        '.1f')
    w = ExcelWriter('{}\\{}.xlsx'.format(PATH, 'compara_cruzada'))
    compare.to_excel(w)
    w.close()
    time_percent = (similar_time.shape[0] / timesize) * 100

    print("{:_<50}".format(''))
    print("{:^50}".format(place))
    print("{:_<50}".format(''))
    print("{:<30} | {:<20}".format('Aquisição conjunta', 'Percentual'))
    print("{:<6} x {:<21} | {:<20}".format(
        ocndata[0][0], ocndata[1][0], round(time_percent, 1)))

    print("{:_<50}".format(''))
    print("{:^50}".format('Fazendo análise mensal'))
    print("{:_<50}".format(''))

    mensal = DataFrame()
    for x, m in enumerate(mes):
        mslc = similar_time[similar_time.index.month == x + 1]
        crosstable = stc.percentual_cruzado(
            mslc,
            eval('limites_{}'.format(ocndata[0][0])),
            eval('limites_{}'.format(ocndata[1][0])),
            '.1f')
        mensal = mensal.append(concat(
            [crosstable], keys=[m], names=['Mês']))
    wm = ExcelWriter('{}\\{}_mensal.xlsx'.format(PATH, 'compara_cruzada'))
    mensal.to_excel(wm)
    wm.close()
    print("{:^50}".format('[Feito]'))
