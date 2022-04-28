'''
    Autor: Francisco Thiago Franca Parente
    Data de Criação: 22/09/2020

    Rotina que acha valores de intensidade do vento acima de um
    limite operacional e exporta excel

    Caso queira fazer uma busca por todas as ucds das reigões, seguem
    os IDs de cada regiões registrada do banco OCN.

        'Bacia de Campos': XX,
        'Bacia Sergipe Alagoas': XXXXX,
        'Bacia de Camamu': XX,
        'Bacia Potiguar': XX,
        'Bacia do Espírito Santo': XX,
        'Bacia do Ceará': XX,
        'Bacia de Santos': XX}

'''
import numpy as np
# _____________________________________________________________________________
#                           Modificar aqui
# _____________________________________________________________________________
# Lista com as UCDs de interesse.
ucds = [
    'XXXXXXXXXXXX']

# Diretório onde serão salvos os resultados
PATH = ('XXXXXXXXXXXXXXX')

# Data inical e final da análise dos dados
datemin = u"01/01/2010 00:00:00"
datemax = u"22/09/2020 02:00:00"

# Limite
limite = 19

# Unidade de medida para vento e corrente
unid = 'm/s'

# Caso queiram avaliar rajada, utilize True, caso contrário False
gust = False

# _____________________________________________________________________________
#               Importando biblioteca de funções necessárias
# _____________________________________________________________________________
from sys import path as syspath
from os import path
from pandas import ExcelWriter, DataFrame
import ocnpylib as ocpy
import time

normpath = path.normpath(PATH)
pth1 = 'M:\\Rotinas\\python\\'
dirs = ['data']
for d in dirs:
    pth2 = pth1 + d
    syspath.append(pth2)
import OCNdb as ocn

# _____________________________________________________________________________
#               Carregando dados de todas as bases do OCEANOP
# _____________________________________________________________________________
LOG = open('{}\\LOG.txt'.format(PATH), 'w')
casos = DataFrame()

for ucd in ucds:

    ucdid = ocpy.SECRET(ucd)
    name = ocpy.SECRET(ucdid)
    print('#############################################')
    print('Buscando em {}'.format(name[0]))
    try:
        # início do cronometro
        start = time.time()

        # carregando os dados
        data = ocn.get_BDs(name,
                    [datemin, datemax],
                    'meteo', 
                    gust=gust)
        print('Tempo de carregamento: {:.2f} min'.format(
            (time.time() - start) / 60))
        
        if data.shape[0] > 1:

            # corventendo para nós caso usuário escolha esta unidade de med
            if unid == 'nós':
                data.WSPD = data.WSPD * 1.94384449

            # achando valore acima do limite definido
            found = data[data.WSPD > limite]

            # apendando os casos encontrados
            if found.shape[0] > 1:
                print('{} registros encontrados em {} de {}.'.format(
                    found.shape[0], name[0], data.shape[0]))
                LOG.write('{}/n{} {} de {}'.format(
                    '#############################################',
                    found.shape[0], 'registros encontrados em',
                    name[0], data.shape[0]))
                casos = casos.append(found)
            else:
                print('Nenhum registro acima de {} {} encontrado'.format(
                    limite, unid))
        else:
            print('Sem dados no período solicitado')

    except Exception:
        print('Falha ao carregar dados de {}.'.format(name[0]))
        continue
LOG.close()
# _____________________________________________________________________________
#                               Gravando excel
# _____________________________________________________________________________

w = ExcelWriter('{}\\Casos_de_interesse.xlsx'.format(PATH))
casos.to_excel(w)
w.close()
