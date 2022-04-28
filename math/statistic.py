#!/usr/bin/env python

'''

    Funções de análise estatística de dados

    Data de criação: 01/04/2020

'''
import numpy as np
from pandas import core as cr
from pandas import concat
from pandas import ExcelWriter, DataFrame, Series
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from datetime import timedelta
from calendar import monthrange


def Namostral(df):
    N = 0
    for y in set(df.index.year):
        ysl = df[df.index.year == y]
        for m in set(ysl.index.month):
            N += monthrange(y, m)[1] * 24
    return N


def movingaverage(series, window_size):
    window = np.ones(int(window_size)) / float(window_size)
    return Series(np.convolve(series, window, 'same'), index=series.index)


def more_than_1_tick(s, i, l, f):
    df = {}
    total = float(s.count().sum())
    if total > 0:
        for n, limite in enumerate(i):
            if n != len(i) - 1:
                casos = float(s.where(
                    (s >= limite) &
                    (s < i[n + 1])).count().sum())
                df.update({
                    '{:{f}} \u2264 {} < {:{f}}'.format(
                        limite, l, i[n + 1], f=f): round(
                            casos / total * 100, 2)})
            else:
                casos = float(s.where(
                    (s >= limite)).count().sum())
                df.update({
                    '{} \u2265 {:{f}}'.format(
                        l, limite, f=f): round(casos / total * 100, 2)})
    else:
        for n, limite in enumerate(i):
            if n != len(i) - 1:
                df.update({
                    '{:{f}} \u2264 {} < {:{f}}'.format(
                        limite, l, i[n + 1], f=f): np.nan})
            else:
                df.update({
                    '{} \u2265 {:{f}}'.format(
                        l, limite, f=f): np.nan})
    return df


def percentual(serie, ticks, fmt, lbl, atype='interim', signal=0):

    '''
        Autor: Francisco Thiago Franca Parente (BHYK)

        Função que calcula o percentual de dados em intervalo(s) de
        interesse

        Data criação: 22/04/2020

        * Argumentos___________________________________________________________
            serie   |   DataFrame com a série de interesse
            ticks   |   Lista com intervalos de interesse (Ex.: range(10))
            fmt     |   Formatação para escrita dos ticks (Ex.:'.2f')
            lbl     |   Nome no parâmetro avaliado (Ex.: 'Intensidade')
            atype   |   Argumento que define qual tipo de análise será
                    |   realizada.
                    |   As opções são:
                    |       'interim' - Considera todo o período selecionado
                    |       'anual'   - Análise anual
                    |       'mensal'  - Análise mensal
            signal  |   Argumento em string que define o interesse do usário
                    |   Este argumento só importa no caso de ter 1 só limite
                    |       0 - para intervalo maior que
                    |       1 - para intervalo menor que
        * Edições _____________________________________________________________
            + 10/09/2020: Foi um condição para o cálculo do percentual. O cál-
                culo só é realizado caso o período considerado tenha uma opera-
                cionalidade maior que 80%
    '''
    # variavel de corte para operacionalidade (float | .1 para 10% e etc)
    cut = .8
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    try:
        time = serie.index.get_level_values('DT_DATA')
    except Exception:
        time = serie.index

    if len(ticks) == 1:
        percent = DataFrame()
        if atype == 'interim':
            total = float(serie.count().sum())
            Nesperado = Namostral(serie)
            # Condição para operacinalidade maior que X%
            if round(total / Nesperado, 1) >= cut:
                if signal is 0:
                    casos = float(serie.where(serie >= ticks[0]).count().sum())
                    lblcolm = '\u2265 {:{fmt}}'.format(ticks[0], fmt=fmt)
                else:
                    casos = float(serie.where(serie <= ticks[0]).count().sum())
                    lblcolm = '\u2264 {:{fmt}}'.format(ticks[0], fmt=fmt)
                percent = percent.append(DataFrame(
                    data={lblcolm: round(casos / total * 100, 2)},
                    index=['{i} - {f}'.format(
                        i='{:{dfmt}}'.format(time[0], dfmt='%d/%m/%Y'),
                        f='{:{dfmt}}'.format(time[-1], dfmt='%d/%m/%Y'))])
                )

        elif atype == 'anual':
            for x, y in enumerate(np.unique(time.year)):
                yserie = serie[time.year == y].copy()
                try:
                    time2 = yserie.index.get_level_values('DT_DATA')
                except Exception:
                    time2 = yserie.index
                total = float(yserie.count().sum())
                Nesperado = Namostral(yserie)
                # Condição para operacinalidade maior que X%
                if round(total / Nesperado, 1) >= cut:
                    if signal is 0:
                        casos = float(yserie.where(
                            yserie >= ticks[0]).count().sum())
                        lblcolm = '\u2265 {:{fmt}}'.format(ticks[0], fmt=fmt)
                    else:
                        casos = float(yserie.where(
                            yserie <= ticks[0]).count().sum())
                        lblcolm = '\u2264 {:{fmt}}'.format(ticks[0], fmt=fmt)
                    percent = percent.append(DataFrame(
                        data={lblcolm: round(casos / total * 100, 2)},
                        index=['{}'.format(y)])
                    )
        elif atype == 'mensal':
            for m in np.arange(len(meses)):
                mserie = serie[time.month == m + 1].copy()
                try:
                    time2 = mserie.index.get_level_values('DT_DATA')
                except Exception:
                    time2 = mserie.index
                if mserie.shape[0] != 0:
                    total = float(mserie.count().sum())
                    Nesperado = Namostral(mserie)
                    # Condição para operacinalidade maior que X%
                    if round(total / Nesperado) >= cut:
                        if signal is 0:
                            casos = float(mserie.where(
                                mserie >= ticks[0]).count().sum())
                            lblcolm = '\u2265 {:{fmt}}'.format(
                                ticks[0], fmt=fmt)
                        else:
                            casos = float(mserie.where(
                                mserie <= ticks[0]).count().sum())
                            lblcolm = '\u2264 {:{fmt}}'.format(
                                ticks[0], fmt=fmt)
                        percent = percent.append(DataFrame(
                            data={lblcolm: round(casos / total * 100, 2)},
                            index=['{}'.format(meses[m])])
                        )
                else:
                    if signal is 0:
                        lblcolm = '\u2265 {:{fmt}}'.format(
                            ticks[0], fmt=fmt)
                    else:
                        lblcolm = '\u2264 {:{fmt}}'.format(
                            ticks[0], fmt=fmt)
                    percent = percent.append(DataFrame(
                        data={lblcolm: np.nan},
                        index=['{}'.format(meses[m])])
                    )

            percent = percent.reindex(meses)

    else:
        if atype == 'interim':
            total = float(serie.count().sum())
            Nesperado = Namostral(serie)
            # Condição para operacinalidade maior que X%
            if round(total / Nesperado, 1) >= cut:
                df = more_than_1_tick(serie, ticks, lbl, fmt)
                percent = DataFrame(
                    df,
                    index=['{i} - {f}'.format(
                        i='{:{dfmt}}'.format(time[0], dfmt='%d/%m/%Y'),
                        f='{:{dfmt}}'.format(time[-1], dfmt='%d/%m/%Y'))])

        elif atype == 'anual':
            percent = DataFrame()
            for x, y in enumerate(np.unique(time.year)):
                yserie = serie[time.year == y].copy()
                try:
                    time2 = yserie.index.get_level_values('DT_DATA')
                except Exception:
                    time2 = yserie.index
                # Condição para operacinalidade maior que X%
                Nesperado = Namostral(yserie)
                if round(yserie.count().sum() / Nesperado, 1) >= cut:
                    df = more_than_1_tick(yserie, ticks, lbl, fmt)

                    df2 = DataFrame(df, index=['Total'])
                    df3 = concat([df2], keys=[y], names=['Ano'])
                    percent = percent.append(df3)
                else:
                    percent.append(concat(
                        [DataFrame({
                            '{:{f}} \u2264 {} < {:{f}}'.format(
                                ticks[0], lbl, ticks[1], f=fmt): np.nan,
                            '{} \u2265 {:{f}}'.format(
                                lbl, ticks[1], f=fmt): np.nan},
                            index=['Total'])],
                        keys=[y], names=['Ano']))

                df2 = DataFrame()
                for m in np.arange(len(meses)):
                    mserie = yserie[time2.month == m + 1].copy()
                    # Condição para operacinalidade maior que X%
                    Nesperado = Namostral(mserie)
                    if round(mserie.count().sum() / Nesperado, 1) >= cut:
                        df = more_than_1_tick(mserie, ticks, lbl, fmt)
                        df2 = df2.append(DataFrame(df, index=[meses[m]]))
                df2 = df2.reindex(meses)

                df3 = concat([df2], keys=[y], names=['Ano'])
                percent = percent.append(df3)

        if atype == 'mensal':
            percent = DataFrame()
            for m in np.arange(len(meses)):
                mserie = serie[time.month == m + 1].copy()
                Nesperado = Namostral(mserie)
                # Condição para operacinalidade maior que X%
                if round(mserie.count().sum() / Nesperado) >= cut:
                    df = more_than_1_tick(mserie, ticks, lbl, fmt)
                    df2 = DataFrame(df, index=[meses[m]])
                    percent = percent.append(df2)
            percent = percent.reindex(meses)
    return percent


def percentual_cruzado(serie, tick1, tick2, fmt):

    '''
        Autor: Francisco Thiago Franca Parente (BHYK)
        Data de criação: 18/05/2020

        Função que calcula o percentual de dados em duas categorias diferentes,
        relacionando uma com a outra.
        Esta função foi criada para elaborar as tabelas de acordo com o
        determinado para os relatórios do Ibama.

        * Argumentos___________________________________________________________
            serie   |   DataFrame multiindex com a estrutura
                    |   UCD/BACIA/CAMPO     Tempo (DT_DATA)   c1   c2
                    |   .                   .                        .     .
                    |   .                   .                        .     .
            tick1   |   Intervalos de interesse para coluna 1
            tick2   |   Intervalos de interesse para coluna 2
                    |   Se os intervalos forem direção, colocar 'dir'
                    |   Ex.: tick2 = 'dir'
                    |   Se não, usar uma lista comum, Ex.: tick2 = [0, 10, 15]
            fmt     |   Formato de escrita do percentual (Ex.: '.1f')
            tickdir |   Caso haja alguma coluna que se refira à direção,
                    |   definir neste argumento. Se não houver, tickdir = None
        * Edições _____________________________________________________________
            + 31/07/2020
                Após reunião com equipe, verificado que o percentual estava
                sendo calculado considerando os NaN, e agora não.
    '''
    dir_bin = np.arange(-22.5, 337.6, 45)
    direc_lbl = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

    def ini_fim(tick):
        if tick[-1] / 10 > .2:
            ibusca, fbusca, lbl = .05, .04, .1
        else:
            ibusca, fbusca, lbl = .005, .004, .01
        return ibusca, fbusca, lbl

    # Retirando linhas com NaN
    data = serie.dropna(axis=0, how='all')

    if tick2 is 'dir':
        # Ajustando direções no caso do Norte
        data[data.columns[1]][data[data.columns[1]] >= 337.5] = data[
            data.columns[1]][data[data.columns[1]] >= 337.5] - 360

        for x, d in enumerate(direc_lbl):
            slc = data[
                (data[data.columns[1]] >= dir_bin[x]) &
                (data[data.columns[1]] < dir_bin[x + 1])]
            df = DataFrame()
            deltai, deltaf, ilbl = ini_fim(tick1)
            for ii, i in enumerate(tick1):
                if ii == len(tick1) - 1:
                    lbl = "\u2265 {:{ft}}".format(i + ilbl, ft=fmt)
                    df = df.append(DataFrame(
                        data={d: slc[
                            slc[slc.columns[0]] >= i + deltai].shape[0]},
                        index=[lbl]))
                else:
                    lbl = "{:{ft}} - {:{ft}}".format(
                        i + ilbl,
                        tick1[ii + 1], ft=fmt)
                    df = df.append(DataFrame(
                        data={d: slc[
                            (slc[slc.columns[0]] >= i + deltai) &
                            (slc[slc.columns[0]] < tick1[ii + 1] + deltaf)
                        ][slc.columns[0]].count()},
                        index=[lbl]))
            value_round = int(fmt.split('.')[1].split('f')[0])
            df = df.append(DataFrame(
                data={d: [
                    slc[slc.columns[0]].count(),
                    np.round(
                        (slc[slc.columns[1]].count() /
                         data[data.columns[1]].count()) * 100,
                        value_round),
                    np.round(slc[slc.columns[0]].mean(), value_round),
                    np.round(slc[slc.columns[0]].max(), value_round)]},
                index=['Total', 'Perc. (%)', 'Média', 'Máximo']))
            if x == 0:
                table = df.copy()
            else:
                table = concat([table, df], axis=1)

        # Calculando o total de registros em cada intensidade e o percentual
        Ttper = DataFrame()
        for ii, i in enumerate(tick1):
            if ii == len(tick1) - 1:
                valor = data[data[data.columns[0]] >= i + deltai][
                    data.columns[0]].count()
                lbl = "\u2265 {:{ft}}".format(i + ilbl, ft=fmt)
            else:
                valor = data[
                    (data[data.columns[0]] >= i + deltai) &
                    (data[data.columns[0]] < tick1[ii + 1] + deltaf)][
                        data.columns[0]].count()
                lbl = "{:{ft}} - {:{ft}}".format(
                    i + ilbl,
                    tick1[ii + 1], ft=fmt)
            Ttper = Ttper.append(DataFrame(
                data={
                    'Total': valor,
                    'Perc (%)': np.round(
                        (valor / data[data.columns[0]].count()) * 100,
                        int(fmt.split('.')[1].split('f')[0]))},
                index=[lbl]))

        table = concat([table, Ttper], axis=1).reindex(table.index)

    else:
        deltai1, deltaf1, ilbl1 = ini_fim(tick1)
        deltai2, deltaf2, ilbl2 = ini_fim(tick2)

        for x, d in enumerate(tick2):
            if x == len(tick2) - 1:
                slc = data[data[data.columns[1]] >= d + deltai2]
                colbl = "\u2265 {:{ft}}".format(d + ilbl2, ft=fmt)
            else:
                slc = data[
                    (data[data.columns[1]] >= d + deltai2) &
                    (data[data.columns[1]] < tick2[x + 1] + deltaf2)]
                colbl = "{:{ft}} - {:{ft}}".format(
                    d + ilbl2,
                    tick2[x + 1],
                    ft=fmt)
            df = DataFrame()
            for ii, i in enumerate(tick1):
                if ii == len(tick1) - 1:
                    lbl = "\u2265 {:{ft}}".format(i + ilbl1, ft=fmt)
                    df = df.append(DataFrame(
                        data={colbl: slc[
                            slc[slc.columns[0]] >= i + deltai1][
                                slc.columns[0]].count()},
                        index=[lbl]))
                else:
                    lbl = "{:{ft}} - {:{ft}}".format(
                        i + ilbl1, tick1[ii + 1], ft=fmt)
                    df = df.append(DataFrame(
                        data={colbl: slc[
                            (slc[slc.columns[0]] >= i + deltai1) &
                            (slc[slc.columns[0]] < tick1[ii + 1] + deltaf1)
                        ][slc.columns[0]].count()},
                        index=[lbl]))
            value_round = int(fmt.split('.')[1].split('f')[0])
            df = df.append(DataFrame(
                data={colbl: [
                    slc[slc.columns[0]].count(),
                    np.round(
                        (slc[slc.columns[0]].count() /
                         data[data.columns[0]].count()) * 100,
                        value_round),
                    np.round(slc[slc.columns[0]].mean(), value_round),
                    np.round(slc[slc.columns[0]].max(), value_round)]},
                index=['Total', 'Perc. (%)', 'Média', 'Máximo']))
            if x == 0:
                table = df.copy()
            else:
                table = concat([table, df], axis=1)

        # Calculando o total de registros em cada intensidade e o percentual
        Ttper = DataFrame()
        for ii, i in enumerate(tick1):
            if ii == len(tick1) - 1:
                valor = data[data[data.columns[0]] >= i + deltai1][
                    data.columns[0]].count()
                lbl = "\u2265 {:{ft}}".format(i + ilbl1, ft=fmt)
            else:
                valor = data[
                    (data[data.columns[0]] >= i + deltai1) &
                    (data[data.columns[0]] < tick1[ii + 1] + deltaf1)][
                        data.columns[0]].count()
                lbl = "{:{ft}} - {:{ft}}".format(
                    i + ilbl1,
                    tick1[ii + 1], ft=fmt)
            Ttper = Ttper.append(DataFrame(
                data={
                    'Total': valor,
                    'Perc (%)': np.round(
                        (valor / data[data.columns[0]].count()) * 100,
                        int(fmt.split('.')[1].split('f')[0]))},
                index=[lbl]))

        table = concat([table, Ttper], axis=1).reindex(table.index)

    return table


def janelas_operacionais(df, limites, janelas, op):

    '''
        Autor: Francisco Thiago Franca Parente (BHYK)

        Função que calcula o número de janelas operacionais para um parâmetro.

        Data criação: 31/07/2020

        * Argumentos___________________________________________________________
            df      |   DataFrame com parâmetro de interesse.
                    |       Atenção! O DataFrame deve conter somente a coluna
                    |       do parâmetro de interesse.
            limites |   Lista com intervalos de interesse (Ex.: [1, 2, 3])
            janelas |   Lista com duração das janelas em horas
                    |   (Ex.: [12, 24, 48])
            op      |   String que define qual interesse do usuário. As opções
                    |   são:
                    |       'menor' -   Janelas com valor menor que o limite
                    |       'maior' -   Janelas com valor maior que o limite
                    |       'igual' -   Janelas com valor igual aos limites
    '''

    if len(df.columns) > 1:
        raise RuntimeError("O DataFrame deve conter somente uma colunha!")

    dfwindow = DataFrame()
    for lim in limites:

        if op is 'igual':
            # ver ordem de grandeza !!!!!!!!!!!!!!!!!!
            check = df[
                (df > lim - .6) &
                (df < lim + .5)].dropna()
            column = lim
        elif op is 'maior':
            check = df[df > lim].dropna()
            column = "> {}".format(lim)
        elif op is 'menor':
            check = df[df < lim].dropna()
            column = "< {}".format(lim)
        else:
            raise RuntimeError('Argumento op inválido! Ver descrição.')

        # Intervalo de tempo entre os registros
        diftime = check.index[1:] - check.index[:-1]

        mask = np.concatenate(
            ([False], diftime == timedelta(hours=1), [False]))
        if ~mask.any():
            windows = [0]
        else:
            idx = np.nonzero(mask[1:] != mask[:-1])[0]
            windows = list(idx[1::2] - idx[::2])

        # criando lista com número de janelas
        n_windows = [windows.count(x) for x in janelas]
        n_windows.insert(0, diftime[diftime != timedelta(hours=1)].shape[0])

        data = DataFrame(
            n_windows,
            columns=[column],
            index=['< 1 h'] + ["{} h".format(x) for x in janelas])
        dfwindow = concat([dfwindow, data], axis=1)

    return dfwindow


def janela_tempo(time, janelas):

    '''
        Autor: Francisco Thiago Franca Parente (BHYK)

        Função que calcula o número de janelas operacionais para o caso de
        envolver mais de um parâmetro na janela operacional. Neste caso,
        a entrada da função se limita somente aos indícies de tempo em que
        os parâmetros estiveram dentro das faixas consideradas.

        Data criação: 31/07/2020

        * Argumentos___________________________________________________________
            time    |   DatetimeIndex dtype='datetime64[ns]
            janelas |   Lista com duração das janelas em horas
                    |   (Ex.: [12, 24, 48])
    '''

    # Intervalo de tempo entre os registros
    diftime = time[1:] - time[:-1]

    mask = np.concatenate(
        ([False], diftime == timedelta(hours=1), [False]))
    if ~mask.any():
        windows = [0]
    else:
        idx = np.nonzero(mask[1:] != mask[:-1])[0]
        windows = list(idx[1::2] - idx[::2])

    # criando lista com número de janelas
    n_windows = [windows.count(x) for x in janelas]
    n_windows.insert(
        0, diftime[diftime != timedelta(hours=1)].shape[0])

    return n_windows
