from ocnpylib import id2uv
from pandas import DataFrame
import matplotlib.pyplot as plt
from numpy import arange, sqrt


def uv_std_max_calc(data):
    '''
    Calcula componentes de velocidade u e v, assim como também o desvio padrão
    da intensidade, da corrente para as ucds que registraram máximo de corrente
    acima de 1,0 nó.

    :param data:    DataFrame - output dos dados retirados da api

    :return DataFrame com os valores calculados para cada ucd 
    '''
    # Calculando o máximo
    maxc = data.groupby('DS_MISSION').agg({'HCSP': ['max']})
    maxc.columns = ['Max.']

    # listando ucds com máximo de corrente acima de 1 nó
    atention = maxc[maxc['Max.'] >= 1.].index.to_list()

    if len(atention) != 0:
        box_data = DataFrame()
        for ucd in atention:
            slc = data[data.DS_MISSION == ucd]
            # calcula u e v para média vetorial
            u, v = id2uv(
                slc.HCSP.astype(float),
                slc.HCDT.astype(float),
                str_conv='ocean')
            # calcula devio padrão da intensidade
            dpad = slc.HCSP.std()
            maxx = slc.HCSP.max()
            box_data = box_data.append(DataFrame(
                {'u': u.mean(), 'v': v.mean(), 'stdv': dpad, 'max.': maxx},
                index=[ucd]))
    else:
        box_data = DataFrame()
    return box_data
