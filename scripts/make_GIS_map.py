'''
    Rotina de elaboração de mapa para unidades.

    Autor: Francisco Thiago Franca Parente (BHYK)
    Data de criação: 20/04/2020

'''
# _____________________________________________________________________________
#                               MODIFICAR AQUI
# _____________________________________________________________________________

# Path de saída da imagem do mapa
PATH = ("XXXXXXXXXXXXXXXXXXXXXXX")

# UCD QUE SERÁ IMPRESSA NO MAPA
UCDS = ['XXXXXXXXXXXXXXXXXXX']

# Bacia de exploração onde a UCD está inserida
BACIA = 'Bacia de Campos'
# _____________________________________________________________________________
#                          Bibliotecas utilizadas
# _____________________________________________________________________________

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, AnchoredText, OffsetImage
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature, NaturalEarthFeature
from shapely.geometry import Polygon, Point
from shapely.ops import nearest_points
import matplotlib.patheffects as PathEffects
import matplotlib.patches as mpatches
import matplotlib.cm as mcm
from pandas import DataFrame
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from sys import path
import ocnpylib as ocn
import numpy as np

# _____________________________________________________________________________
#                 Definição e leitura dos shapes para mapa
# _____________________________________________________________________________
imge_path = 'XXXXXXXXXXXXXXXXXXXX'
SOURCE = 'Esri, GEBCO, NOAA, National Geographic, Garmin, HERE, Geonames.org, NGDC, and other contributors'
url = 'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}'
url1 = 'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}'

image = cimgt.GoogleTiles(url=url)
image1 = cimgt.GoogleTiles(url=url1, desired_tile_form="RGBA")
p = image1.crs
projection = ccrs.PlateCarree()

# _____________________________________________________________________________
#                          Definições gráficas
# _____________________________________________________________________________
# Definindo cores do oceano
boundaries = {
    "Bacia de Campos": [-42, -39, -21, -24],
    "Bacia de Santos": [-47, -41, -21, -27],
    "Bacia do Espírito Santo": [-42, -39, -20, -22]}

# _____________________________________________________________________________
#                               Plotando
# _____________________________________________________________________________
COORD = boundaries[BACIA]
# Definindo projeção
projection = ccrs.PlateCarree()

# Elaborando Mapa
fig, ax = plt.subplots(
    figsize=(12, 8),
    subplot_kw=dict(projection=projection))
ax.set_extent(COORD)
ax.add_image(image, 10)
ax.add_image(image1, 9)

#Add map sources
text = AnchoredText(SOURCE, loc=4, prop={'size': 7}, frameon=False)
ax.add_artist(text)

# Desenhando linhas de lat e lon
gl = ax.gridlines(draw_labels=True, color='w', linestyle='--')
gl.xlabel_style = {'size': 8}
gl.ylabel_style = {'size': 8}
gl.xlabels_top = False
gl.ylabels_right = False

# Formatando os labels de lon e lat
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

# Make tmc horizontally centred on the middle of the map,
tmc = ccrs.TransverseMercator(
    (COORD[0] + COORD[1]) / 2, (COORD[1] + COORD[2]) / 2)
# Get the extent of the plotted area in coordinates in metres
x0, x1, y0, y1 = ax.get_extent(tmc)
# Turn the specified scalebar location into coordinates in metres
# Generate the x coordinate for the ends of the scalebar
sbx_le = x0 + (x1 - x0) * 0.1
sbx_mi = sbx_le + 20000  # scale bar x position 20 kilometer
sbx_ri = sbx_le + 37040  # scale bar x position 20 nautical miles
sby_top = y0 + (y1 - y0) * 0.08  # scale bar y position top
sby_mid = y0 + (y1 - y0) * 0.07  # scale bar y position center
sby_bot = y0 + (y1 - y0) * 0.04  # scale bar y position bottom

# Plot the scalebar
ax.plot(
    [sbx_le, sbx_mi], [sby_mid, sby_mid],
    transform=tmc, c='k', lw=1, marker=2, ms=10)
ax.plot(
    [sbx_le, sbx_ri], [sby_mid, sby_mid],
    transform=tmc, c='k', lw=1, marker=3, ms=10)
# Plot the scalebar label
ax.text(
    (sbx_le + sbx_mi) / 2, sby_top, '20 km',
    transform=tmc, c='k', size=8, ha='center', va='bottom')
ax.text(
    (sbx_le + sbx_ri) / 2, sby_bot, '20 nm',
    transform=tmc, c='k', size=8, ha='center', va='bottom')

# Plotando posição e nome da UCD
for ucd in UCDS:
    # Pegando informações geográficas da(s) UCD(s)
    lon, lat = ocn.SECRET(ocn.SECRET(ucd))
    points = ax.projection.transform_point(lon,
                                           lat,
                                           src_crs=projection)
    at_x, at_y = points[0], points[1]
    plt.plot(
        at_x,
        at_y,
        markersize=8,
        marker='o',
        markerfacecolor='white',
        markeredgecolor='black',
        markeredgewidth=3,
        linewidth=0,
        transform=projection)
    bbox_props = dict(
        boxstyle="round,pad=0.2", fc="w",
        ec='w', alpha=.5)
    txt = ax.annotate(
        ucd,
        xy=(at_x + .05, at_y),
        ha='left', va='top', fontsize=14,
        color='k', bbox=bbox_props)
    plt.setp(
        txt,
        path_effects=[PathEffects.withStroke(
            linewidth=2,
            foreground='w')])

# Plotando logo da Petrobras/Oceanop
star = plt.imread(imge_path + 'windrose.png')
fig.add_axes(
    [.627, .715, 0.17, 0.17], frameon=False, axisbelow=True,
    xticks=[], yticks=[])
fig.axes[-1].imshow(star)
# [.76, .7, 0.2, 0.07]
# Plotando logo da Petrobras/Oceanop
logo = plt.imread(imge_path + 'oceanop_logo.png')
fig.add_axes(
    [
        fig.axes[0].get_position().get_points()[0, 0] - 0.0105,
        1 - (1 - fig.axes[0].get_position().get_points()[1, 1]) +
        0.01, 0.2, 0.07],
    frameon=False, axisbelow=True,
    xticks=[], yticks=[])
fig.axes[-1].imshow(logo)

# fig.savefig(PATH + '\\mapa.png',
#             format='png',
#             bbox_inches='tight',
#             dpi=300)
