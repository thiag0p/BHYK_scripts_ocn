'''

    Rotina que lê dados de precipitação (GPM FINAL RUN), dados de vento 
    e onda do BD OCN e calcula o percentual de registros em um intervalo de
    interesse, tanto para cada parametro individual quando para os três
    simultanemanete.

    Vale ressaltar que esta rotina foi criada para o suporte as paradas
    programadas, com isso os dados de vento são rebatido para a altua de
    trabalho fornecida pelo usuário na variável HOP.

    Atualmente ela trabalha somente com um limite operacional para cada
    parametro. Ainda, é o usado o sinal de igualdade para o limite de chuva,
    atenção para isso. Foi usado isso inicialmente pois tinha o interesse de
    saber o percentual de dias secos, ou seja, chuva==0.

    Autor: Francisco Thiago Franca Parente (BHYK)
    Data de criação: 08/03/2021
    Versão: 1.0

'''
import numpy as np
# _____________________________________________________________________________
#                               Modificar aqui
# _____________________________________________________________________________
# Diretório onde serão salvos os resultados
path = (u"XXXXXXXXXXXXXXXX")

# UCD de interesse
ucdwind = ['XXXXXXXXXXXX']
ucdwave = ['XXXXXXXXXXXX']

# Data inicial e Data final da busca
datemin = u"01/01/2019 03:00:00"
datemax = u"31/03/2019 23:00:00"

# Altura de trabalho
HOP = 70.

# Limites
limit_vento = 21.6
limit_onda = 3.

# Limite de chuva seguindo critério do WMO
limit_chuva = 0 # [0, 0.1, 0.5, 2.5, 10., 50.]

# Convertendo limites para altura de trabalho
WND_LIM10 = limit_vento / (1 + 0.137 * np.log(HOP / 10.))

# _____________________________________________________________________________

import xarray
from datetime import datetime as dt
import ocnpylib as ocpy
from pandas import ExcelWriter, date_range, concat, DataFrame
from sys import path as syspath

pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data', 'math']
for d in dirs:
    pth2 = pth1 + d
    syspath.append(pth2)
import OCNdb as ocn
import statistic as stc
# _____________________________________________________________________________

opendap_link = (
    'http://XXXXXXXXXXXXXXXXXXXX')

print("{:<55} | {:^20}".format("Lendo dados de precipitação", ucdwind[0]))

precip = xarray.open_dataset(opendap_link)

DATERANGE = date_range(dt.strptime(datemin, '%d/%m/%Y %H:%M:%S'),
                       dt.strptime(datemax, '%d/%m/%Y %H:%M:%S'),
                       freq='H')
print("{:<55} | {:^20}".format(precip.institution, ""))
print("{:<55} | {:^20}".format(precip.title, ""))

# _____________________________________________________________________________
# Lendo dados de precipitação
# procura lat e lon da UCD
id_ucd = ocpy.SECRET(ucdwind)
coord = ocpy.SECRET(id_ucd)
# Seleção de uma lat e lon e busca ponto proximo
chuva = precip.sel(
    latitude=coord[1],
    longitude=coord[0],
    method='nearest',
    time=DATERANGE)
chuva = chuva.to_dataframe()

print("{:_<55} | {:^20}".format("", "Ok"))

# _____________________________________________________________________________
# Lendo dados de vento e onda

print("{:<55} | {:^20}".format("Lendo BD OCEANOP", " "))

vento = ocn.get_BDs(ucdwind, [datemin, datemax], 'meteo').droplevel(
    [0, 1]).WSPD.to_frame() * 1.94384449
print("{:<55} | {:^20}".format("* Vento - " + ucdwind[0], "Ok"))

onda = ocn.get_BDs(ucdwave, [datemin, datemax], 'wave').droplevel(
    [0, 1]).VAVH.to_frame()
print("{:<55} | {:^20}".format("* Onda " + ucdwave[0], "Ok"))

# _____________________________________________________________________________
# Colocando ambos no mesmo DataFrame

df = concat([
    chuva.drop(['longitude', 'latitude'], axis=1),
    vento,
    onda],
    axis=1)

# Pegando somente o período em que ambos possuem dados
data = df.dropna(how='any')

timesize = len(date_range(
    dt.strptime(datemin, '%d/%m/%Y %H:%M:%S'),
    dt.strptime(datemax, '%d/%m/%Y %H:%M:%S'),
    freq='H'))

print("{:<55} | {:^20}".format("Período avaliado", ""))
print("{:>26} - {:<26} | {:^20}".format(
    data.index[0].strftime('%d/%m/%Y %H'),
    data.index[-1].strftime('%d/%m/%Y %H'), ""))
print("{:<55} | {:^20}".format("Percentual de tempo registrado", ""))
print("{:>54}% | {:^20}".format(
    round((data.shape[0] / timesize) * 100, 1), ""))

# _____________________________________________________________________________
# Fazendo análise mensal

# Labels dos meses do ano
MNTHLBL = ('Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
           'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez')

pevent = DataFrame()

for x in np.unique(data.index.month):
    wavslc = onda[onda.index.month == x]
    widslc = vento[vento.index.month == x]
    chuslc = chuva[chuva.index.month == x]
    allslc = data[data.index.month == x]

    eventos_chuva = chuslc[chuslc.prec1h == limit_chuva]
    eventos_vento = widslc[widslc.WSPD < WND_LIM10]
    eventos_onda = wavslc[wavslc.VAVH < limit_onda]

    event1 = allslc[(allslc.prec1h == limit_chuva) &
        (allslc.WSPD < WND_LIM10) &
        (allslc.VAVH < limit_onda)]

    pevent = pevent.append(DataFrame(
        {
            'Vento < {} nós | Hs < {} m | Dias seco'.format(WND_LIM10,
                                                            limit_onda):
            event1.count()[0] / allslc.count()[0] * 100,
            'Onda < {} m'.format(limit_onda):
            eventos_onda.count()[0] / wavslc.count()[0] * 100,
            'Vento < {} nós'.format(WND_LIM10):
            eventos_vento.count()[0] / widslc.count()[0] * 100,
            'Dias Secos':
            eventos_chuva.count()[0] / chuslc.count()[0] * 100},
        index=[MNTHLBL[x-1]]))

pevent = pevent.round(2)
# Escrevendo na tabela excel
tab = ExcelWriter(path + '\Percentual_cruzado.xlsx')
pevent.to_excel(tab)
tab.close()
