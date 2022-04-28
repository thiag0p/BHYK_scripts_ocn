import numpy as np
from pandas import to_datetime, DataFrame, concat, date_range
from datetime import timedelta, datetime
from sys import path as syspath
syspath.append('XXXXXXXXXXXXXXXXX')
from geo import geo
import time as crono


def adjust_time(time1, time2, hbf=None, haf=None):
    '''
        ajuste do tempo para busca do dado

        :param time1: datetime tempo inicial
        :param time2: datetime tempo final
        :param hbf: int tempo de decrescimo do tempo inicial
        :param haf: int tempo de acrescimo do tempo final
    '''
    data_inicial = time1
    data_final = time2

    # Ajuste do tempo inicial
    if data_inicial.minute < 25:
        data_inicial = data_inicial
    else:
        data_inicial = (data_inicial + timedelta(hours=1))
    data_inicial = data_inicial.replace(minute=0, second=0)

    # Ajuste do tempo final
    if data_final.minute < 25:
        data_final = data_final
    else:
        data_final = (data_final + timedelta(hours=1))
    data_final = data_final.replace(minute=0, second=0)

    if hbf:
        data_inicial = data_inicial - timedelta(hours=hbf)
    if haf:
        data_final = data_final + timedelta(hours=haf)

    return data_inicial, data_final


def search_wind(table, data, col_di='DataInical UTC', col_df=None,
                col_ucd=None, col_lat=None, col_lon=None, col_xutm=None,
                col_yutm=None, hora_antes=None, hora_depois=None):
    '''
    Preenche tabela de apontamento com os dados de vento encontrados

    :param table: tabela com os apontamentos                    (DataFrame)
    :param data: dados carregados via ocnpylib                  (table.load_data)
    :param col_di: nome da coluna data inicial                  (str)
    :param col_di: nome da coluna data final                    (str)
    :param col_ucd: nome da coluna da UCD                       (str)
    :param col_lat: nome da coluna latitude em graus decimais   (str)
    :param col_lon: nome da coluna longitude em graus decimais  (str)
    :param col_xutm: nome da coluna coordenada este UTM         (str)
    :param col_yutm: nome da coluna coordenada norte UTM        (str)
    :param hora_antes: valor em horas                           (int)
    :param hora_depois: valor em horas                          (int)

    :return DataFrame
    '''
    #  retirando levels do multiindex para facilitar processo de busca de dados
    data_ = data.reset_index()
    data_ = data_.set_index('DT_DATA')
    # Adicionado para evitar repetição de laços sem necessidade quando for uma
    # tabela com somente uma UCD.
    if col_ucd:
        ucds = set(table[col_ucd])
        if len(ucds) == 1:
            dist = geo.calc_dist_ucd_vs_ucds(list(ucds)[0])

    start = crono.time()
    dist_max = geo.raio_busca().wind
    output = DataFrame()
    for line in table.index:
        table_slc = table[table.index == line]
        print(
            "# {:<56} #".format(f'Linha {line + 1} de {table.index[-1] + 1}'))
        # Definindo data inicial e final da busca
        if not col_df:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dtf = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dti, dtf = adjust_time(
                time1=dti,
                time2=dtf,
                hbf=hora_antes,
                haf=hora_depois)
        else:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dtf = to_datetime(table_slc[col_df].values[0], dayfirst=True)
            dti, dtf = adjust_time(
                time1=dti,
                time2=dtf,
                hbf=hora_antes,
                haf=hora_depois)
        # Achando as UCDs mais próximas ao pontos de interesse
        if col_ucd:
            if len(set(table[col_ucd])) != 1:
                ucd = table_slc[col_ucd].values[0]
                dist = geo.calc_dist_ucd_vs_ucds(ucd)
        elif col_lat and col_lon:
            lat = table_slc[col_lat].values[0]
            lon = table_slc[col_lon].values[0]
            dist = geo.calc_dist_lon_lat_vs_ucds(lon, lat)
        elif col_xutm and col_yutm:
            utmx = table_slc[col_xutm].values[0]
            utmy = table_slc[col_yutm].values[0]
            dist = geo.calc_dist_utm_vs_ucds(utmx, utmy)
        elif not col_lat and not col_lon and not col_xutm and not col_yutm:
            raise RuntimeError(
                'Falta indicar coluna da UCD ou ponto geografico')
        # Laço para busca nas ucds próximas ao apontamento
        for ucdproxima, dx in zip(dist.index, dist.values):
            # Se a distancia for maior que o raio permitido
            if dx[0] < dist_max:
                if '-' in ucdproxima[0]:
                    ucdname = ''.join(ucdproxima[0].split('-'))
                else:
                    ucdname = ucdproxima[0].split(' ')[-1]
                # Tentativa de preenchimento do apontamento
                try:
                    # Passos para pegar maior valor caso haja mais de um sensor
                    data_slc = data_[data_[['SENSOR']].squeeze().str.contains(
                        ucdname)]
                    maxvalue = data_slc.sort_values(
                        ['WSPD'], ascending=False).reset_index(
                        ).drop_duplicates(
                            subset=['DT_DATA'], keep="first").set_index(
                                'DT_DATA')[['WSPD', 'WDIR']].sort_index()
                    data_slc = maxvalue[dti:dtf]
                    data_slc.index.name = 'DT_DATA'
                    ivalues = data_slc['WSPD'].values
                    dvalues = data_slc['WDIR'].values
                    # Caso um dos parametros não tenham dados, busque outra
                    if np.isnan(ivalues).all() or np.isnan(dvalues).all():
                        continue
                    else:
                        data_slc.columns = ['INT_VENTO (m/s)', 'DIR_VENTO (°)']
                        # Ajustando para hora local
                        data_slc.index = data_slc.index - timedelta(hours=3)
                        for clname in table_slc.columns:
                            data_slc = concat(
                                [data_slc],
                                keys=list(table_slc[clname].values),
                                names=[clname])
                        data_slc['UCD Wind'] = ucdproxima[0]
                        output = output.append(data_slc)
                        print("# {:<56} #".format(
                            f'Dados encontrados em {ucdproxima[0]}'))
                        break
                except Exception:
                    continue
            else:
                print("# {:<56} #".format('dados não encontrados'))
                insert = DataFrame(
                    columns=[
                        'INT_VENTO (m/s)',
                        'DIR_VENTO (°)'],
                    index=[dti])
                insert.index.name = 'DT_DATA'
                insert.index = insert.index - timedelta(hours=3)
                for clname in table_slc.columns:
                    insert = concat(
                        [insert],
                        keys=list(table_slc[clname].values),
                        names=[clname])
                insert['UCD Wind'] = np.nan
                output = output.append(insert)
                break
    endtime = (crono.time() - start) / 60
    print("# {:<56} #".format(f'Tempo: {str(round(endtime, 1))} min'))

    if col_df:
        return output.droplevel(['DataInical UTC', col_df])
    else:
        return output.droplevel('DataInical UTC')


def search_wave(table, data, col_di='DataInical UTC', col_df=None,
                col_ucd=None, col_lat=None, col_lon=None, col_xutm=None,
                col_yutm=None, hora_antes=None, hora_depois=None):
    '''
    Preenche tabela de apontamento com os dados de onda encontrados

    :param table: tabela com os apontamentos                    (DataFrame)
    :param data: dados carregados via api                       (table.load_data)
    :param col_di: nome da coluna data inicial                  (str)
    :param col_di: nome da coluna data final                    (str)
    :param col_ucd: nome da coluna da UCD                       (str)
    :param col_lat: nome da coluna latitude em graus decimais   (str)
    :param col_lon: nome da coluna longitude em graus decimais  (str)
    :param col_xutm: nome da coluna coordenada este UTM         (str)
    :param col_yutm: nome da coluna coordenada norte UTM        (str)
    :param hora_antes: valor em horas                           (int)
    :param hora_depois: valor em horas                          (int)

    :return DataFrame
    '''
    #  retirando levels do multiindex para facilitar processo de busca de dados
    data_ = data.reset_index()
    data_ = data_.set_index('DT_DATA')
    # Adicionado para evitar repetição de laços sem necessidade quando for uma
    # tabela com somente uma UCD.
    if col_ucd:
        ucds = set(table[col_ucd])
        if len(ucds) == 1:
            dist = geo.calc_dist_ucd_vs_ucds(list(ucds)[0])

    start = crono.time()
    dist_max = geo.raio_busca().wave
    output = DataFrame()
    for line in table.index:
        table_slc = table[table.index == line]
        print(
            "# {:<56} #".format(f'Linha {line + 1} de {table.index[-1] + 1}'))
        # Definindo data inicial e final da busca
        if not col_df:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dtf = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dti, dtf = adjust_time(
                time1=dti,
                time2=dtf,
                hbf=hora_antes,
                haf=hora_depois)
        else:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dtf = to_datetime(table_slc[col_df].values[0], dayfirst=True)
            dti, dtf = adjust_time(
                time1=dti,
                time2=dtf,
                hbf=hora_antes,
                haf=hora_depois)
        # Achando as UCDs mais próximas ao pontos de interesse
        if col_ucd:
            if len(set(table[col_ucd])) != 1:
                ucd = table_slc[col_ucd].values[0]
                dist = geo.calc_dist_ucd_vs_ucds(ucd)
        elif col_lat and col_lon:
            lat = table_slc[col_lat].values[0]
            lon = table_slc[col_lon].values[0]
            dist = geo.calc_dist_lon_lat_vs_ucds(lon, lat)
        elif col_xutm and col_yutm:
            utmx = table_slc[col_xutm].values[0]
            utmy = table_slc[col_yutm].values[0]
            dist = geo.calc_dist_utm_vs_ucds(utmx, utmy)
        elif not col_lat and not col_lon and not col_xutm and not col_yutm:
            raise RuntimeError(
                'Falta indicar coluna da UCD ou ponto geografico')
        # Laço para busca nas ucds próximas ao apontamento
        for ucdproxima, dx in zip(dist.index, dist.values):
            # Se a distancia for maior que o raio permitido
            if dx[0] < dist_max:
                if '-' in ucdproxima[0]:
                    ucdname = ''.join(ucdproxima[0].split('-'))
                else:
                    ucdname = ucdproxima[0].split(' ')[-1]
                # Tentativa de preenchimento do apontamento
                try:
                    # Passos para pegar maior valor caso haja mais de um sensor
                    data_slc = data_[data_[['SENSOR']].squeeze().str.contains(
                        ucdname)]
                    maxvalue = data_slc.sort_values(
                        ['VAVH'], ascending=False).reset_index(
                        ).drop_duplicates(
                            subset=['DT_DATA'], keep="first").set_index(
                                'DT_DATA')[['VAVH', 'VPEDM', 'VTPK1']
                                ].sort_index()
                    data_slc = maxvalue[dti:dtf]
                    data_slc.index.name = 'DT_DATA'
                    hvalues = data_slc['VAVH'].values
                    # Caso só tenha direção ou período e não tenha Hs
                    if np.isnan(hvalues).all():
                        continue
                    else:
                        data_slc.columns = [
                            'HS_ONDA (m)', 'DIR_ONDA (°)', 'PER. ONDA (s)']
                        # Ajustando para hora local
                        data_slc.index = data_slc.index - timedelta(hours=3)
                        for clname in table_slc.columns:
                            data_slc = concat(
                                [data_slc],
                                keys=list(table_slc[clname].values),
                                names=[clname])
                        data_slc['UCD Wave'] = ucdproxima[0]
                        output = output.append(data_slc)
                        print("# {:<56} #".format(
                            f'Dados encontrados em {ucdproxima[0]}'))
                        break
                except Exception:
                    continue
            else:
                print("# {:<56} #".format('dados não encontrados'))
                insert = DataFrame(
                    columns=['HS_ONDA (m)',
                             'DIR_ONDA (°)',
                             'PER. ONDA (s)'],
                    index=[dti])
                insert.index.name = 'DT_DATA'
                insert.index = insert.index - timedelta(hours=3)
                for clname in table_slc.columns:
                    insert = concat(
                        [insert],
                        keys=list(table_slc[clname].values),
                        names=[clname])
                insert['UCD Wave'] = np.nan
                output = output.append(insert)
                break
    endtime = (crono.time() - start) / 60
    print("# {:<56} #".format(f'Tempo: {str(round(endtime, 1))} min'))

    if col_df:
        return output.droplevel(['DataInical UTC', col_df])
    else:
        return output.droplevel('DataInical UTC')


def search_curr(table, data, col_di='DataInical UTC', col_df=None,
                col_ucd=None, col_lat=None, col_lon=None, col_xutm=None,
                col_yutm=None, hora_antes=None, hora_depois=None):
    '''
    Preenche tabela de apontamento com os dados de corrente encontrados

    :param table: tabela com os apontamentos                    (DataFrame)
    :param data: dados carregados via api                       (table.load_data)
    :param col_di: nome da coluna data inicial                  (str)
    :param col_di: nome da coluna data final                    (str)
    :param col_ucd: nome da coluna da UCD                       (str)
    :param col_lat: nome da coluna latitude em graus decimais   (str)
    :param col_lon: nome da coluna longitude em graus decimais  (str)
    :param col_xutm: nome da coluna coordenada este UTM         (str)
    :param col_yutm: nome da coluna coordenada norte UTM        (str)
    :param hora_antes: valor em horas                           (int)
    :param hora_depois: valor em horas                          (int)

    :return DataFrame
    '''
    #  retirando levels do multiindex para facilitar processo de busca de dados
    data_ = data.reset_index()
    data_ = data_.set_index('DT_DATA')
    # Adicionado para evitar repetição de laços sem necessidade quando for uma
    # tabela com somente uma UCD.
    if col_ucd:
        ucds = set(table[col_ucd])
        if len(ucds) == 1:
            dist = geo.calc_dist_ucd_vs_ucds(list(ucds)[0])

    start = crono.time()
    dist_max = geo.raio_busca().curr
    output = DataFrame()
    for line in table.index:
        table_slc = table[table.index == line]
        print(
            "# {:<56} #".format(f'Linha {line + 1} de {table.index[-1] + 1}'))
        # Definindo data inicial e final da busca
        if not col_df:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dtf = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dti, dtf = adjust_time(
                time1=dti,
                time2=dtf,
                hbf=hora_antes,
                haf=hora_depois)
        else:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dtf = to_datetime(table_slc[col_df].values[0], dayfirst=True)
            dti, dtf = adjust_time(
                time1=dti,
                time2=dtf,
                hbf=hora_antes,
                haf=hora_depois)
        # Achando as UCDs mais próximas ao pontos de interesse
        if col_ucd:
            if len(set(table[col_ucd])) != 1:
                ucd = table_slc[col_ucd].values[0]
                dist = geo.calc_dist_ucd_vs_ucds(ucd)
        elif col_lat and col_lon:
            lat = table_slc[col_lat].values[0]
            lon = table_slc[col_lon].values[0]
            dist = geo.calc_dist_lon_lat_vs_ucds(lon, lat)
        elif col_xutm and col_yutm:
            utmx = table_slc[col_xutm].values[0]
            utmy = table_slc[col_yutm].values[0]
            dist = geo.calc_dist_utm_vs_ucds(utmx, utmy)
        elif not col_lat and not col_lon and not col_xutm and not col_yutm:
            raise RuntimeError(
                'Falta indicar coluna da UCD ou ponto geografico')
        # Laço para busca nas ucds próximas ao apontamento
        for ucdproxima, dx in zip(dist.index, dist.values):
            # Se a distancia for maior que o raio permitido
            if dx[0] < dist_max:
                if '-' in ucdproxima[0]:
                    ucdname = ''.join(ucdproxima[0].split('-'))
                else:
                    ucdname = ucdproxima[0].split(' ')[-1]
                # Tentativa de preenchimento do apontamento
                try:
                    # Passos para pegar maior valor caso haja mais de um sensor
                    data_slc = data_[data_[['SENSOR']].squeeze().str.contains(
                        ucdname)]
                    maxvalue = data_slc.sort_values(
                        ['HCSP'], ascending=False).reset_index(
                        ).drop_duplicates(
                            subset=['DT_DATA'], keep="first").set_index(
                                'DT_DATA')[['HCSP', 'HCDT']].sort_index()
                    data_slc = maxvalue[dti:dtf]
                    data_slc.index.name = 'DT_DATA'
                    ivalues = data_slc['HCSP'].values
                    # Caso um dos parametros não tenham dados, busque outra
                    if np.isnan(ivalues).all():
                        continue
                    else:
                        data_slc.columns = ['INT_COR (m/s)', 'DIR_COR (°)']
                        # Ajustando para hora local
                        data_slc.index = data_slc.index - timedelta(hours=3)
                        for clname in table_slc.columns:
                            data_slc = concat(
                                [data_slc],
                                keys=list(table_slc[clname].values),
                                names=[clname])
                        data_slc['UCD Curr'] = ucdproxima[0]
                        output = output.append(data_slc)
                        print("# {:<56} #".format(
                            f'Dados encontrados em {ucdproxima[0]}'))
                        break
                except Exception:
                    continue
            else:
                print("# {:<56} #".format('dados não encontrados'))
                insert = DataFrame(
                    columns=[
                        'INT_COR (m/s)',
                        'DIR_COR (°)'],
                    index=[dti])
                insert.index.name = 'DT_DATA'
                insert.index = insert.index - timedelta(hours=3)
                for clname in table_slc.columns:
                    insert = concat(
                        [insert],
                        keys=list(table_slc[clname].values),
                        names=[clname])
                insert['UCD Curr'] = np.nan
                output = output.append(insert)
                break
    endtime = (crono.time() - start) / 60
    print("# {:<56} #".format(f'Tempo: {str(round(endtime, 1))} min'))

    if col_df:
        return output.droplevel(['DataInical UTC', col_df])
    else:
        return output.droplevel('DataInical UTC')
