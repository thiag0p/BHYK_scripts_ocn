import xarray as xr
from datetime import datetime
import matplotlib.pyplot as plt

# ROTINA QUE EXPORTA DADOS DE MARÉ DO FES2014

# ____________________________________________________________________________
#                       MODIFICAR AQUI
# ____________________________________________________________________________
# diretório onde serão salvos os dados
path = ('C:\\Users\\bhyk\\OneDrive - PETROBRAS\\Desktop\\random\\teste')
# data_inicial dia/mes/ano hora:min:seg
data_inicial = '01/01/2021 00:00:00'
# data final dia/mes/ano hora:min:seg
data_final = '03/01/2021 00:00:00'

# latitude de interesse (graus decimais)
latitude = -22.4
# longitude de interesse (graus decimais)
longitude = -41.

# ____________________________________________________________________________
# endereço opendap
FES2014 = '{}{}'.format(
    'http://s650opend.cenpes.petrobras.com.br:8080/thredds/dodsC/',
    'aviso/fes2014_timeseries')
# acessando opendap
opendap = xr.open_dataset(FES2014)
# lendo opendap
data = opendap.sel(
    latitude=latitude, longitude=longitude, method='nearest').sel(
        time=slice(
            datetime.strptime(data_inicial, '%d/%m/%Y %H:%M:%S'),
            datetime.strptime(data_final, '%d/%m/%Y %H:%M:%S'))).load()
# salvando excel com dados solicitados
export = data.to_dataframe()
export = export.rename(columns={
    'sw_tide_msl': 'Altura (m)',
    'sw_tide_u': 'U (m/s)',
    'sw_tide_v': 'V (m/s)'})
export.to_excel(f'{path}\\FES2014.xlsx')

# Plotando imagem da amplitude de maré
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
data.to_dataframe().sw_tide_msl.plot(ax=ax, linewidth=2)
ax.set_ylabel('Altura da Maré em relação\n ao nível médio do mar (m)',
              fontsize=14)
fig.savefig(f'{path}\\altura_mare.png',
            format='png',
            bbox_inches='tight',
            dpi=300)

# Plotando u e v de maré
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
ax.quiver(
    data.to_dataframe().index,
    [[0] * len(data.to_dataframe().index)],
    data.to_dataframe().sw_tide_u,
    data.to_dataframe().sw_tide_v,
    angles='uv',
    width=0.005,
    headwidth=5,
    headlength=5,
    headaxislength=2)
ax.set_ylabel('Velocidade (m/s)', fontsize=14)
fig.savefig(f'{path}\\uv_stickplot.png',
            format='png',
            bbox_inches='tight',
            dpi=300)