import numpy as np
from pandas import to_datetime, DataFrame, concat
from datetime import timedelta
from sys import path as syspath
syspath.append('XXXXXXXXXXXXX')
from geo import geo
import time as crono


def search_wind(table, data, col_di='DataInical UTC', col_df=None,
                col_ucd=None, col_lat=None, col_lon=None, col_xutm=None,
                col_yutm=None, hora_antes=None, hora_depois=None):
    '''
    Preenche tabela de apontamento com os dados de vento encontrados

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
    start = crono.time()
    dist_max = geo.raio_busca().wind
    output = DataFrame()
    for line in table.index:
        table_slc = table[table.index == line]
        print(f'Linha {line + 1} de {table.shape[0]}')
        print(table_slc)
        # Definindo data inicial e final da busca
        if not col_df:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            if hora_antes:
                dti = dti - timedelta(hours=hora_antes)
            dtf = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            if hora_depois:
                dtf = dtf + timedelta(hours=hora_depois)
        else:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dtf = to_datetime(table_slc[col_df].values[0], dayfirst=True)
            if hora_antes:
                dti = dti - timedelta(hours=hora_antes)
            if hora_depois:
                dtf = dtf + timedelta(hours=hora_depois)
        # Achando as UCDs mais próximas ao pontos de interesse
        if col_ucd:
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
                # Tentativa de preenchimento do apontamento
                try:
                    data_slc = data[
                        data['DS_MISSION'] == ucdproxima[0]][dti:dtf][
                            ['METE_VL_WSPD', 'METE_VL_WDIR']].convert_objects(
                                convert_numeric=True)
                    ivalues = data_slc['METE_VL_WSPD'].values
                    dvalues = data_slc['METE_VL_WDIR'].values
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
                        print(f'Dados encontrados em {ucdproxima[0]}')
                        break
                except Exception:
                    continue
            else:
                print('dados não encontrados')
                insert = DataFrame(
                    columns=['INT_VENTO (m/s)', 'DIR_VENTO (°)'],
                    index=[np.nan])
                for clname in table_slc.columns:
                    insert = concat(
                        [insert],
                        keys=list(table_slc[clname].values),
                        names=[clname])
                insert['UCD Wind'] = np.nan
                output = output.append(insert)
                break
    endtime = (crono.time() - start) / 60
    print(f'Tempo: {str(round(endtime, 1))} min')

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
    start = crono.time()
    dist_max = geo.raio_busca().wave
    output = DataFrame()
    for line in table.index:
        table_slc = table[table.index == line]
        print(f'Linha {line + 1} de {table.shape[0]}')
        print(table_slc)
        # Definindo data inicial e final da busca
        if not col_df:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            if hora_antes:
                dti = dti - timedelta(hours=hora_antes)
            dtf = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            if hora_depois:
                dtf = dtf + timedelta(hours=hora_depois)
        else:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dtf = to_datetime(table_slc[col_df].values[0], dayfirst=True)
            if hora_antes:
                dti = dti - timedelta(hours=hora_antes)
            if hora_depois:
                dtf = dtf + timedelta(hours=hora_depois)
        # Achando as UCDs mais próximas ao pontos de interesse
        if col_ucd:
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
                # Tentativa de preenchimento do apontamento
                try:
                    data_slc = data[
                        data['DS_MISSION'] == ucdproxima[0]][dti:dtf][[
                            'OCEA_VL_VAVH', 'OCEA_VL_VPEDM', 'OCEA_VL_VTPK1']
                        ].convert_objects(convert_numeric=True)
                    hvalues = data_slc['OCEA_VL_VAVH'].values
                    # Caso só tenha direção ou período e não tenha Hs
                    if np.isnan(hvalues).all():
                        continue
                    else:
                        data_slc.columns = [
                            'HS_ONDA (m/s)', 'DIR_ONDA (°)', 'PER. ONDA (s)']
                        # Ajustando para hora local
                        data_slc.index = data_slc.index - timedelta(hours=3)
                        for clname in table_slc.columns:
                            data_slc = concat(
                                [data_slc],
                                keys=list(table_slc[clname].values),
                                names=[clname])
                        data_slc['UCD Wave'] = ucdproxima[0]
                        output = output.append(data_slc)
                        print(f'Dados encontrados em {ucdproxima[0]}')
                        break
                except Exception:
                    continue
            else:
                print('dados não encontrados')
                insert = DataFrame(
                    columns=['HS_ONDA (m/s)',
                             'DIR_ONDA (°)',
                             'PER. ONDA (s)'],
                    index=[np.nan])
                for clname in table_slc.columns:
                    insert = concat(
                        [insert],
                        keys=list(table_slc[clname].values),
                        names=[clname])
                insert['UCD Wave'] = np.nan
                output = output.append(insert)
                break
    endtime = (crono.time() - start) / 60
    print(f'Tempo: {str(round(endtime, 1))} min')

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
    start = crono.time()
    dist_max = geo.raio_busca().curr
    output = DataFrame()
    for line in table.index:
        table_slc = table[table.index == line]
        print(f'Linha {line + 1} de {table.shape[0]}')
        print(table_slc)
        # Definindo data inicial e final da busca
        if not col_df:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            if hora_antes:
                dti = dti - timedelta(hours=hora_antes)
            dtf = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            if hora_depois:
                dtf = dtf + timedelta(hours=hora_depois)
        else:
            dti = to_datetime(table_slc[col_di].values[0], dayfirst=True)
            dtf = to_datetime(table_slc[col_df].values[0], dayfirst=True)
            if hora_antes:
                dti = dti - timedelta(hours=hora_antes)
            if hora_depois:
                dtf = dtf + timedelta(hours=hora_depois)
        # Achando as UCDs mais próximas ao pontos de interesse
        if col_ucd:
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
                # Tentativa de preenchimento do apontamento
                try:
                    data_slc = data[
                        data['DS_MISSION'] == ucdproxima[0]][dti:dtf][
                            ['OCEA_VL_HCSP', 'OCEA_VL_HCDT']
                        ].convert_objects(convert_numeric=True)
                    ivalues = data_slc['OCEA_VL_HCSP'].values
                    dvalues = data_slc['OCEA_VL_HCDT'].values
                    # Caso um dos parametros não tenham dados, busque outra
                    if np.isnan(ivalues).all() or np.isnan(dvalues).all():
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
                        print(f'Dados encontrados em {ucdproxima[0]}')
                        break
                except Exception:
                    continue
            else:
                print('dados não encontrados')
                insert = DataFrame(
                    columns=['INT_COR (m/s)', 'DIR_COR (°)'],
                    index=[np.nan])
                for clname in table_slc.columns:
                    insert = concat(
                        [insert],
                        keys=list(table_slc[clname].values),
                        names=[clname])
                insert['UCD Curr'] = np.nan
                output = output.append(insert)
                break
    endtime = (crono.time() - start) / 60
    print(f'Tempo: {str(round(endtime, 1))} min')

    return output.droplevel('DataInical UTC')
