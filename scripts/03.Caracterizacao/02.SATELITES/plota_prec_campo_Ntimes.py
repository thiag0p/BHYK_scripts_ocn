'''
    Código para criação de mapa 2D de precipitação para a Bacia de Santos.
    Para executar o código, basta selecionar a pasta onde sertão salvas as
    imagens (PATH) e a data inicial de final de interesse (dd/mm/YYYY).

'''

# _____________________________________________________________________________
#                            Modificar aqui
# _____________________________________________________________________________
# Diretório onde serão salvas as imagens
PATH = (u"XXXXXXXXXXXX")
# Datas inicial e final de interesse
DATAINICIAL = '01/01/2019'
DATAFINAL = '01/02/2019'
# Caso queira criar um gif, usar gif=True
gif = True
# _____________________________________________________________________________
#                          funções e paths
# _____________________________________________________________________________

import matplotlib.cm as mcm
import xarray
from pandas import date_range
from datetime import datetime as dt
import numpy as np
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sys import path
import time as cronom
path.append('M:\\Rotinas\\python\\graph\\custom')
import colors
import ocnpylib
# Path e arquivos necessários para elaboração do mapa
shaps_path = 'XXXXXXXXXXXX'
coast_file = "ne_10m_coastline.shp"
bathy_file = ["ne_10m_bathymetry_K_200.shp",
              "ne_10m_bathymetry_J_1000.shp"]
ocean = "batim_area.shp"
lakes_file = "ne_10m_rivers_lake_centerlines.shp"
states = "Estados_BRt.shp"
logo = plt.imread(
    'XXXXXXXXXXXXXX.png')

# _____________________________________________________________________________
#                               DEFINIÇÕES
# _____________________________________________________________________________
# Fonte dos dados
opendap_link = (
    'http://XXXXXXXXXXXXXXXXXX')

# Cores
FGCOLORCST = (0.000, 0.075, 0.000)
BGCOLORCST = (0.000, 0.075, 0.000)
BGCOLORLKS = (0.100, 0.200, 0.275)
FGCOLORGRD = (0.500, 0.500, 0.500)
TXCOLORLGT = (0.900, 0.900, 0.900)
TXCOLORRGT = (0.700, 0.700, 0.300)
TXCOLORSCL = (0.700, 0.700, 0.700)
TXCOLORQNT = (0.700, 0.700, 0.300)

# Coordenadas
COORD = [-49.0, -42.166666666666664, -26.95, -22.404166666666665]

DATERANGE = date_range(
        dt.strptime(DATAINICIAL, '%d/%m/%Y'),
        dt.strptime(DATAFINAL, '%d/%m/%Y'),
        freq='D').to_pydatetime().tolist()
projection = ccrs.PlateCarree()

# Lendo shapes de batimetria
bat_lines = {}
for x, bat in enumerate(bathy_file):
    bat_lines[x] = cfeature.ShapelyFeature(
        Reader(shaps_path + bat).geometries(),
        ccrs.PlateCarree(),
        edgecolor='#d5d8dc',
        facecolor='none',
        linewidth=1)
# _____________________________________________________________________________
#                 Desenhando Mapa
# _____________________________________________________________________________


def makebackmap():
    """ ... """

    wcoord, ecoord, scoord, ncoord = COORD

    fig, ax = plt.subplots(
        figsize=(12, 8),
        subplot_kw=dict(projection=projection))
    # ax.stock_img()
    ax.set_extent([wcoord, ecoord, scoord, ncoord], crs=ccrs.PlateCarree())

    # Lendo linha de costa
    states_feature = cfeature.ShapelyFeature(
        Reader(shaps_path + states).geometries(),
        projection,
        facecolor=FGCOLORCST,
        edgecolor='gray',
        linewidth=0.5)
    lines_feature = cfeature.ShapelyFeature(
        Reader(shaps_path + states).geometries(),
        projection,
        facecolor='none',
        edgecolor='gray',
        linewidth=0.5)

    # ocean_feature = cfeature.ShapelyFeature(
    #     Reader(shaps_path + ocean).geometries(),
    #     projection)
    # lakes_feature = cfeature.ShapelyFeature(
    #     Reader(shaps_path + lakes_file).geometries(),
    #     projection,
    #     facecolor='none',
    #     edgecolor=BGCOLORLKS,
    #     alpha=0.6)
    ax.add_feature(states_feature, zorder=5)
    ax.add_feature(lines_feature, zorder=8)
    # ax.add_feature(ocean_feature, zorder=4)

    # Plota Batimetria
    for x in bat_lines.values():
        ax.add_feature(x)

    grids = ax.gridlines(
        crs=ccrs.PlateCarree(), draw_labels=True, zorder=8,
        linewidth=.5, color=FGCOLORGRD, alpha=0.5, linestyle='--')

    grids.xlabels_top = True
    grids.ylabels_left = True
    grids.xlabels_bottom = False
    grids.ylabels_right = False
    grids.xlines = True
    grids.xlocator = mticker.FixedLocator(np.linspace(-49.0, -42.12, 6))
    grids.ylocator = mticker.FixedLocator(np.linspace(-26.95, -22.4, 8))
    grids.xformatter = LONGITUDE_FORMATTER
    grids.yformatter = LATITUDE_FORMATTER
    grids.xlabel_style = {'size': 8.0, 'color': FGCOLORGRD}
    grids.ylabel_style = {'size': 8.0, 'color': FGCOLORGRD}

    pos = (0.19, 0.685, 0.170, 0.225)
    axl = fig.add_axes(
        pos, frameon=False, axisbelow=True, xticks=[], yticks=[])
    axl.imshow(logo)

    ax.text(
        pos[0] + 0.001, pos[1] + pos[3] / 3.25 - 0.002,
        'XXXXXXXXXXXXXXXXXX',
        alpha=0.5,
        fontsize=6.15,
        fontweight='bold',
        color=(0., 0., 0.),
        horizontalalignment='left',
        verticalalignment='center',
        transform=fig.transFigure,
        zorder=13)

    ax.text(
        pos[0], pos[1] + pos[3] / 3.25,
        'XXXXXXXXXXXXXXXXX',
        fontsize=6.15,
        fontweight='bold',
        color=TXCOLORLGT,
        horizontalalignment='left',
        verticalalignment='center',
        transform=fig.transFigure,
        zorder=13)

    ax.text(
        pos[0], pos[1] + pos[3] / 10.0,
        'BACIA DE SANTOS',
        fontsize=14.0,
        fontweight='bold',
        color=TXCOLORRGT,
        horizontalalignment='left',
        verticalalignment='center',
        transform=fig.transFigure,
        zorder=13)

    return fig, ax


def plot_ucds(ax):

    UCD_SELECT = ['XXXXXXXXXXXXXXXXXXXXXXXXX']
    UCDNAMES = ocnpylib.SECRET(
        ocnpylib.SECRET([8])) 
    UCDCOORD = ocnpylib.SECRET(
        ocnpylib.SECRET([8]))

    bbox_props = dict(boxstyle="round,pad=0.2", fc="w",
                      ec='black', alpha=.5)

    for u, ucd in enumerate(UCDNAMES):
        ax.plot(
            UCDCOORD[u][0],
            UCDCOORD[u][1],
            markersize=2,
            marker='o',
            markerfacecolor='black',
            markeredgecolor='black',
            markeredgewidth=0.5,
            linewidth=0,
            transform=projection,
            zorder=8)
        if ucd in UCD_SELECT:
            ax.annotate(
                ucd,
                xy=(UCDCOORD[u][0], UCDCOORD[u][1]),
                xytext=(-30, -5), textcoords='offset points',
                fontsize=4.5,
                transform=projection,
                arrowprops=dict(
                    arrowstyle='->',
                    color='k',
                    linewidth=.5),
                zorder=8)

# _____________________________________________________________________________
#                 Baixando e selecionando os dados de interesse
# _____________________________________________________________________________
# Lendo os dados
datasource = xarray.open_dataset(opendap_link)
# Selecionando área de interesse
selectdata = datasource.sel(
    latitude=slice(COORD[-2] - .5, COORD[-1] + .5),
    longitude=slice(COORD[0]- .5, COORD[1] + .5))

# _____________________________________________________________________________
#                               Plotando
# _____________________________________________________________________________

start = cronom.time()
for time in DATERANGE:

    fig, ax = makebackmap()

    timeslc = selectdata.sel(time=time, method=None).prec24h
    im = timeslc.where(timeslc>0).plot.contourf(
        ax=ax,
        transform=projection,
        cmap=mcm.get_cmap('cptsst'),
        levels=np.arange(0, 105, 1),
        extend='both',
        add_colorbar=False,
        zorder=6,
        add_labels=False)

    plot_ucds(ax)

    axcb = fig.add_axes(
        (0.19, 0.615, 0.18, 0.015),
        frameon=False, axisbelow=True, xticks=[], yticks=[])
    # cbticks = np.linspace(min, max, 11)
    cb = fig.colorbar(
        im, cax=axcb, ax=ax,
        ticks=np.arange(0, 105, 10),
        orientation='horizontal', use_gridspec=True, 
        extend='both', format='%.0f', drawedges=False)
        # ticks=cbticks, drawedges=params[u"edges"])
    cb.ax.tick_params(colors='w', labelsize=8)
    cb.set_label('mm', fontsize=8, color='w')
    cb.outline.set_edgecolor(TXCOLORSCL)
    cb.outline.set_linewidth(0.5)

    ax.text(
        0.19, 0.68,
        "Precipitação Hidroestimador [GPM]\nMosaico: {}".format(
            dt.strftime(time,'%d/%m/%Y')),
        alpha=0.5,
        fontsize=10.0,
        fontweight='normal',
        fontname='Arial',
        color=(0., 0., 0.),
        horizontalalignment='left',
        verticalalignment='center',
        multialignment='left',
        transform=fig.transFigure,
        zorder=13)

    ax.text(
        0.19 + 0.001, 0.68,
        "Precipitação Hidroestimador [GPM]\nMosaico: {}".format(
            dt.strftime(time,'%d/%m/%Y')),
        fontsize=10.0,
        fontweight='normal',
        fontname='Arial',
        color=TXCOLORQNT,
        horizontalalignment='left',
        verticalalignment='center',
        multialignment='left',
        transform=fig.transFigure,
        zorder=13)


    fig.savefig('{}\\BS_{}.png'.format(PATH, dt.strftime(time, '%Y-%m-%d')),
                format='png',
                bbox_inches='tight',
                dpi=300)
    plt.close()

print('Data Inicial: {} | Data Final: {} | Tempo: {} min'.format(
    dt.strftime(DATERANGE[0], '%d/%m/%Y'),
    dt.strftime(DATERANGE[-1], '%d/%m/%Y'),
    (cronom.time() - start) / 60)
)

# _____________________________________________________________________________
#                        Criando animação
# _____________________________________________________________________________
if gif is True:
    # CRIANDO GIF
    import os
    im = [i for i in os.listdir(PATH) if i.endswith('.png') is True]
    # Ordenando as imagens
    datas = [dt.strptime(x.split('_')[1].split('.')[0], '%Y-%m-%d') for x in im]
    datas.sort()
    # Create the frames
    frames = []
    for i in datas:
        arq = [x for x in im if dt.strftime(i, '%Y-%m-%d') in x][0]
        frames.append(Image.open("{}\\{}".format(PATH, arq)))
    # Save into a GIF file that loops forever
    frames[0].save('{}\\{}'.format(PATH, 'precipitacao.gif'), format='gif',
                append_images=frames[1:], save_all=True, duration=1000, loop=0)
