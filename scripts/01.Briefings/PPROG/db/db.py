import requests
from requests.auth import HTTPBasicAuth
import json
from pandas import DataFrame
from datetime import datetime, timedelta
import time
import numpy as np
from sys import path
brpath = 'M:\\Rotinas\\python\\scripts\\01.Briefings'
path.append(brpath)
path.append('M:\\Rotinas\\python')
from data import OCNdb as ocn
import security


def get_forecast(UCD):
    '''
        Lê boletim de previsão para UCD de interesse.

        :param UCD: string da UCD de interesse.
        :return forecast: DataFrame com os dados da previsão
    '''

    URL = requests.get(
        '{}{}{}'.format(
            'http://XXXXXXX',
            UCD),
        auth=HTTPBasicAuth(
            'CHAVE',
            security.decrypt(
                open("{}\\secret.key".format(brpath), "rb").read()))
    )

    data = json.loads(URL.content)
    df = DataFrame()
    for ix, x in enumerate(data):
        df = df.append(DataFrame(
            x,
            index=[datetime.strptime(x['DataInicio'], '%d/%m/%Y %H:%M:%S')])
        )

    forecast = df[[
        'DirecaoVento', 'VelocidadeVento', 'Rajada',
        'DirecaoOnda', 'AlturaOnda', 'AlturaMaximaOnda',
        'PeriodoPicoOnda', 'Precipitacao']
    ].replace(',', '.', regex=True).astype('float64')

    return forecast


def get_data24h(ucdwind, ucdwave, ucdcurr):
    '''
        Baixa dados de vento, onda e corrente do BD do OCEANOP

        :param ucdwind: lista de strings com as UCDs de interesse (vento)
        :param ucdwave: lista de strings com as UCDs de interesse (onda)
        :param ucdcurr: lista de strings com as UCDs de interesse (corrente)

        :return tuple: tuple com dados de vento, onda e corrente

        *ATENÇÃO: saída dos dados está em nós para intensidade!
    '''
    # Verificando data final e inicial da busca de dados
    dtmx = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    dtmn = dtmx + timedelta(days=-1)

    # Setando formato da data para busca no banco de dados
    datemax = dtmx.strftime("%d/%m/%Y %H:%M:%S")
    datemin = dtmn.strftime("%d/%m/%Y %H:%M:%S")

    vento = ocn.get_BD(
        ucds=ucdwind,
        dates=[datemin, datemax],
        param='meteo')
    if vento.shape[0] >= 1:
        vento = vento[['WSPD', 'WDIR']]
        vento.WSPD = vento.WSPD * 1.94384449

    onda = ocn.get_BD(
        ucds=ucdwave,
        dates=[datemin, datemax],
        param='wave')
    if onda.shape[0] >= 1:
        onda = onda[['VAVH', 'VPEDM', 'VTPK1']]

    corrente = ocn.get_BD(
        ucds=ucdcurr,
        dates=[datemin, datemax],
        param='curr')
    if corrente.shape[0] >= 1:
        corrente.HCSP = corrente.HCSP * 1.94384449
    return (vento, onda, corrente)
