import matplotlib.pyplot as plt


def color_backgroud(x, y1, y2, ax):
    '''
        Pinta fundo do gráfico

        :param x: xticks
        :param y1: ylim inferior
        :param y2: ylim superior
        :param ax: axis eixo do gráfico
    '''
    ax.fill_between(
        x, y1, y2,
        facecolor='#FFE4B2', edgecolor='#FFE4B2', alpha=0.7)
    ax.fill_between(
        x, y2, 100,
        facecolor='#FFB2B2', edgecolor='#FFE4B2', alpha=0.7)


def escreve_valores(ax, xi, values, sfmt, dy, clr):
    '''
        Escreve os valores dos pontos ao longo da série

        :param ax: eixo do gráfico
        :param xi: xticks
        :param values: valores dos pontos que serão escritos
        :param sfmt: formato da string de saída
        :param dy: distância do ponto para a escrita
        :param clr: cor da fonte
    '''
    texto = ['{:{fmt}}'.format(x, fmt=sfmt).replace('.', ',') for x in values]
    for xx, x in enumerate(xi):
        ax.text(
            x, values[xx] + dy,
            texto[xx],
            horizontalalignment='center',
            fontsize=8,
            color=clr)
