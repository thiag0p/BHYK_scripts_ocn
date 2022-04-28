
from ocnpylib import id2uv, uv2id
from pandas import DataFrame, concat, date_range
from datetime import timedelta


def labels_hms(cota):
    '''
    Retorna os labels que são utilizados no sistema HMS e que serão utilizados
    para plot das imagens.

    :param cota: int or float da cota do instrumento.
    '''
    labels = {
        'SECRET': 'Intensidade inst. a 10 m (nós)',
        'SECRET': 'Intensidade 2min a 10 m (nós)',
        'SECRET': 'Rajada 2min a 10 m (nós)',
        'SECRET': f'Intensidade inst. a {cota} m (nós)',
        'SECRET': f'Intensidade 2min a {cota} m (nós)',
        'SECRET': f'Rajada 2min a {cota} m (nós)',
        'SECRET': 'Direcao inst. (deg m)',
        'SECRET': f'Intensidade media movel a {cota} m (nós) (10 min)',
        'SECRET': 'Intensidade media movel a 10 m (nós) (10 min)',
        'SECRET': f'Intensidade média (10 min) a {cota} m (nós)',
        'SECRET': 'Intensidade média (10 min) a 10 m (nós)'
    }

    return labels


def labels_epta():
    '''
    Retorna os labels que são utilizados no sistema EPTA e que serão utilizados
    para plot das imagens.
    '''

    labels = {
        'SECRET': 'Intensidade inst. (nós)',
        'SECRET': 'Intensidade 2min (nós)',
        'SECRET': 'Intensidade 10min (nós)',
        'SECRET': 'Direção inst. (deg m)'
    }

    return labels


def dir_media_movel(df, INTCOTA, DIR):
    '''
    Calcula a média móvel da direção do vento.

    :param df:        DataFrame com os dados de vento
    :param INTCOTA:   String com label da intensidade do vento
    :param DIR:       String com label da direção do vento

    :return DataFrame com adição da coluna da média móvel para direção 
    '''
    tmp = df.copy()
    tmp2 = DataFrame()
    tmp['U'] = id2uv(tmp[INTCOTA].values, tmp[DIR].values)[0]
    tmp2['Umedio'] = tmp['U'].rolling(600, min_periods=50).mean()
    tmp['V'] = id2uv(tmp[INTCOTA].values, tmp[DIR].values)[1]
    tmp2['Vmedio'] = tmp['V'].rolling(600, min_periods=50).mean()
    _, tmp2['Direcao media movel (10 min)'] = uv2id(tmp2['Umedio'].values,
                                                    tmp2['Vmedio'].values)
    output = tmp2['Direcao media movel (10 min)'].copy()
    output = output.to_frame()
    return output


def dir_media(df, INTCOTA, DIR):
    '''
    Calcula a média da direção do vento.

    :param df:        DataFrame com os dados de vento
    :param INTCOTA:   String com label da intensidade do vento
    :param DIR:       String com label da direção do vento

    :return output: DataFrame com média para direção 
    '''
    tmp = df.copy()
    tmp2 = DataFrame()
    tmp['U'] = id2uv(tmp[INTCOTA].values, tmp[DIR].values)[0]
    tmp2['Umedio'] = tmp['U'].resample('10T').mean()

    tmp['V'] = id2uv(tmp[INTCOTA].values, tmp[DIR].values)[1]
    tmp2['Vmedio'] = tmp['V'].resample('10T').mean()
    _, tmp2['Direcao media (10 min)'] = uv2id(tmp2['Umedio'].values,
                                              tmp2['Vmedio'].values)
    output = tmp2['Direcao media (10 min)'].copy()
    output.index = output.index + timedelta(seconds=600)
    return output


def mean_and_rollingmean(HMSDATA, INTCOTA, INT10M,
                         INTRMCOTA10MIN, INTRM10M10MIN,
                         INTMCOTA10MIN, INTM10M10MIN, DIR):
    '''
    Calcula a média e a média móvel da série de dados de vento do HMS.
    '''

    rmdata = HMSDATA[[INTCOTA, INT10M, DIR]]
    # Retirando indices duplicados
    rmdata = rmdata[~rmdata.index.duplicated(keep='first')]
    rmdata = rmdata.reindex(date_range(
        rmdata.index[0],
        rmdata.index[-1], freq='1s'))

    # Calculando média móvel de 10 min
    rmdata[INTRMCOTA10MIN] = rmdata[INTCOTA].rolling(
        600,
        min_periods=50).mean()
    rmdata[INTRM10M10MIN] = rmdata[INT10M].rolling(
        600,
        min_periods=50).mean()
    dirmediamovel = dir_media_movel(rmdata, INTCOTA, DIR)
    rmdata = concat([rmdata, dirmediamovel], axis=1)
    
    mdata = rmdata[INTCOTA].resample('10T').mean()
    mdata.index = mdata.index + timedelta(seconds=600)
    mvm10m = rmdata[INT10M].resample('10T').mean()
    mvm10m.index = mvm10m.index + timedelta(seconds=600)
    mdata = concat([mdata, mvm10m], axis=1)
    dirmedia = dir_media(rmdata, INTCOTA, DIR)
    mdata = concat([mdata, dirmedia], axis=1)
    mdata.columns = [INTMCOTA10MIN, INTM10M10MIN, 'Direcao media (10 min)']

    return mdata, rmdata
