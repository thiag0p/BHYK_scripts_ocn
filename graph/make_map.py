import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, AnchoredText, OffsetImage
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = "Segoe ui"
plt.ioff()


def tmc(lonw, lats, ruler, ax, ymod):
    # Make tmc horizontally
    tmc = ccrs.TransverseMercator(lonw, lats + 5)

    # Get the extent of the plotted area in coordinates in metres
    x0, x1, y0, y1 = ax.get_extent(tmc)
    # Turn the specified scalebar location into coordinates in metres
    # Generate the x coordinate for the ends of the scalebar
    sbx_le = x0 + (x1 - x0) * 0.04
    sbx_mi = sbx_le + (ruler * 1000)  # scale bar x position 20 kilometer
    sby_top = y0 + (y1 - y0) * ymod + .005  # scale bar y position top
    sby_mid = y0 + (y1 - y0) * ymod  # scale bar y position center

    # Plot the scalebar
    ax.plot(
        [sbx_le, sbx_mi],
        [sby_mid, sby_mid],
        transform=tmc,
        c='k',
        lw=1,
        marker=2,
        ms=10)

    # Plot the scalebar label
    ax.text((
        sbx_le + sbx_mi) / 2,
        sby_top,
        f'{ruler} km',
        transform=tmc,
        c='k',
        size=7,
        ha='center',
        va='bottom')


def plot(lats, latn, lonw, lone):
    '''
        Plota mapa com imagens do servidor do arcgis

        :param lats:    float   Latitude norte em graus decimais
        :param latn:    float   Latitude sul em graus decimais
        :param lonw:    float   Longitude oeste em graus decimais
        :param lone:    float   Longitude leste em graus decimais
    '''
    SOURCE = '{}{}'.format(
        'Esri, GEBCO, NOAA, National Geographic, Garmin, HERE, Geonames.org,',
        'NGDC, and other contributors')
    URL = '{}{}'.format(
        'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Oc',
        'ean_Base/MapServer/tile/{z}/{y}/{x}')
    URL1 = '{}{}'.format(
        'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Oc',
        'ean_Reference/MapServer/tile/{z}/{y}/{x}')
    image = cimgt.GoogleTiles(url=URL)
    image1 = cimgt.GoogleTiles(url=URL1, desired_tile_form="RGBA")
    projection = image1.crs

    fig, ax = plt.subplots(
        figsize=(8.5, 11),
        dpi=300,
        subplot_kw={"projection": projection})

    ax.set_extent([lonw, lone, lats, latn])

    # Add Map
    ax.add_image(image, 10)
    ax.add_image(image1, 9)

    # Add map sources
    text = AnchoredText(SOURCE, loc=4, prop={'size': 7}, frameon=False)
    ax.add_artist(text)

    # Add gridlines in map
    gl=ax.gridlines(draw_labels=True, edgecolor='gray', linewidth=.75)
    gl.xlabel_style = {'size': 8,}
    gl.ylabel_style = {'size': 8,}


    return fig, ax


def bs():
    '''
        Plota mapa da Bacia de Santos
    '''

    SOURCE = '{}{}'.format(
        'Esri, GEBCO, NOAA, National Geographic, Garmin, HERE, Geonames.org,',
        'NGDC, and other contributors')
    URL = '{}{}'.format(
        'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Oc',
        'ean_Base/MapServer/tile/{z}/{y}/{x}')
    URL1 = '{}{}'.format(
        'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Oc',
        'ean_Reference/MapServer/tile/{z}/{y}/{x}')
    image = cimgt.GoogleTiles(url=URL)
    image1 = cimgt.GoogleTiles(url=URL1, desired_tile_form="RGBA")
    projection = image1.crs

    fig, ax = plt.subplots(
        figsize=(8.5, 11),
        dpi=300,
        subplot_kw={"projection": projection})

    lonw, lone, lats, latn = -47, -41, -27, -21
    ax.set_extent([lonw, lone, lats, latn])

    # Add Map
    ax.add_image(image, 10)
    ax.add_image(image1, 9)

    # Add map sources
    text = AnchoredText(SOURCE, loc=4, prop={'size': 7}, frameon=False)
    ax.add_artist(text)

    # Add gridlines in map
    gl=ax.gridlines(draw_labels=True, edgecolor='gray', linewidth=.75)
    gl.xlabel_style = {'size': 8,}
    gl.ylabel_style = {'size': 8,}

    tmc(lonw, lats, 50, ax, .05)

    return fig, ax


def bc():
    '''
        Plota mapa da Bacia de Santos
    '''
    SOURCE = '{}{}'.format(
        'Esri, GEBCO, NOAA, National Geographic, Garmin, HERE, Geonames.org,',
        'NGDC, and other contributors')
    URL = '{}{}'.format(
        'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Oc',
        'ean_Base/MapServer/tile/{z}/{y}/{x}')
    URL1 = '{}{}'.format(
        'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Oc',
        'ean_Reference/MapServer/tile/{z}/{y}/{x}')
    image = cimgt.GoogleTiles(url=URL)
    image1 = cimgt.GoogleTiles(url=URL1, desired_tile_form="RGBA")
    projection = image1.crs

    fig, ax = plt.subplots(
        figsize=(8.5, 11),
        dpi=300,
        subplot_kw={"projection": projection})

    lonw, lone, lats, latn = -42, -39, -24, -21
    ax.set_extent([lonw, lone, lats, latn])

    # Add Map
    ax.add_image(image, 10)
    ax.add_image(image1, 9)

    # Add map sources
    text = AnchoredText(SOURCE, loc=4, prop={'size': 7}, frameon=False)
    ax.add_artist(text)

    # Add gridlines in map
    gl=ax.gridlines(draw_labels=True, edgecolor='gray', linewidth=.75)
    gl.xlabel_style = {'size': 8,}
    gl.ylabel_style = {'size': 8,}

    tmc(lonw, lats, 30, ax, .05)

    return fig, ax


def bes():
    '''
        Plota mapa da Bacia de Santos
    '''

    SOURCE = '{}{}'.format(
        'Esri, GEBCO, NOAA, National Geographic, Garmin, HERE, Geonames.org,',
        'NGDC, and other contributors')
    URL = '{}{}'.format(
        'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Oc',
        'ean_Base/MapServer/tile/{z}/{y}/{x}')
    URL1 = '{}{}'.format(
        'https://server.arcgisonline.com/arcgis/rest/services/Ocean/World_Oc',
        'ean_Reference/MapServer/tile/{z}/{y}/{x}')
    image = cimgt.GoogleTiles(url=URL)
    image1 = cimgt.GoogleTiles(url=URL1, desired_tile_form="RGBA")
    projection = image1.crs

    fig, ax = plt.subplots(
        figsize=(8.5, 11),
        dpi=300,
        subplot_kw={"projection": projection})

    lonw, lone, lats, latn = -42, -39, -22, -20
    ax.set_extent([lonw, lone, lats, latn])

    # Add Map
    ax.add_image(image, 10)
    ax.add_image(image1, 9)

    # Add map sources
    text = AnchoredText(SOURCE, loc=4, prop={'size': 7}, frameon=False)
    ax.add_artist(text)

    # Add gridlines in map
    gl=ax.gridlines(draw_labels=True, edgecolor='gray', linewidth=.75)
    gl.xlabel_style = {'size': 8,}
    gl.ylabel_style = {'size': 8,}

    tmc(lonw, lats, 20, ax, .05)

    return fig, ax
