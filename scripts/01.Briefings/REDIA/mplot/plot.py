import cartopy.crs as ccrs
import matplotlib.cm as mcm
import numpy as np
import matplotlib.pyplot as plt
from pandas import to_datetime
from sys import path
path.append('M:\\Rotinas\\python\\graph')
from custom import colors


def tsm(data, ax, addtitle):
    '''
    Plota dados de TSM.

    :param data: xarray com dados de TSM.
    :param ax: eixo grafico que será inserida a TSM.
    :param addtitle: str texto para inclusão no titulo da fig
    '''
    im = data.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap=mcm.get_cmap('cptsst'),
        levels=np.arange(19, 32.1, .1),
        ticks=np.arange(19, 32.1, 2),
        extend='both',
        add_colorbar=False)
    ax.set_title('')
    im.set_clim(19, 32)

    # Setando o colorbar
    # cbar = plt.colorbar(
    #     im, ticks=[19, 21, 23, 26, 28, 30, 32])
    # cbar.ax.set_ylabel('Temperatura', fontsize=16)
    ax.set_title(
        'Data TSM: {}\n{}'.format(
            to_datetime(data.time.values).strftime('%d/%m/%Y'),
            addtitle),
        loc='right', pad=20)


def allucds(ucds, ax):
    '''
    Plota todas as ucds no mapa

    :param ucds: multiindex com informações das ucds
    :param ax: eixo do mapa utilizado para plot
    '''
    for ucd in ucds.index.get_level_values(0):
        ax.plot(
            ucds.loc[ucd].lon.values[-1],
            ucds.loc[ucd].lat.values[-1],
            transform=ccrs.PlateCarree(),
            marker='o',
            markersize=2,
            color='k')


def ucds_curr(data, ucdsinf, ax):
    '''
    Plota ucds com sensor de corrente operacional, colorindo de verde as que
    não registraram corrente acima de 1,0 nó e de vermelho as que registraram.

    :param data:    DataFrame com os dados de corrente
    :param ucdsinf: DataFrame com as informações geográficas das ucds
    :param ax:      Eixo do mapa onde será plotado. 
    '''
    # Pegando os valores máximos medidos
    maxd = data.groupby('DS_MISSION').agg({'HCSP': ['max']})
    for ucd in maxd.index:
        maxx = float(maxd[maxd.index == ucd].values[0])
        if maxx >= 1:
            color = '#e74c3c'
        else:
            color = '#2ecc71'
        x, y = ucdsinf.loc[ucd].lon.values[-1], ucdsinf.loc[ucd].lat.values[-1]
        ax.plot(
            x,
            y,
            transform=ccrs.PlateCarree(),
            marker='o',
            markerfacecolor='w',
            markeredgecolor=color,
            markeredgewidth=3,
            markersize=8)
        xx, yy = ax.projection.transform_point(
            x + .05,
            y,
            src_crs=ccrs.PlateCarree())
        ax.annotate(
            ucd,
            xy=(xx, yy),
            ha='left',
            va='top',
            color='k')


def inf_box(ax, points, data, scale):
    '''
    Plota no mapa as informações sobre as ucds que apresentaram corrente acima
    de 1.0 nó.

    :param ax:  eixo gráfico do mapa
    :param points: list -   lista com os valores de referencia para o plot no
                            mapa [X, Y, dx, dy]
    :param data:   DataFrame -  DataFrame com os dados de corrente
    :param scale:  int - escala para plot do vetor no mapa
    '''

    X, Y, dx, dy = points
    X, Y = map(np.asanyarray, ([X], [Y]))
    # Laço por UCD
    for ucd in data.index.to_list():
        slc = data[data.index == ucd]
        U, V = map(np.asanyarray, (slc.u, slc.v))
        # Normalizando U e V
        U = U / np.sqrt(U**2 + V**2)
        V = V / np.sqrt(U**2 + V**2)

        TEXT = '{:10.10s}    {:1.2f}'.format(ucd, slc['max.'].values[0])
        ax.quiver(
            X,
            Y,
            U,
            V,
            transform=ccrs.PlateCarree(),
            angles='uv',
            scale=scale,
            width=.008,
            headwidth=3.,
            headlength=2.5,
            headaxislength=2.5,
            pivot='mid')

        xt, yt = ax.projection.transform_point(
            X + dx, Y, src_crs=ccrs.PlateCarree())
        ax.annotate(
            TEXT,
            xy=(xt, yt),
            ha='left',
            va='center',
            color='k',
            fontsize=15,
            fontweight='bold')
        Y -= dy
