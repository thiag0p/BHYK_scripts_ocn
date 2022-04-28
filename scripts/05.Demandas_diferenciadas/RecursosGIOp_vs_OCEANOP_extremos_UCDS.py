"""
A ferramenta tem o propósito de consultar valores de mínimo e máximo de
intensidade de vento, corrente e altura significativa de onda nas UCDs,
cujas localizações sejam as mais próximas daquelas das embarcações
operadas pela GIOp-SUB durante seus períodos de parada sob aguardo das
condições meteo-oceanográficas.

O chamado "Relatório de Atividades Realizadas" fornece o intervalo de
tempo de parada e as localizações geográficas das embarcações em estado
de aguardo. Tais informações servem de referência para identificação
das UCDs mais próximas contendo dados aquisitados no período, dos quais
são computados os valores extremos. Estes valores para cada embarcação
e/ou serviço são então exportados em arquivo formatado XLSX, na chamada
"Tabela de Paradas por Condição de Mar", juntamente com seus respectivos
identificadores de UCD de referência consultada e distância radial
relativa.
"""

import sys
from io import open as ioopen
from numpy import isnan as npisnan
from numpy import arange as nparange
from numpy import array as nparray
from numpy import sqrt as npsqrt
from numpy import nan as npnan
from numpy import nanmin as npnanmin
from numpy import nanmax as npnanmax
from locale import getpreferredencoding
from collections import OrderedDict
from datetime import datetime as dtt
from datetime import timedelta as tdl
from pandas import read_excel, DataFrame
from os.path import normpath, join
from pyproj import Proj
from traceback import format_exception
import ocnpylib
sys.path.append('M:\\Rotinas\\python\\data')
import OCNdb as ocn
from warnings import filterwarnings
filterwarnings("ignore")
# _____________________________________________________________________________
#                           MODIFICAR AQUI
# _____________________________________________________________________________

TABLE = "Tabela_Paradas_Condição_de_Mar-20211226_B.xlsx"

# _____________________________________________________________________________

# Caminho completo e nomenclatura do arquivo de entrada associado ao
# "Relatório de Atividades Realizadas".
REPORTINFILEPATH = (
    'XXXXXXXXXXXXX')
REPORTINFILENAME = TABLE

# Caminho completo e nomenclatura do arquivo de saída associado à
# "Tabela de Paradas por Condição de Mar".
REPORTOUTFILEPATH = (
    'XXXXXXXXXXXXXXXXXXX')
REPORTOUTFILENAME = ("{}{}".format(TABLE.split("_B.")[0], "_proc.xls"))

# Identificação de coluna e valor de filtragem no relatório para seleção
# das embarcações de interesse.
SHIPSELECT = {"Tipo Atividade": "AGUARDANDO CONDIÇÕES METEOCEANOGRÁFICAS"}

# Colunas originais do relatório selecionadas para exportação.
REPORTEXPCOLS = ["Nr Serviço",
                 "Tipo Recurso",
                 "Recurso",
                 "Descrição Serviço",
                 "Observação",
                 "Início",
                 "Término"]

# Distância máxima para busca de dados medidos
dmaxwind = 40000      # em metros
dmaxwave = 40000      # em metros
dmaxcurr = 6000       # em metros

# Diferença entre horários locais e horário UTC.
DTUTC = -3  # em horas

# Acréscimo/decréscimo temporal na janela de consulta aos dados das UCDs
# ANTERIOR ao horário de início da parada das embarcações.
DTBEFORE = -1   # em horas

# Acréscimo/decréscimo temporal na janela de consulta aos dados das UCDs
# POSTERIOR ao horário de término da parada das embarcações.
DTAFTER = 1   # em horas

# Flag para uso na ausência de valores extremos computáveis.
NANFLAG = "-"

# Impressão do processo de execução em tela em tempo real.
VERBOSE = True

# _____________________________________________________________________________
# Atributos de configuração]

# Encoding do sistema para exportação de conteúdo.
sysencoding = getpreferredencoding()

# Grandezas físicas de interesse para computação de valores extremos.
# (a ordenação de declaração é respeitada na exportação)

quants = (
    ("Vento", {"params": 'meteo',
               "unit": "nós",
               "data": ('WSPD', float, '.0f'),
               "found": False,
               "lim": dmaxwind}),
    ("Hs Onda", {"params": 'wave',
                 "unit": "(m)",
                 "data": ('VAVH', float, '.1f'),
                 "found": False,
                 "lim": dmaxwave}),
    ("Corrente", {"params": 'curr',
                  "unit": "nós",
                  "data": ('HCSP', float, '.2f'),
                  "found": False,
                  "lim": dmaxcurr}))

# _____________________________________________________________________________
#                   Definições e arranjos iniciais
# _____________________________________________________________________________
# Normalização de caminho completo ao relatório de entrada.
repinfullfn = join(normpath(REPORTINFILEPATH), REPORTINFILENAME)

# Normalização de caminho completo ao relatório de saída.
repoutfullfn = join(normpath(REPORTOUTFILEPATH), REPORTOUTFILENAME)

# Cabeçalho identificador do contexto de execução.
loggmsg = ("{:s}{:s}\n{:s} + log filename: **empty log file**\n".format(
    "| " + str(dtt.now()).ljust(26, "0") + " | ",
    42 * "+",
    30 * " ") +
    "{:s} + input filename: {:s}\n".format(
    30 * " ",
    repinfullfn) +
    "{:s} + output filename: {:s}\n".format(
    30 * " ",
    repoutfullfn) +
    "{:s} + local timezone: {:s} hours\n".format(
    30 * " ",
    str(DTUTC)) +
    "{:s} + data time shift".format(
    30 * " ") +
    " before ship stop: {:s} hours\n".format(
    str(DTBEFORE)) +
    "{:s} + data time shift".format(
    30 * " ") +
    " after ship stop: {:s} hours\n".format(
    str(DTAFTER)) +
    "{:s} + quantities: {:s}\n".format(
    30 * " ",
    str(list([x[0] for x in quants]))[1:-1]) +
    "{:s} {:s}".format(
    30 * " ",
    42 * "+"))
# Impressão em tela.
if VERBOSE:
    print(loggmsg)
# Tentativa de importação do relatório.
loggmsg = ("{:s}Input report check \"{:s}\" ...\n".format(
    "| " + str(dtt.now()).ljust(26, "0") +
    " | ",
    REPORTINFILENAME))
if VERBOSE:
    print((loggmsg), end=' ')
try:
    rep = read_excel(repinfullfn, header=3, skiprows=0)
except Exception as err:
    loggmsg = "[ERROR]"
    # Impressão em tela.
    if VERBOSE:
        print(loggmsg)
    raise err
else:
    loggmsg = "{:s}{:s}".format(
        "| " + str(dtt.now()).ljust(26, "0") + " | ",
        "Leitura tabela de Atividades bem sucedida")
    # Impressão em tela.
    if VERBOSE:
        print(loggmsg)

# Seleção de linhas conforme critério de filtragem por coluna.
shiprows = rep[list(SHIPSELECT.keys())[0]] == list(SHIPSELECT.values())[0]
# Seleção de colunas para computação explícita de períodos de
# duração das paradas e distâncias radiais das embarcações às UCDs.
repfiltcols = list(REPORTEXPCOLS)
for column in ["Início", "Término", "Coord. Leste",
               "Coord. Norte", "Merid. Central"]:
    if column not in repfiltcols:
        repfiltcols.append(column)
# Relatório de trabalho filtrado.
repfilt = rep.loc[shiprows][repfiltcols]
# Tradução em dicionário para facilitação de manipulação.
shipstops = repfilt.T.to_dict()
# Consulta de identificadores, nomes e localizações das UCDs.
loggmsg = ("{:s}{:s}\n{:s} + Total de apontamentos: {}\n".format(
    "| " + str(dtt.now()).ljust(26, "0") + " | ",
    42 * "+",
    30 * " ",
    len(shipstops)))
if VERBOSE:
    print((loggmsg), end=' ')

# _____________________________________________________________________________
#                       Pegando informações das UCDS
# _____________________________________________________________________________
# Todos os ID_LOCAL
id_local = ocnpylib.SECRET()
# As bacias de cada
coord = ocnpylib.SECRET(id_local)
# Retirando UCDs inválidas
try:
    while coord.index(None):
        ix = coord.index(None)
        id_local.pop(ix)
        coord.pop(ix)
except Exception:
    pass
# Conversão a arrays para facilitação de operações futuras.
ucdnames = nparray(ocnpylib.SECRET(id_local))
ucdcoords = (nparray([point[0] for point in coord]),
             nparray([point[1] for point in coord]))

# _____________________________________________________________________________
# Inclusão do período de parada da embarcação ao relatório de saída
# caso a coluna original não esteja declarada explicitamente para
# exportação.
colnmtstop = "Duração"
colnmtstopadd = False

if colnmtstop not in REPORTEXPCOLS:
    REPORTEXPCOLS.append(colnmtstop)
    colnmtstopadd = True

# _____________________________________________________________________________
#                       Laço principal sobre embarcações
# _____________________________________________________________________________

# Para cada embarcação em aguardo, presente no relatório filtrado,
# são computadas as distâncias relativas a cada UCD nas quais os
# valores extremos dos dados são consultados por grandeza física e
# por equipamento de interesse.
for shpidx, (shp, shpinfo) in enumerate(shipstops.items()):

    loggmsg = ("{:s}{:s}\n{:30} + Apontamento: {} de {}\n".format(
        "| " + str(dtt.now()).ljust(26, "0") + " | ",
        42 * "+",
        " ",
        shpidx + 1,
        len(shipstops)) + "{:30} + Recurso: {}\n".format(
        " ",
        shpinfo["Recurso"]) + "{:30} + {}\n".format(
        " ",
        shpinfo["Descrição Serviço"]) + "{:30} + Início: {}\n".format(
        " ",
        shpinfo["Início"]) + "{:30} + Fim: {}\n".format(
        " ",
        shpinfo["Término"]) +
        "{:30} + Coord (E, N, Central - UTM): {:d}, {:d}, {:+d}\n".format(
        " ",
        int(shpinfo["Coord. Leste"]),
        int(shpinfo["Coord. Norte"]),
        int(-shpinfo["Merid. Central"])))
    # Impressão em tela.
    if VERBOSE:
        print(loggmsg)

    # Definição de projeção cartográfica usual da embarcação.
    # Referências sobre DATUM e declarações em Proj4:
    #
    #   SIRGAS 2000 / UTM zone 23S (central_meridian -45)
    #   EPSG:31983 - http://spatialreference.org/ref/epsg/31983/
    #
    #   SIRGAS 2000 / UTM zone 24S (central_meridian -39)
    #   EPSG:31984 - http://spatialreference.org/ref/epsg/31984/
    prjct = Proj(
        "+proj=utm " +
        "+lon_0={:d} ".format(int(-shpinfo["Merid. Central"])) +
        "+south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs")

    # Representação de longitudes e latitudes das UCDs na projeção
    # usualmente adotada pelas embarcações.
    # utmy, utmx = prjct(ucdcoords[:, 0], ucdcoords[:, 1])
    utmy, utmx = prjct(ucdcoords[0],
                       ucdcoords[1])

    # Distâncias relativas entre embarcação e UCDs.
    dst = npsqrt((shpinfo["Coord. Leste"] - utmx) ** 2 +
                 (shpinfo["Coord. Norte"] - utmy) ** 2)

    # Distâncias ordenadas por proximidade geográfica.
    dstord = dst.argsort()

    # Armazenamento temporário das informações de consulta para cada
    # par de valores extremos computados com sucesso.
    linfo = len(quants) * ["[" + NANFLAG + "]"]

    # Computação, formatação e agregação do período de parada da
    # embarcação ao relatório de saída caso a coluna original não
    # esteja declarada explicitamente para exportação.
    if colnmtstopadd:
        # Duração do período de parada da embarcação.
        stoptw = (dtt.strptime(shpinfo["Término"], "%d/%m/%Y %H:%M") -
                  dtt.strptime(shpinfo["Início"], "%d/%m/%Y %H:%M"))

        # Formatação em 'HH:MM' do período de parada da embarcação.
        stoptwf = "{:d}:{:02d}".format(
            int(stoptw.total_seconds() / (3600)),
            int(stoptw.total_seconds() % (3600) / 60))

        # Agregação do período de parada da embarcação ao relatório
        # de saída.
        shipstops[shp][colnmtstop] = stoptwf

    # [Laço secundário sobre UCDs] -------------------------------
    # ============================================================ #

    # Para cada UCD, iniciando pela mais próxima geograficamente,
    # são consultados dados existentes e computados os extremos para
    # cada grandeza física dentro do período de parada da embarcação.
    # Quando não há dados disponíveis para determinada grandeza na UCD mais
    # próxima, os mesmos são buscados nas subsequentes até que todos valores
    # extremos sejam computados ou até que todas UCDs sejam
    # consultadas sem que dados sejam localizados.
    for ucd, ds in zip(ucdnames[dstord], dst[dstord]):

        # [Laço terciário sobre grandezas físicas] ---------------
        # ======================================================== #
        for i in nparange(len(quants)):
            quant = quants[i][0]
            qinfo = quants[i][1]

            # Declaração e agregação temporária do valor extremo
            # mínimo da grandeza física ao relatório de saída.
            colnmmin = quant + " Min " + qinfo["unit"]

            if colnmmin not in REPORTEXPCOLS:
                REPORTEXPCOLS.append(colnmmin)
                shipstops[shp][colnmmin] = npnan

            # Declaração e agregação temporária do valor extremo
            # máximo da grandeza física ao relatório de saída.
            colnmmax = quant + " Max " + qinfo["unit"]

            if colnmmax not in REPORTEXPCOLS:
                REPORTEXPCOLS.append(colnmmax)
                shipstops[shp][colnmmax] = npnan

            # Consulta condicional aos dados de outro equipamento
            # caso nenhum dado tenha sido identificado nos
            # anteriores.
            if not qinfo["found"] and ds < qinfo["lim"]:
                # Valores extremos são computados se há dados
                # disponíveis para o respectivo equipamento.
                # Ocorrência de exceções resultam na consulta ao
                # próximo equipamento.
                try:
                    # Janela temporal de consulta.
                    tini = (dtt.strptime(
                        shpinfo["Início"],
                        "%d/%m/%Y %H:%M") + tdl(hours=-DTUTC + DTBEFORE))

                    tfin = (dtt.strptime(
                        shpinfo["Término"],
                        "%d/%m/%Y %H:%M") + tdl(hours=-DTUTC + DTAFTER))
                    # Consulta aos dados.
                    data = ocn.get_BD(
                        [ucd],
                        [tini.strftime("%d/%m/%Y %H:00:00"),
                         tfin.strftime("%d/%m/%Y %H:00:00")],
                        qinfo["params"])
                    if data.shape[0] > 1:

                        # Excluindo os levels do Multiindex desnecessários
                        if qinfo['params'] in ['curr']:
                            data = data.loc[ucd].droplevel(
                                [0, 1])[qinfo['data'][0]].to_frame()
                        else:
                            data = data.loc[ucd].droplevel(
                                [0])[qinfo['data'][0]].to_frame()

                        # Escrevendo no terminal
                        loggmsg = ("{:30} + {}: Dado encontrado em {}".format(
                            " ",
                            quant,
                            ucd) + " (dist = {:.2f}km)\n".format(ds / 1000) +
                            "{:30} + Período avaliado: {} - {}".format(
                                " ",
                                (data.index[0] + tdl(hours=DTUTC)).strftime(
                                    "%d/%m/%Y %H:00:00"),
                                (data.index[-1] + tdl(hours=DTUTC)).strftime(
                                    "%d/%m/%Y %H:00:00")
                            )
                        )
                        if VERBOSE:
                            print(loggmsg)

                        # Convertendo para unidade de medida em nós
                        if qinfo['params'] in ['meteo', 'curr']:
                            data[qinfo['data'][0]] = data[
                                qinfo['data'][0]] * 1.94384449
                except Exception:
                    # Captura e exibição de exceção geral.
                    errtype, errvalue, errtbk = sys.exc_info()
                    tbkmsg = format_exception(
                        errtype, errvalue, errtbk)
                    loggmsg = ("{:30} +     **ERRO** >> {}{}\n".format(
                        " ",
                        errtype, errvalue))
                    # Impressão em tela.
                    if VERBOSE:
                        print(loggmsg)
                else:
                    if data.shape[0] > 1:
                        if npisnan(list(data.values)).all():
                            # Dados faltantes no banco (só NaNs).
                            loggmsg = (
                                "{:30} + {}\n".format(
                                    " ",
                                    "    NaN found only."))
                            # Impressão em tela.
                            if VERBOSE:
                                print(loggmsg)
                        else:
                            # Computação valor mínimo escalado.
                            mdata = (npnanmin(data))
                            shipstops[shp][colnmmin] = mdata

                            # Computação valor máximo escalado.
                            mdata = npnanmax(data)
                            shipstops[shp][colnmmax] = mdata

                            # Informações da consulta.
                            linfo[i] = (
                                "[" + ucd + "|" + "{:.3f}".format(ds) +
                                " m]")

                            # Remarcação de flag para dados encontrados
                            # e valores extremos computados.
                            qinfo["found"] = True
            # Interrupção explícita do laço secundário se todos valores
            # extremos já foram computados e nenhuma outra UCD necessita ser
            # consultada.
            if nparray([quants[i][1]["found"]
                        for i in nparange(len(quants))]).all():
                break
    # Agregação das informações de consulta ao relatório de saída.
    colnminfo = "Info"
    if colnminfo not in REPORTEXPCOLS:
        REPORTEXPCOLS.append(colnminfo)
    shipstops[shp][colnminfo] = " ".join(linfo)

    # Reinicialização de flags de consulta.
    for i in nparange(len(quants)):
        quants[i][1]["found"] = False

# Exportação da "Tabela de Paradas por Condição de Mar".
loggmsg = ("{:s}reporting to \"{:s}\" ...".format(
    "| " + str(dtt.now()).ljust(26, "0") + " | ",
    REPORTOUTFILENAME))

# Impressão em tela.
if VERBOSE:
    print((loggmsg), end=' ')

try:
    repout = DataFrame.from_dict(shipstops, orient='index')
    repout.to_excel(repoutfullfn,
                    na_rep=NANFLAG,
                    columns=REPORTEXPCOLS,
                    index=False)
except Exception as err:
    loggmsg = "[ERROR]"
    # Impressão em tela.
    if VERBOSE:
        print(loggmsg)
    raise err
else:
    loggmsg = ("[DONE]\n{:s}{:s}".format(
        "| " + str(dtt.now()).ljust(26, "0") + " | ",
        42 * "+"))
    # Impressão em tela.
    if VERBOSE:
        print(loggmsg)
input("Press <ENTER> key to exit...")
