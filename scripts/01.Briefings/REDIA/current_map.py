print('{}'.format(60 * '#'))
print('# {:^56} #'.format('START'))
print('# {} #'.format(56 * '-'))

from sys import path
path.append('M:\\Rotinas\\python\\graph')
path.append('M:\\Rotinas\\python\\scripts\\09.Busca_dados_apontamentos')
path.append('M:\\Rotinas\\python\\scripts\\01.Briefings\\REDIA')
from cor import cor
from db import get_api
from geo import geo
import make_map
from sst import load as loadsst
from mplot import plot as mplot
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from warnings import filterwarnings
filterwarnings('ignore')

# Diretório onde serão salvas as imagens
PATH = 'M:\\Previsao\\1.Briefings\\CIOP\\Briefing_REDIA\\imagens'

# Definindo as datas para busca de dados
NOW = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

# Carregando dados do OCEANOP via api
print('# {:<56} #'.format('+ Carregando dados OCN via api.'))
ucds = geo.ucds_coords()
local_names = [x[0] for x in ucds.index]
ocndata = get_api.api_curr(
    local_names,
    NOW - timedelta(days=1),
    NOW + timedelta(days=1))
# convertendo valores de corrente para nós
ocndata['HCSP'] = ocndata['HCSP'].astype(float) * 1.9438

# Lendo dados de TSM do opendap
print('# {:<56} #'.format('+ Carregando TSM.'))
TSM = loadsst.sst_seBR((NOW - timedelta(days=1)).strftime('%m/%d/%Y'))

# Calculando direção média para plot no mapa
box = cor.uv_std_max_calc(ocndata)

# criando lista de ucds das bacias
ucds_bc = list(set(
    [x[0] for x in ucds[ucds.bacia == 'Bacia de Campos'].index.to_list()]))
ucds_bs = list(set(
    [x[0] for x in ucds[ucds.bacia == 'Bacia de Santos'].index.to_list()]))
ucds_bes = list(set(
    [x[0] for x in ucds[
        ucds.bacia == 'Bacia do Espirito Santo'].index.to_list()]))

# _____________________________________________________________________________
#                               PLOTANDO OS MAPAS
# _____________________________________________________________________________
# Texto para inclusão no título do mapa
time_curr_data = 'Corrente: {:%d/%m/%Y %Hh} até {:%d/%m/%Y %Hh}'.format(
    ocndata.index.min() - timedelta(hours=3),
    ocndata.index.max() - timedelta(hours=3))
# plota Bacia de Campos
print('# {:<56} #'.format('° Plotando Bacia de Campos'))
fig, ax = make_map.bc()
mplot.tsm(TSM, ax=ax, addtitle=time_curr_data)
mplot.allucds(ucds[ucds['bacia'] == 'Bacia de Campos'], ax)
mplot.ucds_curr(ocndata, ucds, ax)
if box[box.index.isin(ucds_bc)].shape[0] != 0:
    mplot.inf_box(
        ax=ax,
        points=[-41.9, -21.1, .05, .1],
        data=box[box.index.isin(ucds_bc)],
        scale=24)
fig.savefig(f'{PATH}\\Bacia de Campos.png')

# plota Bacia de Santos
fig, ax = make_map.bs()
print('# {:<56} #'.format('° Plotando Bacia de Santos'))
mplot.tsm(TSM, ax=ax, addtitle=time_curr_data)
mplot.allucds(ucds[ucds['bacia'] == 'Bacia de Santos'], ax)
mplot.ucds_curr(ocndata, ucds, ax)
if box[box.index.isin(ucds_bs)].shape[0] != 0:
    mplot.inf_box(
        ax=ax,
        points=[-46.8, -21.2, .2, .2],
        data=box[box.index.isin(ucds_bs)],
        scale=26)
fig.savefig(f'{PATH}\\Bacia de Santos.png')


# plota Bacia do Espirito Santo
fig, ax = make_map.bes()
print('# {:<56} #'.format('° Plotando Bacia do Esp. Santo'))
mplot.tsm(TSM, ax=ax, addtitle=time_curr_data)
mplot.allucds(ucds[ucds['bacia'] == 'Bacia do Espírito Santo'], ax)
mplot.ucds_curr(ocndata, ucds, ax)
if box[box.index.isin(ucds_bes)].shape[0] != 0:
    mplot.inf_box(
        ax=ax,
        points=[-41.8, -20.1, .1, .1],
        data=box[box.index.isin(ucds_bes)],
        scale=24)
fig.savefig(f'{PATH}\\Bacia do Espirito Santo.png')
