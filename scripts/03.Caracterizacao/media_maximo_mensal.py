# -*- coding: utf-8 -*-
'''
    Autor: Francisco Thiago Franca Parente
    Data de Criação: 08/05/2020

    Rotina que calcula média, desvio padrão e máximo de uma série temporal.
    Gera uma tabela excel e um gráfico.

'''
# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________

# Diretório onde serão salvos os resultados
diretorio = ('XXXXXXXXXXXXXXXXXXXXXX')

# Data inical e final da análise dos dados
datemin = u"01/01/2018 00:00:00"
datemax = u"31/12/2020 23:00:00"

# Bacia de exploração de interesse, caso não tenha, colocar None
# Deve estar entre chaves, ex.: ['Bacia de Campos', 'Bacia de Santos']
bacias = None

# Campo de previsão de interesse, caso não tenha, colocar None
# Deve estar entre chaves, ex: ['Profunda Central', 'Polo Sul']
campos = None

# UCD(s) de interesse, deve estar entre chaves. Ex: ['P-19']
ucdmeteo = None
ucdwave = None
ucdcurr = ['XXXXXXXXXXXXX']

# Qual parâmetro de interesse? (Opções: 'meteo', 'curr', 'wave')
param = ['curr']

# Unidade de medida para vento e corrente
unidadedemedida = 'nós'

# Instrumento de corrente de interesse, caso haja! Se não ouver um específico,
# deixar esta variável como None (Ex.: inst = None)
instrumeto = None

# Caso queira avaliar rajada usar 'True', caso contrário 'False'
gust = 'False'

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________

import matplotlib.pyplot as plt
from sys import path as syspath
from os import path, mkdir, listdir
from pandas import ExcelWriter, concat, DataFrame
from collections import namedtuple
import numpy as np
import pyocnp
import ocnpylib

normpath = path.normpath(diretorio)
pth1 = 'XXXXXX'
dirs = ['XXXXXXXX']
for d in dirs:
    pth2 = pth1 + d
    syspath.append(pth2)
import histograma as hist
import definitions as mopdef
from custom import plot_custom
import statistic as stc
import math
from rosa import new_rose
import OCNdb as ocn
plt.style.use('seaborn-whitegrid')
from warnings import filterwarnings
filterwarnings("ignore")
# _____________________________________________________________________________
#                       Definição dos labels e valores
# _____________________________________________________________________________

meses = [
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
# Definindo raio das rosas dos ventos
raio = {'meteo': 50, 'wave': 50, 'curr': 50}
# Definindo bins das rosas dos ventos
rosebins = {
    'meteo': np.arange(0, 21, 3),
    'wave': np.arange(0, 3.1, .5),
    'curr': np.arange(0, 1.4, .2)}
# Definindo formato do float de cada parametro
fmtprm = {'meteo': '.1f', 'wave': '.1f', 'curr': '.2f'}
# Definindo ordem de acesso aos dados de cada parametro para confecção
# do histograma
seqacc = {
    'meteo': ['WSPD', 'WDIR'], 'wave': ['VAVH', 'VPEDM'],
    'curr': ['HCSP', 'HCDT']}
# Definindo ylim dos hitogramas de cada parêmtro
hylm = {'meteo': 50, 'wave': 50, 'curr': 50}

# _____________________________________________________________________________
#  Lendo quais as UCDS serão avaliada para o caso de busca por campo ou bacia
# _____________________________________________________________________________
print('{}'.format(60 * '#'))
print('# {:^56} #'.format('Período de análise'))
print('# {:^56} #'.format(56 * '-'))

if bacias is not None:
    ucdmeteo, ucdwave = [], []
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
            filter(None,
            [ucd for ucd in inf.loc[campo].ONDA]))

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

print('# {:<56} #'.format('Data inicial (UTC): ' + datemin))
print('# {:<56} #'.format('Data final (UTC): ' + datemax))

# _____________________________________________________________________________
#                       Carrengado os dados de interesse
# _____________________________________________________________________________
print('{}'.format(60 * '#'))
print('# {:^56} #'.format('Carregando banco de dados de interesse'))
print('# {:^56} #'.format(56 * '-'))

datatup = namedtuple('database', 'parametro data')
alldata = []
# Laço para os parâmetros escolhidos pelo usuário
for prm in param:

    # Lendo os dados de todas as reigões de interesse
    data = DataFrame()
    if eval('ucd{}'.format(prm)) is not None:
        for x in range(len(eval('ucd{}'.format(prm)))):
            place = eval('ucd{}[x][0]'.format(prm))
            if campos is None and bacias is None:
                nameplace = ocnpylib.SECRET(
                    ocnpylib.SECRET([place]))[0]
                print('# {:^26}  | {:^26} #'.format(
                    nameplace,
                    'Carregando ' + prm))
            else:
                nameplace = place
                print('# {:^26}  | {:^26} #'.format(
                    place,
                    'Carregando ' + prm))
            ucds_ = eval('ucd{}[x][1]'.format(prm))
            nameucds = [ocnpylib.SECRET(
                ocnpylib.SECRET([x]))[0] for x in ucds_]

            _raw = ocn.get_BDs(nameucds, [datemin, datemax], prm)
            if _raw.shape[0] > 0:
                if prm == 'curr':
                    data = data.append(
                        concat(
                            [_raw.droplevel([0, 1, 2])],
                            keys=[nameplace],
                            names=['Place']))
                else:
                    data = data.append(
                        concat(
                            [_raw.droplevel([0, 1])],
                            keys=[nameplace],
                            names=['Place']))
        alldata.append(datatup(prm, data))

# _____________________________________________________________________________
#                       Criando pastas para cada mês
# _____________________________________________________________________________
for m in set(alldata[0].data.index.get_level_values(1).month):
    if meses[m-1] in listdir(diretorio):
        pass
    else:
        mkdir('{}\\{}'.format(diretorio, meses[m-1]))

# _____________________________________________________________________________
#                       Calculando e plotando resultados
# _____________________________________________________________________________
print('{}'.format(60 * '#'))
print('# {:^56} #'.format('Calculando estatística e plotando'))
print('# {:^56} #'.format(56 * '-'))

for looparam in alldata:
    prm = looparam.parametro
    dtf = looparam.data
    print('# {:<26}  | {:^26} #'.format(
        'Executando line plot',
        ''))
    if dtf.shape[0] is not 0:
        # _____________________________________________________________________
        #           Plota média, máxima e desvio padrão mensal
        # _____________________________________________________________________

        # Laço para as variáveis
        for clm in dtf.columns:
            excel_file = DataFrame()
            if clm in ['HCSP', 'WSPD', 'VAVH', 'RELH', 'ATMS', 'DRYT']:
                fig, ax = plt.subplots(
                    len(dtf.index.levels[0]), 1, figsize=(12, 9))
                # Check de unidade de medida fornecida pelo usuário
                if clm in ['WSPD', 'HCSP']:
                    if unidadedemedida == 'nós':
                        dtf[clm] = dtf[clm] * 1.94384449
                # Laço por região
                for sbplt, place in enumerate(dtf.index.levels[0]):
                    st = concat(
                        [
                            dtf.loc[place].groupby(
                                [dtf.loc[place].index.month]).mean()[clm],
                            dtf.loc[place].groupby(
                                [dtf.loc[place].index.month]).std()[clm],
                            dtf.loc[place].groupby(
                                [dtf.loc[place].index.month]).min()[clm],
                            dtf.loc[place].groupby(
                                [dtf.loc[place].index.month]).max()[clm]],
                        axis=1)
                    st.columns = ['media', 'desvio', 'minimo', 'maximo']
                    st.round(decimals=1)

                    try:
                        axx = ax[sbplt]
                    except Exception:
                        axx = ax

                    axx.fill_between(
                        st.index,
                        st.media.values - st.desvio.values,
                        st.media.values + st.desvio.values,
                        color='k',
                        alpha=.2)
                    axx.plot(
                        st.index,
                        st.media.values,
                        marker='o',
                        label='Média')
                    axx.plot(
                        st.index,
                        st.maximo.values,
                        marker='o',
                        label="Máximo")
                    ylimits = [
                        np.nanmin(st.media.values - st.desvio.values),
                        np.nanmax(st.maximo.values)]
                    if ylimits[0] < 5:
                        ylimits[0] = 0
                    else:
                        ylimits[0] = ylimits[0] - round(
                            math.log(ylimits[0], 10), 0)

                    axx.set_xlim([1, 12])
                    axx.set_xticks(st.index)
                    axx.set_ylim([
                        ylimits[0],
                        ylimits[1] + round(math.log(ylimits[1], 10), 0)])

                    if clm in ['DRYT', 'RELH', 'ATMS']:
                        axx.plot(
                            st.index,
                            st.minimo.values,
                            marker='o',
                            label="Mínimo")
                        try:
                            axx.set_ylim([
                                np.nanmin(st.minimo.values) - round(
                                    math.log(
                                        np.nanmin(st.minimo.values), 10), 0),
                                ylimits[1] + round(
                                    math.log(ylimits[1], 10), 0)])
                        except Exception:
                            axx.set_ylim([
                                np.nanmin(st.minimo.values),
                                ylimits[1] + round(math.log(ylimits[1], 10), 0)])
                    if clm in ['WSPD', 'HCSP']:
                        axx.set_ylabel(
                            '{} ({})'.format(
                                pyocnp.SECRET,
                                unidadedemedida),
                            fontsize=14)
                    else:
                        axx.set_ylabel(
                            '{} ({})'.format(
                                pyocnp.SECRET,
                                pyocnp.SECRET),
                            fontsize=14)

                    if len(dtf.index.levels[0]) < 3:
                        axx.set_xticklabels(meses, fontdict={'fontsize': 12})
                    else:
                        if sbplt == len(dtf.index.levels[0]) - 1:
                            axx.set_xticklabels(
                                meses,
                                fontdict={'fontsize': 12})
                        else:
                            axx.set_xticklabels([], fontdict={'fontsize': 12})

                    axx.set_title(place, loc='left', fontdict={'fontsize': 14})

                    st.index = meses
                    dst = concat([st], keys=[place], names=["Região"])
                    excel_file = excel_file.append(dst)
                    if prm is 'HCSP':
                        excel_file = excel_file.round(2)
                    else:
                        excel_file = excel_file.round(1)

                # adicionando legenda
                # fig.add_axes([left, bottom, width, hight]
                fig.add_axes(
                    [
                        axx.get_position().get_points()[0, 0] / 2 + .25,
                        axx.get_position().get_points()[0, 1],
                        .2,
                        .2],
                    frameon=False, axisbelow=True, xticks=[], yticks=[])
                axx.legend(
                    prop={'size': 14},
                    bbox_to_anchor=(
                        fig.axes[-1].get_position().get_points()[1, 0],
                        fig.axes[-1].get_position().get_points()[0, 1] -
                        (fig.get_size_inches()[0]/40)),
                    ncol=3,
                    loc='center')

                # Salvando a figura
                fig.savefig(
                        '{}\\{}_media_mensal.png'.format(
                            diretorio,
                            pyocnp.SECRET.replace(' ', '_')),
                        format='png',
                        bbox_inches='tight',
                        dpi=300)

                w = ExcelWriter("{}\\{}_media_mensal.xlsx".format(
                    diretorio,
                    pyocnp.SECRET(clm)[0].replace(' ', '_')))
                excel_file.to_excel(w)
                w.close()
        print('# {:<26}  | {:^26} #'.format(
            'Line plot',
            'OK'))
        # _____________________________________________________________________
        #                   Plotando rosas de distribuição
        # _____________________________________________________________________
        print('# {:<26}  | {:^26} #'.format(
            'Rosas e histogramas',
            ''))
        for place in dtf.index.levels[0]:
            dfplace = dtf.loc[place]
            # fig, ax = plt.subplots(4, 3, figsize=(15, 10))
            for group in dfplace.groupby([dfplace.index.month]):

                mdata = group[1]
                inte = mdata[mdata.columns[
                    mdata.columns.str.contains("WSPD|HCSP|VAVH")]].values
                inte = np.array([x[0] for x in inte])
                dire = mdata[mdata.columns[
                    mdata.columns.str.contains("WDIR|HCDT|VPEDM")]].values
                dire = np.array([x[0] for x in dire])
                fig = new_rose(
                    spd=inte,
                    dir=dire,
                    spd_bins=rosebins[prm],
                    rlim=raio[prm],
                    unid=unidadedemedida,
                    fmt=fmtprm[prm])
                plt.suptitle(meses[group[0] - 1], fontsize=30)

                # Salva imagem de rosa de distribuição
                fig.savefig(
                    '{}\\{}\\{}_rosa_{}.png'.format(
                        diretorio, meses[group[0] - 1], place, prm),
                    format='png',
                    bbox_inches='tight',
                    dpi=300)

                # Calculando percentuais em diferentes faixas

                table = stc.percentual_cruzado(
                    concat(
                        [mdata[seqacc[prm]]], keys=[place], names=['UCD']),
                    rosebins[prm],
                    'dir',
                    fmt=fmtprm[prm])
                w = ExcelWriter("{}\\{}\\{}_tabela_{}.xlsx".format(
                    diretorio, meses[group[0] - 1], place, prm))
                table.to_excel(w)
                w.close()

                if prm == 'wave':
                    table = stc.percentual_cruzado(
                        concat(
                            [mdata[['VAVH', 'VTPK1']]],
                            keys=[place], names=['UCD']),
                        rosebins[prm],
                        np.arange(4, 16, 2),
                        fmt=fmtprm[prm])
                    w = ExcelWriter("{}\\{}\\{}_tabela2_{}.xlsx".format(
                        diretorio, meses[group[0] - 1], place, prm))
                    table.to_excel(w)
                    w.close()

                if prm != 'wave':
                    lbl1 = 'Direção'
                    lbl2 = 'Intensidade média ({})'.format(unidadedemedida)
                else:
                    lbl1 = 'Período de pico primário (s)'
                    lbl2 = 'Altura significativa (m)'

                # Plotando Histogramas
                x = [
                    (lbl1, list(table.columns[:-2].values)),
                    (lbl2, list(table.index[:-4].values))]
                y = [
                    (0, table[table.index == 'Perc. (%)'].values[0][:-2]),
                    (1, table['Perc (%)'].values[:-4])]

                fig = hist.comum(
                    x,
                    y,
                    wd=.5,
                    textb=3,
                    leg=False,
                    txtsize=10,
                    ylim=hylm[prm],
                    disp=False)

                # Salva imagem do histograma
                fig.savefig(
                    '{}\\{}\\{}_histograma_{}.png'.format(
                        diretorio, meses[group[0] - 1], place, prm),
                    format='png',
                    bbox_inches='tight',
                    dpi=300)

    print('# {:^26}  | {:^26} #'.format(
        prm,
        'OK')) 
print('{}'.format(60 * '#'))
print('FIM.')
plt.close('all')
