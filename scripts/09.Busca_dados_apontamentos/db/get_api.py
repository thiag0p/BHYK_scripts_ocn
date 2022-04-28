from pandas import DataFrame, to_datetime, concat
from datetime import timedelta, datetime
import numpy as np
from geo import geo
from sys import path as syspath
import ocnpylib
from warnings import filterwarnings
from re import search
import time as crono
import json
import requests
filterwarnings("ignore")
user = "XXXXXXXX"
pasw = "XXXXXXXXXXXX"
LOGPATH = 'xxxxxxxxxxxxxxxxxxxx'


def api_wind(local, inicio, fim):
    '''
    Função de acesso aos dados de vento via api

    :param local: UCDs de interesse             (list)
    :param inicio: Data inicial                 (datetime)
    :param fim: Data final                      (datetime)

    :return DataFrame
    '''
    LOG = open(f'{LOGPATH}\\LOG_APIwind.txt', 'w', newline='\r\n')
    start = crono.time()
    QRY = '{}{}{}XXXXXXXXXXXX{}XXXXXXXXXXXXXX{}'.format(
        "http://XXXXXXXXXXXX",
        "XXXXXXXXXXXX",
        'XXXXXXXXX'.join(local),
        inicio.strftime('%m%%2F%d%%2F%Y%%20%H%%3A%M%%3A%S'),
        fim.strftime('%m%%2F%d%%2F%Y%%20%H%%3A%M%%3A%S'))
    URL = requests.get(QRY, auth=(user, pasw))    
    JSN = json.loads(URL.content)
    if JSN['success']:
        df = DataFrame(JSN['data'])
        enD = crono.time() - start
        if len(df.index) is 0:
            print('x SEM DADOS NAS UCDS DURANTE PERÍODO REQUISITADO')
        else:
            time = df['DT_ACQUISITION'].values
            df.index = [datetime.strptime(x, '%d/%m/%Y %H:%M:%S') for x in time]
            df = df.sort_index().drop(labels=['DT_ACQUISITION'], axis=1)
        time = df.index
        nsensr = len(set(df.DS_MISSION))
        ucds = '; '.join(local)
        LOG.write(f'Input UCDs: {ucds}\n')
        LOG.write(f'Total de Sensores carregadas: {nsensr}\n')
        dti = time.min().strftime('%d/%m/%Y %Hh')
        dtf = time.max().strftime('%d/%m/%Y %Hh')
        LOG.write(f'Data inicial: {dti}\n')
        LOG.write(f'Data final: {dtf}\n')
        LOG.write(f'Tempo de processamento: {enD} s\n')
        LOG.close()
    else:
        print('ERRO:' + JSN['errors'][0])
        df = DataFrame()

    return df


def api_wave(local, inicio, fim):
    '''
    Função de acesso aos dados de onda via api

    :param local: UCDs de interesse             (list)
    :param inicio: Data inicial                 (datetime)
    :param fim: Data final                      (datetime)

    :return DataFrame
    '''

    QRY = '{}{}{}XXXXXXXXXXXXXX{}XXXXXXXXXXXXXXXX{}'.format(
        "http://XXXXXXXXXXXXXX",
        "XXXXXXXXXXXX",
        'XXXXXXXXXX'.join(local),
        inicio.strftime('%m%%2F%d%%2F%Y%%20%H%%3A%M%%3A%S'),
        fim.strftime('%m%%2F%d%%2F%Y%%20%H%%3A%M%%3A%S'))
    URL = requests.get(QRY, auth=(user, pasw))
    JSN = json.loads(URL.content)
    if JSN['success']:
        df = DataFrame(JSN['data'])
        if len(df.index) is 0:
            print('x SEM DADOS NAS UCDS DURANTE PERÍODO REQUISITADO')
        else:
            time = df['DT_ACQUISITION'].values
            df.index = [datetime.strptime(x, '%d/%m/%Y %H:%M:%S') for x in time]
            df = df.sort_index().drop(labels=['DT_ACQUISITION'], axis=1)
    else:
        print('ERRO:' + JSN['errors'][0])
        df = DataFrame()
    return df


def api_curr(local, inicio, fim):
    '''
    Função de acesso aos dados de onda via api

    :param local: UCDs de interesse             (list)
    :param inicio: Data inicial                 (datetime)
    :param fim: Data final                      (datetime)

    :return DataFrame
    '''

    QRY = '{}{}{}XXXXXXXXXXXXXX{}XXXXXXXXXXXXXXXX{}'.format(
        "XXXXXXXXXXXXXXX",
        "XXXXXXXXXXXX",
        'XXXXXX'.join(local),
        inicio.strftime('%m%%2F%d%%2F%Y%%20%H%%3A%M%%3A%S'),
        fim.strftime('%m%%2F%d%%2F%Y%%20%H%%3A%M%%3A%S'))
    URL = requests.get(QRY, auth=(user, pasw))
    JSN = json.loads(URL.content)

    if JSN['success']:
        df = DataFrame(JSN['data'])
        if len(df.index) is 0:
            print('x SEM DADOS NAS UCDS DURANTE PERÍODO REQUISITADO')
        else:
            time = df['DT_ACQUISITION'].values
            df.index = [datetime.strptime(x, '%d/%m/%Y %H:%M:%S') for x in time]
            df = df.sort_index().drop(labels=['DT_ACQUISITION'], axis=1)
    else:
        print('ERRO:' + JSN['errors'][0])
        df = DataFrame()

    return df


def api_curr_profile(local, inicio, fim):
    '''
    Função de acesso aos dados de perfil de corrente via api, onde só é
    retornada a camada 0 do perfilador

    :param local: UCDs de interesse             (list)
    :param inicio: Data inicial                 (datetime)
    :param fim: Data final                      (datetime)

    :return df
    '''
    QRY = '{}{}{}XXXXXXXXXXXXXX{}XXXXXXXXXXXXXXXX{}'.format(
        "XXXXXXXXXXXXXXX",
        "XXXXXXXXXXXX",
        'XXXXXX'.join(local),
        inicio.strftime('%m%%2F%d%%2F%Y%%20%H%%3A%M%%3A%S'),
        fim.strftime('%m%%2F%d%%2F%Y%%20%H%%3A%M%%3A%S'))
    URL = requests.get(QRY, auth=(user, pasw))
    JSN = json.loads(URL.content)
    if JSN['success']:
        df = DataFrame(JSN['data'])
        df = df[df.OCEA_VL_LAYER == 0.]
        if len(df.index) is 0:
            print('x SEM DADOS NAS UCDS DURANTE PERÍODO REQUISITADO')
        else:
            time = df['DT_ACQUISITION'].values
            df.index = [datetime.strptime(x, '%d/%m/%Y %H:%M:%S') for x in time]
            df = df.sort_index().drop(labels=['DT_ACQUISITION'], axis=1)
    else:
        print('ERRO:' + JSN['errors'][0])
        df = DataFrame()

    return df
