# -*- coding: utf-8 -*-
"""
    Acesso/leitura sobre Conjunto de Aquivos (DADAS) brutos HMS.

    Essa biblioteca de funções é um ajuste de python2 para python3 da rotina
    MoP_hmsraw.py criada por V71N e modificada por AL4N.

    As mudanças herdadas do código anterior são:
        + v01 - AL4N: corrigido o problema para a data, para arquivos em que o
                    cabeçalho se referiam ao último segundo da hora anterior
                    (H:M:59) e também para aqueles em que a referência era a hora
                    cheia (H:M:00) na função hms_qry
        >> 15/10/2018
        + v02 - AL4N: adaptação da rotina para ambos os cabeçalhos (com ou sem
                    informações de altura dos sensores)
                    bem como numero de colunas (com ou sem o aproamento da unidade)
                    na função hms_qry
        >> 26/02/2022
        + v03 - BHYK: adição de leitura dos dados de epta.
    ----------

"""

from datetime import datetime, timedelta
import numpy as np
from os.path import normpath, join, isfile, isdir
from glob import glob
import zlib as zb
import ocnpylib as ocn
from pandas import DataFrame, Series, concat, date_range
from pyocnp import DESVVV, ASCIIII, UCDIDNAME, ODBQRY
import re


def roundTime(d=None, dateDelta=timedelta(minutes=1)):
    """
        Round a datetime object to a multiple of a timedelta

        d : datetime.datetime object, default now.
        dateDelta : timedelta object, we round to a multiple of this,
                    default 1 minute.

        Author: Thierry Husson 2012 - Use it as you want but don't blame me.
            Stijn Nevens 2014 - Changed to use only datetime objects
                                as variables
    """
    roundTo = dateDelta.total_seconds()

    if d is None:
        d = datetime.now()
    seconds = (d - d.min).seconds
    # // is a floor division, not a comment on following line:
    rounding = (seconds + roundTo / 2) // roundTo * roundTo
    return d + timedelta(0, rounding - seconds, -d.microsecond)


def fmt_time(X):
    '''
    Formata a hora para carregar os arquivos
    '''
    try:
        return datetime.strptime(X['str_time'], '%Y-%m-%d-%H-%M')
    except:
        return datetime.strptime(X['str_time'], '%d-%m-%Y-%H')


def gen_path(UCDNAME, SYSTEM):
    '''
        Gera, automaticamente, o caminho em DESV onde estão salvos os
        arquivos de HMS da unidade

        :param UCDNAME: ``unicode string`` unidade alvo
        :param SYSTEM:  ``unicode string`` 'HMS' ou 'EPTA'
    '''

    # ocnpylib.name_byid_local()
    IDdesv = UCDIDNAME(
        UCDNAME, flt_tol=.9, str_dbaccess=DESVVV)[0]
    DBQRY = (
        "SELECT {0}.PAIN_TX_PATH_ARQ FROM {0}"
        " WHERE {0}.LOIN_CD_LOCAL = {1}"
        " AND {0}.EQUI_CD_EQUIPAMENT = 1").format('USERRR.TB_PARAMETROS_INST',       
                                                  IDdesv)
    QRYRESULTS = ODBQRY(
        DBQRY, ASCIIII(DESVVV))
    PATH = QRYRESULTS[0][0][:-4] + SYSTEM

    return PATH


def fmt_string(UCDNAME, PATH, FILENAMES):
    '''
        verifica se os arquivos listados são mesmo da plataforma
        de interesse
    '''
    IDs = [str(re.sub('\D', '', x.replace(PATH + '\\', '')[0:4]))
           for x in FILENAMES]

    UCDIDold = str(UCDIDNAME([UCDNAME])[0])
    UCDIDnew = str(ocn.id_local_byname([UCDNAME])[0])
    mask = [x.startswith((UCDIDold, UCDIDnew)) for x in IDs]

    # exclui os arquivos em que o ID do nome não corresponde ao da unidade
    FILENAMES = FILENAMES.where(mask, other=np.nan).dropna()

    return FILENAMES


def gen_file_list(UCDNAME, DATEIN, DATEFI, SYSTEM):
    '''
    Gera a lista de arquivos a serem carregados

    :param UCDNAME: ``unicode string`` Nome da Unidade de Coleta de Dados (UCD)
    :param DATETIN: ``unicode string`` Data inicial - "DD/MM/YYYY HH:MI:SS"
    :param DATETFI: ``unicode string`` Data final - "DD/MM/YYYY HH:MI:SS"
    :param PATH:    ``unicode string`` caminho onde são encontrados os arquivos
    :param SYSTEM:  ``unicode string`` 'EPTA' ou 'HMS'
    :return FILENAMES: ``list of strings``

    Notas
    -----
    O horario no nome do arquivo é o de fechamento do mesmo (o conteudo
    começa uma hora antes)
    Para acessar os dados do período de interesse e corrigir este problema,
    a função adiciona 1h ao DATEIN e DATEFI
    '''
    # Formato dos arquivos
    EXT = {'HMS': '*.hms_gz', 'EPTA': '*.epta_gz'}
    # Acessando IDs da UCD de interesse
    UCDIDold = str(UCDIDNAME([UCDNAME])[0])
    UCDIDnew = str(ocn.id_local_byname([UCDNAME])[0])

    PATH = gen_path(UCDNAME, SYSTEM)

    # Normalização sistêmica de sintaxe do caminho dos arquivos.
    PATH = normpath(PATH.replace("\\", "/"))

    files = glob(join(PATH, EXT[SYSTEM]))

    dti = datetime.strptime(DATEIN, '%d/%m/%Y %H:%M:%S') + timedelta(hours=1)
    dtf = datetime.strptime(DATEFI, '%d/%m/%Y %H:%M:%S') + timedelta(hours=1)

    FILENAMES = []
    if len(files) > 0:
        for fname in files:
            arq = fname.split('\\')[-1]
            if not arq[0].isdigit():
                continue
            else:
                filedate = datetime.strptime(
                    re.search(r'(\d{4}-\d{2}-\d{2}-\d{2}-\d{2})',
                              fname).group(1),
                    '%Y-%m-%d-%H-%M')
                if (filedate >= dti) & (filedate <= dtf):
                    if arq.startswith(UCDIDold) or arq.startswith(UCDIDnew):
                        FILENAMES.append(fname)
        if len(FILENAMES) == 0:
            raise RuntimeError(
                "Não há dados de {} no período especificado: {} - {}".format(
                    SYSTEM, DATEIN, DATEFI))
    return FILENAMES


def get_gz_file(GZFILE):
    '''
        Função de de abertura/leitura do arquivo gz.
    '''
    # Tentativa de abertura/leitura do arquivo GZ.
    try:
        with open(GZFILE, 'rb') as filegz:
            txtgz = filegz.read()
    except IOError as err:
        print('<<Reading Error>> File: ' + repr(GZFILE))
        print('{}: [Errno {}] {}'.format(
            repr(err)[0:repr(err).find('(')],
            err.args[0],
            err.args[1])
        )
    else:
        # Tentativa de descompactação do conteúdo arquivado.
        try:
            GZTXT = zb.decompress(txtgz).decode('cp1252')
            return GZTXT
        except zb.error as err:
            # Reportagem de erro de descompactação do conteúdo.
            print('<<Decompressing Error>> File: ' + repr(GZFILE))
            print('  zlibError: ' + err)


def fmt_gz_file(GZTXT):
    '''
        le os arquivos GZ, formata e extrai as informações que estão
        na forma de texto
    '''

    try:
        # Substituição de tabulações por espaços.
        GZTXT = GZTXT.replace(u"\t", u" ")
        # Substituição de valores não aquisitados por 'NaN',
        # demarcados originalmente com o símbolo padrão '--'.
        GZTXT = GZTXT.replace(u"*.*", u" --")
        GZTXT = GZTXT.replace(u"*", u" ")
        GZTXT = GZTXT.replace(u" --", u" NaN")
        # Particionamento do conteúdo do arquivo em linhas.
        TXTLNS = GZTXT.splitlines()

        return TXTLNS

    except Exception as err:
        # erro ao ler o conteudo do arquivo GZ
        print(err)


def get_vars(TXTLNS, GZFILE, SYSTEM):
    '''
        Carrega os valores das variaveis escolhidas pelo usuário.

        :param TXTLNS:
        :param GZFILE:
        :param SYSTEM:  unicode string - 'EPTA' ou 'HMS'
    '''
    try:
        if SYSTEM is 'HMS':
            # Cota de instalação
            r = re.compile('Cota de instalacao do helideque')
            cota = list(filter(r.match, TXTLNS))
            # Declinação Mag
            r = re.compile('Declinacao magnetica')
            decm = list(filter(r.match, TXTLNS))
            # Sensor de atitude
            r = re.compile('Sensor de atitude')
            sens = list(filter(r.match, TXTLNS))
            # Data
            r = re.compile('Data hora da u')
            data = re.search(
                '(\d+/\d+/\d+)', list(filter(r.match, TXTLNS))[0]).group(1)
        elif SYSTEM is 'EPTA':
            # Data
            r = re.compile('Data hora da ú')
            data = re.search(
                '(\d+/\d+/\d+)', list(filter(r.match, TXTLNS))[0]).group(1)
        # Parametros de cada coluna
        r = re.compile('Hora')
        parm = re.split('\s\s+', list(filter(r.match, TXTLNS))[0])[1:]
        parm = [y for x in parm for y in x.split('. ')]
        # Unidades de medida
        r = re.compile('\s+Knots')
        unid = re.split('\s\s+', list(filter(r.match, TXTLNS))[0])[1:]
        unid = [x.replace(u'Knots', u'nós') for x in unid]
        # Unidades de medida
        r = re.compile('\s+Inst')
        freq = re.split('\s\s+', list(filter(r.match, TXTLNS))[0])[1:]
        clms = ['{} {} ({})'.format(
            parm[x], freq[x].lower(), unid[x].lower())
            for x in range(len(unid))]
        # Lendo os registros
        r = re.compile('\d{2}:\d{2}:\d{2}')
        nl = list(filter(r.match, TXTLNS))
        nn = [x.split() for x in nl]
        DATAOUT = DataFrame(nn)
        # Criando index e drop coluna de horas
        DATAOUT.index = [
            datetime.strptime('{} {}'.format(data, x[0]), "%d/%m/%Y %H:%M:%S")
            for x in DATAOUT[[0]].values]
        DATAOUT = DATAOUT.drop([0], axis=1)
        # Definindo colunas
        DATAOUT.columns = clms
        DATAOUT[clms] = DATAOUT[clms].astype(float) 
        # Convertendo em informações numéricas

        if SYSTEM is 'HMS':
            # Inserindo informações do cabeçalho
            nti = DATAOUT.shape[0]
            DATAOUT[sens[0].split(':')[0]] = [sens[0].split(':')[1]] * nti
            DATAOUT[decm[0].split(':')[0]] = [
                float(decm[0].split(':')[1])] * nti
            DATAOUT[cota[0].split(':')[0]] = [
                float(cota[0].split(':')[1])] * nti

        return DATAOUT

    except Exception as err:
        # Reportagem de erro de importação do conteúdo.
        print('<<Importing Error>> File: ' + repr(GZFILE))
        print('  {}: {}'.format(
            repr(err)[0:repr(err).find('(')],
            err)
        )


def qry(UCDNAME, DATEIN, DATEFI, SYSTEM='HMS', PATH=None):
    '''
    Consultar parâmetros e dados brutos de Posicionamento DADAS.

    :param UCDNAME: ``unicode string`` Nome da UCD.
    :param DATETIN: ``unicode string`` Data inicial - "DD/MM/YYYY HH:MI:SS"
    :param DATETFI: ``unicode string`` Data final - "DD/MM/YYYY HH:MI:SS"
    :param SYSTEM: ``unicode string`` 'HMS' ou 'EPTA'
    :param PATH: ``unicode string``
    Especificar o caminho completo de localização dos arquivos
    na forma u"C:\\..." (Windows-like) ou u"C:/..." (Unix-like)
    (ex: u"F:/SBCFS07/OCEANOP_SR/DADOS_UCDS/P40") se ele não for
    o caminho usual do banco de DESV

    :return DATAOUT: DataFrame com os dados

    '''

    FILENAMES = gen_file_list(UCDNAME, DATEIN, DATEFI, SYSTEM)

    # Definindo um DataFrame vazio para ser preenchido a cada arquivo
    DATAOUT = DataFrame()

    # Importação sequencial de parâmetros e dados armazenados em cada
    # arquivo encontrado no caminho especificado.
    for GZFILE in FILENAMES:
        # Tentativa de abertura/leitura do arquivo.
        try:
            GZTXT = get_gz_file(GZFILE)
            TXTLNS = fmt_gz_file(GZTXT)
            DATAOUT = DATAOUT.append(get_vars(TXTLNS, GZFILE, SYSTEM))
        except:
            pass

    return DATAOUT
