# -*- coding: utf-8 -*-
'''
    Autor: Francisco Thiago Franca Parente
    Data de Criação: 05/06/2020

    Plota histograma de percentual de dados em diferentes intervalos de
    temperatura

'''

import numpy as np
# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________

# Diretório onde serão salvos os resultados
diretorio = ('C:\\Users\\bhyk\\Desktop\\teste')

# Data inical e final da análise dos dados
datainicial = u"01/01/2011 00:00:00"
datafinal = u"31/05/2020 23:00:00"

# Intervalos de temperatura
range_temp = [0, 13, 15, 20, 25, 30]

# Bacia de exploração de interesse, caso não tenha, colocar None
# Deve estar entre chaves, ex.: ['Bacia de Campos', 'Bacia de Santos']
bacias = None

# Campo de previsão de interesse, caso não tenha, colocar None
# Deve estar entre chaves, ex: ['Profunda Central', 'Polo Sul']
campos = None

# UCD(s) de interesse, deve estar entre chaves. Ex: ['P-19']
ucdtemp = ['XXXXXXXXXXXXXXX']

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________

import matplotlib.pyplot as plt
from sys import path as syspath
from os import path
from pandas import ExcelWriter, concat

normpath = path.normpath(diretorio)
pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'graph', 'settings', 'math']
for d in dirs:
    pth2 = pth1 + d
    syspath.append(pth2)
import histograma as hist
import definitions as mopdef
from custom import plot_custom
import functions
import statistic as st
import math
plt.style.use('seaborn-whitegrid')
fucmop = functions.func()

# _____________________________________________________________________________
#  Lendo quais as UCDS serão avaliada para o caso de busca por campo ou bacia
# _____________________________________________________________________________

if bacias is not None:
    ucdwind, ucdwave = [], []
    inf = mopdef.get_ucds_representativas()
    for bacia in bacias:
        uwd = list(filter(
            None,
            [item for ucd in inf.loc[bacia].VENTO.values
             for item in ucd]))
        uwv = list(
            filter(None,
            [item for ucd in inf.loc[bacia].ONDA.values
             for item in ucd]))
        
        ucdwind.append((bacia, uwd))
        ucdwave.append((bacia, uwv))
        ucdcurr = None

if campos is not None:
    ucdwind, ucdwave = [], []
    inf = mopdef.get_ucds_representativas().droplevel(0)
    for campo in campos:
        uwd = list(filter(
            None,
            [ucd for ucd in inf.loc[campo].VENTO]))
        uwv = list(
            filter(None,
            [ucd for ucd in inf.loc[campo].ONDA]))
        
        ucdwind.append((campo, uwd))
        ucdwave.append((campo, uwv))
        ucdcurr = None

# _____________________________________________________________________________
#           Definindo variavel de acesso aos parametros de interesse
# _____________________________________________________________________________

param = {
    'sclr': (
        [ucdtemp, datainicial, datafinal],
        'mete_DDDD',
        '.1f',
        'temp'
    )}

# _____________________________________________________________________________
#           Carrengado os dados de interesse
# _____________________________________________________________________________

for p in param.keys():
    if param[p][0][0] is not None:
        if bacias is not None:
            dic = param[p][0][0]
            for n, x in enumerate(range(len(dic))):
                print('[Carregando {} - {}...]'.format(p, dic[x][0])) 
                argumentos = param[p][0].copy()
                argumentos[0] = dic[x][1]

                # Carrega o banco de dados
                ucds = fucmop[p](*argumentos)
                load = concat([ucds], keys=[dic[x][0]], names=['Bacia']) 
                if n == 0:
                    data = load.copy()
                else:
                    data = data.append(load)
        if campos is not None:
            dic = param[p][0][0].copy()
            for n, x in enumerate(range(len(dic))):
                print('[Carregando {} - {}...]'.format(p, dic[x][0])) 
                argumentos = param[p][0].copy()
                argumentos[0] = dic[x][1]

                # Carrega o banco de dados
                ucds = fucmop[p](*argumentos)
                load = concat([ucds], keys=[dic[x][0]], names=['Campo']) 
                if n == 0:
                    data = load.copy()
                else:
                    data = data.append(load)      
        if bacias is None and campos is None:
            print('[Carregando {}...]'.format(p))            
            # Carrega o bando de dados
            data = fucmop[p](*param[p][0])

        serie = data[param[p][1]]

        perc = st.percentual(
            serie,
            range_temp,
            param[p][2],
            param[p][3],
            atype='interim',
            signal=0).drop('operacionalidade', axis=1)

        x = [('Temperatura (°C)', perc.columns)]
        y = [('Percentual', perc.values[0])]
        fig = hist.comum(
            x, y,
            borda_texto=3, leg=False, txtsize=14)

        fig.savefig(
            '{}\\histograma.png'.format(diretorio),
            format='png',
            bbox_inches='tight',
            dpi=300)

        w = ExcelWriter('{}\\temperatura.xlsx'.format(diretorio))
        perc.to_excel(w)
        w.close()
