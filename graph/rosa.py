'''
    Função que plota rosa de distribuição seguindo padrão da MOP

    Data de criação: 15/05/2020
    Autor: Francisco Thiago Franca Parente (BHYK)
    Email: thiagoparente.AMBILEV@petrobras.com.br

'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import math
# from windrose import WindroseAxes
import matplotlib.patches as mpatches
plt.ioff()


def new_rose(spd, dir, spd_bins, rlim, unid, fmt='.1f'):

    '''
        Cria gráfico de barras polar / rosa de distribuição

        * Argumentos___________________________________________________________
            spd     |   array com valores de intensidade
            dir     |   array com valores de direção
            spd_bins|   Intervalos de interesse da intensidade
            rlim    |   limite do raio da rosa
            unid    |   unidade de medida da intensidade
            fmt     |   formato do string dos valores de intensidade da legenda
        * Edições______________________________________________________________

    '''
    if spd_bins[-1] / 10 > .2:
        deltalbl = .1
    else:
        deltalbl = .01

    spd_bins = np.append(spd_bins, spd_bins[-1] * 10)
    dir_bin = np.arange(-22.5, 337.6, 45)

    # Ajustando direções no caso do Norte
    dir[dir >= 337.5] = dir[dir >= 337.5] - 360

    # Ocorrência do vento binado.
    fig0, ax0 = plt.subplots()
    counts, xedges, yedges, _ = ax0.hist2d(dir, spd, bins=[dir_bin, spd_bins])
    # calculando percentual
    counts = (counts / len(spd)) * 100
    # somando para sobreposição de barras
    ncounts = np.hstack(
        (np.zeros((counts.shape[0], 1)), counts)).cumsum(axis=1)

    # Selecionando cores do colormap.
    interval = np.linspace(.1, .95, len(yedges))
    colors = [plt.cm.jet(i) for i in interval]

    fig_kw = dict(figsize=(13, 11), facecolor='white')
    subplot_kw = dict(polar=True)
    fig, ax = plt.subplots(subplot_kw=subplot_kw, **fig_kw)
    ax.set_axisbelow(True)
    ax.grid(
        b=True, axis='both', which='major', color='k',
        linestyle='--', linewidth=1.2, alpha=.5)
    # fig.suptitle(suptitle, y=.99, fontsize=15, fontweight='semibold')
    # _ = ax.set_title(title, fontsize=12)

    # Mudando para direção horária
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("N")
    angles = np.arange(0., 360., 45)
    _, __ = ax.set_thetagrids(angles, fontweight='semibold')
    theta = np.radians(dir_bin + 22.5)
    for i in range(len(dir_bin) - 1):
        for j in range(len(spd_bins) - 1):
            left, width = theta[i], theta[i + 1] - theta[i]
            height, bottom = ncounts[i, j + 1] - ncounts[i, j], ncounts[i, j]
            if height > 0.:
                ax.bar(
                    left, height, width=width, bottom=bottom,
                    facecolor=colors[j], edgecolor='white', linewidth=1,
                    alpha=.9)

    # Escrevendo raios dos valores percentuais
    ax.set_xticklabels([
        'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
        dict(fontsize=15))
    ax.set_rlabel_position(-68.)
    ax.set_yticks(np.arange(0, 100, 20))
    sum_direc = [x.sum() for x in counts]
    maxr = np.nanmax(sum_direc)
    if maxr < rlim:
        ax.set_ylim(0, rlim)
    else:
        ax.set_ylim(0, maxr + 3)
    yticklabels = [int(label) for label in ax.get_yticks()]
    for i, yticklabel in enumerate(yticklabels):
        if i != 0:
            yticklabels[i] = '{}%'.format(str(yticklabels[i]))
        _ = ax.set_yticklabels(
            yticklabels, dict(
                horizontalalignment='right', fontsize=20,
                verticalalignment='bottom', zorder=2))
    # Criar labels para legenda.
    labels = [
        ('{:{ft}} - {:{ft}} {}'.format(
            spd_bins[i] + deltalbl, spd_bins[i + 1], unid, ft=fmt)).replace(
                '.', ',')
        for i in range(len(spd_bins) - 2)]
    labels.append('\u2265 {:{ft}} {}'.format(
        spd_bins[-2] + deltalbl, unid, ft=fmt).replace('.', ','))
    # Criar patch da legenda, atualizar handles e labels.
    patch_legend = [mpatches.Patch(color=colors[i], alpha=.9, label=label)
                    for i, label in enumerate(labels)]
    handles, _ = ax.get_legend_handles_labels()
    handles.append(patch_legend)
    legend = ax.legend(
        handles[0], labels, bbox_to_anchor=(-.05, -.13),
        loc='lower left', scatterpoints=1, ncol=4,
        title=u'', fancybox=True, borderaxespad=.2, fontsize=15)
    frame = legend.get_frame()
    frame.set_color('w')
    frame.set_edgecolor('#808080')

    return fig


# def rose(inte, dire, bins, nsector, ylim, unid, paramlbl, fmt='.1f'):

#     def ini_fim(tick):
#         if tick[-1]/10 > .2:
#             ibusca, fbusca, lbl = .05, .04, .1
#         else:
#             ibusca, fbusca, lbl = .005, .004, .01
#         return ibusca, fbusca, lbl
#     try:
#         fig = plt.figure(figsize=[4., 4.])
#         rect=[1,1,.8,.8]
#         ax = WindroseAxes(fig, rect)
#         fig.add_axes(ax)
#         ax.bar(
#             dire, inte, bins=bins, normed=True,
#             nsector=nsector, cmap=plt.get_cmap('jet'))
#         ax.set_xticklabels(['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'])
#         for label in ax.xaxis.get_majorticklabels():
#             label.set_fontsize(9)
#         ax.set_ylim([0, ylim])
#         ax.yaxis.set_ticks(range(20, ylim, 20))
#         ax.set_yticklabels(['' for x in range(20, ylim, 20)])
#         for label in ax.yaxis.get_majorticklabels():
#             label.set_fontsize(7)
#         # Text formatting
#         text = ['{0:.1f}'.format(round(x, 2)) + '%'
#                 for x in range(20, ylim, 20)]

#         for x, values in enumerate(range(20, ylim, 20)):
#             txt = ax.text(
#                 157.5 * np.pi / 180,
#                 values,
#                 text[x],
#                 horizontalalignment='center')
#             plt.setp(
#                 txt,
#                 path_effects=[PathEffects.withStroke(
#                     linewidth=3,
#                     foreground="w")])

#         # # creating legend
#         leg =[]
#         for x, i in enumerate(bins):
#             deltai, deltaf, ilbl = ini_fim(bins)
#             if x != len(bins)-1:
#                 leg.append('{:{ft}} - {:{ft}}'.format(
#                     i+ilbl, bins[x+1], ft=fmt))
#             else:
#                 leg.append('{} \u2265 {:{ft}}'.format(
#                     paramlbl, i+ilbl, ft=fmt))

#         ncols = len(bins)/2. + 1.

#         lgd = ax.legend(ncol=math.floor(ncols),  loc='center',
#                         decimal_places=2,
#                         frameon=False, bbox_to_anchor=(0.5, -0.2),
#                         prop={'size': 9},
#                         title="({})".format(unid),
#                         title_fontsize=10)
#         lgd._legend_box.align = "left"
#         for l in range(len(lgd.get_texts())):
#             lgd.get_texts()[l].set_text(leg[l])
#     except:
#         raise RuntimeError("Check as variáveis.")

#     return fig
