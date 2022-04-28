# -*- coding: utf-8 -*-

'''
    Gera tabelas e imagens para relatório do IBAMA.

    Autor: Francisco Thiago F Parente
    Criação: 09/04/2020

    Edição:
    + 15/05/2020
        Modificada a legenda da rosa de distribuição.
        Modificada a forma de carregar os dados.
        Modificado os labels das figuras para conterem a mesma informação.

    + 31/07/2020
        Modificada a rosa de distribuição.
        Agora, são criados dois histogramas! Um com o percentual considerando
        todos os dados (alldata) e outro com o percentual somente dos instantes
        em que tanto direção e intensidade tem dados. Isto foi feito devido
        aos casos em que há um grande número de registros reprovados para um
        destes parâmetros.

    + 20/07/2021
        Mudanças de sintaxe do código
    + 21/07/2021
        Correção de bug no caso dos dados de onda de FSI3D que não possuem
        direção e na conversão para nós
'''
import os
import numpy as np
# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________
# diretório onde serão salvos os outputs (ATENÇÃO: as contrabarras devem ser
# duplicadas! Ex.: '"C:\\Users\\chave\\...')
diretorio = os.path.normpath("XXXXXXXXXXXXXXX")
# ucd de vento (Caso não queira vento, colocar None. Ex.: ucdwind = None)
ucdwind = ['XXXXXXXXXXXXXXXXX']
# ucd de onda (Caso não queira onda, colocar None. Ex.: ucdwave = None)
ucdwave = ['XXXXXXXXXXXXXXXXX']
# ucd de corrente (Caso não queira corrente, colocar None. Ex.: ucdcurr = None)
ucdcurr = ['XXXXXXXXXXXXXXXXX']
# data inicial UTC
datemin = "01/01/2019 00:00:00"
# data final UTC
datemax = "01/07/2019 23:00:00"
# instrumento de corrente (deve ser string)
curinst = 'ADCP'
# unidade de medida de corrente e vento
unid = "m/s"
# Flag dos dados (Opções: 'portal' e 'fora')
flag = 'portal'

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________

from sys import path
from pandas import DataFrame, ExcelWriter, Series, read_csv, concat, date_range
import os
from datetime import datetime as dt
import traceback as tbk
from warnings import filterwarnings
import matplotlib.pyplot as plt
pth1 = 'XXXXXXXXXXXXXXXXX'
dirs = ['data', 'graph', 'settings', 'math']
for d in dirs:
    pth2 = pth1 + d
    path.append(pth2)
import histograma as hist
import statistic as st
from rosa import new_rose
import OCNdb as ocn
import pyocnp
filterwarnings("ignore")
plt.ioff()
# _____________________________________________________________________________
#      Definindo classes de vento, onda e corrente e seus atributos
# _____________________________________________________________________________


class vento:
    name = 'vento'
    getdata = [ucdwind, [datemin, datemax], 'meteo']    # input para acesso
    acronym1 = 'WSPD'   # acronimo de intensidade do vento
    acronym2 = 'WDIR'   # acronimo de direção do vento
    nfmt = '.1f'        # formato das casas decimais
    bins = np.arange(0, 21, 3)      # bins de intensidade do vento
    rlim = 50           # limite do raio da rosa de distribuição
    ylim = 60           # limite do eixo y dos histogramas
    und = unid          # unidade de medida


class onda:
    name = 'onda'
    getdata = [ucdwave, [datemin, datemax], 'wave']      # input para acesso
    acronym1 = 'VAVH'   # acronimo de altura significativa
    acronym2 = 'VPEDM'  # acronimo de direção média
    acronym3 = 'VTPK1'  # acronimo de período de pico primário
    nfmt = '.1f'        # formato das casas decimais
    bins = np.arange(0, 3.1, .5)    # bins de Hs
    bins2 = np.arange(4, 16, 2)     # bins de período
    rlim = 50           # limite do raio da rosa de distribuição
    ylim = 60           # limite do eixo y dos histogramas
    und = 'm'           # unidade de medida


class corrente:
    name = 'corrente'
    getdata = [ucdcurr, [datemin, datemax], 'curr', curinst]    # input access
    acronym1 = 'HCSP'   # acronimo de intensidade
    acronym2 = 'HCDT'   # acronimo de direção
    nfmt = '.2f'        # formato das casas decimais
    bins = np.arange(0, 1.4, .2)    # bins de intensidade
    rlim = 50           # limite do raio da rosa de distribuição
    ylim = 70           # limite do eixo y dos histogramas
    und = unid          # unidade de medida


# _____________________________________________________________________________
#                           Carrega os dados
# _____________________________________________________________________________

print('{}'.format(60 * '#'))
print('# {:^56} #'.format('ACESSO AO BD'))
print('# {} #'.format(56 * '-'))
data = DataFrame()
for param in (vento(), onda(), corrente()):
    # checando se foi solicitado ucds do parametro
    if param.getdata[0] is not None:
        print('# {:<56} #'.format('+ Carregando {}'.format(param.name)))
        # Carrega o bando de dados
        d = ocn.get_BDs(*param.getdata, flag=flag).round(
            int(param.nfmt.split('.')[1].split('f')[0]))
        if d.shape[0] > 1:
            if isinstance(param, corrente):
                d = d.droplevel(2)
            data = data.append(concat([d],
                                      keys=[param.name],
                                      names=['Parametro']))
print('# {} #'.format(56 * '-'))
# _____________________________________________________________________________
#                       Plota e salva os dados
# _____________________________________________________________________________
print('# {:^56} #'.format('PLOTANDO'))
print('# {} #'.format(56 * '-'))

# Laço para cada parâmetro
for n in data.index.levels[0]:
    print('#     {:<52} #'.format(f'° {n}'))
    # pegando informações da classe do parâmetro
    setups = eval(n + '()')

    # Se caso houver dados de MIROS, retira dados negativos
    if n == 'corrente':
        if 'MIROS' in np.unique(data.loc[n].index.get_level_values(1)):
            inte = data.loc[n].xs('MIROS', level=1)[setups.acronym1]
            inte[inte < 0] = np.nan
            data.loc[(n, inte.index.levels[0][0], 'MIROS')][
                setups.acronym1] = inte.droplevel([0])

    # Condição para caso o instrumento for FSI3D e não tenha direção no BD
    inst = list(set(data.loc[n].index.get_level_values(1)))[0]
    if n == 'onda' and inst == 'FSI3D':
        pass
    else:
        data_dropna = data.loc[n][[setups.acronym1, setups.acronym2]].dropna()
        data_all = data.loc[n][[setups.acronym1, setups.acronym2]]

        if setups.und == 'nós':
            print('#         {:<48} #'.format('+ conversão para nós'))
            data_dropna[setups.acronym1] = data_dropna[
                setups.acronym1] * 1.9438445
            data_all[setups.acronym1] = data_all[setups.acronym1] * 1.9438445

        inte = data_dropna[setups.acronym1].values
        dire = data_dropna[setups.acronym2].values

        # Fazendo rosa de distribuição
        fig = new_rose(spd=inte,
                       dir=dire,
                       spd_bins=setups.bins,
                       rlim=setups.rlim,
                       unid=setups.und,
                       fmt=setups.nfmt)
        # Salva imagem de rosa de distribuição
        fig.savefig('{}\\{}_rosa.png'.format(diretorio, n),
                    format='png',
                    bbox_inches='tight',
                    dpi=300)
        print('#         {:<48} #'.format('> rosa ok'))

        # Calculando percentual nos intervalos de int, direção e periodo
        table1 = st.percentual_cruzado(data_all,
                                       setups.bins,
                                       'dir',
                                       fmt=setups.nfmt)
        w = ExcelWriter("{}\\{}_tabela_alldata.xlsx".format(diretorio, n))
        table1.to_excel(w)
        w.close()
        print('#         {:<48} #'.format('> tabela alldata ok'))

        table2 = st.percentual_cruzado(data_dropna,
                                       setups.bins,
                                       'dir',
                                       fmt=setups.nfmt)
        w = ExcelWriter("{}\\{}_tabela_dropna.xlsx".format(diretorio, n))
        table2.to_excel(w)
        w.close()
        print('#         {:<48} #'.format('> tabela dropna ok'))

    if n == 'onda':
        table1 = st.percentual_cruzado(
            data.loc[n][[setups.acronym1, setups.acronym3]],
            setups.bins,
            setups.bins2,
            fmt=setups.nfmt)
        w = ExcelWriter("{}\\{}_tabela2_alldata.xlsx".format(diretorio, n))
        table1.to_excel(w)
        w.close()
        print('#         {:<48} #'.format('> tabela alldata 2 ok'))

        table2 = st.percentual_cruzado(
            data.loc[n][[setups.acronym1, setups.acronym3]].dropna(),
            setups.bins,
            setups.bins2,
            fmt=setups.nfmt)
        w = ExcelWriter("{}\\{}_tabela2_dropna.xlsx".format(diretorio, n))
        table2.to_excel(w)
        w.close()
        print('#         {:<48} #'.format('> tabela dropna 2 ok'))

    if n != 'onda':
        lbl1 = 'Direção'
        lbl2 = 'Intensidade média ({})'.format(setups.und)
    else:
        lbl1 = 'Período de pico primário (s)'
        lbl2 = 'Altura significativa (m)'

    # Plotando Histogramas
    x = [(lbl1, list(table1.columns[:-2].values)),
         (lbl2, list(table1.index[:-4].values))]
    y1 = [(0, table1[table1.index == 'Perc. (%)'].values[0][:-2]),
          (1, table1['Perc (%)'].values[:-4])]
    y2 = [(0, table2[table2.index == 'Perc. (%)'].values[0][:-2]),
          (1, table2['Perc (%)'].values[:-4])]

    fig = hist.comum(x,
                     y1,
                     wd=.5,
                     textb=3,
                     leg=False,
                     txtsize=10,
                     ylim=setups.ylim,
                     disp=False)

    # Salva imagem do histograma
    fig.savefig('{}\\{}_histograma_alldata.png'.format(diretorio, n),
                format='png',
                bbox_inches='tight',
                dpi=300)
    print('#         {:<48} #'.format('> histograma alldata ok'))

    fig = hist.comum(x, y2,
                     wd=.5,
                     textb=3,
                     leg=False,
                     txtsize=10,
                     ylim=setups.ylim,
                     disp=False)

    # Salva imagem do histograma
    fig.savefig('{}\\{}_histograma_dropna.png'.format(diretorio, n),
                format='png',
                bbox_inches='tight',
                dpi=300)
    print('#         {:<48} #'.format('> histograma dropna ok'))

# _____________________________________________________________________________
#                       Salva tabela escalares
# _____________________________________________________________________________
if 'vento' in data.index.levels[0]:
    df = data.loc['vento'][['DRYT', 'RELH', 'ATMS']]
    sclr_stc = DataFrame()
    sclr_stc = sclr_stc.append([df.min(), df.mean(), df.max()]).T
    sclr_stc.columns = ['Mínimo', 'Média', 'Máximo']
    # Colocando descrição dos acronimos
    new_index = ['{} ({})'.format(
        pyocnp.SECRET(acrn)[0],
        pyocnp.SECRET(acrn)[1]) for acrn in sclr_stc.index]
    sclr_stc.index = new_index
    sw = ExcelWriter('{}\\Escalares.xlsx'.format(diretorio))
    sclr_stc.round(1).to_excel(sw)
    sw.close()
    print('#     {:<52} #'.format('° Escalares ok'))
print('# {} #'.format(56 * '-'))
print('# {:^56} #'.format('FINALIZADO'))
print('{}'.format(60 * '#'))
