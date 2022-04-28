# -*- coding: utf-8 -*-
'''
    Autor: Francisco Thiago Franca Parente
    Data de Criação: 13/05/2020

    Rotina que plota controuf o campo de corrente fornecido por uma série
    temporal de perfil de corrente.

'''

import numpy as np
# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________

# Diretório onde serão salvos os resultados
PATH = ('XXXXXXXXXXXXXX')

# Data inical e final da análise dos dados
datemin = "26/06/2020 03:00:00"
datemax = "29/06/2020 02:00:00"

# UCD(s) de interesse
UCDS = ['XXXXXXXXXXXX']

# Unidade de medida para vento e corrente
unidadedemedida = 'nós'

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sys import path as syspath
from os import path
from scipy import interpolate
from pandas import ExcelWriter, concat
from datetime import timedelta

normpath = path.normpath(PATH)
pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'graph', 'settings', 'math']
for d in dirs:
    pth2 = pth1 + d
    syspath.append(pth2)
from custom import caxes
import OCNdb as ocn
plt.style.use('seaborn-whitegrid')
# _____________________________________________________________________________
#                       Lendo dados de corrente
# _____________________________________________________________________________

corr = ocn.get_BD(
    UCDS,
    [datemin, datemax],
    'curr',
    layers=list(np.arange(0, 40, 1)),
    inst='ADCP')
if corr.shape[0] is 0:
    raise RuntimeError("Não há dados de ADCP.")


if unidadedemedida == 'nós':
    corr.HCSP = corr.HCSP * 1.94384449

# Escrevendo numa planilha excel
w = ExcelWriter("{}\\dados_perfil.xlsx".format(PATH))
exc = corr.copy().round(2)
exc.columns = ['Velocidade', 'Direção']
exc.to_excel(w)
w.close()

# Ajustando para uma distribuição espacial
# Laco por UCD
for x, u in enumerate(UCDS):
    data = corr.loc[u].xs('ADCP', level=0)
    # Laço por profundidade
    for n, p in enumerate(data.index.levels[0]):
        timesch = data.loc[p].T
        timesch1 = timesch[timesch.index == 'HCSP']
        timesch1.index = [p]
        timesch2 = timesch[timesch.index == 'HCDT']
        timesch2.index = [p]
        if n == 0:
            spd_field = timesch1.copy()
            dir_field = timesch2.copy()
        else:
            spd_field = concat([spd_field, timesch1])
            dir_field = concat([dir_field, timesch2])
    spd_field.index.name = 'profundidade'
    dir_field.index.name = 'profundidade'

    CORR = concat(
        [spd_field], keys=['velocidade'], names=['Param.'])
    CORR = CORR.append(
        concat([dir_field], keys=['direcao'], names=['Param.']))
    CORR = concat([CORR], keys=[u], names=['UCD'])
    if x == 0:
        cor_profile = CORR.copy()
    else:
        cor_profile = cor_profile.append(CORR)

# _____________________________________________________________________________
#                               Plotando
# _____________________________________________________________________________

c_map = [plt.cm.jet, plt.cm.hsv, plt.cm.ocean]
c_0 = c_map[0]
c_1 = c_map[1]

for u in UCDS:

    # pegando valores de profundiadade
    profundidades = cor_profile.loc[u].index.levels[1].values

    # gridando e colocando mudando de hora UTC para local
    xi, yi = np.meshgrid(
        cor_profile.loc[u].columns - timedelta(hours=3),
        cor_profile.loc[u].index.levels[1])

    # Interpolando com método linear
    interpolado = {}
    for p in ['velocidade', 'direcao']:
        vals = ~np.isnan(cor_profile.loc[u].loc[p].values)
        fint = interpolate.Rbf(
            xi[vals], yi[vals],
            cor_profile.loc[u].loc[p].values[vals],
            function='linear')
        interpolado[p] = fint(xi, yi)

    # Organizando as variáveis
    dataplot = (
        ('bruto', {
            'velocidade': cor_profile.loc[u].loc['velocidade'].values,
            'direcao': cor_profile.loc[u].loc['direcao'].values
        }),
        ('interpolado', interpolado))

    # Plotando
    for f in range(len(dataplot)):

        fig = plt.figure(f, facecolor=(1.0, 1.0, 1.0), figsize=(10, 8))
        # Diagramação e exibição da figura.
        fig.subplots_adjust(bottom=0.1, right=0.985, top=0.95)
        axSP = fig.add_subplot(211)
        axDT = fig.add_subplot(212, sharex=axSP)

        maxint = np.nanmax(dataplot[f][1]['velocidade'])
        levels_cs = np.arange(
            0,
            np.nanmax(maxint) + 0.1, 0.01)
        levels_cd = np.arange(0, 360.1, 5)

        # Plota intensidade
        cs = axSP.contourf(
            xi, yi,
            dataplot[f][1]['velocidade'],
            levels=levels_cs, cmap=c_0,
            cbar_kwargs={"label": '[m/s]', 'pad': 0.0125})

        # Plota direção
        cd = axDT.contourf(
            xi, yi,
            dataplot[f][1]['direcao'],
            levels=levels_cd, cmap=c_1,
            cbar_kwargs={"label": 'Graus', 'pad': 0.0125})

        axSP.set_ylim([0, profundidades[-1]])
        axDT.set_ylim([0, profundidades[-1]])
        axSP.invert_yaxis()
        axDT.invert_yaxis()
        axSP.set_ylabel("Profundidade (m)")
        axDT.set_ylabel("Profundidade (m)")
        axSP.tick_params(axis='y', labelsize=10)
        axDT.tick_params(axis='y', labelsize=10)

        ticks = [
            '{:.0f}'.format(i)
            for i in axDT.get_yticks()]
        ticks[0] = 'Superfície'
        axSP.set_yticklabels(ticks)
        axDT.set_yticklabels(ticks)

        caxes.fmt_time_axis(axSP)
        caxes.fmt_time_axis(axDT)

        plt.colorbar(
            cs, ax=axSP,
            extend='both',
            label="Intensidade ({})".format(unidadedemedida),
            ticks=np.arange(0, maxint + .2, .1))
        dbar = plt.colorbar(
            cd, ax=axDT,
            extend='both',
            label="Direção (°)",
            ticks=np.arange(0, 361, 45))

        fig.canvas.draw()
        fig.savefig(
            "{}\\Corrente_{}_{}.png".format(PATH, dataplot[f][0], u),
            format='png',
            bbox_inches='tight',
            dpi=600)
