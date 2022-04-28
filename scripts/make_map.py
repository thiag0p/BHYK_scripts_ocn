'''
    Rotina de elaboração de mapa para unidades.

    Autor: Francisco Thiago Franca Parente (BHYK)
    Data de criação: 20/04/2020

'''
# _____________________________________________________________________________
#                               MODIFICAR AQUI
# _____________________________________________________________________________

# Path de saída da imagem do mapa
PATH = ("XXXXXXXXXXXXXXXXXXXXXX")

# UCD QUE SERÁ IMPRESSA NO MAPA
UCDS = ['P-35', 'P-40', 'P-19', 'P-18']

# Bacia de exploração onde a UCD está inserida
BACIA = 'Bacia de Campos'
# _____________________________________________________________________________
#                          Bibliotecas utilizadas
# _____________________________________________________________________________

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
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
# Definindo projeção
projection = ccrs.PlateCarree()
# Path e arquivos necessários para elaboração do mapa
shps_path = (
    'XXXXXXXXXXXXXXXX')
imge_path = (
    'XXXXXXXXXXXXXXXXXXXXX')
coast_file = "ne_10m_coastline.shp"
lakes_file = "ne_10m_rivers_lake_centerlines.shp"
bathy_file = "batim_area.shp"

# Lendo shape da linha de costa
coast_feature = cfeature.ShapelyFeature(
    Reader(shps_path + coast_file).geometries(),
    projection,
    facecolor='w',
    edgecolor='#d5d8dc',
    linewidth=1)
# Lendo shape dos rios
lakes_feature = cfeature.ShapelyFeature(
    Reader(shps_path + lakes_file).geometries(),
    projection,
    facecolor='none',
    edgecolor='#d5d8dc',
    linewidth=.5)
# Lendo shape de batimetria
bathymetry = Reader(shps_path + bathy_file)
# _____________________________________________________________________________
#                          Definições gráficas
# _____________________________________________________________________________
# Definindo cores do oceano
ocean_colors = {-5.: '#1fc1c3', -100.: '#1fb2c3', -300.: '#1fa3c3',
                -600.: '#1f94c3', -900.: '#1f76c3', -1200.: '#1f67c3',
                -1500.: '#1f49c3', -1800.: '#1f2ec3', -2100.: '#261fc3',
                -2400.: '#201aa5', -2700.: '#191489', -3000.: '#130f68'}
boundaries = {
    "Bacia de Campos": [-42, -39, -21, -24],
    "Bacia de Santos": [-47, -41, -21, -27],
    "Bacia do Espírito Santo": [-42, -39, -20, -22]}

# _____________________________________________________________________________
#                               Plotando
# _____________________________________________________________________________
#COORD = boundaries[BACIA]
COORD = [-40.4, -39.8, -22.2, -22.8]
# Elaborando Mapa
fig, ax = plt.subplots(
    figsize=(12, 8),
    subplot_kw=dict(projection=projection))
ax.set_extent(COORD)

ax.add_feature(coast_feature, zorder=0, color='k')
ax.add_feature(lakes_feature, zorder=0)

# Desenhando linhas de lat e lon
gl = ax.gridlines(draw_labels=True, color='w', linestyle='--')
gl.xlabels_top = False
gl.ylabels_right = False

# Formatando os labels de lon e lat
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

# Plotando isolinhas
for x in bathymetry.records():
    if x.attributes['PROFUNDIDA'] in ocean_colors.keys():
        deepocean = cfeature.ShapelyFeature(
            x.geometry,
            projection,
            facecolor=ocean_colors[x.attributes['PROFUNDIDA']],
            edgecolor='#d5d8dc',
            linewidth=1)
        ax.add_feature(deepocean, alpha=.6, zorder=1)

        # valid_geoms = x.geometry
        # square = Polygon([(COORD[0], COORD[2]), (COORD[1], COORD[2]),
        #                 (COORD[1], COORD[3]), (COORD[0], COORD[3])])
        # ref_point = Point(COORD[0], COORD[3] + 1)
        # intersect = square.intersection(valid_geoms[0].buffer(0))        
        # p1, _ = nearest_points(intersect, ref_point)
        # txt = ax.text(
        #     *tuple(p1.coords)[0], '{} m'.format(x.attributes['PROFUNDIDA']),
        #     verticalalignment='center', horizontalalignment='center',
        #     fontsize=10, rotation=40,
        #     bbox=dict(facecolor='white', edgecolor='none', alpha=0.3))
        # plt.setp(
        #     txt,
        #     path_effects=[PathEffects.withStroke(
        #         linewidth=2,
        #         foreground='w')])

# Plotando posição e nome da UCD
for ucd in UCDS:
    # Pegando informações geográficas da(s) UCD(s)
    lon, lat = ocn.SECRET(ocn.SECRET(ucd))
    points = ax.projection.transform_point(lon,
                                           lat,
                                           src_crs=projection)
    at_x, at_y = points[0], points[1]
    plt.plot(at_x,
            at_y,
            markersize=8,
            marker='o',
            markerfacecolor='white',
            markeredgecolor='black',
            markeredgewidth=3,
            linewidth=0,
            transform=projection)
    bbox_props = dict(boxstyle="round,pad=0.2", fc="w",
                    ec='w', alpha=.5)
    txt = ax.annotate(ucd,
                    xy=(at_x + .05, at_y),
                    ha='left', va='top', fontsize=14,
                    color='k', bbox=bbox_props)
    plt.setp(txt,
            path_effects=[PathEffects.withStroke(linewidth=2,
                                                foreground='w')])

# Plotando logo da Petrobras/Oceanop
star = plt.imread(imge_path + 'windrose.png')
fig.add_axes(
    [.235, .1, 0.17, 0.17], frameon=False, axisbelow=True,
    xticks=[], yticks=[])
fig.axes[-1].imshow(star)
# [.76, .7, 0.2, 0.07]
# Plotando logo da Petrobras/Oceanop
logo = plt.imread(imge_path + 'br_oceanop_logo.png')
fig.add_axes(
    [
        fig.axes[0].get_position().get_points()[0, 0] - 0.0105,
        1 - (1 - fig.axes[0].get_position().get_points()[1, 1]) +
        0.01, 0.2, 0.07],
    frameon=False, axisbelow=True,
    xticks=[], yticks=[])
fig.axes[-1].imshow(logo)

fig.savefig(PATH + '\\mapa.png',
            format='png',
            bbox_inches='tight',
            dpi=300)
