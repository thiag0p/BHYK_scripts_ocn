
'''
    Funções para leitura dos arquivos de alta frequência armazenados pelo log
    do SISMO ou do DADAS.

    Autor: Francisco Thiago Franca Parente
    Chave: BHYK

    Data de criação - 03/09/2020
'''
from pandas import DataFrame, read_csv, to_datetime
from os.path import join


def read_fsi2d_log_SISMO(PATH, ARQ, SEP, DTI=None, DTF=None, DELTA=None):
    '''
        Função de leitura do aquivo de FSI do SISMO.

        * Atributros___________________________________________________________
            PATH    |   Diretório onde estão os CSV que serão lidos
            ARQ     |   Lista de arquicos .csv que serão lidos
            SEP     |   ";"" OU ",", depende do arquivo
            DTI     |   Data e horário que o arquivo foi criado
            DTF     |   Data e horário que o arquivo foi finalizado
            DELTA   |   Intervalo entre medições sucessivas
                    |   ("S" para freq de 1 seg, "2S para frequencia de 2 seg")

        Autor: Francisco Thiago Franca Parente (BHYK)

    '''

    FSICOLMS = {13: [u"Heading", u"VX", u"VY", u"TX", u"TY", u"HX", u"HY",
                     u"HZ", u"VN", u"VE", u"Temperature", u"SV", u"Pressure"],
                14: [u"Heading", u"VX", u"VY", u"VZ", u"TX", u"TY", u"HX",
                     u"HY", u"HZ", u"VN", u"VE", u"Temperature", u"SV",
                     u"Pressure"],
                18: [u"CTDConductivity", u"CTDTemp", u"CTDDepth",
                     u"CTDSalinity", u"CTDSV", u"Heading", u"VX", u"VY", u"TX",
                     u"TY", u"HX", u"HY", u"HZ", u"VN", u"VE", u"Temperature",
                     u"SV", u"Pressure"],
                19: [u"CTDConductivity", u"CTDTemp", u"CTDDepth",
                     u"CTDSalinity", u"CTDSV", u"Heading", u"VX", u"VY", u"VZ",
                     u"TX", u"TY", u"HX", u"HY", u"HZ", u"VN", u"VE",
                     u"Temperature", u"SV", u"Pressure"],
                20: [u"hh:mm:ss", u"mm-dd-yyyy", u"CTDConductivity",
                     u"CTDTemp", u"CTDDepth", u"CTDSalinity", u"CTDSV",
                     u"Heading", u"VX", u"VY", u"TX", u"TY", u"HX", u"HY",
                     u"HZ", u"VN", u"VE", u"Temperature", u"SV", u"Pressure"],
                21: [u"hh:mm:ss", u"mm-dd-yyyy", u"CTDConductivity",
                     u"CTDTemp", u"CTDDepth", u"CTDSalinity", u"CTDSV",
                     u"Heading", u"VX", u"VY", u"VZ", u"TX", u"TY", u"HX",
                     u"HY", u"HZ", u"VN", u"VE", u"Temperature",
                     u"SV", u"Pressure"]}

    df = DataFrame()
    for n, FILE in enumerate(ARQ):
        data = read_csv(join(PATH, FILE),
                        error_bad_lines=False,
                        header=None,
                        prefix='Column',
                        sep=SEP)
        data.columns = FSICOLMS[len(data.columns)]

        # Retirando linhas erradas
        data.drop(data.index[data.SV <= 100000], inplace=True)

        # Convertendo as datas em datetimes
        try:
            data.index = to_datetime(
                '{} {}'.format(
                    data['mm-dd-yyyy'].values,
                    data[u"hh:mm:ss"].values),
                format="%m/%d/%Y %H:%M:%S")
        except:
            dti = dt.datetime.strptime(DTI[n], '%d/%m/%Y %H:%M:%S')
            dtf = dt.datetime.strptime(DTF[n], '%d/%m/%Y %H:%M:%S')
            data.index = date_range(dti, dtf, freq=DELTA)
        df = df.append(data.copy())

    return df


def read_fsi2d_DADAS(PATH, ARQ):                                 # BHYK
    '''
        Função de leitura do aquivo de FSI do DADAS.

        * Atributros___________________________________________________________
            PATH    |   Diretório onde estão os CSV que serão lidos
            ARQ     |   Lista de arquicos .csv que serão lidos

        Autor: Francisco Thiago Franca Parente (BHYK)

    '''
    FSICOLMS = {13: ["Heading", "VX", "VY", "TX", "TY", "HX", "HY",
                     "HZ", "VN", "VE", "Temperature", "SV", "Pressure"],
                14: ["Heading", "VX", "VY", "VZ", "TX", "TY", "HX",
                     "HY", "HZ", "VN", "VE", "Temperature", "SV",
                     "Pressure"],
                18: ["CTDConductivity", "CTDTemp", "CTDDepth",
                     "CTDSalinity", "CTDSV", "Heading", "VX", "VY", "TX",
                     "TY", "HX", "HY", "HZ", "VN", "VE", "Temperature",
                     "SV", "Pressure"],
                19: ["CTDConductivity", "CTDTemp", "CTDDepth",
                     "CTDSalinity", "CTDSV", "Heading", "VX", "VY", "VZ",
                     "TX", "TY", "HX", "HY", "HZ", "VN", "VE",
                     "Temperature", "SV", "Pressure"]}

    df = DataFrame()
    for FILE in ARQ:
        data = read_csv(join(PATH, FILE),
                        error_bad_lines=False,
                        header=None,
                        prefix='Column')
        data.columns = FSICOLMS[len(data.columns)]

        # Retirando linhas erradas
        data.drop(data.index[
            (data.SV <= 130000) & (data.SV >= 160000)], inplace=True)
        data.drop(
            data.index[
                data[data.columns[0]].str.split('-',
                                                expand=True)[0] == '100.000'],
            inplace=True)

        # Convertendo as datas em datetimes
        data.index = to_datetime(
            data[data.columns[0]].str.split('-', expand=True)[0].values,
            format="%Y%m%d %H%M%S")
        data[data.columns[0]] = data[
            data.columns[0]].str.split(':', expand=True)[1]
        df = df.append(data.copy())

    return df
