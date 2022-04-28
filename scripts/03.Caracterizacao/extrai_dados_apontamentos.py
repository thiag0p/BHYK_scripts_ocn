# -*- coding: utf-8 -*-
'''
    Autor: Francisco Thiago Franca Parente
    Data de Criação: 14/10/2020

    Rotina que extrai dados de vento (médio), onda e corrente de acordo com
    apontamento de tabela enviada pelo cliente. Este código foi feito pensando
    na formatação da tabela enviada pela solicitação do dia 08/10/2020.
    Desta forma, sempre será necessário adequar o código à tabela do cliente,
    até o momento da rotina ficar operacional para todos os casos.

'''
# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________

# Diretório onde está a tabela do cliente e onde serão salvos os outputs
PATH = ('XXXXXXXXXXXXXXXXXXX')
# Nome da planilha com .extensão
ARQ = 'jan2020_SDSV_ATIVIDADES_REALIZADAS.xls'
# Nomes das colunas das variáveis tempo e latlon
# Data inicial
COLDTI = "XXXXXXXXX"
# Data final
COLDTF = "XXXXXXXXXX"
# Longitude
COLLON = 'Coord. Leste'
# Latitude
COLLAT = 'Coord. Norte'
# Meridiano central para os casos de UTM
COLMDC = 'Merid. Central'
# Coluna referente à UCD
COLUCD = None
# Formatação da data
DATEFT = '%d/%m/%Y %H:%M'

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________

from sys import path as syspath
from os import path
from pandas import ExcelWriter, concat, DataFrame, read_excel
from pandas import date_range
import numpy as np
from pyproj import Proj
import ocnpylib
from datetime import timedelta, datetime
from warnings import filterwarnings
filterwarnings("ignore")

normpath = path.normpath(PATH)
syspath.append('XXXXXXXXXXXXX')
import OCNdb as ocn

# _____________________________________________________________________________
#                         Lendo tabela do cliente
# _____________________________________________________________________________

excel_file = '{}\\{}'.format(PATH, ARQ)
table = read_excel(excel_file, header=1, skiprows=2)

# Retirando os apontamentos com duração 0:00 (default tabelas ciem2)
try:
    table = table[table['Duração'] != '0:00']
except Exception:
    pass

# Retirando os apontamentos não operacionais
try:
    droplines = table[table['Tipo Atividade'].str.contains(
        '{}{}'.format(
            'ABASTECENDO|AGUARDANDO|ALMOÇO|EMBARQUE|DESEMBARQUE|',
            'NAVEGAÇÃO|REPOUSO|TROCA DE TURMA'))
    ].copy()
    droplines = droplines[
        droplines['Tipo Atividade'] != 'AGUARDANDO CONDIÇÕES METEOCEANOGRÁFICAS']
    table = table.drop(droplines.index, axis=0)

except Exception:
    pass


# _____________________________________________________________________________
#               Informações geográficas para busca em raio representativo
# _____________________________________________________________________________

id_local = ocnpylib.SECRET()
# As bacias de cada
coord = ocnpylib.SECRET(id_local)
# Retirando UCDs inválidas
try:
    id_local.pop(coord.index(None))
    coord.remove(None)
except Exception:
    pass
# Conversão a arrays para facilitação de operações futuras.
ucdnames = np.array(ocnpylib.SECRET(id_local))
ucdcoords = (np.array([point[0] for point in coord]),
             np.array([point[1] for point in coord]))

# _____________________________________________________________________________
#                     Definindo limites para o raio de busca de dados
# _____________________________________________________________________________

distancia = {'meteo': 40000, 'wave': 40000, 'curr': 6000}
MERIDIANO_CENTRAL = {
    'Bacia de Santos': -45,
    'Bacia de Campos': -39,
    'Bacia do Espírito Santo': -39}
# _____________________________________________________________________________
#                         Buscando dados por apontamento.
# _____________________________________________________________________________
new_table = DataFrame()
print('{}'.format(60 * '#'))
print('# {:^56} #'.format('Início da Consulta'))
print('# {} #'.format(56 * '-'))
for x, line in enumerate(table.index):
    print('# {:<56} #'.format(
        'Linha ' + str(x + 1) + ' de ' + str(table.shape[0])))
    lineslc = table[table.index == line]
    print('# {:<56.56} #'.format(
        lineslc['Descrição Serviço'].values[0]))
    # definindo data inicial e final, convertendo em UTC, 1h antes e depois
    dti = (datetime.strptime(
        str(lineslc[COLDTI].values[0]), DATEFT
        ) + timedelta(hours=2)).strftime('%d/%m/%Y %H:00:00')
    dtf = (datetime.strptime(
        str(lineslc[COLDTF].values[0]), DATEFT
        ) + timedelta(hours=4)).strftime('%d/%m/%Y %H:00:00')

    # Criando colunas que serão inseridas na tabelas
    insert = DataFrame(
        columns=[
            'UCD_VENTO', 'DIRECAO_VENTO (°)', 'INTENSIDADE VENTO (m/s)',
            'UCD_CORRENTE', 'DIRECAO_CORRENTE (°)',
            'INTENSIDADE_CORRENTE (m/s)',
            'UCD_ONDA', 'ALTURA_SIGNIFICATIVA (m)', 'DIRECAO_ONDA (°)',
            'PERIODO_PICO_PRIMARO (s)'])

    if COLUCD is not None:
        # Pegando ucd de interesse
        ucdname = lineslc['UCD'].values[0]
        idlocal = ocnpylib.SECRET(ucdname)
        ubacia = ocnpylib.SECRET(id_local)

        lon, lat = ocnpylib.SECRET(
            )
        prjct = Proj(
            "+proj=utm " +
            "+lon_0={:d} ".format(MERIDIANO_CENTRAL[ubacia[0]]) +
            "+south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs")
        # Representação de longitudes e latitudes das UCDs na projeção
        # usualmente adotada pelas embarcações.
        # utmy, utmx = prjct(ucdcoords[:, 0], ucdcoords[:, 1])
        utmy, utmx = prjct(ucdcoords[0], ucdcoords[1])

        # Calculando distância das UCDs
        ucd_utmy, ucd_utmx = prjct(lon, lat)
        dst = np.sqrt((ucd_utmx - utmx) ** 2 + (ucd_utmy - utmy) ** 2)
        # Ordenando a distância
        dstord = dst.argsort()

    else:
        try:
            prjct = Proj(
                "+proj=utm " +
                "+lon_0={:d} ".format(int(-lineslc[COLMDC].values[0])) +
                "+south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs")
        except Exception:
            continue

        # Representação de longitudes e latitudes das UCDs na projeção
        # usualmente adotada pelas embarcações.
        # utmy, utmx = prjct(ucdcoords[:, 0], ucdcoords[:, 1])
        utmy, utmx = prjct(ucdcoords[0], ucdcoords[1])

        # Distâncias relativas entre embarcação e UCDs.
        dst = np.sqrt((lineslc[COLLON].values[0] - utmx) ** 2 +
                      (lineslc[COLLAT].values[0] - utmy) ** 2)

        # Distâncias ordenadas por proximidade geográfica.
        dstord = dst.argsort()
    print('# {} #'.format(56 * '-'))
    for param in ['meteo', 'wave', 'curr']:
        print('# {:<56} #'.format('+' + param.upper()))
        for ucd, ds in zip(ucdnames[dstord], dst[dstord]):
            print('#     {:<52} #'.format('° Busca em ' + ucd))            
            if ds < distancia[param]:
                data = ocn.get_BDs(ucds=[ucd], dates=[dti, dtf], param=param)

                if data.shape[0] > 0:
                    if param == 'curr':
                        for inst in ['FSI2D', 'ADCP', 'FSI3D', 'HADCP']:
                            try:
                                data = data.xs([inst], level=['SENSOR'])
                                break
                            except Exception:
                                continue
                    if param == 'curr' and data.index.levels[1][0] == 'MIROS':
                        print('#         {:<48} #'.format(
                            'x Miros não é válido para corrente'))
                    else:
                        try:
                            data = data.reset_index().set_index('level_2')
                        except:
                            data = data.reset_index().set_index('DT_DATA')

                        # Colocando em hora local
                        data.index = data.index - timedelta(hours=3)

                        if param == 'meteo':
                            print('#         {:<48} #'.format(
                                '> Dados de vento encontrados em ' + ucd))
                            try:
                                insert['UCD_VENTO'] = data['UCD']
                                insert['DIRECAO_VENTO (°)'] = data['WDIR']
                                insert[
                                    'INTENSIDADE VENTO (m/s)'] = data['WSPD']
                            except:
                                continue
                        if param == 'wave':
                            print('#         {:<48} #'.format(
                                '> Dados de onda encontrados em ' + ucd))
                            try:
                                insert['UCD_ONDA'] = data['UCD']
                                insert['DIRECAO_ONDA (°)'] = data['VPEDM']
                                insert[
                                    'ALTURA_SIGNIFICATIVA (m)'] = data['VAVH']
                                insert[
                                    'PERIODO_PICO_PRIMARO (s)'] = data['VTPK1']
                            except:
                                continue
                        if param == 'curr':
                            try:
                                insert['UCD_CORRENTE'] = data['UCD']
                                insert['DIRECAO_CORRENTE (°)'] = data['HCDT']
                                insert[
                                    'INTENSIDADE_CORRENTE (m/s)'] = data[
                                        'HCSP']
                                print('#         {:<48} #'.format(
                                    '> Dados de corrente encontrados em ' + ucd
                                ))
                            except Exception as erro:
                                print('#         {:<48.48} #'.format(erro))
                                continue
                        break
            else:
                print('#         {:<48} #'.format('x Fora do raio de busca'))
                break

        for c, clm in enumerate(lineslc.columns):
            if c == 0:
                df = concat(
                    [insert],
                    keys=[lineslc[clm].values[0]],
                    names=[clm])
            else:
                df = concat(
                    [df],
                    keys=[lineslc[clm].values[0]],
                    names=[clm])

    new_table = new_table.append(df)
    print('# {} #'.format(56 * '-'))


w = ExcelWriter('{}\\Tabela_preenchida_{}.xlsx'.format(
    PATH, ARQ.split('.')[0]))
new_table.to_excel(w)
w.close()

print('Consulta finalizada')
