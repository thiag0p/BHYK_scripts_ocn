from ocnpylib import id2uv
import numpy as np
import matplotlib.pyplot as plt
from sys import path
path.append('M:\\Rotinas\\python\\scripts\\01.Briefings\\PPROG')
path.append('M:\\Rotinas\\python\\graph')
from custom import caxes
from data import OCNdb as ocn
from plot import background, set_axis
from datetime import timedelta
from pandas import DatetimeIndex
from matplotlib import colors
from pyocnp import acronym2ext as acron


def plot_wind(forecast, wkheight, PATH, UCD):
    '''
        Plota vento

        :param forecast: DataFrame com os dados de previsão
        :param wkheight: lista com valores das alturas de trabalho
        :param PATH: string com diretório onde será salva a imagem
        :param UCD: string com o nome da ucd para nomear o arquivo de saída
    '''
    selectime = select_time(forecast)
    plot = forecast.loc[selectime]
    u, v = id2uv(
        np.ones(len(plot.VelocidadeVento)),
        plot.DirecaoVento,
        str_conv='meteo')

    for altura in [10] + wkheight:

        fator = (1 + 0.137 * np.log(altura / 10.))
        intensidade = (plot.VelocidadeVento * fator).round(2)
        rajada = (plot.Rajada * fator).round(2)

        fig, ax = plt.subplots(figsize=(15, 8))
        background.color_backgroud(
            x=plot.index,
            y1=21.6,
            y2=24.8,
            ax=ax)

        # PLOTANDO SÉRIE
        ax.plot(
            plot.index,
            intensidade,
            linewidth=2,
            marker='o',
            color='black',
            label=u"Intensidade Média")
        ax.plot(
            plot.index,
            rajada,
            linewidth=2,
            marker='o',
            color='#C0C0C0',
            label=u"Rajada")

        # LEGENDA
        ax.legend(
            bbox_to_anchor=(0., 1.10, 1., .102),
            loc=3,
            ncol=2,
            borderaxespad=0.)
        # VETORES
        set_axis.plot_vetores(
            xticks=plot.index,
            centro=[[0] * (len(plot.index))],
            u=u.values,
            v=v.values,
            clr='black')

        # DEFININDO LIMITES DO EIXO X
        ax.set_xlim(plot.index[0], plot.index[-1])

        # YLABEL
        ax.set_ylabel(
            f"Intensidade média do vento (nós) a \n {altura} m de altitude",
            fontsize=12)
        # YLIM
        ax.set_ylim(
            intensidade.min() - 3,
            rajada.max() + 3)
        # PLOTANDO DIAS E HORAS
        set_axis.plot_days_hours(ax=ax)
        # ESCREVENDO OS VALORES
        background.escreve_valores(
            ax=ax,
            xi=plot.index,
            values=intensidade.values,
            sfmt='.0f',
            dy=.7,
            clr='black')
        background.escreve_valores(
            ax=ax,
            xi=plot.index,
            values=rajada.values,
            sfmt='.0f',
            dy=.7,
            clr='grey')
        fig.savefig(
            f'{PATH}\\Vento_previsto_{UCD}_{altura}m.png',
            format='png')
    plt.close('all')


def plot_wave(forecast, PATH, UCD):
    '''
        Plota onda

        :param forecast: DataFrame com os dados de previsão
        :param PATH: string com o diretório onde será salva imagem
        :param UCD: string com o nome da ucd para nomear o arquivo de saída
    '''
    selectime = select_time(forecast)
    plot = forecast.loc[selectime]

    uo, vo = id2uv(
        np.ones(len(plot.AlturaOnda)),
        plot.DirecaoOnda,
        str_conv='meteo')

    fig, ax = plt.subplots(figsize=(15, 8))
    plt.fill_between(
        plot.index,
        3,
        100,
        facecolor='#FFB2B2',
        edgecolor='#FFE4B2',
        alpha=0.7)

    # PLOTANDO SÉRIE
    ax.plot(
        plot.index,
        plot.AlturaOnda,
        linewidth=2,
        marker='o',
        color='#030381',
        label=u"Altura Significativa")
    ax.plot(
        plot.index,
        plot.AlturaMaximaOnda,
        linewidth=2,
        marker="^",
        color='#61C1DB',
        label=u"Altura Máxima")

    # PLOTANDO PERÍODO DE PICO
    ax3 = ax.twinx()
    ax3.plot(
        plot.index,
        plot.PeriodoPicoOnda,
        linewidth=1,
        color='red',
        label=u"Período de Pico Primário")

    # LEGENDA
    fig.legend(
        bbox_to_anchor=(0.125, .88, 1., .102),
        loc=3,
        ncol=3,
        borderaxespad=0.)
    # VETORES
    set_axis.plot_vetores(
        xticks=plot.index,
        centro=[[0] * (len(plot.index))],
        u=uo.values,
        v=vo.values,
        clr='#030381')

    # DEFININDO LIMITES DO EIXO X
    ax.set_xlim(plot.index[0], plot.index[-1])

    # PLOTANDO DIAS E HORAS
    set_axis.plot_days_hours(ax=ax)
    # YLABELS
    # ALTURA DE ONDA
    ax.set_ylabel("Altura de Onda (m)", fontsize=12, color='#030381')
    [t.set_color('#030381') for t in ax.yaxis.get_ticklines()]
    [t.set_color('#030381') for t in ax.yaxis.get_ticklabels()]
    # PERIODO DE PICO
    ax3.set_ylabel("Período de Pico Primário (s)", fontsize=12, color='red')
    [t.set_color('red') for t in ax3.yaxis.get_ticklines()]
    [t.set_color('red') for t in ax3.yaxis.get_ticklabels()]
    # YLIM
    ax.set_ylim(
        plot.AlturaOnda.min() - 1,
        plot.AlturaMaximaOnda.max() + 1)
    ax3.set_ylim(
        plot.PeriodoPicoOnda.min() - 1,
        plot.PeriodoPicoOnda.max() + 1)
    # ESCREVENDO OS VALORES
    background.escreve_valores(
        ax=ax,
        xi=plot.index,
        values=plot.AlturaOnda.values,
        sfmt='.1f',
        dy=.2,
        clr='#030381')
    background.escreve_valores(
        ax=ax,
        xi=plot.index,
        values=plot.AlturaMaximaOnda.values,
        sfmt='.1f',
        dy=.2,
        clr='#61C1DB')
    # SALVANDO IMAGEM
    fig.savefig(
        f'{PATH}\\Onda_prevista_{UCD}.png',
        format='png')
    plt.close('all')


def plot_rain(forecast, PATH, UCD, wkheight, tipo=1):
    '''
        Plota chuva

        :param forecast: DataFrame com os dados de previsão
        :param PATH: string com o diretório onde será salva imagem
        :param UCD: string com o nome da ucd para nomear o arquivo de saída
        :param wkheight: int ou float da altura de trabalho
        :param tipo: int 1 ou N - parametro criado devido solicitacao do
            cliente. Caso queira colorir os limites de chuva no plot (tipo 1) e
            caso queira color os limites de vento no plot de chuva (tipo 2 ou
            qualquer outro número)
    '''
    selectime = select_time(forecast)
    plot = forecast.loc[selectime]

    fator = (1 + 0.137 * np.log(wkheight / 10.))
    intensidade = (plot.VelocidadeVento * fator).round(2)

    u, v = id2uv(
        np.ones(len(plot.VelocidadeVento)),
        plot.DirecaoVento,
        str_conv='meteo')

    fig, ax = plt.subplots(figsize=(15, 8))
    # PLOTANDO SÉRIE
    ax2 = ax.twinx()
    # colorindo limites
    if tipo == 1:
        background.color_backgroud(
            x=plot.index,
            y1=10,
            y2=20,
            ax=ax)
    else:
        background.color_backgroud(
            x=plot.index,
            y1=21.6,
            y2=24.8,
            ax=ax2)

    ax.bar(
        plot.index,
        plot.Precipitacao,
        width=.1,
        color='#056C9B')
    ax.set_xlim(
        plot.index[0],
        plot.index[-1])
    # PLOTANDO VENTO NA ALTURA DE TRABALHO
    ax2.plot(
        plot.index,
        intensidade,
        linewidth=2,
        marker='o',
        color='black',
        label=u"Intensidade média do vento")

    # YLIM
    if plot.Precipitacao.max() < 10:
        ax.set_ylim(0, 15)
    else:
        ax.set_ylim(0, plot.Precipitacao.max() + 10)
    # PLOTANDO DIAS E HORAS
    set_axis.plot_days_hours(ax=ax)
    # LEGENDA
    fig.legend(bbox_to_anchor=(0.125, .88, 1., .102), loc=3,
               ncol=2, borderaxespad=0., fontsize=12)
    # YLABELS
    ax.set_ylabel(
        "Precipitação acumulada em 3h (mm)",
        fontsize=12,
        color='#056C9B')
    [t.set_color('#056C9B') for t in ax.yaxis.get_ticklines()]
    [t.set_color('#056C9B') for t in ax.yaxis.get_ticklabels()]
    ax2.set_ylabel(
        u"Intensidade média do vento a\n {} m de altitude (nós)".format(
            wkheight),
        fontsize=12,
        color='black')
    # YLIM
    ax2.set_ylim(
        intensidade.min() - 3,
        intensidade.max() + 3)
    # VETORES
    set_axis.plot_vetores(
        xticks=plot.index,
        centro=[[0] * (len(plot.index))],
        u=u.values,
        v=v.values,
        clr='black')
    # ESCREVENDO OS VALORES
    background.escreve_valores(
        ax=ax2,
        xi=plot.index,
        values=intensidade.values,
        sfmt='.0f',
        dy=.7,
        clr='black')
    fig.savefig(
        f'{PATH}\\Precipitacao_prevista_{UCD}.png',
        format='png')
    plt.close('all')


def select_time(forecast):

    '''
        Seleciona os tempos que os dados serão impressos para evitar poluição
        visual

        :param forecast: DataFrame com dados da previsão
    '''
    selectime, c1, c2 = [], 0, 0
    for x, stm in enumerate(forecast.index):
        if stm == forecast.index[0]:
            selectime.append(stm)
        else:
            if stm == forecast.index[-1]:
                selectime.append(stm)
            elif forecast.index[x + 1] - stm == timedelta(hours=1):
                c1 += 1
                if c1 == 6:
                    c1 = 0
                    selectime.append(stm)
            elif forecast.index[x + 1] - stm == timedelta(hours=3):
                c2 += 1
                if c2 == 2:
                    c2 = 0
                    selectime.append(stm)
            elif forecast.index[x + 1] - stm > timedelta(hours=3):
                selectime.append(stm)
    selectime = DatetimeIndex(selectime)

    return selectime


def pcolor_gust(forecast, wkheight, PATH, UCD):
    '''
        Plota pcolormesh da rajada para diversas alturas de trabalho

        :param forecast: DataFrame com os dados de previsão
        :param wkheight: lista com valores das alturas de trabalho
        :param PATH: string com diretório onde será salva a imagem
        :param UCD: string com o nome da ucd para nomear o arquivo de saída
    '''

    selectime = select_time(forecast)
    plot = forecast.loc[selectime]
    u, v = id2uv(
        np.ones(len(plot.VelocidadeVento)),
        plot.DirecaoVento,
        str_conv='meteo')

    tab = forecast.Rajada.to_frame()

    # CRIANDO ARRAY DAS ALTITUDES
    if wkheight[-1] <= 25:
        alt = np.arange(10, wkheight[-1] + 1, 1)
    elif wkheight[-1] > 25 and wkheight[-1] <= 50:
        alt = np.arange(10, wkheight[-1] + 1, 2)
    else:
        alt = np.arange(10, wkheight[-1] + 1, 5)
    # CALCULANDO AS RAJADAS PARA CADA ALTURA
    for t in alt:
        fator = (1 + 0.137 * np.log(t / 10.))
        tab[str(t)] = (tab.Rajada * fator).round(2)

    # RETIRANDO OS VALORES DE RAJADA DA PREVISÃO
    tab = tab.drop(columns=['Rajada'])

    # TRANSPONDO O DF RESULTANTE
    tab = tab.T

    # INICIO DO PLOT ESTILO PCOLORMESH
    fig, ax = plt.subplots(figsize=(15, 8))
    # LISTANDO AS CORES DA CLASSIFICAÇÃO
    cmap = colors.ListedColormap(['palegreen', '#FFE4B2', '#FFB2B2'])
    # LIMITES DA CLASSIFICAÇÃO
    bounds = [0, 21.6, 24.8, 60]
    N = 3
    norm = colors.BoundaryNorm(bounds, cmap.N)
    # PLOTANO O GRÁFICO TIPO PCOLOR
    ax.pcolormesh(
        tab.columns,
        alt,
        tab,
        cmap=cmap,
        norm=norm,
        edgecolors='white',
        linewidths=.1,
        shading='auto')
    ax.set_yticks(alt)
    ax.set_ylabel('Altitude (m)')
    # ax.tick_params(axis='y', labelsize=10, pad=5,
    #                which='both', labelright=True)
    # SETANDO OS LABELS DOS EIXOS X
    ax.set_xlim(forecast.index[0], forecast.index[-1])

    set_axis.plot_days_hours(ax)

    # VETORES
    set_axis.plot_vetores(
        xticks=plot.index,
        centro=[[0] * (len(plot.index))],
        u=u.values,
        v=v.values,
        clr='black')

    fig.savefig(
        f'{PATH}\\Rajada_prevista_{UCD}.png',
        format='png')
    plt.close('all')


def plot_data24h(wind, wave, curr, wkheight, PATH):
    '''
        plota dados do BD do OCEANOP

        :param wind: DataFrame Multiindex saída de OCNdb.get_BD
        :param wave: DataFrame Multiindex saída de OCNdb.get_BD
        :param curr: DataFrame Multiindex saída de OCNdb.get_BD
        :param wkheight: int ou float referente à altura de trabalho de
                         referência para conversão dos limites de vento
                         para 10 m
        :param PATH: string com diretório onde serão salvas as figuras
    '''
    for name, pplot in zip(['wind', 'wave', 'curr'], [wind, wave, curr]):
        if pplot.shape[0] >= 1:
            fig, ax = plt.subplots(
                len(pplot.columns),
                1,
                figsize=[8, 8],
                facecolor='w',
                sharex=True)
            # Laço para UCDs
            for i in np.unique(pplot.index.get_level_values(0)):
                plot = pplot.loc[i]
                # Laço por Instrumento
                for inst in np.unique(plot.index.get_level_values(0)):
                    iplot = plot.loc[inst]
                    if name == 'curr':
                        dep = np.unique(iplot.index.get_level_values(0))[0]
                        iplot = iplot.xs(dep)
                        leg = f"{i} ({inst} - {dep} m)"
                    else:
                        leg = f"{i} ({inst})"
                    # Laço por parâmetro / subplot
                    for sbpl, clname in enumerate(plot.columns):
                        time = iplot.index - timedelta(hours=3)
                        ax[sbpl].plot(
                            time,
                            iplot[clname],
                            marker='o',
                            label=leg)
                        if clname in ['WSPD', 'HCSP']:
                            ax[sbpl].set_ylabel(f'{acron(clname)[0]} (nós)')
                        else:
                            ax[sbpl].set_ylabel(
                                f'{acron(clname)[0]} ({acron(clname)[1]})')
                        ax[sbpl].legend(loc='upper right')
                        caxes.fmt_time_axis(ax[sbpl])
                        ax[sbpl].grid('on')
                        if clname in ['WDIR', 'HCDT', 'VPEDM']:
                            caxes.direction_yaxis(ax[sbpl])
                        ax[sbpl].set_xlim(time[0], time[-1])
            if name == 'wind':
                WND_LIM10 = [21.6, 24.8] / (1 + 0.137 * np.log(wkheight / 10.))
                ymin, ymax = ax[0].get_ylim()
                ax[0].fill_between(
                    time,
                    WND_LIM10[0],
                    WND_LIM10[1],
                    color='#FFE4B2',
                    alpha=.6)
                ax[0].fill_between(
                    time,
                    WND_LIM10[1],
                    60,
                    color='#FFB2B2',
                    alpha=.6)
                ax[0].set_ylim([ymin, ymax])
            fig.savefig(f'{PATH}\\{name}_24h.png', format='png')
