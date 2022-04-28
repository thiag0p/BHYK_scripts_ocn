'''

    Rotina que lê o banco de dados das UCDS de referência de cada bacia
    e plota gráficos de barra com limites de "atenção" e "alerta", assim como
    gera tabela excel com estas informações.

    Autor: Francisco Thiago Franca Parente (BHYK)
    Criação: 11/03/2020

    Edições:
        + 27/08/2020:
            Modificado o gráfico dos últimos dois anos. Foi acrescentado dois
            xticks aos gráfico. Um referente à média ponderada entre janeiro e
            o mês de interesse e outro com o percentual anual do ano anterior.

            Ainda, foi adicionado ao código uma nova forma de exportar os
            resultados já exatamente como exposto na tabela do relatório.

'''

# _____________________________________________________________________________
#                               Modificar aqui
# _____________________________________________________________________________
import os
# Diretório onde serão salvos os outputs
PATH = os.path.normpath("XXXXXXXXXXXXXXXX")

# Intervalo de data para busca no banco de dados
DATEMIN = u"01/01/2010 00:00:00"
DATEMAX = u"31/01/2022 23:00:00"

# Bacias de interesse
BACIAS = ['Bacia de Santos', 'Bacia de Campos', 'Bacia do Espírito Santo']
# Definindo os limites de atenção e alerta de vento e onda
wind_lim = [20., 28.]
wave_lim = [1.5, 2., 2.5]

# NÚMERO do mês de interesse (1 -jan, 2-fev, ...)
m_interesse = [1]

# Unidade de medida para vento
unidademedida = 'nós'

# _____________________________________________________________________________

from warnings import filterwarnings
# Desativação de alertas minimizando mensagens no console
filterwarnings("ignore")

from sys import path
from datetime import timedelta
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import matplotlib.patheffects as PathEffects
import time
pth1 = 'XXXXXXXXXXXXXXX'
dirs = ['data', 'math', 'settings', 'graph']
for d in dirs:
    pth2 = pth1 + d
    path.append(pth2)

import definitions as mopdef
import statistic as stc
import OCNdb as ocn
import histograma as htg
from calendar import monthrange
# _____________________________________________________________________________

# Variável de escrita excel
wave_writer = pd.ExcelWriter(PATH + '\\wave_todas_bacias.xlsx')
wind_writer = pd.ExcelWriter(PATH + '\\wind_todas_bacias.xlsx')

# Labels dos meses do ano
MNTHLBL = ('Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
           'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez')

# datetime para reindexação
dti = dt.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S')
dtf = dt.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S')

# Carregando quais são as unidades unidades representativas das bacias
UCDS = mopdef.get_ucds_bacias()

# Verificando os anos que serão avaliados
# ano atual
YEAR = int(DATEMAX[6:10])

start = time.time()
_wind, _wave = pd.DataFrame(), pd.DataFrame()
for bx, bacia in enumerate(BACIAS):
    # Pegando as ucds de referência de cada bacia
    ucds_wind = list(filter(None,
                            [item for ucd in UCDS.loc[bacia].VENTO.values
                             for item in ucd]))
    ucds_wave = list(filter(None,
                            [item for ucd in UCDS.loc[bacia].ONDA.values
                             for item in ucd]))
    # Lendo dados do banco
    crono = time.time()
    print("{} // {}".format('Lendo vento de', bacia))
    wind = ocn.get_BDs(ucds_wind, [DATEMIN, DATEMAX], 'meteo')
    print("{} // {:.2f} min".format(
        'Tempo de leitura do vento',
        (time.time() - crono) / 60))
    print("{} // {}".format('Lendo onda de', bacia))
    crono = time.time()
    wave = ocn.get_BDs(ucds_wave, [DATEMIN, DATEMAX], 'wave')
    print("{} // {}".format('Finalizada consulta de dados de', bacia))
    print("{} // {:.2f} min".format(
        'Tempo de leitura do onda',
        (time.time() - crono) / 60))
    # Verificando unidade de medidia
    if unidademedida == 'nós':
        wind.WSPD = wind.WSPD * 1.94384449

    # # Plotando para verificação da série que será analisada
    # fig, ax = plt.subplots(1, 1, figsize=[15, 10])
    # wind.groupby(level=[2]).median().WSPD.plot(ax=ax)
    # ax.set_title("Vento {}".format(bacia))
    # fig.savefig(
    #     '{}\\Vento_{}.png'.format(PATH, bacia),
    #     format='png',
    #     bbox_inches='tight',
    #     dpi=600)

    # fig, ax = plt.subplots(1, 1, figsize=[15, 10])
    # wave.groupby(level=[2]).median().VAVH.plot(ax=ax)
    # ax.set_title("Onda {}".format(bacia))
    # fig.savefig(
    #     '{}\\Onda_{}.png'.format(PATH, bacia),
    #     format='png',
    #     bbox_inches='tight',
    #     dpi=600)

    # Calculando percentual de dados.
    p_wind = stc.percentual(
        wind.groupby(level=[2]).median().WSPD,
        wind_lim,
        '.1f',
        'Int.',
        atype='anual')
    p_wave = stc.percentual(
        wave.groupby(level=[2]).median().VAVH,
        wave_lim,
        '.1f',
        'Hs',
        atype='anual')
    _wind = _wind.append(pd.concat([p_wind], keys=[bacia], names=['Bacia']))
    _wave = _wave.append(pd.concat([p_wave], keys=[bacia], names=['Bacia']))
    print('[{}: Ok]'.format(bacia))

_wind.to_excel(wind_writer)
_wave.to_excel(wave_writer)
wind_writer.close()
wave_writer.close()

print("{} // {:.2f} min".format(
    'Tempo Total de leitura dos dados',
    (time.time() - start) / 60))
# _____________________________________________________________________________
#                              Plotando
# _____________________________________________________________________________

width = .45

# PLOTA DADO DE TODOS OS ANOS DO MÊS DE INTERESSE
for name, param in zip(['wind', 'wave'], [_wind, _wave]):
    for m in m_interesse:
        fig = plt.figure(figsize=(12, 9))

        ordem = ['Bacia de Santos', 'Bacia de Campos', 'Bacia do Espírito Santo']
        for splt, bc in enumerate(ordem):

            xlbl = [str(x) for x in param.index.levels[1]]
            xtik = np.arange(0, len(xlbl), 1)

            if param.loc[bc].xs(MNTHLBL[m - 1], level=1).shape[0] != len(xlbl):
                ckdata = param.loc[bc].xs(MNTHLBL[m - 1], level=1)
                for ey in xlbl:
                    if int(ey) not in ckdata.index:
                        ckdata = ckdata.append(
                            pd.DataFrame(
                                data=[],
                                index=[int(ey)],
                                columns=ckdata.columns))
                ckdata = ckdata.sort_index()
                bars = {x: ckdata[x].values for x in ckdata.columns}
            else:
                ckdata = param.loc[bc].xs(MNTHLBL[m - 1], level=1)
            lmts = list(ckdata.columns)
            lmts.reverse()
            bars = {x: ckdata[x].values for x in lmts}

            ax = fig.add_subplot(
                int('{}1{}'.format(len(param.index.levels[0]), splt + 1)))

            if len(bars) > 2:
                colors = ['#E24A33', '#FBC15E', '#27AE60']
            else:
                colors = ['#E24A33', '#FBC15E']

            bottom = np.zeros(len(xtik))
            for n, bar in enumerate(bars.keys()):
                rects2 = ax.bar(
                    xtik,
                    bars[bar],
                    width, color=colors[n],
                    bottom=np.nan_to_num(bottom),
                    align='center', alpha=.7,  edgecolor='k',
                    label=bar)
                bottom += bars[bar]


            if name == 'wind':
                ax.set_ylim(0., 40)
                dy, legx = 6, .738
            else:
                ax.set_ylim(0., 120)
                dy, legx = 10, .868
            ax.set_xlim(0 - width, xtik[-1] + width)
            ax.set_ylabel('Registros (%)', fontsize=14)
            
            ax.text(-0.4, ax.get_ylim()[1] - dy, bc, fontsize=14, weight='bold')

            plt.xticks(xtik, xlbl, fontsize=14)
            for label in ax.xaxis.get_majorticklabels():
                label.set_fontsize(14)
            for label in ax.yaxis.get_majorticklabels():
                label.set_fontsize(14)
            # COLOCANDO VALORES NAS BARRAS
            texto = [(bars[x]) for x in bars.keys()]

            bottom = np.zeros(len(xtik))
            for tx in texto:
                strnumb = ['{0:2.1f}%'.format(round(x, 2)).replace('.', ',') for x in tx]
                for _, x in enumerate(range(len(xtik))):
                    txt = ax.text(
                        xtik[x],
                        tx[x] + bottom[x],
                        strnumb[x],
                        horizontalalignment='center',
                        fontsize=11)
                    plt.setp(
                        txt,
                        path_effects=[
                            PathEffects.withStroke(linewidth=3, foreground="w")])
                bottom += tx

    ax.legend(
        prop={'size': 14},
        bbox_to_anchor=(legx, -.2),
        ncol=len(bars))

    fig.savefig(
        '{}\\{}_anual.png'.format(PATH, name),
        format='png',
        bbox_inches='tight')


# _____________________________________________________________________________
#                       PLOTA DADO DOS ÚLTIMOS DOIS ANOS
# _____________________________________________________________________________
newlabel = MNTHLBL.__add__(tuple(
    ['Média \n ponderada \n (Jan - {})'.format(MNTHLBL[m_interesse[0]-1]),
     'Total \n de {}\n e {}'.format(param.index.levels[1][-2], param.index.levels[1][-3])]
))

xax2 = np.append(np.arange(1, 13), 14)*1.3
width = 0.3

for name, param in zip(['wind', 'wave'], [_wind, _wave]):
    fig = plt.figure(figsize=(12, 9))
    yr = list(param.index.levels[1][-3:])

    ordem = ['Bacia de Santos', 'Bacia de Campos', 'Bacia do Espírito Santo']
    for splt, bc in enumerate(ordem):

        ax = fig.add_subplot(int('{}1{}'.format(
            len(param.index.levels[0]),
            splt + 1)))
        for i, y in enumerate(yr):
            if i == 0:
                dx = -.3
                sb = .3
                linewidth = 1
            elif i == 1:
                dx = .0
                sb = .7
                linewidth = 1
            else:
                dx = .3
                sb = 1.
                linewidth = 2

            # Calculado o peso de cada mês para média ponderada
            peso = []
            for m in np.arange(1, 13, 1):
                peso.append(np.mean([
                    monthrange(y, m)[1]
                for y in np.unique(param.loc[bc].index.get_level_values(0))
            ]) / 31)
            try:
                # pegando somente os percentuais dos meses até o mês de interesse
                sqz = param.loc[bc].loc[y].drop('Total', axis=0)
                # pegando percentuais até o mes de interesse para acumulado
                avg = param.loc[bc].loc[y].drop('Total', axis=0)[:m_interesse[0]]

                lmts = list(param.columns)
                lmts.reverse()
                bars = {}
                for cll in lmts:
                    bars[cll] = np.nan_to_num(np.append(
                        sqz[cll].values,
                        round(np.average(
                            avg[cll].values,
                            weights=peso[:m_interesse[0]]), 2)))

                # the bars
                if len(bars) > 2:
                    colors = ['#E24A33', '#FBC15E', '#27AE60']
                else:
                    colors = ['#E24A33', '#FBC15E']

                bottom = np.zeros(len(xax2))
                for n, bar in enumerate(bars.keys()):
                    rects2 = ax.bar(
                        xax2 + dx,
                        bars[bar],
                        width, color=colors[n],
                        bottom=np.nan_to_num(bottom),
                        align='center', alpha=sb,  edgecolor='k',
                        label=bar, linewidth=linewidth)
                    bottom += np.nan_to_num(bars[bar])

                for label in ax.xaxis.get_majorticklabels():
                    label.set_fontsize(14)
                for label in ax.yaxis.get_majorticklabels():
                    label.set_fontsize(14)
            except Exception:
                continue
            # texto = [(bars[x]) for x in bars.keys()]

            # bottom = np.zeros(len(xax2))
            # for tx in texto:
            #     strnumb = ['{0:2.1f}%'.format(round(x, 2)).replace('.', ',') for x in tx]
            #     for _, x in enumerate(range(len(xax2))):
            #         txt = ax.text(
            #             xax2[x] + dx,
            #             tx[x] + bottom[x],
            #             strnumb[x],
            #             horizontalalignment='center',
            #             fontsize=11)
            #         plt.setp(
            #             txt,
            #             path_effects=[
            #                 PathEffects.withStroke(linewidth=3, foreground="w")])
            #     bottom += tx

        # ax.set_xlim(0, 17)
        if name == 'wind':
            ax.set_ylim(0., 40)
            ax.text(0.2, ax.get_ylim()[1] - 6, bc, fontsize=14, weight='bold')

        else:
            ax.set_ylim(0., 110)
            ax.text(0.2, ax.get_ylim()[1] - 10, bc, fontsize=14, weight='bold')
        ax.set_ylabel('Registros (%)', fontsize=14)

        sb, dx = [.3, .7], [-.3, .3]
        for m, yss in enumerate(yr[:-1]):
            btm = 0
            for n, cll in enumerate(lmts):
                acmval = param.loc[bc].loc[yss].loc['Total'][cll]
                acum = ax.bar(
                    16*1.3 + dx[m], acmval,
                    width + .2, color=colors[n],
                    align='center', alpha=sb[m], bottom=btm, edgecolor='k')
                btm += acmval
        if splt == len(param.index.levels[0]) - 1:
            plt.xticks(np.append(xax2, 16 * 1.3), newlabel,
                       fontsize=14, rotation=0)
        else:
            plt.xticks([])

    if name == 'wind':
        bboxx = (.86, -.40)
        xx0, yy0 = -1., -23
        xx1, yy1 = 5.6, -23
        xx2, yy2 = 12.6, -23
    if name == 'wave':
        bboxx = (.82, -.4)
        xx0, yy0 = .03, -60
        xx1, yy1 = 6.0, -60
        xx2, yy2 = 12.5, -60
    ax.text(xx2, yy2, str(yr[2]), weight='bold')
    ax.text(xx1, yy1, str(yr[1]), weight='bold')
    ax.text(xx0, yy0, str(yr[0]), weight='bold')

    ax.legend(
        prop={'size': 12},
        bbox_to_anchor=bboxx,
        frameon=False,
        ncol=3,
        columnspacing=5.5)

    fig.savefig(
        '{}\\{}_compara_{}_{}_{}.png'.format(PATH, name, yr[0], yr[1], yr[2]),
        format='png',
        bbox_inches='tight')

# _____________________________________________________________________________
#                   EXPORTANDO TABELA UTILIZADA NO RELATÓRIO 
# _____________________________________________________________________________
windtable = _wind.xs(MNTHLBL[m_interesse[0] - 1], level=2)
wavetable = _wave.xs(MNTHLBL[m_interesse[0] - 1], level=2)
indyrs = np.arange(2018, windtable.index.levels[1][-1] + 1, 1)

twd, twv = pd.DataFrame(), pd.DataFrame()
for bc in windtable.index.levels[0]:
    wd = windtable.loc[bc].loc[indyrs]
    mnyrs = windtable.loc[bc][:-1].mean().to_frame().T
    mnyrs.index = ['{} a {}'.format(windtable.loc[bc].index[0],
                                    windtable.loc[bc].index[-2])]
    wd = wd.append(mnyrs)
    wd["Total"] = wd.sum(axis=1)
    wd = wd.round(1)

    twd = twd.append(pd.concat([wd], keys=[bc], names=['Bacia']))

    wv = wavetable.loc[bc].loc[indyrs]
    mnyrs = wavetable.loc[bc][:-1].mean().to_frame().T
    mnyrs.index = ['{} a {}'.format(wavetable.loc[bc].index[0],
                                    wavetable.loc[bc].index[-2])]
    wv = wv.append(mnyrs)
    wv["Total"] = wv.sum(axis=1)
    wv = wv.round(1)

    twv = twv.append(pd.concat([wv], keys=[bc], names=['Bacia']))

bcorder = ['Bacia de Santos', 'Bacia de Campos', 'Bacia do Espírito Santo']
excel = pd.ExcelWriter('{}\\Tabela_relatorio.xlsx'.format(PATH))
for sheet, parm in zip(('vento', 'onda'), (twd, twv)):
    parm.T[bcorder].T.to_excel(excel, sheet_name=sheet)
excel.close()

#_________________________________________________________________
# Linhas para plot de comparação entre UCDs, média e mediana

    # fig, ax = plt.subplots(1, 1, figsize=[15, 10])
    # for ucd in wind.index.levels[0]:
    #     wind.loc[ucd].loc['YOUNG'].WSPD.plot(
    #         ax=ax,
    #         alpha=1,
    #         linewidth=0,
    #         marker='o',
    #         markersize=4)
    # wind.groupby(level=[2]).median().WSPD.plot(
    #     ax=ax,
    #     linestyle='-',
    #     alpha=1,
    #     linewidth=2,
    #     color='k')
    # wind.groupby(level=[2]).mean().WSPD.plot(
    #     ax=ax,
    #     linestyle='-',
    #     alpha=1,
    #     linewidth=2,
    #     color='r')
    # fig.savefig(
    #     '{}\\teste1.png'.format(PATH),
    #     format='png',
    #     bbox_inches='tight',
    #     dpi=600)

    # fig, ax = plt.subplots(1, 1, figsize=[15, 10])
    # for ucd in wind.index.levels[0]:
    #     wind.loc[ucd].loc['YOUNG'].WSPD[:200].plot(
    #         ax=ax,
    #         alpha=1,
    #         linewidth=0,
    #         marker='o',
    #         markersize=4)
    # wind.groupby(level=[2]).median().WSPD[:200].plot(
    #     ax=ax,
    #     linestyle='-',
    #     alpha=.7,
    #     linewidth=3,
    #     color='k')
    # wind.groupby(level=[2]).mean().WSPD[:200].plot(
    #     ax=ax,
    #     linestyle='-',
    #     alpha=.7,
    #     linewidth=3,
    #     color='r')
    # fig.savefig(
    #     '{}\\teste2.png'.format(PATH),
    #     format='png',
    #     bbox_inches='tight',
    #     dpi=600)
