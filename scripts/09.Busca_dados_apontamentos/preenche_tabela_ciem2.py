'''
    Busca dados de apontamento que seguem o padrão da tabela de Atividades
    realizadas disponibilizada no ciem2.petrobras.biz
'''
# _____________________________________________________________________________
#                                   Modificar aqui
# _____________________________________________________________________________
# diretório onde está a tabela
path = 'XXXXXXXXXXXXX'
# nome da tabela com extensão
tabela = 'ATIVIDADES.xlsx'
# número de linhas descartadas para chegar ao cabeçalho
skiprows = 3
# Opção para retirar células mescladas (True - retira, False - mantem)
split_merge_cells = True
# Caso queiera plotar série temporal de cada rescurso deixe True, se não False
plot_recursos = False
# Variável criada para o caso do Fidelis! Deixe False caso contrário
Fidelis = True
# Variável para retirar ou não linhas de atividades não operacionais
# True - mantém todas as linhas da tabela mãe | False - retira linhas NOP
all_lines = True
# _____________________________________________________________________________
#                                   Pare aqui
# _____________________________________________________________________________

from pandas import read_excel, ExcelWriter, concat
from sys import path as syspath
syspath.append('XXXXXXXXXXXXXXX')
from table import table as tb
from table import get_available_data, search_ocnpylibdata
from geo import geo
from db import get_ocnpylib
import time as crono
from warnings import filterwarnings
import numpy as np
filterwarnings('ignore')

# _______________________________________________________________
#                           Lendo tabela
# _______________________________________________________________
tempo0 = crono.time()
table = read_excel(f'{path}\\{tabela}', header=0, skiprows=skiprows)
table2 = tb.ajusta_ciem2_table(table, all_lines)
table2.insert(0, 'id', np.arange(0, table2.shape[0]))

# _______________________________________________________________
#                        Carregando dados
# _______________________________________________________________
print('{}'.format(60 * '#'))
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

print('{}'.format(60 * '#'))
print('# {:<56} #'.format('+ Vento'))
wdtb = search_ocnpylibdata.search_wind(
    table2,
    data=wddata,
    col_df='DataFinal UTC',
    col_xutm='Coord. Leste',
    col_yutm='Coord. Norte',
    hora_antes=None, hora_depois=None)

print('# {:<56} #'.format('+ Onda'))
wvtb = search_ocnpylibdata.search_wave(
    table2,
    data=wvdata,
    col_df='DataFinal UTC',
    col_xutm='Coord. Leste',
    col_yutm='Coord. Norte',
    hora_antes=None, hora_depois=None)

print('# {:<56} #'.format('+ Corrente'))
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

if Fidelis:
    alltbs = tb.include_column_Fidelis(alltbs)

# _______________________________________________________________
#                       Salvando Tabela
# _______________________________________________________________
prefixo = tabela.split('.')[0]
excel = ExcelWriter(f'{path}\\{prefixo}_preenchida.xlsx')
if split_merge_cells:
    exfile = alltbs.reset_index().set_index('id')
else:
    exfile = alltbs

exfile.to_excel(excel, 'MetoceanData')
# Ajustando tamanho das colunas para melhor leitura do excel
for idx in range(50):
    worksheet = excel.sheets['MetoceanData']
    worksheet.set_column(idx, idx, 22)
excel.close()

tempo1 = crono.time() - tempo0
print(f'RunTime: {round(tempo1, 1)} seg // {round(tempo1 / 60, 1)} min')

# _____________________________________________________________________________
#                  PLOTANDO SÉRIE TEMPORAL POR RECURSO
# _____________________________________________________________________________

if plot_recursos:
    tb.plot_recursos_ciem2(wdtb, wvtb, crtb, path)
