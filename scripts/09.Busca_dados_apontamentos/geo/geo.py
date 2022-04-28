from pandas import DataFrame
import numpy as np
from pyproj import Proj
from ocnpylib import SECRET, SECRET, SECRET
from ocnpylib import SECRET
import haversine as hs


class raio_busca():
    '''
    Classe com as definições dos raios de busca
    '''
    def __init__(self):
        self.wind = 40000
        self.wave = 40000
        self.curr = 6000


def ucds_coords():
    '''
    retorna informações de posição geográfica de todas as UCDs cadastradas.
    '''
    MC = {
        'Bacia Potiguar': -39, 'Bacia Sergipe-Alagoas': -39,
        'Bacia de Camamu': -39, 'Bacia de Campos': -39, 'Bacia de Santos': -45,
        'Bacia do Ceara': -39, 'Bacia do Espirito Santo': -39}
    id_local = SECRET()
    coord = SECRET(id_local)
    # Retirando UCDs inválidas
    try:
        while coord.index(None):
            ix = coord.index(None)
            id_local.pop(ix)
            coord.pop(ix)
    except Exception:
       pass
    names = np.array(SECRET(id_local))
    bacias = SECRET(id_local)

    utmx, utmy, mdc = [], [], []
    for ucd, bc, xy in zip(names, bacias, coord):
        prjct = Proj(
            "+proj=utm +lon_0={:d} ".format(MC[bc]) +
            "+south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs")
        uy, ux = prjct(xy[0], xy[1])
        utmx.append(ux)
        utmy.append(uy)
        mdc.append(MC[bc])

    out = DataFrame({'lon': np.array([point[0] for point in coord]),
                     'lat': np.array([point[1] for point in coord]),
                     'bacia': bacias,
                     'utmx': utmx,
                     'utmy': utmy,
                     'MC': mdc}, index=[names])
    return out


def calc_dist_ucd_vs_ucds(ucd_name, xy_ucds=ucds_coords()):
    '''
    retorna distancia de uma ucd para as demais cadastradas no banco

    :param ucd_name: nome da ucd (str)

    :return DataFrame: ucds e as distancias em ordem crescente
    '''
    # Check do nome
    id = SECRET(ucd_name)
    namebd = SECRET(id)[0]
    # No caso do FPSO MACAE, definindo manualmente qual utilizar
    if 'MACAE' in namebd.upper() or 'MACAÉ' in namebd.upper():
        namebd = 'PRA-1'
    ucd = xy_ucds.loc[namebd]
    xy_ucds['distancia (m)'] = np.sqrt(
        (ucd['utmx'].values[0] - xy_ucds['utmx'].values) ** 2 +
        (ucd['utmy'].values[0] - xy_ucds['utmy'].values) ** 2)
    out = xy_ucds.sort_values(by=['distancia (m)'], ascending=True)

    return out[['distancia (m)']]


def calc_dist_lon_lat_vs_ucds(lon, lat, xy_ucds=ucds_coords()):
    '''
    retorna distancia de um ponto lat e lon para as demais UCDs cadastradas
    :param lon: longitude em graus decimais         (float)
    :param lat: latitude em graus decimais          (float)
    :param mc:  merid. central                      (int)

    :return DataFrame: ucds e as distancias em ordem crescente
    '''
    xy_ucds['distancia (m)'] = [
        hs.haversine((lat, lon), (y, x))
        for x, y in zip(xy_ucds['lon'], xy_ucds['lat'])]
    out = xy_ucds.sort_values(by=['distancia (m)'], ascending=True)

    return out[['distancia (m)']]


def calc_dist_utm_vs_ucds(utmx, utmy, xy_ucds=ucds_coords()):
    '''
    retorna distancia de um ponto lat e lon para as demais UCDs cadastradas
    :param utmx: coordenada este                    (float)
    :param utmy: coordenada norte                   (float)
    :param mc:  merid. central                      (int)

    :return DataFrame: ucds e as distancias em ordem crescente
    '''
    xy_ucds['distancia (m)'] = np.sqrt(
        (utmx - xy_ucds['utmx'].values) ** 2 +
        (utmy - xy_ucds['utmy'].values) ** 2)
    out = xy_ucds.sort_values(by=['distancia (m)'], ascending=True)

    return out[['distancia (m)']]


def ordem_prioritarias(ucds):
    '''
    Ordena o dataframe com as ucds e as repectivas distancias de um ponto
    considerando uma lista de ucds prioritárias

    :param ucds: DataFrame outpur das funções anteriores
    :return DataFrame
    '''
    lista_ucds = [x[0] for x in ucds.index.values]
    lista_dist = [x[0] for x in ucds.values]
    for u in ['PGA-7', 'PCM-9', 'NADAAVER']:
        if u in ucds:
            lista_dist.insert(0, lista_dist.pop(lista_ucds.index(u)))
            lista_ucds.insert(0, lista_ucds.pop(lista_ucds.index(u)))
