'''
    Código de acesso ao banco de dados do ciem2 no nível de tarefas.

    Autor: Francisco Thiago Franca Parente (BHYK)
    Criação: 06/12/2021

'''

from pandas import DataFrame
import os
from sys import path
import time
import cx_Oracle as cxOr
dc = 'XXXXXXXXXXXXXXXX'
path.append(dc)
from dbc.security import decrypt
'''
    Quando usar o sqlalchemy seguir a sequencia na str de acesso ao bd
    'oracle+cx_oracle://USERNAME:PASSWRD@HOSTNAME:PORT/?service_name=SERVICENAME'
'''


def load_table(date, path):
    '''
    Lê tabela de nível tarefa do ciem2. O usuário dita uma data inicial e a
    função pega todas as atividades ocorridas depois da data fornecida.

    :param date: str da data inicial do filtro de busca ('DD/MM/YYYY')
    :param path: str com diretório onde será salvo o .csv com as informações.

    return: DataFrame
    '''
    # configuração da língua pra não conflito de codificação
    os.environ["NLS_LANG"] = "BRAZILIAN PORTUGUESE_BRAZIL.WE8ISO8859P15"
    dbinf = decrypt(open(f'{dc}\\dbc\\secret.key', "rb").read()).split('--')
    dbciem = cxOr.connect(user=dbinf[0], password=dbinf[1], dsn=dbinf[2])

    t0 = time.time()
    # Criação e apontamento do cursor de requisição.
    dbcurs = dbciem.cursor()
    dbqry = (
        "SELECT"
        " * "
        "FROM"
        " XXXXXXXXXXXX "
        "WHERE"
        " \"Início Tarefa\">="
        f" TO_DATE('{date}', 'DD/MM/YYYY')")

    # Requisição ao banco e extração dos dados.
    dbcurs.execute(dbqry)
    columns = [row[0] for row in dbcurs.description]
    qryresult = dbcurs.fetchall()

    df = DataFrame(qryresult, columns=columns)
    df.to_csv(f'{path}\\ciem2_table.csv')
    # Desapontamento do cursor e encerramento da conexão com o banco.
    dbcurs.close()
    dbciem.close()
    print(f'Tempo: {(time.time() - t0) / 60} min')
