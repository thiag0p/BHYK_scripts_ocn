'''

    Rotina de Leitura de dados de precipitação
    Esta rotina busca os dados do Final Run, o produto mais confiável
    fornecido pela Nasa! Porém, há um gap de cerca de 3 meses para 
    disponibilização dos dados --> dados disponíveis até dezembro de 2020. Para os dados mais recentes, é necessário
    buscar o banco Late Run (rotina precipitacao_late_run.py)

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

#                                                                              |
import xarray
from datetime import datetime as dt
import ocnpylib as ocpy
from pandas import ExcelWriter, date_range
                              
opendap_link = ('http://XXXXXXXXXXXXXXX')

path = (u"XXXXXXXXXXXXXX")

ds = xarray.open_dataset(opendap_link)

UCDS = ['XXXXXXXXXXXXXXX']

DATEINI = u"01/02/2020 00:00:00"
DATEFIN = u"10/03/2020 23:00:00"

DATERANGE = date_range(dt.strptime(DATEINI, '%d/%m/%Y %H:%M:%S'),
                       dt.strptime(DATEFIN, '%d/%m/%Y %H:%M:%S'),
                       freq='D')

# # Selecionando um domínio
# bacia = ds.sel(latitude=slice(BC[2], BC[3]),
#                longitude=slice(BC[0], BC[1]),
#                time=DATERANGE)

tab = ExcelWriter(path + '\dfpitacao.xlsx')
for ucd in UCDS:
    # procura lat e lon da UCD
    id_ucd = ocpy.SECRET(ucd)
    coord = ocpy.SECRET(id_ucd) 

    # Seleção de uma lat e lon e busca ponto proximo
    p_ucd = ds.sel(latitude=coord[1],
                   longitude=coord[0],
                   method='nearest',
                   time=DATERANGE)
    df = p_ucd.to_dataframe()

    #Escrevendo na tabela excel 
    df.to_excel(tab, sheet_name=ucd)
tab.close()
