# -*- coding: utf-8 -*-
'''
    Compara os dados de corrente coletados a bordo das
    embarcações com os dados medidos pelos sensores de corrente
    da OCN.

    Autor: Francisco Thiago Parente (BHYK)
    Criação: 03/09/2020

    * Modificações:__________________________________________________
    
        * ATENÇÃO: esta rotina é um ajuste de python 2.7 para 3.6. Com isso,
        herdou os ajustes ocorridos anteriormente. 
        
        + 22/10/2018 (AL4N) - sistema de 'chaves' para determinar se o dado OCN
        vem de ADCP (HADCP) ou FSI (2D ou 3D);
        Padronização do dataframe gerado (OCNP) para qualquer um destes
        equipamentos; uso de planilha excel vinda do barco, não arquivo csv.

        + 26/11/2018 (AL4N) - BOATUNIT inserida para caso a unidade da medição
        do barco seja em nós - atualiza a unidade das figuras e muda a do
        sensor OCN.
'''

# _____________________________________________________________________________
#                               MODIFICAR AQUI
# _____________________________________________________________________________

# Diretório do relatório
PATH = ("XXXXXXXXXXXXXXXXXXXXXXX")
# Nome da embarcação
NAME = "TOP Coral do Atlântico"

# Arquivo da embarcação com extensão (Ex. "NomeDoArquivo.xlsx")
BOATFILE = 'Anexo_3-Planilha_Teste_Correntometro_TCA.xlsx'
# Unidade de medida dos dados da embarcação
# 'cm/s', 'm/s' ou 'nós'
BOATUNIT = 'm/s'

# Intrumento para comparação
INSTR = 'FSI-3D'

# Arquivos dos dados de corrente do FSI, ADCP ou HADCP e FSI
# ** ATENÇÃO ** Os arquivos são nomeados em hora UTC!
UCDFILE = [
    "XXXXXXXXXXXXXXX.CSV"]
# ADCP
# UCDFILE = ["P61_ADCP_camada0_singleping.txt"]

# Unidade de medida em que os dados da UCD foram medidos/'cm/s','m/s' ou 'nós'
UCDUNIT = 'cm/s'

# Definição da referência de tempo ('LOCAL' ou 'UTC')
UCDTIME = 'LOCAL'

# # Data de criação do(s) arquivo(s) gerado(s) para o caso do ADCP
# DATAFI = ["03/08/2019 17:45:10"]
# # Datas inciais e finais dos arquivos de FSI
# DTI = ["04/07/2019 15:33:00", "04/07/2019 17:06:00"]
# DTF = ["04/07/2019 16:33:46", "04/07/2019 17:36:03"]

# Programa de armezanamento dos dados (SISMO ou DADAS)
SFTWR = "DADAS"
# SFTWR = "SISMO"

# Formato da data caso as células de data não sejam strings
datefmt = '%Y-%m-%d'

# _____________________________________________________________________________
#                         Carregando bibliotecas necessárias
# _____________________________________________________________________________

from os.path import join
import datetime as dt
from pandas import to_datetime, DataFrame
from pandas import read_excel, read_table, date_range
import numpy as np
import matplotlib.pyplot as plt
from ocnpylib import id2uv, uv2id
from sys import path
from matplotlib.dates import DateFormatter

pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'graph', 'math']
for d in dirs:
    pth2 = pth1 + d
    path.append(pth2)

import OCNdb as ocn
import rawdata
from statistic import movingaverage
from datetime import timedelta


plt.rc('font', family='Arial')

# _____________________________________________________________________________
#     Definindo fator de conversão dos dados de intensidade da embarcação
# _____________________________________________________________________________

if BOATUNIT.lower() == 'm/s':
    BFATOR = 1
elif BOATUNIT.lower() == 'cm/s':
    BFATOR = .01
else:
    BFATOR = 1 / 1.94384

if UCDUNIT.lower() == 'm/s':
    UFATOR = 1
elif UCDUNIT.lower() == 'cm/s':
    UFATOR = .01
else:
    UFATOR = 1 / 1.94384

# _____________________________________________________________________________
#                         Lendo Dados do OCEANOP
# _____________________________________________________________________________

# Lendo dados do FSI2D
if "FSI" in INSTR:
    if SFTWR == "SISMO" or SFTWR == "FSIOCN":
        try:
            # Primeiro tenta ler com as colunas de data do arquivo bruto
            FSIDATA = rawdata.read_fsi2d_log_SISMO(PATH, UCDFILE, ",")
        except Exception:
            # Caso o arquivo nao tenha data, cria o indice com as datas
            # fornecidas pelo usuario
            FSIDATA = rawdata.read_fsi2d_log_SISMO(PATH,
                                                   UCDFILE,
                                                   ",",
                                                   DTI,
                                                   DTF,
                                                   "S")
    else:
        FSIDATA = rawdata.read_fsi2d_DADAS(PATH, UCDFILE)

    # Ajuste no horário
    #    FSIDATA.index = FSIDATA.index - dt.timedelta(hours=1)

    # # check se todos os dados são float
    # for ck in range(FSIDATA.shape[0]):
    #     FSIDATA.VN[ck] = float(FSIDATA.VN[ck])
    #     FSIDATA.VE[ck] = float(FSIDATA.VE[ck])

    OCNP = DataFrame(
        data={
            'Speed': uv2id(FSIDATA.VE, FSIDATA.VN, 'ocean')[0],
            'Direction': uv2id(FSIDATA.VE, FSIDATA.VN, 'ocean')[1],
            'U': FSIDATA.VE,
            'V': FSIDATA.VN},
        index=FSIDATA.index)

if "ADCP" in INSTR:
    OCNP = DataFrame()

    # Lendo dados do ADCP
    for idx, arq in enumerate(UCDFILE):
        INT, DIR, U, V, TIME = [], [], [], [], []

        ADCPDATA = read_table(join(PATH, arq), header=10)
        ADCPDATA = ADCPDATA.iloc[2:]
        for x in range(len(ADCPDATA)):
            TIME.append(dt.datetime(2000 + int(ADCPDATA.YR.values[x]),
                                    int(ADCPDATA.MO.values[x]),
                                    int(ADCPDATA.DA.values[x]),
                                    int(ADCPDATA.HH.values[x]),
                                    int(ADCPDATA.MM.values[x]),
                                    int(ADCPDATA.SS.values[x])))
            INT.append(float(ADCPDATA.Mag.values[x]) / 1000.)
            if isinstance(ADCPDATA.Dir.values[x], str):
                DIR.append(float(ADCPDATA.Dir.values[x].replace(',', '.')))
            else:
                DIR.append(np.nan)
            U.append(float(ADCPDATA.Eas.values[x]) / 1000.)
            V.append(float(ADCPDATA.Nor.values[x]) / 1000.)

        # ~ Ajustando o horário
        DFT = dt.datetime.strptime(DATAFI[idx], "%d/%m/%Y %H:%M:%S")
        intrv = TIME[1] - TIME[0]
        delta = TIME[-1] - TIME[0]
        dti = DFT - delta

        OCNP = OCNP.append(DataFrame(data={'Speed': INT,
                                           'Direction': DIR,
                                           'U': U,
                                           'V': V},
                                     index=date_range(dti, DFT, freq=intrv)))
    OCNP.dropna(axis='index', how='all', inplace=True)


# _____________________________________________________________________________
#              Ajutando o tempo dos nosso dados para hora local
# _____________________________________________________________________________
if UCDTIME.upper() == 'UTC':
    OCNP.index = OCNP.index - timedelta(hours=3)
# Convertendo para m/s os dados da UCD de acordo com
# unidade de medida informada
OCNP.Speed = OCNP.Speed * UFATOR
# _____________________________________________________________________________
#                               DADOS DA EMBARCAÇÃO
# _____________________________________________________________________________

try:
    BOAT = read_excel(join(PATH, BOATFILE),
                      skiprows=14)
except Exception as err:
    print('Erro ao ler a planilha enviada pelo barco.\n' +
          'Verifique a formatação da planilha')

# Convertendo para m/s os dados do barco de acordo com
# unidade de medida informada
BOAT.Speed = BOAT.Speed * BFATOR
dateclm = [x for x in BOAT.columns if 'DATE' in x.upper()][0]
hourclm = [x for x in BOAT.columns if 'TIME' in x.upper()][0]
try:
    BOAT.index = to_datetime(['{} {}'.format(
        BOAT[dateclm][x][0:10],
        BOAT[hourclm][x]) for x in range(len(BOAT))])
except:
    try:
        BOAT.index = to_datetime([
            '{} {}'.format(
                dt.datetime.strftime(BOAT[dateclm][x], datefmt),
                BOAT[hourclm][x].strftime('%H:%M:%S'))
            for x in range(len(BOAT))])
    except Exception:
        raise RuntimeError('Erro na formatação da data!')

BOAT = BOAT.drop([dateclm, hourclm], axis=1)

BOAT = BOAT[~BOAT.index.duplicated()]

BOAT[u"U"], BOAT[u"V"] = id2uv(BOAT['Speed'],
                               BOAT['Direction'],
                               str_conv='ocean')

# _____________________________________________________________________________
#                           MÉDIA MÓVEL DE 1 MIN
# _____________________________________________________________________________

# Retirando indices duplicados
OCNP = OCNP[~OCNP.index.duplicated()]
BOAT = BOAT[~BOAT.index.duplicated()]

dt_boat = BOAT.index[1] - BOAT.index[0]
dt_ocnp = OCNP.index[2] - OCNP.index[1]

# média da velocidade
OCNP[u"Mean spd"] = movingaverage(OCNP[u"Speed"], 60 / dt_ocnp.seconds)
BOAT["Mean spd"] = movingaverage(BOAT[u"Speed"], 60 / dt_boat.seconds)
# média da direção
OCNP[u"Mean dir"] = uv2id(
    movingaverage(OCNP[u"U"],
                  60 / dt_ocnp.seconds),
    movingaverage(OCNP[u"V"],
                  60 / dt_ocnp.seconds),
    str_conv="ocean")[1]

BOAT["Mean dir"] = uv2id(
    movingaverage(BOAT[u"U"], 60 / dt_boat.seconds),
    movingaverage(BOAT[u"V"], 60 / dt_boat.seconds),
    str_conv="ocean")[1]

# _____________________________________________________________________________
#                                   PLOTANDO
# _____________________________________________________________________________

fig = plt.figure(figsize=(15, 12))
ax = plt.subplot(2, 1, 1)
try:
    ax.plot(OCNP[u"Speed"][BOAT.index[0]:BOAT.index[-1]].index,
            OCNP[u"Speed"][BOAT.index[0]:BOAT.index[-1]],
            alpha=.4, color="#E24A33")
    ax.plot(OCNP[u"Mean spd"][BOAT.index[0]:BOAT.index[-1]].index,
            OCNP[u"Mean spd"][BOAT.index[0]:BOAT.index[-1]],
            color="#E24A33")
except Exception:
    print('Não há dados no mesmo período para os dois bancos de dados!')

ax.plot(BOAT.index, BOAT[u"Speed"], alpha=.4, color="#348ABD")
ax.plot(BOAT.index, BOAT["Mean spd"], color="#348ABD")

# informações gráficas
ax.grid(axis='both')
ax.set_ylabel('Intensidade (m/s)', fontsize=12)
labels = [item.get_text() for item in ax.get_xticklabels()]
empty_string_labels = [''] * len(labels)
ax.set_xticklabels(empty_string_labels)

ax = plt.subplot(2, 1, 2)
try:
    ax.plot(OCNP['Direction'][BOAT.index[0]:BOAT.index[-1]].index,
            OCNP['Direction'][BOAT.index[0]:BOAT.index[-1]],
            label="OCN", alpha=.4, color='#E24A33')
    ax.plot(OCNP['Mean dir'][BOAT.index[0]:BOAT.index[-1]].index,
            OCNP['Mean dir'][BOAT.index[0]:BOAT.index[-1]],
            color='#E24A33')
except Exception:
    print('Não há dados no mesmo período para os dois bancos de dados!')

ax.plot(BOAT.index, BOAT['Direction'], label=NAME, alpha=.4, color='#348ABD')
ax.plot(BOAT.index, BOAT['Mean dir'], color='#348ABD')

# Formatação do eixo de tempo
ax.xaxis.set_major_formatter(DateFormatter('%d/%m%Y\n %H:%M:%S'))

# informações gráficas
ax.grid(axis='both')
ax.set_ylabel('Direção (°)', fontsize=12)

ax.set_ylim(0, 360)
ax.set_yticks(np.arange(0, 361, 90))

# Posicionando e plotando legenda
if len(ax.lines) == 2:
    lgd = ax.legend(ax.lines,
                    [NAME + " (1 Hz)", NAME],
                    ncol=2,
                    fontsize=12,
                    loc='upper center',
                    bbox_to_anchor=(0.5, -0.1),
                    fancybox=True,
                    shadow=True)
else:
    lgd = ax.legend([ax.lines[1], ax.lines[-1]],
                    ["OCN", NAME],
                    ncol=2,
                    fontsize=12,
                    loc='upper center',
                    bbox_to_anchor=(0.5, -0.1),
                    fancybox=True,
                    shadow=True)

fig.savefig(PATH + '\\comparacao' + INSTR + '.png',
            bbox_extra_artists=(lgd,),
            bbox_inches='tight',
            format='png')

# _____________________________________________________________________________
#                                   PLOTANDO
# _____________________________________________________________________________

# Diferença absoluta media
try:
    SPD_DIF = np.mean(np.abs(OCNP["Mean spd"] - BOAT["Mean spd"]).dropna())
    DIR_DIF = np.mean(np.abs(OCNP["Mean dir"] - BOAT["Mean dir"]).dropna())

except Exception:
    print('Não há dados no mesmo período para os dois bancos de dados!')

print('{}: {}'.format('Diferença média vel.', SPD_DIF))
print('{}: {}'.format('Diferença média dir.', DIR_DIF))
