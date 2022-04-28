#!/usr/bin/env python
'''

    Rotina para carregar e salvar dados de corrente do OpenDap.
    Exporta arquivo excel com dados do modelo 96h antes no momento atual e 120h
    depois.
    Caso haja perfilador disponível, a rotina exporta perfil de corrente do
    momento extrapolado juntando dados medido com dados de modelo.


    Autor: Francisco Thiago Franca Parente (BHYK)
    Data de criação: 09/07/2020
    Versão: 1.0

    Edições:
        + 09/09/2020: Adição do modelo hycom 1-24 grid v1

'''
from datetime import datetime, timedelta
from os.path import normpath
# _____________________________________________________________________________
#                                   Modificar aqui
# _____________________________________________________________________________

# Diretório onde serão salvos os dados e figuras
PATH = normpath('XXXXXXXXXXXXXXX')

# UCD de interesse
UCD = ['XXXXXXXXXXXXXX']

# Modelo de interesse, as opções são:
#   'Hycom 1/12 3D (gv1)'   |   REMO HYCOM 1/12 (analysis, grid v1) 3D
#   'Hycom 1/12 3D (gv2)    |   REMO HYCOM 1/12 (analysis, grid v2) 3D
#   'Hycom 1/24 2D (gv1)'   |   REMO HYCOM 1/24 (analysis, grid v1) 2D
#   'Hycom 1/24 3D (gv1)'   |   REMO HYCOM 1/24 (analysis, grid v1) 3D
#   'Hycom 1/24 2D (gv2)'   |   REMO HYCOM 1/24 (analysis, grid v2) 2D
#   'Hycom 1/24 3D (gv2)'   |   REMO HYCOM 1/24 (analysis, grid v2) 3D
#   'mercator'              |   MERCATOR

# ATENÇÃO! Caso não tenha um modelo de interesse e queira comprar os resultados
# de todos os listados a cima, deixar esta variável como None
# Ex.: modelo = None
modelo = None

# Datas de interesse (HORA UTC)
# Aqui eu deixei um default de 24h antes da execução da rotina e 48h depois
# Caso queira um período diferente, comente as linhas default e escreva a data
# no formato dd/mm/YYYY HH:MM:SS entre aspas simples
# (Ex.: '01/01/2020 00:00:00')
now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
DATEMIN = (now - timedelta(hours=72)).strftime('%d/%m/%Y %H:%M:%S')
DATEMAX = (now + timedelta(hours=72)).strftime('%d/%m/%Y %H:%M:%S')

# _____________________________________________________________________________

import xarray
from pandas import ExcelWriter, date_range, DataFrame, concat
import ocnpylib as ocpy
from sys import path
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
pth1 = 'M:\\Rotinas\\python\\'
for d in ['data', 'graph']:
    pth2 = pth1 + d
    path.append(pth2)
import OCNdb as ocn
from custom import caxes
from sklearn.linear_model import LinearRegression
from collections import namedtuple

# _____________________________________________________________________________

opendap_link = {
    'REMO HYCOM 1/12 2D (analysis, v1)': '{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxx'),
    'REMO HYCOM 1/12 3D (analysis, v1)': '{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxxxxxxx'),
    'REMO HYCOM 1/24 2D (analysis, v1)': '{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxxx'),
    'REMO HYCOM 1/24 3D (analysis, v1)': '{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxxxx'),
    'REMO HYCOM 1/12 2D (analysis, v2)': '{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxxxxxxx'),
    'REMO HYCOM 1/12 3D (analysis, v2)': '{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxxxx'),
    'REMO HYCOM 1/24 2D (analysis, v2)': '{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxxxxxxxxxxxxx'),
    'REMO HYCOM 1/24 3D (analysis, v2)': '{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxx'),
    'MERCATOR GLORYS12V1': '{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxxxxxx'),
    'Hycom Consortium 3D': '{}{}{}'.format(
        'xxxxxxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxxxxxxxxx',
        'xxxxxx'),
    'Hycom Consortium 2D': '{}{}{}'.format(
        'xxxxxxxxxxxxxxxx',
        'xxxxxxxxxxxxxxxxxx',
        'xxxxxxxxx')
}

# cores para vetores da media vetorial
colors = ['#c0392b', '#196f3d', '#f1c40f', '#884ea0']
# _____________________________________________________________________________
#                       LENDO DADOS DO MODELO
# _____________________________________________________________________________

# Pegando posição da UCD
bdname = ocpy.SECRETl(ocpy.SECRET(UCD))[0]
lon, lat = ocpy.SECRET(ocpy.SECRET(UCD))
# Criando variável de tempo para busca nos dados do opendap
dti = datetime.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S')
dtf = datetime.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S')

# Primeiro, caso o usuário não tenha determinado um modelo de interesse
head = namedtuple('modelos', 'title data')
raw = []
print('{:_<40} | {:_<40}'.format('Lendo dados do OpenDap', ' '))

if modelo is None:
    modelos = opendap_link.keys()
else:
    if modelo in opendap_link.keys():
        modelos = [modelo]
    else:
        raise RuntimeError('{} - Opção de modelo inválida'.format(modelo))

for source in modelos:
    OpenDap = xarray.open_dataset(
        opendap_link[source]).sel(
            latitude=lat,
            longitude=lon,
            method='nearest')
    label = source
    dist = (abs(float(OpenDap.latitude.values) - lat),
            abs(float(OpenDap.longitude.values) - lon))
    # Verificação se ponto de lat e lon esta dentro do domínio
    if max(dist) > 1:
        print('{:_<40} | {:_<40}'.format(
            label, 'Não possui ponto próximo ao de interesse'))
        continue
    # Seleção temporal do OpenDap
    dtfopd = datetime.utcfromtimestamp(
        OpenDap.time[-1].values.tolist() / 1e9)
    if dti < dtfopd:
        print('{:<40} | {:<40}'.format(label, OpenDap.source))
        OpenDap = OpenDap.sel(
            time=date_range(dti, dtf, freq='H'),
            method='nearest')
        # Criando DataFrame com informações do OpenDap
        OpenDap.load()
        data = OpenDap.to_dataframe().reset_index().set_index('time')
        select_data = data[(data.index >= dti) & (data.index <= dtf)]
        raw.append(head(label, select_data))
    else:
        print('{:_<40} | {:_<40}'.format(
            label,
            'Sem dados no período solicitado'))

# _____________________________________________________________________________
#       Retirando duplicatas e colunas indesejadas / calculando int e dir
# _____________________________________________________________________________
acron = {'REMO': ['sw_cur_u', 'sw_cur_v'],
         'MERCATOR': ['u', 'v'],
         'Hycom': ['sw_cur_u', 'sw_cur_v']}
opendap = []
print('{:_<40} | {:_<40}'.format(
    'Retirando duplicatas',
    'Calculando int e dir'))

for ix in range(raw.__len__()):
    slcdata = raw[ix].data
    # laço de profundidade para retirada de duplicatas
    clean_data = DataFrame()
    for depth in np.unique(slcdata['depth'].values):
        clean_data = clean_data.append(slcdata[
            slcdata['depth'] == depth].drop_duplicates())
    # calculando intensidade e direção e adicionando ao DataFrame
    clean_data['Int'], clean_data['Dir'] = ocpy.SECRET(
        clean_data[acron[raw[ix].title.split(' ')[0]][0]].values,
        clean_data[acron[raw[ix].title.split(' ')[0]][1]].values,
        'ocean')
    opendap.append(head(raw[ix].title.replace('/', '-'), clean_data))

# _____________________________________________________________________________
#           Escrevendo tabela excel com dados do(s) modelo(s)
# _____________________________________________________________________________
excel_modelos = ExcelWriter('{}\\modelos.xlsx'.format(PATH))
for sheet in range(opendap.__len__()):
    opendap[sheet].data.to_excel(
        excel_modelos,
        sheet_name='{:30.30}'.format(opendap[sheet].title.replace('/', '-')))
excel_modelos.close()

# _____________________________________________________________________________
#                       LENDO DADOS DO OCEANOP
# _____________________________________________________________________________

ocndata = ocn.get_BD(
    UCD, [DATEMIN, DATEMAX], 'curr', layers=list(np.arange(0, 100)))

if ocndata.shape[0] > 0:


    # Criando arquivo excel
    writer = ExcelWriter("{}\\{}.xlsx".format(
        PATH,
        bdname.replace(' ', '_')))
    # laço por instrumento para reindexação com tempo regular e geração
    # de aqruivo .dat no formato dos dados da pasta de contingência.
    for i in set(ocndata.index.get_level_values(1)):

        regtime = date_range(
            datetime.strptime(DATEMIN, '%d/%m/%Y %H:%M:%S'),
            datetime.strptime(DATEMAX, '%d/%m/%Y %H:%M:%S'),
            freq='h')
        newfmt = DataFrame()
        # ajustando tempo para todas profundidades
        for dp in set(ocndata.loc[bdname].loc[i].index.get_level_values(0)):
            slcd = ocndata.loc[bdname].loc[i].loc[dp].reindex(
                index=regtime,
                fill_value=-9999.)
            newfmt = newfmt.append(concat([slcd], keys=[dp], names=['DEPTH']))

        newfmt = newfmt.sort_index(level=0).reset_index()
        newfmt = newfmt.sort_values(by=['level_1', 'DEPTH'],
                                    ascending=[True, True])

        newfmt['date'], newfmt['time'] = np.nan, np.nan
        newfmt['date'] = newfmt['level_1'].apply(
            lambda x: x.strftime('%Y/%m/%d'))
        newfmt['time'] = newfmt['level_1'].apply(
            lambda x: x.strftime('%H:%M:%S'))
        newfmt = newfmt.drop('level_1', axis=1)

        newfmt = newfmt[['date', 'time', 'HCSP', 'HCDT', 'DEPTH']]
        newfmt.columns = ['date', 'time','Current_Intensity (m/s)',
                          'Current_Direction (Degrees)', 'Depth (m)']

        for cc in newfmt.columns:
            newfmt.loc[newfmt[cc].isnull(), cc] = -9999.

        datfile = open(
            '{}\\{}_{}.dat'.format(PATH,
                                   bdname.replace(' ', '_'),
                                   i),
            'w')
        datfile.write('{}\n# Current data {} at {}\n# UTC {}\n{}\n'.format(
            '# ----------------- OCEANOP ----------------------',
            now,
            bdname,
            '-  Current_Intensity -  Current_Direction  -  Depth',
            '# Time -  (m/s)             -  (Degrees)          -  (m)'))
        newfmt.to_csv(
            datfile,
            header=False,
            sep=" ",
            index=False,
            line_terminator='\n')
        datfile.close()
        newfmt.set_index('date').to_excel(writer, sheet_name=i)
    writer.close()

    # _________________________________________________________________________
    #               Plota série temporal da camada superficial
    # _________________________________________________________________________

    figc, axc = plt.subplots(2, 1, figsize=[20, 15])
    for ix in range(opendap.__len__()):
        axc[0].plot(
            opendap[ix].data.Int[
                opendap[ix].data.depth==opendap[ix].data.depth[0]],
            label=opendap[ix].title,
            marker='o',
            markersize=8,
            linewidth=5,
            alpha=.3)
        axc[1].plot(
            opendap[ix].data.Dir[
                opendap[ix].data.depth==opendap[ix].data.depth[0]],
            label=opendap[ix].title,
            marker='o',
            markersize=8,
            linewidth=5,
            alpha=.3)
    for inst in ocndata.index.levels[1]:
        try:
            prof = np.unique(
                ocndata.loc[bdname].loc[inst].index.get_level_values(0))[0]
        except Exception:
            prof = np.unique(
                [x
                 for x in ocndata.loc[bdname].loc[inst].index.get_level_values(0)
                 if isinstance(x, float)])[0]
        axc[0].plot(
            ocndata.loc[bdname].loc[inst].loc[prof].HCSP,
            label='{} ({} - {} m)'.format(bdname, inst, prof),
            linestyle='--',
            linewidth=2)
        axc[1].plot(
            ocndata.loc[bdname].loc[inst].loc[prof].HCDT,
            label='{} ({} - {} m)'.format(bdname, inst, prof),
            linestyle='--',
            linewidth=2)

    axc[0].grid('on')
    axc[1].grid('on')
    axc[1].set_ylim([0, 360])
    axc[0].set_ylabel('Intensidade (m/s)')
    axc[1].set_ylabel('Direção (°)')

    caxes.direction_yaxis(axc[1])
    caxes.fmt_time_axis(axc[0])
    caxes.fmt_time_axis(axc[1])

    axc[1].legend(
        prop={'size': 14},
        bbox_to_anchor=(.5, -.2),
        ncol=4,
        loc='center')

    figc.savefig('{}\\{}_comparacao.png'.format(PATH, bdname), format='png')

    # _________________________________________________________________________
    #               Plota média vetorial das últimas 24 h
    # _________________________________________________________________________

    figc, axc = plt.subplots(1, 1, figsize=[20, 15])
    vectors = {}
    for ix in range(opendap.__len__()):
        u, v = ocpy.SECRET(
            opendap[ix].data.Int[
                opendap[ix].data.depth==opendap[ix].data.depth[0]][
                    now - timedelta(hours=24):now].values,
            opendap[ix].data.Dir[
                opendap[ix].data.depth==opendap[ix].data.depth[0]][
                    now - timedelta(hours=24):now].values,
            str_conv='ocean')

        U, V, SPD = u.mean(), v.mean(), np.sqrt(u.mean()**2 + v.mean()**2)
        vectors[opendap[ix].title] = [
            U/SPD, V/SPD]

    # Plotando direção dos modelos
    size = len(vectors)
    axc.quiver(
        np.arange(size), [0*np.arange(size)],
        [x[0] for x in vectors.values()],
        [x[1] for x in vectors.values()],
        width=.02, scale=4, headwidth=3.5,
        pivot="mid", headlength=4.5)

    for c, inst in enumerate(ocndata.index.levels[1]):
        try:
            prof = np.unique(
                ocndata.loc[bdname].loc[inst].index.get_level_values(0))[0]
        except Exception:
            prof = np.unique(
                [x
                 for x in ocndata.loc[bdname].loc[inst].index.get_level_values(0)
                 if isinstance(x, float)])[0]

        u, v = ocpy.SECRET(
            ocndata.loc[bdname].loc[inst].loc[prof].HCSP[
                now - timedelta(hours=24):now].values,
            ocndata.loc[bdname].loc[inst].loc[prof].HCDT[
                now - timedelta(hours=24):now].values,
            str_conv='ocean')

        U, V, SPD = u.mean(), v.mean(), np.sqrt(u.mean()**2 + u.mean()**2)

        axc.quiver(
            np.arange(size), [0*np.arange(size)],
            [U/SPD for x in range(size)],
            [V/SPD for x in range(size)], color=colors[c],
            width=.02, scale=4, headwidth=3.5,
            pivot="middle", headlength=4.5, alpha=.5,
            label='{} ({})'.format(ocndata.index.levels[0][0], inst))

    xtiklbl = [
        '{}\n({}'.format(x.split('(')[0], x.split('(')[1]) if x.startswith('R')
        else '{}'.format(x.split(' ')[0]) for x in vectors.keys()]

    axc.set_xlim([-1, size])
    plt.xticks(np.arange(size), xtiklbl, fontsize=18)
    plt.yticks([])

    axc.legend(
        prop={'size': 20},
        loc='upper right')

    axc.set_title('Média vetorial das últimas 24h', fontsize=28)

    figc.savefig(
        '{}\\{}_média vetorial24h.png'.format(PATH, bdname), format='png')

    # _________________________________________________________________________
    #                   MESCLANDO DADOS DE PERFIL OCEANOP + OPENDAP
    # _________________________________________________________________________

    if 'ADCP' in ocndata.index.levels[1]:

        perfil_ocn = ocndata.loc[bdname].loc['ADCP']
        layers = np.unique(perfil_ocn.index.get_level_values(0))

        ocntime = perfil_ocn.index.get_level_values(1)

        for ix in range(opendap.__len__()):

            model_data = opendap[ix].data

            if '3D' in opendap[ix].title:
                similar_time = [
                    time for time in ocntime if time in model_data.index]
                timeplot = [now, similar_time[0], similar_time[1]]

                fig1, _ = plt.subplots(1, 1, figsize=[15, 10])
                plt.subplots_adjust(hspace=.4)
                plt.xticks([]), plt.yticks([])
                fig2, _ = plt.subplots(1, 1, figsize=[15, 10])
                plt.subplots_adjust(hspace=.4)
                plt.xticks([]), plt.yticks([])

                pos = [(1, 2, 1), (2, 2, 2), (2, 2, 4)]

                # Laço temporal
                for x, t in enumerate(timeplot):
                    if t is now:
                        id_search = date_range(
                            model_data.index[0].strftime('%Y/%m/%d %H:%M:%S'),
                            model_data.index[-1].strftime('%Y/%m/%d %H:%M:%S'),
                            freq=model_data.index[1] - model_data.index[0])
                        idt = id_search.get_loc(key=t, method='nearest')
                        tmodelo = id_search[idt]
                    else:
                        tmodelo = t
                    tdata = t

                    inten_opd = model_data[
                        model_data.index == tmodelo].Int.values
                    direc_opd = model_data[model_data.index == tmodelo][
                        'Dir'].values[~np.isnan(inten_opd)]
                    depth_opd = model_data[
                        model_data.index == tmodelo].depth.values[
                            ~np.isnan(inten_opd)]
                    inten_opd = inten_opd[~np.isnan(inten_opd)]

                    depth_ocn = perfil_ocn.xs(tdata, level=1).index.values
                    inten_ocn = perfil_ocn.xs(tdata, level=1).HCSP.values
                    direc_ocn = perfil_ocn.xs(tdata, level=1).HCDT.values

                    # Pegando comportamento das camdas abaixo da última camada
                    # de medição do sensor OCN seguindo o modelo
                    deep_inte = inten_opd[depth_opd > depth_ocn[-1]]
                    deep_direc = direc_opd[depth_opd > depth_ocn[-1]]
                    deep_dept = depth_opd[depth_opd > depth_ocn[-1]]

                    # Criando modelo polinomial
                    xm = deep_dept.reshape((-1, 1))
                    xp = PolynomialFeatures(
                        degree=2,
                        include_bias=False).fit_transform(xm)
                    int_equation = LinearRegression().fit(xp, deep_inte)

                    # Extrapolando camadas sem dados do sensor ocn
                    int_prd = int_equation.predict(
                        xp) / int_equation.predict(xp)[0]
                    int_ext = np.append(inten_ocn, int_prd * inten_ocn[-1])
                    dir_ext = np.append(direc_ocn, deep_direc)
                    dep_ext = np.append(depth_ocn, deep_dept)

                    # _________________________________________________________
                    #                           PLOTANDO
                    # _________________________________________________________
                    ax = fig1.add_subplot(pos[x][0], pos[x][1], pos[x][2])
                    ax.plot(
                        inten_opd, depth_opd,
                        color='b', label=opendap[ix].title,
                        linewidth=3, alpha=.6)
                    ax.plot(
                        int_ext, dep_ext,
                        linestyle='--', color='r', label='Extrapolado')
                    ax.plot(inten_ocn, depth_ocn, color='k', label=bdname)
                    ax.set_ylim([0, ax.get_ylim()[-1]])
                    ax.invert_yaxis()
                    ax.set_xlabel('Intensidade')
                    ax.grid(True)
                    ax.set_title((
                        '{}: {:%d-%m-%Y %H:%M} (UTC)\n'.format(bdname, tdata) +
                        '{}: {:%d-%m-%Y %H:%M} (UTC)\n'.format(
                            opendap[ix].title, tmodelo)),
                        x=1, ha='right', fontsize=10)

                    fig1.suptitle((
                        "{} / Lat: {:.2f} / Lon: {:.2f}\n".format(
                            opendap[ix].title,
                            model_data.latitude[0],
                            model_data.longitude[0]) +
                        "OCEANOP - {} / Lat: {:.2f} / Lon: {:.2f}".format(
                            bdname,
                            lat,
                            lon)), x=.9, fontsize=14, ha='right')
                    if x is 2:
                        lgd = ax.legend(
                            ncol=6, loc='center',
                            frameon=False, bbox_to_anchor=(-0.15, -.2))

                    ax = fig2.add_subplot(pos[x][0], pos[x][1], pos[x][2])
                    ax.plot(
                        direc_opd, depth_opd, color='b',
                        label=opendap[ix].title,
                        linewidth=3, alpha=.6)
                    ax.plot(
                        dir_ext, dep_ext,
                        linestyle='--', color='r', label='Extrapolado')
                    ax.plot(direc_ocn, depth_ocn, color='k', label=bdname)
                    ax.set_ylim([0, ax.get_ylim()[-1]])
                    ax.invert_yaxis()
                    ax.set_xlabel('Direção')
                    ax.grid(True)
                    ax.set_title(
                        '{}: {:%d-%m-%Y %H:%M} (UTC)\n'.format(bdname, tdata) +
                        '{}: {:%d-%m-%Y %H:%M} (UTC)\n'.format(
                            opendap[ix].title,
                            tmodelo),
                        x=1, ha='right', fontsize=10)
                    fig2.suptitle((
                        "{} / Lat: {:.2f} / Lon: {:.2f}\n".format(
                            opendap[ix].title,
                            model_data.latitude[0],
                            model_data.longitude[0]) +
                        "OCEANOP - {} / Lat: {:.2f} / Lon: {:.2f}".format(
                            bdname,
                            lat,
                            lon)), x=.9, fontsize=14, ha='right')
                    if x is 2:
                        lgd = ax.legend(
                            ncol=6, loc='center',
                            frameon=False, bbox_to_anchor=(-0.15, -.2))

                    # Salvando arquivo de perfil extrapolado para a última hora
                    if t is now:
                        ext_perfil = DataFrame(
                            data={'int': int_ext, 'dir': dir_ext},
                            index=[dep_ext]
                        )
                        wr = ExcelWriter(
                            "{}\\{}_com_{}_{:%d-%m-%Y_%Hh%M}_UTC.xlsx".format(
                                PATH,
                                bdname.replace(' ', '_'),
                                opendap[ix].title.replace(' ', '_'),
                                t))
                        ext_perfil.to_excel(wr)
                        wr.close()
                fig1.savefig('{}\\{}_intensidade.png'.format(
                    PATH, opendap[ix].title.replace(' ', '_')), format='png')
                fig2.savefig('{}\\{}_direcao.png'.format(
                    PATH, opendap[ix].title.replace(' ', '_')), format='png')
