import numpy as np
from pandas import to_datetime
from sys import path as syspath
import time as crono
from datetime import timedelta
syspath.append('XXXXXXXXXXXX')
from db.get_ucds import ucds_validas as ucds


def load(table, func, col_df=None,
         col_di='DataInical UTC', col_ucd=None):
    '''
    lê banco de dados com base nas datas inciais e finais da tabela de busca

    :param table: tabela com os apontamentos        (DataFrame)
    :param func: funcao para busca de dados
    :param col_di: nome da coluna da Data Inicial   (str)
    :param col_df: nome da coluna da Data Final     (str)

    '''
    if not col_df:
        dates = table[col_di].values
        inicio = to_datetime(dates.min(), dayfirst=True) - timedelta(hours=6)
        fim = to_datetime(dates.max(), dayfirst=True) + timedelta(hours=6)
    else:
        dti = table[col_di].values
        dtf = table[col_df].values
        inicio = to_datetime(dti.min(), dayfirst=True) - timedelta(hours=6)
        fim = to_datetime(dtf.max(), dayfirst=True) + timedelta(hours=6)
    if col_ucd:
        local = ucds(list(set(table[col_ucd].values)))
    else:
        local = ucds()
    print('# {:<56} #'.format('Carregando dados'))
    start = crono.time()
    data = func(local, inicio, fim)
    endtime = (crono.time() - start) / 60
    print('# {:<56} #'.format(f'Tempo: {str(round(endtime, 1))} min'))

    return data
