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
diretorio = ('XXXXXXXXXXXXXXXX')

arq = 'notificacoes.xlsx'

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________

from sys import path as syspath
from os import path
from pandas import ExcelWriter, concat, DataFrame, read_excel, to_datetime
from pandas import date_range
import numpy as np
from pyproj import Proj
import ocnpylib
from datetime import timedelta, time, datetime
from warnings import filterwarnings
filterwarnings("ignore")

normpath = path.normpath(diretorio)
syspath.append('XXXXXXXXXXXXXX')
import OCNdb as ocn
# _____________________________________________________________________________
#                 Definindo função para calculo de direção média
# _____________________________________________________________________________


def dir_mean(inte, dire, conv):
    '''
        inte - Array com valores de intensidade
        dire - Array com valores de direção
        conv - Tipo de convenção
               'ocean' para OCEANOGRÁFICA
               'meteo' para Meteorológica
    '''
    try:
        u, v = ocnpylib.SECRET(
            inte,
            dire,
            str_conv=conv)
        _, dir_media = ocnpylib.SECRET(u.mean(), v.mean(), str_conv=conv)
        dir_media = round(dir_media, 2)
    except Exception:
        dir_media = np.nan
    return dir_media


# _____________________________________________________________________________
#                         Lendo tabela do cliente
# _____________________________________________________________________________

excel_file = '{}\\{}'.format(diretorio, arq)
reader = read_excel(excel_file, header=0, skiprows=0)

# _____________________________________________________________________________
#               Informações geográficas para busca em raio representativo
# _____________________________________________________________________________

id_local = ocnpylib.XXXXXXXXXXXXXX()
# As bacias de cada
coord = ocnpylib.XXXXXXXXXXXXXX(id_local)
# Retirando UCDs inválidas
try:
    id_local.pop(coord.index(None))
    coord.remove(None)
except Exception:
    pass
# Conversão a arrays para facilitação de operações futuras.
ucdnames = np.array(ocnpylib.XXXXXXXXXXX(id_local))
ucdcoords = (np.array([point[0] for point in coord]),
             np.array([point[1] for point in coord]))

prjct = Proj(
    "+proj=utm " +
    "+lon_0={:d} ".format(-39) +
    "+south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs")

# Representação de longitudes e latitudes das UCDs na projeção
# usualmente adotada pelas embarcações.
# utmy, utmx = prjct(ucdcoords[:, 0], ucdcoords[:, 1])
utmy, utmx = prjct(ucdcoords[0], ucdcoords[1])

# _____________________________________________________________________________
#                     Definindo limites para o raio de busca de dados
# _____________________________________________________________________________

distancia = {'meteo': 40000, 'wave': 40000, 'curr': 12000}

# _____________________________________________________________________________
#                         Buscando dados por apontamento.
# _____________________________________________________________________________
    # Criando colunas que serão inseridas na tabelas
new_columns = [
    'UCD_VENTO', 'DIRECAO_MÉDIA_VENTO (°)', 'INTENSIDADE_MÉDIA_VENTO (m/s)', 
    'UCD_CORRENTE', 'DIRECAO_MÉDIA_CORRENTE (°)',
    'INTENSIDADE_MÉDIA_CORRENTE (m/s)', 'UCD_ONDA',
    'ALTURA_SIGNIFICATIVA_MÉDIA (m)', 'DIRECAO_MÉDIA_ONDA (°)',
    'PERIODO_PICO_PRIMARO_MÉDIO (s)']
new_table = reader.copy()
new_table = concat([
    new_table,
    DataFrame(columns=new_columns)],
    axis=0)
new_table = new_table[list(reader.columns) + new_columns]

print('{}'.format(60*'#'))
print('#{:^58}#'.format('Consulta em andamento'))
for x, line in enumerate(reader.index):
    print('#{}#'.format(58 * '-'))
    print('# {:<57}#'.format('Linha {}'.format(x)))

    lineslc = reader[reader.index == x]
    try:
        # Data e hora local segundo tabela
        time = datetime.strptime('{} {}:{}:00'.format(
            lineslc['Data do sobrevoo'].values[0].astype(str).split("T")[0],
            lineslc['Hora da imagem'].values[0].hour,
            lineslc['Hora da imagem'].values[0].minute), '%Y-%m-%d %H:%M:%S')

        # Convertendo para UTC
        utctime = time + timedelta(hours=3)

        # Verificando o minuto e defininco hora cheia para busca de dados
        if utctime.minute > 30:
            reftime = utctime + timedelta(hours=1)
        else:
            reftime = utctime

        # FAZER AJUSTE PARA UTC DO DADOS DA TABELA QUE ESTÃO EM LOCAL
        utc_ti = (reftime - timedelta(hours=1)).strftime('%d/%m/%Y %H:00:00')
        utc_tf = (reftime + timedelta(hours=1)).strftime('%d/%m/%Y %H:00:00')

        # Pegando ucd de interesse
        ucdname = lineslc['Unidade'].values[0]
        lon, lat = ocnpylib.XXXXXXXXXXX(
            ocnpylib.XXXXXXXXXX([ucdname]))
        # Calculando distância das UCDs
        ucd_utmy, ucd_utmx = prjct(
            lon, lat)
        dst = np.sqrt((ucd_utmx - utmx) ** 2 +
                    (ucd_utmy - utmy) ** 2)
        # Ordenando a distância
        dstord = dst.argsort()

        for param in ['meteo', 'wave', 'curr']:
            print('# {:<57}#'.format('Parâmetro: ' + param))
            for ucd, ds in zip(ucdnames[dstord], dst[dstord]):
                print('# {:<57}#'.format('Busca em ' + ucd))
                if ds < distancia[param]:

                    data = ocn.get_BDs(
                        ucds=[ucd], dates=[utc_ti, utc_tf], param=param)

                    if data.shape[0] > 0:
                        if param == 'curr':
                            for inst in ['FSI2D', 'ADCP', 'FSI3D', 'HADCP']:
                                try:
                                    data = data.xs([inst], level=['SENSOR'])
                                    break
                                except Exception:
                                    continue
                        if param == 'curr' and data.index.levels[1][0] == 'MIROS':
                            print('# {:<57}#'.format(
                                'Miros não é válido para corrente'))
                        else:
                            try:
                                data = data.reset_index().set_index('level_2')
                            except Exception:
                                data = data.reset_index().set_index('DT_DATA')

                            # Colocando em hora local
                            data.index = data.index - timedelta(hours=3)

                            if param == 'meteo':
                                print('# {:<57}#'.format(
                                    'Dados de vento encontrados em ' + ucd))
                                try:
                                    new_table['UCD_VENTO'][
                                        new_table.index == line] = np.unique(
                                            data['UCD'])[0]
                                    new_table[
                                        'DIRECAO_MÉDIA_VENTO (°)'][
                                            new_table.index == line] = dir_mean(
                                                data['WSPD'].values,
                                                data['WDIR'].values,
                                                'meteo')
                                    new_table['INTENSIDADE_MÉDIA_VENTO (m/s)'][
                                        new_table.index == line] = data[
                                            'WSPD'].mean()
                                except Exception as erro:
                                    print('# {:<57}#'.format(
                                        '** Erro: ' + str(erro)))
                            if param == 'wave':
                                print('# {:<57}#'.format(
                                    'Dados de onda encontrados em ' + ucd))
                                try:
                                    new_table['UCD_ONDA'][
                                        new_table.index == line] = np.unique(
                                            data['UCD'])[0]
                                    new_table['DIRECAO_MÉDIA_ONDA (°)'][
                                        new_table.index == line] = dir_mean(
                                            data['VAVH'].values,
                                            data['VPEDM'].values,
                                            'meteo')
                                    new_table[
                                        'ALTURA_SIGNIFICATIVA_MÉDIA (m)'][
                                            new_table.index == line] = data[
                                                'VAVH'].mean()
                                    new_table[
                                        'PERIODO_PICO_PRIMARO_MÉDIO (s)'][
                                            new_table.index == line] = data[
                                                'VTPK1'].mean()
                                except Exception as erro:
                                    print('# {:<57}#'.format(
                                        '** Erro: ' + str(erro)))
                            if param == 'curr':
                                try:
                                    new_table['UCD_CORRENTE'][
                                        new_table.index == line] = np.unique(
                                        data['UCD'])[0]
                                    new_table[
                                        'DIRECAO_MÉDIA_CORRENTE (°)'][
                                            new_table.index == line] = dir_mean(
                                                data['HCSP'].values,
                                                data['HCDT'].values,
                                                'ocean')
                                    new_table[
                                        'INTENSIDADE_MÉDIA_CORRENTE (m/s)'][
                                            new_table.index == line] = data[
                                                'HCSP'].mean()
                                    print('# {:<57}#'.format(
                                        'Dados de corrente encontrados em ' + ucd))
                                except Exception as erro:
                                    print('# {:<57}#'.format(
                                        '** Erro: ' + str(erro)))
                                    continue
                            break
                else:
                    print('# {:<57}#'.format('Fora do raio'))
                    break
    except Exception as error:
        print('# {:<57}#'.format(str(error)))


w = ExcelWriter('{}tabela_preenchida_{}'.format(
    diretorio, arq.split(' ')[-1]))
new_table.to_excel(w)
w.close()

print('Consulta finalizada')
