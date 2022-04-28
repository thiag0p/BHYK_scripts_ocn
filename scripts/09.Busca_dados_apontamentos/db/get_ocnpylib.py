from ocnpylib import SECRET, SECRET, SECRET, SECRET_PROFILE
from ocnpylib import SECRET, SECRET
from ocnpylib import SECRET
from ocnpylib import SECRET, SECRET
import time as crono
import numpy as np
from re import search
from pandas import DataFrame, concat
LOGPATH = 'M:\\Rotinas\\python\\scripts\\09.Busca_dados_apontamentos\\log'


def doit(fx, local, inicio, fim):
    '''
        função que realiza carregamento de dados e escreve LOG

        :param fx: função de acesso ao dados do ocnpylib
    '''
    LOG = open(f'{LOGPATH}\\LOG_LIBwind.txt', 'w', newline='\r\n')
    start = crono.time()
    # Buscando os dados
    timestep = crono.time()
    id_local = SECRET(local)
    find_id = crono.time() - timestep
    timestep = crono.time()
    id_local_install_sensor = SECRET(
        SECRET(id_local))
    find_id_local_install_sensor = crono.time() - timestep
    name = SECRET(id_local)
    dates = [inicio.strftime('%d/%m/%Y %H:%M:%S'),
             fim.strftime('%d/%m/%Y %H:%M:%S')]
    timestep = crono.time()
    if fx == SECRET_PROFILE:
        data = fx(id_local_install_sensor, dates, lst_layer=[0])
    else:
        data = fx(id_local_install_sensor, dates)
    load_data = crono.time() - timestep
    enD = crono.time() - start
    if data.shape[0] == 0:
        LOG.write('NO DATA')
    else:
        # =====================================================================
        #                Filtrando dados aprovados
        # =====================================================================
        timestep = crono.time()
        # if fx == SECRET_PROFILE:
        #     layer0 = DataFrame()
        #     for sensor in set(data.index.get_level_values(0)):
        #         sens = data.loc[sensor]
        #         acrn = list(set(sens.index.get_level_values(0)))[0]
        #         dfme = sens.loc[acrn]
        #         l0 = dfme[dfme['LAYER'] == 0]
        #         layer0 = layer0.append(concat(
        #             [concat([l0], keys=[acrn], names=['SENSOR'])],
        #             keys=[sensor],
        #             names=['ILOC_SENSOR']
        #         ))
        #     data = layer0
        aprovado = SECRET(data)
        aprovado.columns = [x.split('_')[0] for x in aprovado.columns]
        data = data[aprovado][aprovado.columns].dropna(how='all')
        aproved_data = crono.time() - timestep
        nsensr = len(set(data.index.get_level_values(1)))
        # Escrevendo no log
        ucds = '; '.join(local)
        LOG.write(f'Input UCDs: {ucds}\n')
        LOG.write(f'Total de Sensores carregadas: {nsensr}\n')
        time = data.index.get_level_values('DT_DATA')
        dti = time.min().strftime('%d/%m/%Y %Hh')
        dtf = time.max().strftime('%d/%m/%Y %Hh')
        LOG.write(f'Data inicial: {dti}\n')
        LOG.write(f'Data final: {dtf}\n')
        LOG.write(f'Tempo de processamento: {enD} s\n\n\n')
        LOG.write('{}\n'.format(60 * '-'))
        LOG.write(f'Acesso ao ID LOCAL: {find_id} s\n')
        LOG.write('Acesso ao ID LOCAL INSTALL SENSOR: {} s\n'.format(
            find_id_local_install_sensor))
        LOG.write(f'Carregamento os dados: {load_data} s\n')
        LOG.write(f'Filtragem dos aprovados: {aproved_data} s\n')
    LOG.close()

    return data


def get_wind(local, inicio, fim):
    '''
    Acessa os dados de vento disponíveis na UCD

    :param local:   list    ex: ['P-19', 'P-20']
    :param inicio:  datetime data inicial
    :param fim: datetime data final

    :return DataFrame
    '''
    data = doit(SECRET, local, inicio, fim)
    return data


def get_wave(local, inicio, fim):
    '''
    Acessa os dados de vento disponíveis na UCD

    :param local:   list    ex: ['P-19', 'P-20']
    :param inicio:  datetime data inicial
    :param fim: datetime data final

    :return DataFrame
    '''
    data = doit(SECRET, local, inicio, fim)
    return data


def get_curr(local, inicio, fim):
    '''
    Acessa os dados de vento disponíveis na UCD

    :param local:   list    ex: ['P-19', 'P-20']
    :param inicio:  datetime data inicial
    :param fim: datetime data final

    :return DataFrame
    '''
    data = doit(SECRET, local, inicio, fim)
    return data


def get_curr_profile(local, inicio, fim):
    '''
    Acessa os dados de vento disponíveis na UCD

    :param local:   list    ex: ['P-19', 'P-20']
    :param inicio:  datetime data inicial
    :param fim: datetime data final

    :return DataFrame
    '''
    data = doit(ocean_CURR_PROFILE, local, inicio, fim)
    return data
