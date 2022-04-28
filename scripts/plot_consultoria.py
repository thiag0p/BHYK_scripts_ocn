# -*- coding: utf-8 -*-
'''
    Rotina salva arquivo excel e gráfico de série temporal
    Atenção! O arquivo excel é salva em HORA UTC e as figuras são salvas em
    HORA LOCAL.

    * Edições__________________________________________________________________
        + 28/10/2020
            Adicionadas as cores padrões e a opção de plotar rajada e vento
            médio juntos. 
        + 09/11/2020
            Consideradas as cores definidas pela MOP, segundo issue do
            ocnpyvistu disposta no pylab.
        + 21/06/2021
            Inserido filtro para retirar dados espúrios no caso dos dados em
            DESV muito utilizados para consultoria do IBAMA em PMLZ, para o
            caso de corrente de MIROS.

'''
# _____________________________________________________________________________
#                               Modificar aqui
# _____________________________________________________________________________

# Definindo UCD(s) de interesse
# Ao escolher as UCDs, sempre colocar dentro de colchetes, com nomes entre
# aspas simples e separadas por vírgula
# Ex.:
# ucdmeteo = ['P-19']    # Este é o caso para somente uma UCD
# ucdwave = ['P-19', 'P-20']   # Este é o caso para mais de uma UCD
# Caso não haja interesse em nenhuma UCD para um paramétro especifico, coloque
# None, exatamente como escrito. Letra N maiúscula e as demais minúsculas.
# Ex.: 
# ucdmeteo = None
ucdmeteo = ['XXXXXXXXXX']
ucdwave = ['XXXXXXXXXXXXXXXX']
ucdcurr = None

# Definindo as datas iniciais e finais de busca de dados (HORA UTC)
DATEMIN = u"01/01/2021 03:00:00"
DATEMAX = u"10/01/2021 02:00:00"

# Unidade de medida
UNID = 'nós'

# Variável de escolha do usuário para os dados de Anemômetro.
# Caso queira somente vento médio   |   gust = False 
# Caso queira somente rajada        |   gust = True
# Caso queira os dois               |   gust = None
gust = False
# caminho onde devem ser salvos os dados
PATH = ("XXXXXXXXXXXXXX")

# Corrente
#   None - para quando for mais de um equipamento
#   'equipamento' - para um equipamento específico ('FSI2D',
#   'FSI3D', 'ADCP', 'MIROS', 'AWAC', 'AQUADOPP', 'HADCP')
#   Caso não tenha um específico, colocar None (Ex.: curr_inst = None)
curr_inst = None

# Opção para exportar tabela em excel (True ou False)
tabela_excel = True
# Opção para exportar arquivo .txt por unidade e instrumento (True ou False)
txt_file = None

# Opção para manipulação do tempo (contínuo - True / ou não - False)
regtime = False

# Opção para plot de dados aprovados ('portal') ou todos ('fora')
flag = 'portal'
# _____________________________________________________________________________

from datetime import timedelta
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from pandas import ExcelWriter, concat, date_range, DataFrame
from sys import path

pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'graph']
for d in dirs:
    pth2 = pth1 + d
    path.append(pth2)
from custom import caxes, plot_custom
import OCNdb as ocn
plot_custom.temp_serie_config()
from pyocnp import acronym2ext as acron

# _____________________________________________________________________________
#                           Alguns ajustes
# _____________________________________________________________________________

# Definindo delta para ajusta de UTC para hora local
deltat = timedelta(hours=3)
# criando datetime do tempo final e incial para ajusta do eixo
dti = dt.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S') + deltat
dtf = dt.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S') + deltat
meteo_inst = None
wave_inst = None
# Descrição dos acronimos das variaveis de rajada
gustacron = {
    'WSPD3S': 'Intensidade rajada 3s ({})'.format(UNID),
    'WDIR3S': 'Direção rajada 3s (°)',
    'WSPD10S': 'Intensidade rajada 10s ({})'.format(UNID),
    'WDIR10S': 'Direção rajada 10s (°)'
}
regular_time = date_range(
    dt.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S'),
    dt.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S'), freq='H')
# _____________________________________________________________________________
#                           Carregando os dados
# _____________________________________________________________________________

data_dict = {}
for prm in ['meteo', 'wave', 'curr']:
    if eval('ucd{}'.format(prm)) is not None:
        print('{:80}'.format(80 * '#'))
        print('{}{:^76}{}'.format(2 * '#', 'Lendo dados de ' + prm, 2 * '#'))
        if prm is 'meteo':
            if gust is not None:
                data = ocn.get_BDs(
                    ucds=eval('ucd{}'.format(prm)),
                    dates=[
                        DATEMIN,
                        DATEMAX],
                    param=prm,
                    inst=eval('{}_inst'.format(prm)),
                    gust=gust,
                    flag=flag)
            else:
                for atrb in [False, True]:
                    ld = ocn.get_BDs(
                        ucds=eval('ucd{}'.format(prm)),
                        dates=[
                            DATEMIN,
                            DATEMAX],
                        param=prm,
                        inst=eval('{}_inst'.format(prm)),
                        gust=atrb,
                        flag=flag)
                    if atrb is False:
                        data = ld.copy()
                    if atrb is True:
                        for c in ld.columns:
                            if c not in data.columns:
                                data = concat([data, ld[c]], axis=1)
        else:
            data = ocn.get_BDs(
                ucds=eval('ucd{}'.format(prm)),
                dates=[
                    DATEMIN,
                    DATEMAX],
                param=prm,
                inst=eval('{}_inst'.format(prm)),
                flag=flag)
        if data.shape[0] != 0:

            # Conferindo unidade de medida definida pelo usuário
            print('{}  {:<74}{}'.format(
                2 * '#', 'Conferindo unidade de medida..', 2 * '#'))
            if UNID == 'nós':
                print('{}  {:<74}{}'.format(
                    2 * '#', 'Unidade para intensidade = nós', 2 * '#'))
                if prm is 'meteo':
                    if gust is True:
                        data.WSPD3S = data.WSPD3S * 1.94384449
                        data.WSPD10S = data.WSPD10S * 1.94384449
                    elif gust is False:
                        data.WSPD = data.WSPD * 1.94384449
                    else:
                        data.WSPD10S = data.WSPD10S * 1.94384449
                        data.WSPD3S = data.WSPD3S * 1.94384449
                        data.WSPD = data.WSPD * 1.94384449
                if prm is 'curr':
                    data.HCSP = data.HCSP * 1.94384449
            if tabela_excel is True:
                print('{}  {:<74}{}'.format(
                    2 * '#', 'Escrevendo tabela excel com dados..', 2 * '#'))
                wexcel = ExcelWriter('{}\\{}.xlsx'.format(PATH, prm))
                # laço ucd
                for ucd in set(data.index.get_level_values(0)):
                    ud = data.loc[ucd]
                    print('{}    {:<72}{}'.format(
                        2 * '#', '°{}'.format(ucd), 2 * '#'))
                    # laço por instrumento
                    for itr in set(ud.index.get_level_values(0)):
                        uditr = ud.loc[itr]
                        # condição p/ caso de corrente q possui + um level 
                        if prm == 'curr':
                            # laço por profundidade
                            if len(set(uditr.index.get_level_values(0))) > 1:
                                raise RuntimeError(
                                    'Essa rotina não tá pronta pra isso.')
                            else:
                                uditr = uditr.droplevel(0)
                        print('{}        {:<68}{}'.format(
                            2 * '#', '> {}'.format(itr), 2 * '#'))
                        print('{}            {:<64}{}'.format(
                            2 * '#', '+ Data Inicial: {}'.format(
                                uditr.index[0]), 2 * '#'))
                        print('{}            {:<64}{}'.format(
                            2 * '#', '+ Data Final: {}'.format(
                                uditr.index[-1]), 2 * '#'))
                        # colocando tempo regular na serie
                        if regtime is True:
                            excl = uditr.reindex(regular_time)
                        else:
                            excl = uditr
                        excl = excl.rename_axis(
                            'DATA (UTC)',
                            axis=0)
                        excl.columns = [
                            '{} ({})'.format(acron(c)[0], UNID)
                            if c in ['WSPD', 'HCSP'] else
                            '{}'.format(gustacron[c])
                            if c in ['WSPD3S', 'WDIR3S', 'WSPD10S', 'WDIR10S']
                            else '{} ({})'.format(acron(c)[0], acron(c)[1])
                            for c in excl.columns]
                        excl.to_excel(
                            wexcel,
                            sheet_name='{:.20} - {}'.format(ucd, itr))
                        wexcel.sheets[
                            '{:.20} - {}'.format(ucd, itr)].set_column(
                                'A:G', 20)
                        if txt_file is True:
                            # Escrevendo .txt
                            txtf = uditr.dropna(how='all')
                            txtf.columns = excl.columns
                            txtf.to_csv(
                                '{}\\{}_{}.txt'.format(PATH, ucd, itr),
                                header=True, index=True, sep='\t', mode='a')
                wexcel.close()
                print('{}  {:<74}{}'.format(
                    2 * '#', 'Tabela finalizada para ' + prm, 2 * '#'))
        data_dict[prm] = data

print('{:80}'.format(80 * '#'))
print('{}{:^76}{}'.format(
    2 * '#', '**** Carregamento dos dados finalizado ****', 2 * '#'))
print('{:80}'.format(80 * '#'))

# _____________________________________________________________________________
#               Definições gráficas para implementação no plot
# _____________________________________________________________________________
colors = [
    '#1C1C1C', '#1f77b4', '#008B8B', '#D62728', '#7F7F7F', '#9467BD',
    '#Ff7f0e', '#E377C2', '#8C564B', '#BCBD22', '#0000FF', '#2CA02C',
    '#FFA54F', '#B0E2FF', '#CDBA96', '#FF83FA', '#00688B', '#EED5D2',
    '#FF7F50', '#E6E6FA', '#8B7355', '#F0E68C', '#FF0000', '#FF00FF',
    '#2F4F4F', '#17BECF', '#FF6347', '#54FF9F', '#8B8B00', '#FFFF00',
    '#228B22', '#00FFFF', '#9B30FF', '#00FA9A']

seqplot = {
    'WSPD': 0, 'WSPD3S': 0, 'WSPD10S': 0, 'ATMS': 0,
    'HCSP': 0, 'VAVH': 0, 'CHCSP': 0, 'WDIR': 1,
    'WDIR3S': 1, 'WDIR10S': 1, 'DRYT': 1, 'HCDT': 1,
    'VPEDM': 1, 'CHCDT': 1, 'VTPK1': 2, 'RELH': 2}
if gust is not None:
    linestyle = {
        'WSPD': '-', 'WSPD3S': '-', 'WSPD10S': '--', 'ATMS': '-',
        'HCSP': '-', 'VAVH': '-', 'CHCSP': '-', 'WDIR': '-',
        'WDIR3S': '-', 'WDIR10S': '--', 'DRYT': '-', 'HCDT': '-',
        'VPEDM': '-', 'CHCDT': '-', 'VTPK1': '-', 'RELH': '-'}
else:
    linestyle = {
        'WSPD': '-', 'WSPD3S': '--', 'WSPD10S': ':', 'ATMS': '-',
        'HCSP': '-', 'VAVH': '-', 'CHCSP': '-', 'WDIR': '-',
        'WDIR3S': '--', 'WDIR10S': ':', 'DRYT': '-', 'HCDT': '-',
        'VPEDM': '-', 'CHCDT': '-', 'VTPK1': '-', 'RELH': '-'}
# _____________________________________________________________________________
#                           PLOTANDO
# _____________________________________________________________________________

for prm, dataplot in data_dict.items():
    print('{}  {:<74}{}'.format(
        2 * '#', 'Plotando dados de ' + prm, 2 * '#'))
    if prm in ['meteo', 'curr']:
        fig, ax = plt.subplots(2, 1, figsize=[15, 10])
    else:
        fig, ax = plt.subplots(3, 1, figsize=[15, 10])
    if prm == 'meteo':
        # fig dos escalares
        fig2, ax2 = plt.subplots(3, 1, figsize=[15, 10])
    ixcolor = 0
    # Laço por UCD
    for ucd in set(dataplot.index.get_level_values(level=0)):
        plot = dataplot.loc[ucd]
        # Retirando possíveis valores negativos para o caso do MIROS de merluza
        if flag == 'fora':
            plot[plot<0] = np.nan
        # Laço por Instrumento
        for i in np.unique(plot.index.get_level_values(level=0)):
            # Laço por variável do parâmetro
            for cl in dataplot.columns:
                if cl in seqplot.keys():
                    # Escrevendo labels para legenda
                    if prm is 'curr':
                        lblg = "{} ({} - {} m)".format(
                            ucd,
                            i,
                            np.unique(
                                plot.loc[i].index.get_level_values(0))[0])
                        iplt = plot.loc[i].droplevel(0)
                    else:
                        if prm is 'meteo' and gust is None:
                            if cl in ['WSPD', 'WDIR']:
                                lblg = "{} ({} - Vento médio)".format(ucd, i)
                            elif cl in ['WSPD3S', 'WDIR3S']:
                                lblg = "{} ({} - Rajada 3S)".format(ucd, i)
                            elif cl in ['WSPD10S', 'WDIR10S']:
                                lblg = "{} ({} - Rajada 10S)".format(ucd, i)
                            else:
                                lblg = "{} ({})".format(ucd, i)
                        elif prm is 'meteo' and gust is True:
                            if cl in ['WSPD3S', 'WDIR3S']:
                                lblg = "{} ({} - Rajada 3S)".format(ucd, i)
                            elif cl in ['WSPD10S', 'WDIR10S']:
                                lblg = "{} ({} - Rajada 10S)".format(ucd, i)
                            else:
                                lblg = "{} ({})".format(ucd, i)
                        else:
                            lblg = "{} ({})".format(ucd, i)
                        iplt = plot.loc[i]

                    # Plotando escalares
                    if cl in ['ATMS', 'DRYT', 'RELH']:
                        ax2[seqplot[cl]].plot(
                            iplt[cl].dropna().index - deltat,
                            iplt[cl].dropna(),
                            label=lblg,
                            marker='o',
                            color=colors[ixcolor])
                        ax2[seqplot[cl]].grid('on')
                        ax2[seqplot[cl]].set_xlim(
                            [iplt.index[0] - deltat, iplt.index[-1] - deltat])
                        ax2[seqplot[cl]].set_ylabel(
                            '{} ({})'.format(
                                acron(cl)[0],
                                acron(cl)[1]))
                        caxes.fmt_time_axis(ax2[seqplot[cl]])
                        ax2[seqplot[cl]].legend(
                            bbox_to_anchor=(0., 1.02, 1., .102),
                            loc='lower left', ncol=4, mode="expand",
                            borderaxespad=0., fontsize=10)
                        caxes.fmt_time_axis(ax2[seqplot[cl]])
                    else:
                        ax[seqplot[cl]].plot(
                            iplt[cl].dropna().index - deltat,
                            iplt[cl].dropna(),
                            label=lblg,
                            marker='o',
                            linestyle=linestyle[cl],
                            color=colors[ixcolor])
                        ax[seqplot[cl]].grid('on')
                        if prm == 'curr':
                            ax[seqplot[cl]].set_xlim(
                                [min(plot.index.levels[2]) - deltat,
                                max(plot.index.levels[2]) - deltat])
                        else:
                            ax[seqplot[cl]].set_xlim(
                                [min(plot.index.levels[1]) - deltat,
                                max(plot.index.levels[1]) - deltat])
                        if cl in ['WSPD', 'HCSP']:
                            ax[seqplot[cl]].set_ylabel('{} ({})'.format(
                                acron(cl)[0], UNID))
                        elif cl in ['WSPD3S', 'WDIR3S', 'WSPD10S', 'WDIR10S']:
                            ax[seqplot[cl]].set_ylabel(gustacron[cl])
                        else:
                            ax[seqplot[cl]].set_ylabel('{} ({})'.format(
                                acron(cl)[0], acron(cl)[1]))
                        ax[seqplot[cl]].legend(
                            bbox_to_anchor=(0., 1.02, 1., .102),
                            loc='lower left', ncol=4, mode="expand",
                            borderaxespad=0., fontsize=10)
                        caxes.fmt_time_axis(ax[seqplot[cl]])
                        if prm is 'meteo' and gust is not False:
                            ax[0].set_ylabel('Intensidade ({})'.format(UNID))
                            ax[1].set_ylabel('Direção (°)')
                if cl in ['HCDT', 'WDIR', 'VPEDM', 'WDIR3S']:
                    ax[1].set_ylim([0, 361])
                    ax[1].set_yticks(np.arange(0, 361, 45))
                    caxes.direction_yaxis(ax[1])
            ixcolor += 1
        ixcolor += 1
    if prm == 'meteo':
        fig.subplots_adjust(wspace=.35, hspace=.4)
        fig2.subplots_adjust(wspace=.35, hspace=.5)
    if prm == 'curr':
        fig.subplots_adjust(wspace=.35, hspace=.4)
    if prm == 'wave':
        fig.subplots_adjust(wspace=.35, hspace=.5)

    fig.savefig('{}\\{}.png'.format(PATH, prm),
                format='png',
                bbox_inches='tight',
                dpi=600)
try:
    fig2.savefig(
        '{}\\escalares.png'.format(PATH),
        format='png',
        bbox_inches='tight',
        dpi=600)
except Exception:
    pass

print('{}{:^76}{}'.format(
    2 * '#', '**** Elaboração dos plots finalizada ****', 2 * '#'))
print('{:80}'.format(80 * '#'))
