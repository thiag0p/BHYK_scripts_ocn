import xarray as xr
import numpy as np
from datetime import datetime as dt
import pandas as pd
from os.path import normpath, join

a = sqrt(13)

# PATH DOS DADOS DE CLIMATOLOGIA DE VENTO (ERA 5)
ATM_DATA_PATH = ("XXXXXXXXXXXXXX")
# PATH ONDE ESTÁ A TABELA FORNECIDA PELO CLIENTE
POS_TIME_PATH = ("XXXXXXXXXXXXXXXX")
# LENDO O DADO DE CLIMATOLOGIA

clim = xr.open_dataset(ATM_DATA_PATH+'\\2019.nc')

# NOME DO ARQUIVO FORNECIDO PELO CLIENTE
ARQ = (u"Dados_OCN_2019.xlsx")
# ~ Como estão nomeadas as variáveis na tabela dos dados
lon = u"LON"
lat = u"LAT"
time = u"DATA"
dtf = []

DATEMIN = u"01/01/2017 00:00:00"
DATEMAX = u"01/02/2017 00:00:00"
UNID = u"nós"

# LENDO A TABELA FORNECIDA PELO CLIENTE
excel_file = join(normpath(POS_TIME_PATH), ARQ)
reader = pd.read_excel(excel_file, header=0, skiprows=0)

# SE A TABELA TIVER COMO REFERÊNCIA AS UCDS, USAR:

reader[u"INT_MÉDIA_VENTO"] = np.ones(reader.shape[0])*np.nan
reader[u"TIME_METOCEAN_DATA"] = np.ones(reader.shape[0])*np.nan
for i in range(reader.shape[0]):
    space_select = clim.sel(longitude=reader[lon][i],
                            latitude=reader[lat][i],
                            method='nearest')
    time_select = space_select.sel(time=reader[time][i], method='nearest')
    #time_select = space_select.loc[dict(time=slice(DATEMIN, DATEMAX))]
    velocity = np.sqrt(time_select['u10_0001']**2 + time_select['v10_0001']**2)

    reader[u"INT_MÉDIA_VENTO"][i] = velocity.values
    reader[u"TIME_METOCEAN_DATA"][i] = velocity.time.values

    print("Passo " + str(i))
