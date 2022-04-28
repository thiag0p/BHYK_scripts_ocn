from ocnpylib import SECRET1, SECRET2
from sys import path as syspath
import numpy as np
syspath.append('xxxxxxxxxxxxxx')
from geo import geo
from re import search


def ucds_validas(ucds=None):

    '''
    Retorna lista de UCDs válidas para busca de dados

    :param ucds: lista de ucds de interesse         (list)

    :return list
    '''
    estacoes_invalidas = [
        'EDINC', 'FPSO SAO VICENTE', 'GUAMARE', 'IMBETIBA',
        'PORTO DO AÇU', 'SAO TOME']

    if ucds:
        UCDs = []
        for ucd in ucds:
            dist = geo.calc_dist_ucd_vs_ucds(ucd)
            slcu = dist[dist <= geo.raio_busca().wind].dropna()
            names = [x[0] for x in slcu.index]

            # retirando sondas
            avlbe = [x for x in names if not search('SS|NS', x)]
            for uu in estacoes_invalidas:
                try:
                    avlbe.remove(uu)
                except Exception:
                    continue
            UCDs.extend(avlbe)
        UCDs = list(set(UCDs))
    else:
        id_local = SECRET1()
        names = np.array(SECRET2(id_local))
        # retirando sondas
        UCDs = [x for x in names if not search('SS|NS', x)]
        for uu in estacoes_invalidas:
            UCDs.remove(uu)

    return UCDs
