'''

    Descrição:
        Funções de acesso aos BDs do OCEANOP utilizando as funções documentadas
        do endereço:
        scret

    [ pyocnp_func(), cota_instrumento(), get_oBD() ]

        Funções relacionadas ao BD antigo, que utilizam o pacote PyOcnp.
        secret

    [ ocnpylib_func(), inf_ucd(), check_portal(), raw_data(), get_BD() ]

        Funções relacionadas ao BD novo, que utilizam o pacote OCNPyLib.
        secret

    Authors:
        Francisco Thiago Franca Parente (BHYK)
        E-mail: thiagoparente.AMBILEV@petrobras.com.br

    Created - 10 jun 2020
'''
import pyocnp
import ocnpylib
from pandas import DataFrame, concat, date_range
import numpy as np
from pyocnp import DESVVV, PRODD
from datetime import datetime

# _____________________________________________________________________________
#                               Banco antigo
# _____________________________________________________________________________


def pyocnp_func(param):
    '''
        Fornece dicionário de funções de acesso ao BD antigo para cada
        instrumento.

        * Argumentos___________________________________________________________
            param   |   String do parametro de interesse
                    |   Opções: 'meteo', 'curr', 'wave'
    '''
    inst_func = {
        'meteo': {
            'young': {
                'func': pyocnp.secretfunc1,
                'args': ['WSPD', 'WDIR', 'RELH', 'DRYT', 'ATMS', 'GSPD3']}
        },
        'curr': {
            'adcp': {
                'func': pyocnp.secretfunc2,
                'args': ['HCDT', 'HCSP']},
            'fsi2d': {
                'func': pyocnp.secretfunc3,
                'args': ['HCDT', 'HCSP']},
            'fsi3d': {
                'func': pyocnp.secretfunc4,
                'args': ['HCDT', 'HCSP']},
            'hadcp': {
                'func': pyocnp.secretfunc5,
                'args': ['HCDT', 'HCSP']},
            'miros': {
                'func': pyocnp.secretfunc6,
                'args': ['CHCDT', 'CHCSP']}
        },
        'wave': {
            'miros': {
                'func': pyocnp.secretfunc7,
                'args': ['VAVH', 'VPEDM', 'VTPK1']},
            'fsi3d': {
                'func': pyocnp.secretfunc8,
                'args': ['VAVH', 'VTPK1']}
        }}
    inf = inst_func[param]
    return inf


def cota_instrumento(instrumento, id_local, lst_daterange, bd='PROD'):
    '''
        Fornece DataFrame com as informações de cota, distancia entre camadas
        e total de camadas para os correntômetros e perfiladores.

        * Argumentos___________________________________________________________
            instrumeto      |   String do instrumento de interesse
                            |   Opções: 'adcp', 'fsi2d', 'fsi3d', 'hadcp'
            id_local        |   id da unidade de interesse
            lst_daterange   |   lista com data inicial e data final da busca
                            |   Ex.: [
                            |       'dd/mm/YYYY HH:MM:SS',
                            |       'dd/mm/YYYY HH:MM:SS']
    '''

    BANCO = bd.upper()
    access = PRODD
    if BANCO == "DESV":
        access = DESVVV

    inst = instrumento.lower()
    inst_inf = {
        'adcp': {
            'func': pyocnp.secretfunc9,
            'args': ['COTA', 'DST_CAMADA', 'TOT_CAMADA']},
        'fsi2d': {
            'func': pyocnp.secretfunc10,
            'args': ['COTA']},
        'fsi3d': {
            'func': pyocnp.secretfunc11,
            'args': ['COTA']},
        'hadcp': {
            'func': pyocnp.secretfunc12,
            'args': ['COTA', 'DST_FAIXA', 'TOT_FAIXA']}
    }

    if inst not in inst_inf.keys():
        raise RuntimeError('Erro: {} não disponível.'.format(instrumento))
    else:
        rootData = inst_inf[inst]['func'](
            id_local,
            lst_daterange,
            inst_inf[inst]['args'],
            str_dbaccess=access)
    rawData = {}
    for x, arg in enumerate(inst_inf[inst]['args']):
        rawData[arg] = rootData['data{}'.format(x)]
    cota = DataFrame(data=rawData, index=rootData['t'])

    return cota


def get_oBD(ucds, dates, param, layers=[0, 0],
            inst=None, gust=False, bd='PROD'):
    '''
        Função de acesso aos dados do BD antigo.

        * Argumentos___________________________________________________________
        ucds        |   Lista de UCDs (list)
        dates       |   [data inicial, data final]
                    |   data inicial (str - 'dd/mm/YYYY HH:MM:SS')
                    |   data final (str - 'dd/mm/YYYY HH:MM:SS')
        param       |   String do parametro de interesse
                    |   Opções: ['meteo', 'curr', 'wave']
        layers      |   Lista com a primeira camada e a ultima camada de
                    |   interesse (list)
        inst        |   String de instrumento de interesse
                    |   Opções:
                    |   ['young','adcp','fsi2d','fsi3d','hadcp','miros']
        bd          |   Argumento de escolha do banco!
                    |   Opções: 'PROD' ou 'DESV'

        * Edições______________________________________________________________
            + 03/08/2020
                Adicionado o argumento bd para opção de acesso ao banco de DESV
            + 12/08/2020
                Adicionado dados de rajada do banco antigo 
            + 15/06/2020
                Adicionada condição para não acessar dados de MIROS quando for
                solicitado os dados de corrente em PROD e ajustado bug ao
                acessar dados de ADCP
    '''

    BANCO = bd.upper()
    access = PRODD
    if BANCO == "DESV":
        access = DESVVV

    pyocnp_dict = pyocnp_func(param)
    # laço para a lista de ucds definidas pelo usuário
    ocndata = DataFrame()
    for ucd in ucds:
        local = pyocnp.read.ocndb.ucdid_byname_ocndb(
            ucd,
            str_dbaccess=access)[0]
        name = pyocnp.read.ocndb.ucdname_byid_ocndb(
            [local],
            str_dbaccess=access)
        # Checkando se o usuário definiu instrumento ou não
        if inst is not None and inst.lower() in pyocnp_dict.keys():
            inst_list = [inst.lower()]
        elif inst is not None and inst.lower() not in pyocnp_dict.keys():
            raise RuntimeError("[{} <- Instrumento inválido! Ver descrição.]")
        else:
            inst_list = pyocnp_dict.keys()
        # laço para lista de instrumentos possíveis para o parametro
        for i in inst_list:
            func = pyocnp_dict[i]['func']
            args = pyocnp_dict[i]['args']
            if i in ['young', 'fsi2d', 'fsi3d', 'miros']:
                try:
                    # laço para os casos de instrumentos pontuais
                    data = DataFrame()
                    for arg in args:
                        rootData = func(
                            local,
                            dates,
                            [arg],
                            str_dbaccess=access)
                        df = DataFrame(
                            data=rootData['data0'],
                            index=rootData['t'])
                        df.columns = [arg]
                        data = concat([data, df], axis=1)
                    if param == 'curr':
                        if i == 'miros' and BANCO == "PROD":
                            continue
                        elif i == 'miros' and BANCO == "DESV":
                            cota = 0
                            data.columns = ['HCDT', 'HCSP']
                        else:
                            cota = cota_instrumento(i, local, dates, bd=bd)
                        data = concat([data],
                                      keys=[np.mean(np.unique(cota))],
                                      names=['DEPTH'])
                    data = concat([data], keys=[i.upper()], names=['SENSOR'])
                    data = concat([data], keys=[name], names=['UCD'])
                    if i == 'young':
                        if gust is False:
                            data = data.drop(['GSPD3'], axis=1)
                        else:
                            data = data.drop(['WSPD'], axis=1)
                            data = data[
                                ['GSPD3', 'WDIR', 'ATMS', 'DRYT', 'RELH']]
                            data.columns = [
                                'WSPD3S', 'WDIR3S', 'ATMS', 'DRYT', 'RELH']
                    ocndata = ocndata.append(data)
                except Exception:
                    continue
            if i in ['adcp', 'hadcp']:
                try:
                    cota = cota_instrumento(i, local, dates, bd=bd)
                    # laço para os casos de instrumentos perfiladores
                    # laço para pronfundidades
                    rawData, data = DataFrame(), DataFrame()
                    layers_acces = np.arange(layers[0], layers[-1] + 1)
                    for p, n in enumerate(layers_acces):
                        # laço para parametros medidos pelo sensor
                        for x, arg in enumerate(args):
                            # Tentativa para busca de dados
                            try:
                                rootData = func(
                                    local,
                                    [int(n), int(n)],
                                    dates,
                                    [arg],
                                    str_dbaccess=access)
                                df = DataFrame(
                                    data={arg: rootData['data0']},
                                    index=rootData['t'])
                                rawData = concat([rawData, df], axis=1)
                            except Exception:
                                continue
                        # verificando profundidade da camada
                        try:
                            prof = cota.COTA + (n + 1) * cota.DST_CAMADA
                        except Exception:
                            prof = cota.COTA + (n + 1) * cota.DST_FAIXA
                        df = concat([rawData],
                                    keys=[np.mean(np.unique(prof))],
                                    names=['Prof'])
                        data = data.append(df)
                    data = concat([data], keys=[i.upper()], names=['SENSOR'])
                    data = concat([data], keys=[name], names=['UCD'])
                    ocndata = ocndata.append(data)
                except Exception:
                    continue
    try:
        return ocndata
    except Exception:
        return None


# _____________________________________________________________________________
#                               Banco novo
# _____________________________________________________________________________


def ocnpylib_func():

    '''
        Exporta dicionário com biblioteca de funções para acesso
        aos parâmetros disponíveis no BD novo
    '''
    param_f = {
        'meteo': {
            'TMP': ocnpylib.secretfunc,
            'UMD': ocnpylib.secretfunc,
            'BRM': ocnpylib.secretfunc,
            'ANM': [ocnpylib.secretfunc, ocnpylib.secretfunc]},
        'curr': {
            'CRT': ocnpylib.secretfunc,
            'PCV': ocnpylib.secretfunc_PROFILE,
            'PCH': ocnpylib.secretfunc_PROFILE},
        'wave': {
            'OND': ocnpylib.secretfunc,
            'RDR': ocnpylib.secretfunc}}
    return param_f


def inf_ucd(ucd, param):

    '''
        Exporta MultiIndex com sensores disponíveis na UCD para o
        parâmetro especificado.

        * Argumentos___________________________________________________________
            ucd     |   String da UCD de interesse. Ex: 'P-19'.
            param   |   String do parâmetro de interesse.
                    |   Os parâmetros disponíveis são:
                    |   'meteo' - Dados meteorolóficos
                    |   'wave'  - Dados de onda
                    |   'curr'  - Dados de corrente
    '''
    param = param.lower()
    ilocal = ocnpylib.secret(ucd)
    if ilocal[0] is not None:
        iinstl = ocnpylib.secret(ilocal)
        if iinstl[0] is not None:
            isensr = ocnpylib.secret(
                iinstl)
            ucdinf = ocnpylib.secret(isensr)
            df = DataFrame(
                data={
                    'sensor': [x[1] for x in ucdinf],
                    'ds': [x[0] for x in ucdinf],
                    'id_local_install': isensr})

            if param in ['meteo', 'wave', 'curr']:
                if param == 'meteo':
                    inf = df[df['ds'].str.startswith(("BRM", "UMD",
                                                      "ANM", "TMP"))]
                elif param == 'wave':
                    inf = df[df['ds'].str.startswith(("OND", "RDR"))]
                else:
                    inf = df[df['ds'].str.startswith(("CRT", "PCV", "PCH"))]
            else:
                raise RuntimeError(
                    "[{} <- Inválido! Verificar descrição.]".format(param))
    try:
        return inf
    except Exception:
        return None


def check_portal(data):
    '''
        Exporta DataFrame com os dados aprovados com base nas máscaras da
        função ocnpylib.secret(), mantendo somente as colunas
        fornecidas por esta função.
        Desta forma, todas as colunas de flags são dropadas.

        * Argumento
            data        |       RawData from  ocnpylib.secret
    '''

    aprovado = DataFrame()
    # pegando colunas dos parâmetros
    if data.index.levels[1][0].startswith(('PCV', 'PCH', 'CRT')):
        # Verificando o dado aprovado e disposto no portal
        filtro = ocnpylib.secret(data)
        name = data.keys()[data.keys().str.contains("DEPTH")][0]
        if data[name].count() == 0:
            filtro[name] = ['NONE' for x in range(filtro.shape[0])]
        else:
            filtro[name] = data[name]
        for x, depth in enumerate(np.unique(filtro[name])):
            for y, clm in enumerate(filtro.columns[0:-1]):
                df = data[filtro[name] == depth][
                    clm.split('_')[0]][
                        filtro[
                            filtro[name] == depth][
                                clm]].copy().droplevel([0, 1])
                if y == 0:
                    lvldf = df.copy()
                else:
                    lvldf = concat([lvldf, df], axis=1)
            lvlmx = concat(
                [lvldf],
                keys=[depth],
                names=['DEPTH'])
            if x is 0:
                aprovado = lvlmx.copy()
            else:
                aprovado = aprovado.append(lvlmx)
    else:
        filtro = ocnpylib.secret(data)
        for y, clm in enumerate(filtro.columns):
            df = data[
                clm.split('_')[0]][filtro[clm]].copy().droplevel([0, 1])
            aprovado = concat([aprovado, df], axis=1)
    try:
        aprovado = aprovado.to_frame()
    except Exception:
        pass
    return aprovado


def rawdata(data, flag=None):
    """
        Função que pega todos os dados, inclusive os reprovados, ou seja, fora
        do portal.
    """  
    params = ["HCSP", "HCDT", "WSPD3S", "WDIR3S", "WSPD10S", "WDIR10S",
              "RELH", "ATMS", "DRYT", "VAVH", "VTPK1", "VPED1", "VPEDM",
              "WSPD", "WDIR"]
    fvars = ['{}'.format(i) for i in params if i in data.keys()]

    # pegando colunas dos parâmetros
    if data.index.levels[1][0].startswith(('PCV', 'CRT')):
        rawdata = DataFrame()
        name = data.keys()[data.keys().str.contains("DEPTH")][0]
        if data[name].count() == 0:
            rawdata = rawdata.append(concat(
                        [data[fvars].copy().droplevel(
                            [0, 1])],
                        keys=['NONE'],
                        names=['DEPTH']))
        else:
            depths = data[name]
            for x, depth in enumerate(np.unique(depths)):
                rawdata = rawdata.append(concat(
                        [data[fvars][data[name] == depth].copy().droplevel(
                            [0, 1])],
                        keys=[depth],
                        names=['DEPTH']))
    elif data.index.levels[1][0].startswith(('PCH')):
        rawdata = data[fvars]
        rawdata = rawdata.droplevel([0, 1])
        name = data.keys()[data.keys().str.contains("DEPTH")]
        rawdata = concat([rawdata],
                         keys=[np.unique(data[name].values)[0]],
                         names=['DEPTH'])
    else:
        rawdata = data[fvars]
        rawdata = rawdata.droplevel([0, 1])
    return rawdata


def get_BD(ucds, dates, param, layers=[0],
           inst=None, gust=False, flag='portal'):

    '''
        Carrega dados do BD novo.

        * Argumentos___________________________________________________________
            ucds    |   Lista de UCDs (list)
            dates   |   [data inicial, data final]
                    |   data inicial (str - 'dd/mm/YYYY HH:MM:SS')
                    |   data final (str - 'dd/mm/YYYY HH:MM:SS')
            layers  |   Lista com indices das camadas de interesse (list)
            param   |   String do parametro de interesse
                    |   Opções: ['meteo', 'curr', 'wave']
            layers  |   Lista de indices (int) das camadas de
                    |   interesse.
            inst    |   String de instrumento de interesse
                    |   Opções:
                    |   ['adcp','fsi2d','fsi3d','hadcp','miros','awac']
            gust    |   False ou True. Caso usuário tenha interesse em
                    |   acessar dados de rajada, deve optar por True
            flag    |   Atributo de escolha dos dados do portal ou fora
                    |   Opções: 'portal' ou 'fora'  

        *Modificações__________________________________________________________
            + 02/07/2020 -  Foi retirado o período entre 01/08/2019 e
                            10/02/2020 quando não havia controle da
                            equipe de qualidade.
            + 03/08/2020 -  Adicionado o atributo 'flag' para opção de acesso
                            aos dados reprovados 

    '''
    if type(ucds) is not list:
        raise RuntimeError(['[Argumento ucds deve ser uma lista]'])
    if type(dates) is not list:
        raise RuntimeError(['[Argumento dates deve ser uma lista]'])
    # Checando se o parametro definido pelo usuário é válido
    if param in ['meteo', 'wave', 'curr']:
        # listando funções necessárias para acesso ao parâmetro
        fx = ocnpylib_func()[param]
        # Criando dataframe com os dados solicitados
        ocndata = DataFrame()
        # Loop para lista de UCDS
        for u, ucd in enumerate(ucds):
            # Criando DataFrame onde serão inseridos os dados das ucds de busca
            ucd_data = DataFrame()
            # Nome da UCD no BD para padronização
            name = ocnpylib.secret(ocnpylib.secret([ucd]))
            # Listando sensores disponíveis na UCD para o parâmetro escolhido
            ds_ucd = inf_ucd(ucd, param)

            # Meteorológicos devem ser tratados de forma diferente, pois temos
            # a possibilidade de mais de um sensor e de mais de uma função para
            # o mesmo sensor.
            if ds_ucd is not None:
                if param == 'meteo':
                    anm = [x for x in ds_ucd.ds.values if x.startswith('ANM')]
                    brm = [x for x in ds_ucd.ds.values if x.startswith("BRM")]
                    tmp = [x for x in ds_ucd.ds.values if x.startswith("TMP")]
                    umd = [x for x in ds_ucd.ds.values if x.startswith("UMD")]
                    # criando Dataframe com informações de sensores duplicados
                    sensdf = DataFrame()
                    # Loop para o caso de ter mais de um
                    for listsens in [anm, brm, tmp, umd]:
                        df = DataFrame()
                        for sens in listsens:
                            # Lista ids dos sensores disponívéis do parametro
                            id = ds_ucd[
                                ds_ucd.ds == sens].id_local_install.values[0]
                            # No caso do anemometro, há duas possibilidade de
                            # dados definidas pelo usuário no argumento 'gust'
                            if sens.split('_')[0] == 'ANM':
                                if gust is False:
                                    raw = fx['ANM'][0](int(id), dates)
                                else:
                                    raw = fx['ANM'][1](int(id), dates)
                            else:
                                raw = fx[sens.split('_')[0]](int(id), dates)
                            if raw.shape[0] > 0:
                                if flag is 'portal':
                                    bdf = check_portal(raw)
                                elif flag is 'fora':
                                    bdf = rawdata(raw)
                                else:
                                    raise RuntimeError(
                                        'Atributo flag inválido')
                                if bdf.shape[0] > 0:
                                    bdf[:'2020-02-10 13:00:00'] = np.nan
                                    df = df.append(bdf.sort_index())
                        # Preenchendo com o melhor sensor de cada instante
                        try:
                            df = df.groupby(
                                df.index, as_index=True).last(skipna=True)
                            sensdf = concat([sensdf, df], axis=1)
                        except Exception:
                            continue
                    if sensdf.shape[0] > 0:
                        sensdf = concat(
                            [sensdf],
                            keys=[ds_ucd.sensor.values[0]],
                            names=['SENSOR'])
                        ucd_data = ucd_data.append(
                            concat([sensdf], keys=name, names=['UCD']))
                else:
                    if inst is None:
                        # laço para lista de instrumentos disponíveis na ucd
                        for x, id in enumerate(ds_ucd.id_local_install.values):
                            if ds_ucd.ds.values[x].startswith(('PCV', 'PCH')):
                                raw = fx[ds_ucd.ds.values[x][:3]](
                                    int(id),
                                    dates,
                                    lst_layer=layers)
                            else:
                                raw = fx[ds_ucd.ds.values[x][:3]](
                                    int(id),
                                    dates)
                            if raw.shape[0] > 0:
                                if flag is 'portal':
                                    bdf = check_portal(raw)
                                elif flag is 'fora':
                                    bdf = rawdata(raw)
                                else:
                                    raise RuntimeError(
                                        'Atributo flag inválido')
                                if bdf.shape[0] > 0:
                                    if param is 'curr':
                                        df = DataFrame()
                                        for pf in bdf.index.levels[0]:
                                            check = bdf.loc[pf]
                                            check[:'2020-02-10 13:00:00'] = np.nan
                                            df = df.append(concat(
                                                [check.sort_index()],
                                                keys=[pf],
                                                names=['DEPTH']))
                                    else:
                                        df = bdf.sort_index().copy()
                                        df[:'2020-02-10 13:00:00'] = np.nan
                                    if df.shape[0] > 0:
                                        df = concat(
                                            [df],
                                            keys=[ds_ucd.sensor.values[x]],
                                            names=['SENSOR'])
                                        ucd_data = ucd_data.append(
                                            concat(
                                                [df],
                                                keys=name,
                                                names=['UCD']))
                    else:
                        try:
                            fc = ds_ucd[ds_ucd.sensor == inst.upper()]
                            if fc.ds.values[0].startswith(('PCV', 'PCH')):
                                raw = fx[fc.ds.values[0][:3]](
                                    int(fc.id_local_install.values[0]),
                                    dates,
                                    lst_layer=layers)
                            else:
                                raw = fx[fc.ds.values[0][:3]](
                                    int(fc.id_local_install.values[0]),
                                    dates)
                            if raw.shape[0] > 0:
                                if flag is 'portal':
                                    bdf = check_portal(raw)
                                elif flag is 'fora':
                                    bdf = rawdata(raw)
                                else:
                                    raise RuntimeError(
                                        'Atributo flag inválido')
                                if bdf.shape[0] > 0:
                                    df = DataFrame()
                                    for pf in bdf.index.levels[0]:
                                        check = bdf.loc[pf]
                                        check[:'2020-02-10 13:00:00'] = np.nan
                                        df = df.append(concat(
                                            [check.sort_index()],
                                            keys=[pf],
                                            names=['DEPTH']))
                                    if df.shape[0] > 0:
                                        df = concat(
                                            [df],
                                            keys=[fc.sensor.values[0]],
                                            names=['SENSOR'])
                                        ucd_data = concat(
                                            [df],
                                            keys=name,
                                            names=['UCD'])
                        except ValueError:
                            print("[{} sem dados de {}.]".format(name, inst))
            if ucd_data.shape[0] > 0:
                ocndata = ocndata.append(ucd_data)[
                    ucd_data.columns.tolist()]
    else:
        raise RuntimeError(
            '[{} <- Inválido! Verificar descrição.]'.format(param))
    try:
        return ocndata
    except ValueError:
        return None

# _____________________________________________________________________________
#                               Junta BDs
# _____________________________________________________________________________


def get_BDs(ucds, dates, param, inst=None, layer=0, gust=False, flag='portal'):

    '''
        Função para carregar ambos os BDs e compilar as informações
        Em sua primeira versão só será possível a compilação de 1 nível.
        Com isto, não está sendo contemplado o caso dos perfiladores.

        * Argumentos:
            ucds            |   Lista de UCDs (list)
            dates           |   [data inicial, data final]
                            |   data inicial (str - 'dd/mm/YYYY HH:MM:SS')
                            |   data final (str - 'dd/mm/YYYY HH:MM:SS')
            layers          |   Lista com a primeira camada e a ultima camada
                            |   de interesse (list)
            param           |   String do parametro de interesse
                            |   Opções: ['meteo', 'curr', 'wave']
            inst            |   String de instrumento de interesse
                            |   Opções:
                            |   ['adcp','fsi2d','fsi3d','hadcp','miros','awac']
            layer           |   Camada de interesse.

        ** Este argumento ainda está travado em 0, pois a função ainda não
        contempla os perfiladores.

        * Edição:
            + 14/01/2021
                Modificado o get_BDs para buscar somente dados no banco antigo
                quando a data incial for anterior a mudança de banco. Isso foi
                necessário devido ao erro em tentar buscar dados de aquadopp no
                banco antigo.
            + 12/08/2020
                Foi modificado o formato de saída no caso de corrente.
                Anteriormente a saída de corrente não considerava a
                profundidade. Agora a saída contempla também profundidade.
            + 09/11/2020
                Agora a saída não contempla mais profundidades. Começou a
                ocorrer conflitos com outros códigos devido aos labels da
                profundidade.
    '''

    ocndata = DataFrame()

    if flag is 'portal':
        oldbd = 'PROD'
    elif flag is 'fora':
        oldbd = 'DESV'
    else:
        raise RuntimeError('Argumento flag inválido!')

    if datetime.strptime(dates[0], '%d/%m/%Y %H:%M:%S') > datetime(2020, 2, 10):
        ocndata = get_BD(ucds, dates, param, inst=inst, gust=gust, flag=flag)
    else:
        for ucd in ucds:
            try:
                # carregado BD antigo
                oBD = get_oBD([ucd], dates, param, inst=inst,
                              gust=gust, bd=oldbd)
            except Exception:
                oBD = DataFrame()
            try:
                # carrega BD novo
                nBD = get_BD([ucd], dates, param, inst=inst,
                             gust=gust, flag=flag)
            except Exception:
                nBD = DataFrame()
            # Verificando se um dos BDs não possui dados
            if nBD.shape[0] == 0 and oBD.shape[0] == 0:
                continue
            if nBD.shape[0] is 0:
                ocndata = ocndata.append(oBD)
            if oBD.shape[0] is 0:
                ocndata = ocndata.append(nBD)
            # No caso dos dois bancos terem dados
            if nBD.shape[0] > 0 and oBD.shape[0] > 0:
                name = nBD.index.levels[0][0]
                # Pegando todos os instrumentos carregados
                dictinst = list(nBD.index.levels[1])
                dictinst.extend(list(oBD.index.levels[1]))
                dictinst = list(set(dictinst))
                for i in dictinst:
                    try:
                        if param == 'curr':
                            bds = oBD.xs(i, level=1).droplevel([1]).append(
                                nBD.xs(i, level=1).droplevel([1]))
                            bds.index = bds.index.set_names('DT_DATA', level=1)
                        else:
                            bds = oBD.xs(i, level=1).append(nBD.xs(i, level=1))
                            bds.index = bds.index.set_names('DT_DATA', level=1)
                        data = bds.groupby(
                            'DT_DATA',
                            as_index=True).first(skipna=True)
                        if param == 'curr':
                            profs = np.append(
                                np.unique(
                                    oBD.loc[
                                        ucd].loc[i].index.get_level_values(0)),
                                np.unique(
                                    nBD.loc[
                                        ucd].loc[i].index.get_level_values(0)))
                            data = concat(
                                [data],
                                keys=[round(np.mean(profs))],
                                names=['DEPTH'])
                        data = concat([data], keys=[i], names=['SENSOR'])
                        data = concat([data], keys=[name], names=['UCD'])
                        ocndata = ocndata.append(data)
                    except Exception:
                        try:
                            if param == 'curr':
                                ocndata = ocndata.append(
                                    concat(
                                        [concat(
                                            [concat(
                                                [nBD.xs(i, level=1).droplevel(
                                                    [0, 1])],
                                                keys=[
                                                    np.mean(np.unique(
                                                        nBD.xs(
                                                            i, level=1
                                                        ).index.get_level_values(1)
                                                    ))],
                                                names=['DEPTH'])],
                                            keys=[i],
                                            names=['SENSOR'])],
                                        keys=[name],
                                        names=['UCD']))
                            else:
                                ocndata = ocndata.append(
                                    concat(
                                        [concat(
                                            [nBD.xs(i, level=1).droplevel([0])],
                                            keys=[i],
                                            names=['SENSOR'])],
                                        keys=[name],
                                        names=['UCD']))
                        except Exception:
                            if param == 'curr':
                                ocndata = ocndata.append(
                                    concat(
                                        [concat(
                                            [concat(
                                                [oBD.xs(i, level=1).droplevel(
                                                    [0, 1])],
                                                keys=[
                                                    np.mean(np.unique(
                                                        oBD.xs(
                                                            i, level=1
                                                        ).index.get_level_values(1)
                                                    ))],
                                                names=['DEPTH'])],
                                            keys=[i],
                                            names=['SENSOR'])],
                                        keys=[name],
                                        names=['UCD']))
                            else:
                                ocndata = ocndata.append(
                                    concat(
                                        [concat(
                                            [oBD.xs(i, level=1).droplevel(
                                                [0])],
                                            keys=[i],
                                            names=['SENSOR'])],
                                        keys=[name],
                                        names=['UCD']))
    try:
        return ocndata
    except Exception:
        return None
