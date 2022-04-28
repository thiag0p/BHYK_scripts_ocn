'''
    Rotina para atualização dos PNGs da StormGeo

    Autor: Francisco Thiago Franca Parente (BHYK)
    Criação: 11/06/2020
'''

from pandas import read_excel
from os import chdir
import urllib
from warnings import filterwarnings

chdir('{}{}'.format(
    'DIRETORIO'))

urls_arq = (
    'ARQUIVO.XLSX')

urls = read_excel(urls_arq)


def load_html(html, figname, logs, logf):
    '''
        Função que carrega e salva imagem do html

        html:       Endereço html
        figname:    string com nome da imagem salva
        logs:       list que receberá os nomes das imagens carregadas
        logf:       list que receberá os nomes das imagens não carregadas

    '''

    try:
        urllib.request.urlretrieve(html, figname)
        logs.append(figname)
    except Exception:
        logf.append(figname)


logs, logf = [], []
for index in urls.index:
    slc = urls[urls.index == index]
    name = slc.Localidade.values[0].replace(' ', '_')
    print(f'Baixando {name}')
    load_html(slc.WIND.values[0], f'{name}_wind.png', logs, logf)

    load_html(slc.WAVE.values[0], f'{name}_wave.png', logs, logf)

    load_html(
        slc.WEATHER.values[0],
        f'{name}_weather.png',
        logs, logf)

print('{}'.format(60 * '#'))
print('# {:^56} #'.format('CAMPOS ATUALIZADOS COM SUCESSO:'))
print('# {} #'.format(56 * '-'))
for x in logs:
    print('# ° {:<52} #'.format(x))

print('{}'.format(60 * '#'))
print('# {:^56} #'.format('FALHAS DE ATUALIZAÇÃO:'))
print('# {} #'.format(56 * '-'))
for x in logf:
    print('# ° {:<52} #'.format(x))

print('Verifique Log de atualização acima!')
input('Pressione ENTER para fechar prompt.')
