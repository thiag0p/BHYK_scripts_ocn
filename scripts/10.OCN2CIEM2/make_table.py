'''
Busca automática dos dados de apontamento que seguem o padrão da tabela de
Atividades realizadas disponibilizada no ciem2.petrobras.biz

Autor: Francisco Thiago Franca Parente (BHYK)
Criação: 06/12/2021

'''
print('{}'.format(60 * '#'))
print('# {:^56} #'.format('START ROTINA CIEM2 Vs DADO OCN'))
print('# {} #'.format(56 * '-'))
from datetime import datetime as dt
from datetime import timedelta
from pandas import read_csv, ExcelWriter, concat
from sys import path as syspath
syspath.append('XXXXXXXXXX')
syspath.append('XXXXXXXXXXXXXXXXXXXXX')
from table import table as tb
from table import get_available_data, search_ocnpylibdata
from geo import geo
from db import get_ocnpylib
import ciem2
import time as crono
from warnings import filterwarnings
import numpy as np
filterwarnings('ignore')

# diretório onde será salva a tabela
path = 'XXXXXXXXXXXXXXXXXXXX'
# tempo inical da busca
date = dt.now().replace(hour=0, minute=0, second=0, microsecond=0)
date = (date - timedelta(hours=24)).strftime('%d/%m/%Y')
# nome da tabela do ciem2
tabela = 'ciem2_table.csv'

# _______________________________________________________________
#                           Lendo tabela
# _______________________________________________________________
print('# {:<56} #'.format('+ Lendo tabela do ciem2...'))
tempo0 = crono.time()
ciem2.load_table(date, path)
table = read_csv(f'{path}\\{tabela}', header=0)
table2 = tb.ajusta_colunas_oracledb(table)
table2.insert(0, 'id', np.arange(0, table2.shape[0]))
print('# {:<56} #'.format('+ Leitura finalizada.'))
print('# {} #'.format(56 * '-'))
# _______________________________________________________________
#                        Carregando dados
# _______________________________________________________________
print('# {:^56} #'.format('Carregando dados OCN'))
print('# {:<56} #'.format('> Vento'))
wddata = get_available_data.load(
    table2,
    col_df='DataFinal UTC',
    func=get_ocnpylib.get_wind)

print('# {:<56} #'.format('> Onda'))
wvdata = get_available_data.load(
    table2,
    col_df='DataFinal UTC',
    func=get_ocnpylib.get_wave)

print('# {:<56} #'.format('> Corrente'))
crdata1 = get_available_data.load(
    table2,
    col_df='DataFinal UTC',
    func=get_ocnpylib.get_curr)

crdata2 = get_available_data.load(
    table2,
    col_df='DataFinal UTC',
    func=get_ocnpylib.get_curr_profile)

# Juntando sensores pontuais e perfiladores
crdata = crdata1.append(crdata2)

# _______________________________________________________________
#              Preenchendo Tabela de cada parametro
# _______________________________________________________________
print('# {} #'.format(56 * '-'))
print('# {:^56} #'.format('Preenchendo tabela.'))
print('# {:<56} #'.format('° Vento'))
wdtb = search_ocnpylibdata.search_wind(
    table2,
    data=wddata,
    col_df='DataFinal UTC',
    col_xutm='Coord. Leste',
    col_yutm='Coord. Norte',
    hora_antes=None, hora_depois=None)

print('# {:<56} #'.format('° Onda'))
wvtb = search_ocnpylibdata.search_wave(
    table2,
    data=wvdata,
    col_df='DataFinal UTC',
    col_xutm='Coord. Leste',
    col_yutm='Coord. Norte',
    hora_antes=None, hora_depois=None)

print('# {:<56} #'.format('° Corrente'))
crtb = search_ocnpylibdata.search_curr(
    table2,
    data=crdata,
    col_df='DataFinal UTC',
    col_xutm='Coord. Leste',
    col_yutm='Coord. Norte',
    hora_antes=None, hora_depois=None)
crtb.index.names = wdtb.index.names

# _______________________________________________________________
#            Juntando todos parametros em uma só tabela
# _______________________________________________________________

nwdtb = tb.ajusta_output_com_dados_ciem2(wdtb)
nwvtb = tb.ajusta_output_com_dados_ciem2(wvtb)
ncrtb = tb.ajusta_output_com_dados_ciem2(crtb)

# Juntando todos os parametros na mesma tabela e salvando excel
alltbs = nwdtb.join([nwvtb, ncrtb])
alltbs = tb.include_column_Fidelis(alltbs)

# _______________________________________________________________
#                       Salvando Tabela
# _______________________________________________________________
prefixo = tabela.split('.')[0]
excel = ExcelWriter(f'{path}\\{prefixo}_preenchida.xlsx')
exfile = alltbs.reset_index().set_index('id')
exfile.to_excel(excel, 'MetoceanData')

# Ajustando tamanho das colunas para melhor leitura do excel
for idx in range(50):
    worksheet = excel.sheets['MetoceanData']
    worksheet.set_column(idx, idx, 22)
excel.close()

tempo1 = crono.time() - tempo0
print('# {:<56} #'.format('>>> FINALIZADO'))
print('# {:^56} #'.format(
    f'RunTime: {round(tempo1, 1)} seg // {round(tempo1 / 60, 1)} min'))
print('{}'.format(60 * '#'))
