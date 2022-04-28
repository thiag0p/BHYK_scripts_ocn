# _____________________________________________________________________________
#                                   Modificar aqui
# _____________________________________________________________________________
# diretório onde está a tabela
path = 'XXXXXXXXXXXXXXXXXX'
# nome da tabela com extensão
tabela = 'notificacoes1.xlsx'
# número de linhas descartadas para chegar ao cabeçalho
skiprows = 0
# Escolha dos parametros de interesse (True - SIM / False - NÃO)
wind = True
wave = True
curr = False

# >>>>>>>>>>>>>> Nomes das colunas da tabela
# Coluna referente às unidades (colocar None para quando não tiver coluna)
COLUCD = 'UNIDADE'
# Coluna com as datas iniciais (str)
COLDI ='DATAHORA LOCAL'
# Coluna com as datas finais (colocar None para quando não tiver coluna)
COLDF = None
# Coluna horas das datas iniciais (colocar None para quando não tiver coluna)
COLHI = None
# Coluna horas das datas finais (colocar None para quando não tiver coluna)
COLHF = None
# Coluna referente à latitude (colocar None para quando não tiver coluna)
COLAT = None
# Coluna referente à longitude (colocar None para quando não tiver coluna)
COLON = None
# Coluna referente à quantas horas antes do apontado deseja buscar dados
# (colocar None para quando não tiver coluna)
HRANTES=None
# Coluna referente à quantas horas depois do apontado deseja buscar dados
# (colocar None para quando não tiver coluna)
HRDEPOIS=None

# _____________________________________________________________________________
#                                   Pare aqui
# _____________________________________________________________________________
from pandas import read_excel, ExcelWriter, concat
from sys import path as syspath
syspath.append('XXXXXXXXXXXXXXX')
from table import table as tb
from table import search_apidata, get_available_data
from db import get_api, get_ucds

# _____________________________________________________________________________
#                           LENDO TABELA DO CLIENTE
# _____________________________________________________________________________
table = read_excel(f'{path}\\{tabela}',
                   header=0,
                   skiprows=skiprows)
# Check das datas
table2 = tb.check_dates(table,
                        col_di=COLDI,
                        col_hi=COLHI,
                        col_df=COLDF,
                        col_hf=COLHF)
# _____________________________________________________________________________
#                           BUSCA POR DADOS DE VENTO
# _____________________________________________________________________________
if wind:
    data = get_available_data.load(
        table2,
        func=get_api.api_wind,
        col_df=COLDF,
        col_ucd=COLUCD)
    wdtb = search_apidata.search_wind(
        table2,
        data=data,
        col_df=COLDF,
        col_ucd=COLUCD,
        col_lat=COLAT,
        col_lon=COLON,
        hora_antes=HRANTES,
        hora_depois=HRDEPOIS)
    ex = ExcelWriter(f'{path}\\wind_preenchida.xlsx')
    wdtb.to_excel(ex)
    ex.close()

if wave:
    data = get_available_data.load(
        table2,
        col_df=COLDF,
        col_ucd=COLUCD,
        func=get_api.api_wave)
    wvtb = search_apidata.search_wave(
        table2,
        data=data,
        col_df=COLDF,
        col_ucd=COLUCD,
        col_lat=COLAT,
        col_lon=COLON,
        hora_antes=HRANTES,
        hora_depois=HRDEPOIS)
    ex = ExcelWriter(f'{path}\\wave_preenchida.xlsx')
    wvtb.to_excel(ex)
    ex.close()

if wave and wind:
    # Juntando todos os parametros
    all = {'vento': wdtb, 'onda': wvtb}
    exfile = concat(all.values(), axis=1, keys=all.keys())

    ex = ExcelWriter(f'{path}\\wind_wave_preenchida.xlsx')
    kk.to_excel(ex)
    ex.close()
