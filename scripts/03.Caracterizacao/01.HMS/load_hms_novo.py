'''
    Rotina que lê e plota dados de HMS ou EPTA.

    Autor: Francisco Thiago Franca Parente (BHYK)
    Data de criação: 17/09/2020

    Limites de pouso segundo NORMAN - 27/DPC
    ATITUDE     Aeronave A (Pesada)     Aeronave B (Média)
    Pitch               3°                      4°
    Roll                3°                      4°
    Inclinação        -3.5°                   -4.5°

    Limite de acordo com horário (Dia (D) / Noite (N))
    Heave            D 5 m | N 4 m           D 5 m | N 4 m
    Heave vel.   D 1.3 m/s | N 1 m/s     D 1.3 m/s | N 1 m/s

    ** ATENÇÃO **
        O gráfico desta rotina plota em hora local!
        Além disso, os dados de vento estão referenciados à 10m do Helideque.
        A mesma informação que é disposta na tela para os radio operadores.

    *** LISTA DAS UCDs COM SISTEMA HMS ***_____________________________

    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    ***________________________________________________________________________

    * Edição:
        + 12/01/2021: Modificado a forma de plotar o heave, agora é retirada a
                      média da série de heave, pois alguns casos tinham heave
                      negativo devido ao erro na cota do sensor. Além disso foi
                      adicionada a velocidade de heave no plot default.
        + 20/01/2021: Adicionado plot de vento referenciado a 10 m de altitude
                      e direção verdadeira.
        + 15/07/2021: Adicionados à tabela excel os dados de intensidade do
                      vento referenciados à 10m de altitude.
        + 27/02/2022: Inclusão da leitura e plot dos dados de EPTA.

'''
# _____________________________________________________________________________
#                               MODIFICAR AQUI
# _____________________________________________________________________________

PATH = ("xxxxxxxxxxxxxxxxxxxx")

# String da UCD de interesse (*ATENÇÃO: essa rotina só aceita uma UCD)
UCDNAME = 'PRA-1'

# Data incial de interesse UTC (fmt = 'dd/mm/YYYY HH:MM:SS)
DATEIN = '20/02/2022 14:00:00'
# Data final de interesse UTC (fmt = 'dd/mm/YYYY HH:MM:SS)
DATEFI = '21/02/2022 14:00:00'

# OPÇÃO PARA LEITURA DO SISTEMA HMS OU EPTA
SYSTEM = 'HMS'
# _____________________________________________________________________________
#                    Importando bibliotecas necessárias
# _____________________________________________________________________________

from sys import path
import matplotlib.pyplot as plt
pth1 = 'XXXXXXXXXXXXXXXXXX'
dirs = ['data', 'settings', 'math']
for d in dirs:
    pth2 = pth1 + d
    path.append(pth2)
path.append('XXXXXXXXXXXXXXXX')
import _tools
import _plot
import hmsdb
from math_tools import calc_wind_10m

import matplotlib as mpl
from datetime import timedelta, datetime
from pandas.tseries.converter import PandasAutoDateLocator
import time
from pandas import date_range, ExcelWriter, concat, DataFrame
mpl.rcParams['agg.path.chunksize'] = 10000
plt.ioff()

# _____________________________________________________________________________
#                           CARREGANDO OS DADOS
# _____________________________________________________________________________
start = time.time()
print('Início da leitura...')
DATA = hmsdb.qry(UCDNAME, DATEIN, DATEFI, SYSTEM)
print('Tempo de leitura: {} min'.format((time.time() - start) / 60))

PARAMS = list(DATA.columns)

# _____________________________________________________________________________
#               PEGANDO INFORMAÇÃO DE COTA E DECLINAÇÃO MAGNÉTICA
#                       CASO SEJA UM SENSOR DE HMS
# _____________________________________________________________________________
if SYSTEM == 'HMS':
    cota = list(set(DATA['Cota de instalacao do helideque (m)'].values))
    if len(cota) > 1:
        print("** ATENÇÃO! ** Mais de uma cota do Helideque, verificar isso!")
    else:
        cota = cota[0] + 10

    decm = list(set(DATA['Declinacao magnetica (graus)'].values))
    if len(decm) > 1:
        print("** ATENÇÃO! ** Mais de uma dec. mag., verificar isso!")
    else:
        # pegando a primeira verificada
        decm = decm[0]

# _____________________________________________________________________________
#     DEFININDO LABELS QUE SERÃO UTILIZADOS PARA ACESSO E PLOT DOS DADOS
# _____________________________________________________________________________
if SYSTEM == 'HMS':
    labels = _tools.labels_hms(cota)
elif SYSTEM == 'EPTA':
    labels = _tools.labels_epta()

# _____________________________________________________________________________
#       Ajustando indice, calculando valores adicionais e gravando excel
# _____________________________________________________________________________

excfile = ExcelWriter('{}\\{}_{}_data.xlsx'.format(PATH, UCDNAME, SYSTEM))
# Colocando dados em hora local
DATA.index = DATA.index - timedelta(hours=3)
DATA.index = DATA.index.rename("Hora Local")
if SYSTEM == 'HMS':
    DATA[labels['INT10M']] = calc_wind_10m(
        cota,
        DATA['Intensidade inst. (nós)'].values)

    DATA[labels['INT10M2MIN']] = calc_wind_10m(
        cota,
        DATA['Intensidade 2min (nós)'].values)

    DATA[labels['RAJ10M2MIN']] = calc_wind_10m(
        cota,
        DATA['Rajada 2min (nós)'].values)

    DATA = DATA.rename(
        columns={
            'Intensidade inst. (nós)': labels['INTCOTA'],
            'Intensidade 2min (nós)': labels['INTCOTA2MIN'],
            'Rajada 2min (nós)': labels['RAJCOTA2MIN']})

DATA.to_excel(excfile, sheet_name='Data 1Hz')

# _____________________________________________________________________________
#          Cálculo de média e média móvel e adicionando ao excel
# _____________________________________________________________________________
# Reindexando para conhecimento dos intervalos sem dados
if SYSTEM == 'HMS':
    mdata, rmdata = _tools.mean_and_rollingmean(
        HMSDATA=DATA,
        INTCOTA=labels['INTCOTA'],
        INT10M=labels['INT10M'],
        INTRMCOTA10MIN=labels['INTRMCOTA10MIN'],
        INTRM10M10MIN=labels['INTRM10M10MIN'],
        INTMCOTA10MIN=labels['INTMCOTA10MIN'],
        INTM10M10MIN=labels['INTM10M10MIN'],
        DIR=labels['DIR'])

    mdata.to_excel(excfile, sheet_name='Média 10min')
    rmdata.to_excel(excfile, sheet_name='Média móvel 10min')

    # Calculando média e média móvel da direção verdadeira
    df = DATA.copy()
    df[labels['DIR']] = df[
        labels['DIR']].apply(lambda x: (x + decm) % 360).values
    RMDIR = _tools.dir_media_movel(df, labels['INTCOTA'], labels['DIR'])
    MDIR = _tools.dir_media(df, labels['INTCOTA'], labels['DIR'])
excfile.close()

# _____________________________________________________________________________
#                               PLOTANDO
# _____________________________________________________________________________

xaxin = datetime.strptime(DATEIN, '%d/%m/%Y %H:%M:%S') - timedelta(hours=3)
xaxfn = datetime.strptime(DATEFI, '%d/%m/%Y %H:%M:%S') - timedelta(hours=3)

if SYSTEM == 'HMS':
    _plot.plot_hms_young_raw(
        HMSDATA=DATA,
        rmdata=rmdata,
        mdata=mdata,
        INTCOTA=labels['INTCOTA'],
        INTCOTA2MIN=labels['INTCOTA2MIN'],
        INTRMCOTA10MIN=labels['INTRMCOTA10MIN'],
        INTMCOTA10MIN=labels['INTMCOTA10MIN'],
        DIR=labels['DIR'],
        cota=cota,
        xaxin=xaxin,
        xaxfn=xaxfn,
        UCDNAME=UCDNAME,
        PATH=PATH)

    _plot.plot_hms_young_10m(
        HMSDATA=DATA,
        rmdata=rmdata,
        mdata=mdata,
        INT10M=labels['INT10M'],
        INT10M2MIN=labels['INT10M2MIN'],
        INTRM10M10MIN=labels['INTRM10M10MIN'],
        INTM10M10MIN=labels['INTM10M10MIN'],
        DIR=labels['DIR'],
        RMDIR=RMDIR,
        MDIR=MDIR,
        cota=cota,
        decm=decm,
        xaxin=xaxin,
        xaxfn=xaxfn,
        UCDNAME=UCDNAME,
        PATH=PATH)

    _plot.plot_hms_scalar(
        HMSDATA=DATA,
        xaxin=xaxin,
        xaxfn=xaxfn,
        UCDNAME=UCDNAME,
        PATH=PATH)

    _plot.plot_hms_atitude(
        HMSDATA=DATA,
        xaxin=xaxin,
        xaxfn=xaxfn,
        UCDNAME=UCDNAME,
        PATH=PATH,
        PARAMS=PARAMS)
elif SYSTEM == 'ETPA':
    _plot.plot_epta_young_raw(
        EPTADATA=DATA,
        INT=labels['INT'],
        INT2MIN=labels['INT2MIN'],
        DIR=labels['DIR'],
        xaxin=xaxin,
        xaxfn=xaxfn,
        UCDNAME=UCDNAME,
        PATH=PATH)

    _plot.plot_epta_scalar(
        EPTADATA=DATA,
        xaxin=xaxin,
        xaxfn=xaxfn,
        UCDNAME=UCDNAME,
        PATH=PATH)
