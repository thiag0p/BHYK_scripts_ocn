# -*- coding: utf-8 -*-
"""

"""
import glob as gb
import matplotlib.cm as mcm
import matplotlib.image as mimg
from os import path as osp
from numpy import flipud

# Diretório onde estão os pngs dos colorbars
IMGINPATH = ('M:\\Rotinas\\python\\graph\\color_bar')

# Cores/Colormaps Padrões ============================================ #
# ==================================================================== #

BGCOLORPLT = (1.000, 1.000, 1.000)  # fundo figura matplotlib (branco)
BGCOLOROCN = (0.200, 0.200, 1.000)  # fundo oceano (azul escuro)
BGCOLORCST = (0.000, 0.075, 0.000)  # fundo costa (verde escuro)
BGCOLORLKS = (0.100, 0.200, 0.275)  # fundo lagos (azul-cinza escuro)
BGCOLORUCD = (0.000, 0.000, 0.000)  # fundo UCDs inativas (preto)
BGCOLORUBX = (0.800, 0.800, 0.800)  # fundo caixa UCDs (cinza claro)
BGCOLORWRN = (0.500, 0.500, 0.500)  # fundo alerta (cinza escuro)
BGCOLORISB = (0.900, 0.900, 0.900)  # fundo caixa isbóbatas (cinza claro)
FGCOLORISB = (0.200, 0.200, 0.200)  # linhas isbóbatas (cinza escuro)
FGCOLORUCD = (0.200, 0.200, 0.200)  # borda UCDs inativas (cinza escuro)
FGCOLORCST = (0.000, 0.075, 0.000)  # borda costa (verde mata escuro)
FGCOLORGRD = (0.500, 0.500, 0.500)  # borda paralelos/meridianos (cinza)
TXCOLORSCL = (0.700, 0.700, 0.700)  # texto escala (cinza claro)
TXCOLORLGT = (0.900, 0.900, 0.900)  # texto logo (branco)
TXCOLORRGT = (0.700, 0.700, 0.300)  # texto região (amarelo)
TXCOLORGRD = (0.300, 0.300, 0.300)  # texto paralelos/meridianos (cinza)
TXCOLORUCD = (0.000, 0.000, 0.000)  # texto UCDs inativas (preto)
TXCOLORQNT = (0.700, 0.700, 0.300)  # texto grandezas (amarelo)
TXCOLORWRN = (1.000, 0.000, 0.000)  # texto alerta (vermelho)


def colormapreg_byimgfile(imgfile, quantlv=256, gamma=1.0):
    """ Criação/registro de colormap a partir de arquivo de imagem. """

    # Carregamento da imagem.
    img = mimg.imread(imgfile)

    # Exclusão do canal 'A (alpha) da composição RGBA (caso exista).
    if img.shape[-1] == 4:
        cmapcolors = img[:, 0, 0:-1]
    else:
        cmapcolors = img[:, 0, :]

    # Registro do colormap (sentido original).
    cmapname = osp.basename(imgfile).split('_')[0]
    mcm.datad[cmapname] = flipud(cmapcolors)

    mcm.register_cmap(cmap=mcm.colors.LinearSegmentedColormap.from_list(
        cmapname, mcm.datad[cmapname], quantlv, gamma))

    # Registro do colormap (sentido reverso).
    cmapname = osp.basename(imgfile).split('_')[0] + '_r'
    mcm.datad[cmapname] = cmapcolors

    mcm.register_cmap(cmap=mcm.colors.LinearSegmentedColormap.from_list(
        cmapname, mcm.datad[cmapname], quantlv, gamma))


# Registro de colormaps baseados nas imagens disponíveis.
imgfiles = gb.glob(
    osp.abspath(osp.join(IMGINPATH, "*_colorbar.png")))

for imgfile in imgfiles:
    colormapreg_byimgfile(imgfile)
