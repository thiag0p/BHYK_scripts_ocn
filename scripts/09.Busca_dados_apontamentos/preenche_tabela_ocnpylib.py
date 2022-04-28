# _____________________________________________________________________________
#                                   Modificar aqui
# _____________________________________________________________________________
# diretório onde está a tabela
path = 'XXXXXXXXXXXXXXXX'
# nome da tabela com extensão
tabela = 'apontamentos.xlsx'
# número de linhas descartadas para chegar ao cabeçalho
skiprows = 0
# Escolha dos parametros de interesse (True - SIM / False - NÃO)
wind = True
wave = True
curr = True

# Você vai querer que plot série temporal? True se sim e False se não
plotst = True
# Quer plotar de acordo com uma coluna? Se sim, qual coluna informa os plots
# de interesse (String)? Se não, deixe colplot = False
colplot = False
# Ou você deseja plotar por linha de apontamento? Se sim, deixe plotline = True
plotline = True

# >>>>>>>>>>>>>> Nomes das colunas da tabela
# Coluna referente às unidades (colocar None para quando não tiver coluna)
COLUCD = 'UM'
# Coluna com as datas iniciais (str)
COLDI = 'data i'
# Coluna com as datas finais (colocar None para quando não tiver coluna)
COLDF = 'Data f'
# Coluna horas das datas iniciais (colocar None para quando não tiver coluna)
COLHI = 'hora i'
# Coluna horas das datas finais (colocar None para quando não tiver coluna)
COLHF = 'hora f'
# Coluna referente à latitude (colocar None para quando não tiver coluna)
COLAT = None
# Coluna referente à longitude (colocar None para quando não tiver coluna)
COLON = None
# Coluna referente à quantas horas antes do apontado deseja buscar dados
# (colocar None para quando não tiver coluna)
HRANTES = None
# Coluna referente à quantas horas depois do apontado deseja buscar dados
# (colocar None para quando não tiver coluna)
HRDEPOIS = None

# _____________________________________________________________________________
#                                   Pare aqui
# _____________________________________________________________________________
from pandas import read_excel, ExcelWriter, concat
from sys import path as syspath
syspath.append('M:\\Rotinas\\python\\scripts\\09.Busca_dados_apontamentos')
from table import table as tb
from table import get_available_data, search_ocnpylibdata
from db import get_ocnpylib, get_ucds
import time as crono
import matplotlib.pyplot as plt
syspath.append('M:\\Rotinas\\python\\graph')
from custom import caxes, plot_custom


def salva_planilha():

    if wind and wave and curr:
        # Juntando todos os parametros
        exfile = wdtb.join([wvtb, crtb])
        exfile.to_excel(f'{path}\\tabela_preenchida.xlsx')
    elif not(curr) and wind and wave:
        # Juntando todos os parametros
        exfile = wdtb.join([wvtb])
        exfile.to_excel(f'{path}\\tabela_preenchida.xlsx')
    elif not(wave) and wind and curr:
        # Juntando todos os parametros
        exfile = wdtb.join([crtb])
        exfile.to_excel(f'{path}\\tabela_preenchida.xlsx')
    elif not(wind) and wave and curr:
        # Juntando todos os parametros
        exfile = wvtb.join([crtb])
        exfile.to_excel(f'{path}\\tabela_preenchida.xlsx')
    elif not(wind) and not(wave) and curr:
        exfile = crtb.copy()
        exfile.to_excel(f'{path}\\tabela_preenchida.xlsx')
    elif wind and not(wave) and not(curr):
        exfile = wdtb.copy()
        exfile.to_excel(f'{path}\\tabela_preenchida.xlsx')
    elif not(wind) and wave and not(curr):
        exfile = wvtb.copy()
        exfile.to_excel(f'{path}\\tabela_preenchida.xlsx')

    return exfile


# _____________________________________________________________________________
#                           LENDO TABELA DO CLIENTE
# _____________________________________________________________________________
table = read_excel(f'{path}\\{tabela}',
                   header=0,
                   skiprows=skiprows)
table = table.dropna(how='all')
# Check das datasD
table2 = tb.check_dates(table,
                        col_di=COLDI,
                        col_hi=COLHI,
                        col_df=COLDF,
                        col_hf=COLHF)
table2['id'] = table.index
# _____________________________________________________________________________
#                           Carregando os dados disponíveis
# _____________________________________________________________________________
time0 = crono.time()
print('{}'.format(60 * '#'))
print('# {:^56} #'.format('CARREGANDO OS DADOS'))

if wind:
    print('#     {:<52} #'.format('+ Vento'))
    wddata = get_available_data.load(
        table2,
        func=get_ocnpylib.get_wind,
        col_df='DataFinal UTC',
        col_ucd=COLUCD)
if wave:
    print('#     {:<52} #'.format('+ Onda'))
    wvdata = get_available_data.load(
        table2,
        col_df='DataFinal UTC',
        col_ucd=COLUCD,
        func=get_ocnpylib.get_wave)
if curr:
    print('#     {:<52} #'.format('+ Corrente'))
    data1 = get_available_data.load(
        table2,
        col_df='DataFinal UTC',
        col_ucd=COLUCD,
        func=get_ocnpylib.get_curr)
    data2 = get_available_data.load(
        table2,
        col_df='DataFinal UTC',
        col_ucd=COLUCD,
        func=get_ocnpylib.get_curr_profile)
    # Juntando sensores pontuais e perfiladores
    crdata = data1.append(data2)

# _____________________________________________________________________________
#                   BUSCA DOS DADOS E PREENCHIMENTOS DA TABELA
# _____________________________________________________________________________
print('# {} #'.format(56 * '-'))
print('# {:^56} #'.format('BUSCA PELOS DADOS NOS APONTAMENTOS'))
print('# {} #'.format(56 * '-'))

if wind:
    print('#     {:<52} #'.format('> Vento'))
    wdtb = search_ocnpylibdata.search_wind(
        table2,
        data=wddata,
        col_df='DataFinal UTC',
        col_ucd=COLUCD,
        col_lat=COLAT,
        col_lon=COLON,
        hora_antes=HRANTES,
        hora_depois=HRDEPOIS)

if wave:
    print('#     {:<52} #'.format('> Onda'))
    wvtb = search_ocnpylibdata.search_wave(
        table2,
        data=wvdata,
        col_df='DataFinal UTC',
        col_ucd=COLUCD,
        col_lat=COLAT,
        col_lon=COLON,
        hora_antes=HRANTES,
        hora_depois=HRDEPOIS)

if curr:
    print('#     {:<52} #'.format('> Corrente'))
    crtb = search_ocnpylibdata.search_curr(
        table2,
        data=crdata,
        col_df='DataFinal UTC',
        col_ucd=COLUCD,
        col_lat=COLAT,
        col_lon=COLON,
        hora_antes=HRANTES,
        hora_depois=HRDEPOIS)

exfile = salva_planilha()

print('# {:<56} #'.format(
    f'° Tempo de processamento: {round((crono.time() - time0)/ 60, 1)} min'))
print('# **{:^52}** #'.format('Fim'))
print('{}'.format(60 * '#'))

# _____________________________________________________________________________
#                           Plota série temporal
# _____________________________________________________________________________

if plotst:
    plot_custom.temp_serie_config()
    if colplot:
        lopparam = set(table2[colplot].values)
    elif plotline:
        lopparam = table2.index
    for x in lopparam:
        if colplot:
            dataplot = exfile.xs(x, level=colplot)
            print(f'Plotando {x}')
            pname = f'{x}_{param}'
        elif plotline:
            dataplot = exfile.xs(x, level='id')
            print(f'Plotando linha {x}')
            pname = f'Apontamento {x}'
        # retirando levels desnecessários
        dataplot = dataplot.droplevel(dataplot.index.names[:-1])
        # retirando colunas das UCDS
        dropcol = [x for x in dataplot.columns if x.startswith('UCD')]
        dataplot = dataplot.drop(dropcol, axis=1)

        for param in ['VENTO', 'ONDA', 'CORRENTE']:
            paramcols = [x for x in dataplot.columns if param in x]
            paramplot = dataplot[paramcols]
            if len(paramplot.columns) >= 1:
                fig, ax = plt.subplots(
                    len(paramplot.columns),
                    1,
                    figsize=(15, 10))

                for x, clm in enumerate(paramplot.columns):
                    paramplot[clm].plot(ax=ax[x], marker='o')
                    ax[x].set_ylabel(clm)
                    if 'DIR' in clm:
                        caxes.direction_yaxis(ax[x])
                if colplot:
                    ax[0].set_title(x)

                fig.savefig(
                    f'{path}\\{pname}_{param}.png',
                    format='png',
                    bbox_inches='tight',
                    dpi=600)
                plt.close()
    print('Finalizado')
