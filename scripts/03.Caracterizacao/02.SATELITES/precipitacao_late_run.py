'''

    Rotina de Leitura de dados de precipitação

    title:          GPM - Global Precipitation Measurement
    institution:    NASA - National Aeronautics and Space Administration
    source:         Remote Sensing
    history:        2020-01-10T20:14:21Z: nasa_gpm_fix.py
    references:     https://www.nasa.gov/mission_pages/GPM/main/index.html
    conventions:    CF-1.7Global Precipitation Measurement

    Autor: Francisco Thiago Franca Parente (BHYK)
    Data de criação: 21/02/2020
    Versão: 1.0

'''

# _____________________________________________________________________________
#                                   MODIFICAR AQUI
# _____________________________________________________________________________

path = ("xxxxxxxxxxxxxxxx")

UCDS = ['xxxxxxxxxxxxx']

DATEINI = "02/03/2020 00:00:00"
DATEFIN = "05/03/2020 23:00:00"

# Frequência amostral (Opções: 'H' -> HORÁRIA / 'D' -> Acumulado 24h)
freq = 'D'

# _____________________________________________________________________________
#                       IMPORTANDO BIBLIOTECAS
# _____________________________________________________________________________

import xarray
from datetime import datetime as dt
import ocnpylib as ocpy
from pandas import ExcelWriter, date_range

opendap_link = (
    'xxxxxxxxxxxxxxxxxx',
    'xxxxxxxxxxxxxxxxxx')

# _____________________________________________________________________________
#                LENDO E EXPORTANDO DADOS EM EXCEL
# _____________________________________________________________________________

# Lendo o opendap.
if freq is "D":
    print('{}'.format(80*'#'))
    print('{}{:^76}{}'.format(
        2*'#', 'Lendo acumulado de precipitação de 24h', 2*'#'))
    print('{}{:^76}{}'.format(
        2*'#', opendap_link[0], 2*'#'))
    ds = xarray.open_dataset(opendap_link[0])
elif freq is "H":
    print('{}'.format(80*'#'))
    print('{}{:^76}{}'.format(
        2*'#', 'Lendo dado horário de precipitação', 2*'#'))
    print('{}{:^76}{}'.format(
        2*'#', opendap_link[1], 2*'#'))
    ds = xarray.open_dataset(opendap_link[1])
else:
    raise RuntimeError("**ERRO** | Verificar linhas 29 e 30.")

# Definindo intervalo de tempo de interesse.
DATERANGE = date_range(dt.strptime(DATEINI, '%d/%m/%Y %H:%M:%S'),
                       dt.strptime(DATEFIN, '%d/%m/%Y %H:%M:%S'),
                       freq=freq)

# # Selecionando um domínio
# bacia = ds.sel(latitude=slice(BC[2], BC[3]),
#                longitude=slice(BC[0], BC[1]),
#                time=DATERANGE)

tab = ExcelWriter(path + '\dfpitacao.xlsx')
for ucd in UCDS:
    # procura lat e lon da UCD
    id_ucd = ocpy.SECRET(ucd)
    coord = ocpy.SECRET(id_ucd) 

    print('{}  {:<74}{}'.format(
        2*'#', 'Consulta por ' + ocpy.SECRET(id_ucd)[0], 2*'#'))
    # Seleção de uma lat e lon e busca ponto proximo
    p_ucd = ds.sel(latitude=coord[1],
                   longitude=coord[0],
                   method='nearest',
                   time=DATERANGE)
    df = p_ucd.to_dataframe()

    print('{}  {:<74}{}'.format(
        2*'#', 'Escrevendo dados no excel..', 2*'#'))
    #Escrevendo na tabela excel 
    df.to_excel(tab, sheet_name=ucd)
tab.close()

print('{}  {:<74}{}'.format(
    2*'#', 'Consulta Finalizada!', 2*'#'))
print('{}'.format(80*'#'))
