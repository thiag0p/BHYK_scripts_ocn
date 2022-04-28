'''
    Função que plota histograma seguindo padrão da MOP

    Data de criação: 26/04/2020
    Autor: Francisco Thiago Franca Parente (BHYK)
    Email: thiagoparente.AMBILEV@petrobras.com.br


'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
plt.ioff()


def escreve_valor_barra(xp, yp, values, ax, borda=1, size=8, disp=True):
    '''
        Função para escrita dos valores de cada barra no meio destas.

        * Argumentos___________________________________________________________
            xp      |   pontos no eixo x onde serão escritos os valores (list)
            yp      |   pontos no eixo y onde serão escritos os valores (list)
            values  |   valores que serão escritos (list)
            ax      |   eixo gráfico onde serão escritos
                    |   (matplotlib.pyplot.axes)
            borda   |   espessura da borda branca do texto (int)
            size    |   tamanho da fonte que será utilizada (int)
            disp    |   True ou False
                    |       True  - Não mostra valores de barras menores que 10
                    |       False - Mostra todos os valores
    '''

    texto1 = [
        '{0:2.1f}%'.format(x).replace('.', ',')
        for x in values]

    for x in range(len(xp)):
        if disp is True:
            if values[x] >= 10.:
                txt = ax.text(
                    xp[x],
                    yp[x],
                    texto1[x],
                    horizontalalignment='center',
                    fontsize=size)
                plt.setp(
                    txt,
                    path_effects=[
                        PathEffects.withStroke(
                            linewidth=borda,
                            foreground="w")])
        else:
            txt = ax.text(
                xp[x],
                yp[x],
                texto1[x],
                horizontalalignment='center',
                fontsize=size)
            plt.setp(
                txt,
                path_effects=[
                    PathEffects.withStroke(
                        linewidth=borda,
                        foreground="w")])


def comum(x, y, wd=.5, textb=3, leg=True, txtsize=8, ylim=None, disp=True):

    '''
        Cria hisograma comum com uma lista de tuples de x e y

        * Argumentos___________________________________________________________
            x       |   lista de tuples com os labels das sessões do histograma
                    |   e o xlabel de cada.
                    |   Ex.: [(xlabel1, xticklabels1),
                    |         (xlabel2, xticklabels2), ...]
            y       |   lista de tuples com o percentual de cada sessão x
            wd      |   espessura da barra do histograma
            textb   |   espessura da borda do texto que será escrito nas barras
            leg     |   True or False
                    |       True  - Exibe legenda para o gráfico
                    |       False - Não exibe legenda
            txtsize |   tamanho da fonte dos valores q serão escritos na barra
            ylim    |   limite superior o eixo y
            disp    |   True or False
                    |       True  - Não mostra valores de barras menores que 10
                    |       False - Mostra todos os valores
        * Edições______________________________________________________________
            + 13/07/2020
            Modificada a criação dos xlbls para o caso da direção. Felipe
            informou que os labels de direção estavam na forma "N-N, NE-NE.."
            + 26/10/2020
            Modificado os labels do xlbl, troca de '.' por ','.
            + 21/07/2021
            Adicionaa uma condicional para o set do ylim
    '''

    fig, ax = plt.subplots(len(x), 1, figsize=(12, 9))

    for splt in range(len(x)):
        try:
            axx = ax[splt]
        except Exception:
            axx = ax
        xtik = list(range(len(x[splt][1])))
        bot = np.zeros(len(xtik))
        bars = axx.bar(
            xtik,
            y[splt][1],
            wd,
            align='center',
            alpha=.7,
            edgecolor='k',
            bottom=np.nan_to_num(bot),
            label=y[splt][0])
        ty = y[splt][1] + .5
        escreve_valor_barra(
            xtik, ty, y[splt][1], axx, textb, txtsize, disp)
        plt.sca(axx)
        # criando xlabels
        if 'NE' in x[splt][1]:
            xlb = [
                '{}'.format(xl).replace('.', ',') for xl in x[splt][1]]
        else:
            xlb = [
                '{} - {}'.format(xl.split(' ')[0], xl.split(' ')[-1]).replace(
                    '.', ',')
                for xl in x[splt][1]]
            xlb[-1] = '\u2265 {}'.format(
                x[splt][1][-1].split(' ')[-1]).replace('.', ',')
        plt.xticks(xtik, xlb, fontsize=14)
        axx.set_xlim(0 - wd, xtik[-1] + wd)
        axx.set_ylabel('Registros (%)', fontsize=14)
        axx.set_xlabel(x[splt][0], fontsize=14)

        # setando ylim
        max = np.nanmax(y[splt][1])
        if ylim is not None and max < ylim:
            axx.set_ylim(0, ylim)

    if leg is True:
        fig.add_axes(
            [axx.get_position().get_points()[0, 0] / 2 + .25,
             axx.get_position().get_points()[0, 1], .2, .2],
            frameon=False,
            axisbelow=True,
            xticks=[],
            yticks=[])
        axx.legend(
            prop={'size': 14},
            bbox_to_anchor=(
                fig.axes[-1].get_position().get_points()[1, 0],
                fig.axes[-1].get_position().get_points()[0, 1] -
                (fig.get_size_inches()[0] / 60)),
            ncol=3,
            loc='center')
    return fig


def hist_nlevels(x, y, width=.5, pos='acima', legcol=3, btxt=1, txtsize=8):

    '''
        Cria histograma para o caso de ter mais de uma categoria por subplot.

        * Argumentos___________________________________________________________
            x       |   Lista
            y       |   Tuple
                    |
                    |   [ATENÇÃO!] y deve seguir a seguinte estrutura:
                    |       y = (
                    |           Subplot 1,
                    |           (
                    |               (Categoria 1, [y1, y2, y3, ...]),
                    |               (Categoria 2, [y1', y2', y3', ...],
                    |               ...)
                    |           Subplot 2,
                    |           (
                    |               (Categoria 1, [y1, y2, y3, ...]),
                    |               (Categoria 2, [y1', y2', y3', ...]),
                    |               ...)
            width   |   Espessura da barra do plot (int)
            pos     |   Posição onde serão dispostas as barras de categorias
                    |   diferentes, lado a lado ou acima uma da outra.
                    |   as opções são 'acima' ou 'lado'.
            legcol  |   Número de colunas da legenda
            btxt    |   Espessura da borda branca do texto escrito nas barras
            txtsize |   Tamanho da fonte do texto escrito nas barras

    '''

    if pos == 'lado':
        max_subplots = [
            [np.nanmax(y[sb][1][v][1]) for v in range(len(y[sb][1]))]
            for sb in range(len(y))]
        max_total = np.max(max_subplots)
    if pos == 'acima':
        val_subplots = [
            [y[sb][1][v][1] for v in range(len(y[sb][1]))]
            for sb in range(len(y))]
        max_list = []
        for i in range(len(val_subplots)):
            max_subplots = np.zeros(len(val_subplots[0][0]))
            for j in range(len(val_subplots[i])):
                max_subplots += val_subplots[i][j]
            max_list.append(max_subplots)
        max_total = np.max(max_list)

    fig, ax = plt.subplots(len(y), 1, figsize=(12, 9))

    subplots = [y[i][0] for i in range(len(y))]
    for sp, texto in enumerate(subplots):
        plot = y[sp][1]
        xtik = list(range(len(x)))
        bot = np.zeros(len(xtik))
        dx = -len(plot) / len(xtik)
        for categoria in range(len(plot)):
            yplot = plot[categoria][1]
            lbl_categoria = plot[categoria][0]
            if len(subplots) > 1:
                axx = ax[sp]
            else:
                axx = ax
            if pos == 'acima':
                bars = axx.bar(
                    xtik,
                    yplot,
                    width,
                    align='center',
                    alpha=.7,
                    edgecolor='k',
                    bottom=np.nan_to_num(bot),
                    label=lbl_categoria)
                # definindo ponto de escrita do percentual
                if bot.max() == 0:
                    ty = yplot / 2
                else:
                    ty = yplot / 2 + bot
                # definindo o início da barra
                bot += yplot
                # Colocando valores nas barras ________________________
                escreve_valor_barra(xtik, ty, yplot, axx, btxt, txtsize)
                # Escrevendo NAN para os meses que não tiverem dados
                for xp, na in enumerate(yplot):
                    if bool(np.isnan(na)) is True:
                        axx.text(
                            xp,
                            int((axx.get_ylim()[1] / 10) / 2),
                            'NaN',
                            fontsize=10,
                            horizontalalignment='center')

            elif pos == 'lado':
                bars = axx.bar(
                    [x + dx for x in xtik],
                    yplot,
                    width,
                    align='center',
                    alpha=.7,
                    edgecolor='k',
                    bottom=np.nan_to_num(bot),
                    label=lbl_categoria)
                dx += len(plot) / len(xtik)

                # Escrevendo NAN para os meses que não tiverem dados
                for xp, na in enumerate(yplot):
                    if bool(np.isnan(na)) is True:
                        axx.text(
                            [x+dx for x in xtik][xp],
                            int((axx.get_ylim()[1] / 10) / 2),
                            'NaN',
                            fontsize=10,
                            horizontalalignment='center')
            else:
                raise RuntimeError(
                    "Argumento 'pos' inválido! Deve ser 'acima' ou 'lado'")

        plt.sca(axx)
        plt.xticks(xtik, x, fontsize=14)
        axx.set_ylabel('Registros (%)', fontsize=14)
        axx.set_ylim(
            0,
            max_total + 2 * int(max_total / 10))

        if pos == 'acima':
            axx.set_xlim(0 - width, xtik[-1] + width)
        else:
            dx = width + 4/len(xtik)
            axx.set_xlim(0 - dx, xtik[-1] + dx)
        if len(subplots) > 1:
            axx.text(
                axx.get_xlim()[0] + .25,
                max_total + int(max_total / 10),
                '{}'.format(texto),
                fontsize=14)

        if sp == len(y) - 1:
            if len(y[0][1]) > 1:
                fig.add_axes([
                    axx.get_position().get_points()[0, 0] / 2 + .25,
                    axx.get_position().get_points()[0, 1],
                    .2,
                    .2], frameon=False, axisbelow=True, xticks=[], yticks=[])

                dy = (1 / axx.get_ylim()[1]) * 25
                axx.legend(
                    prop={'size': 14},
                    bbox_to_anchor=(
                        fig.axes[-1].get_position().get_points()[1, 0],
                        fig.axes[-1].get_position().get_points()[0, 1] - dy),
                    ncol=legcol,
                    loc='center')
    return fig
