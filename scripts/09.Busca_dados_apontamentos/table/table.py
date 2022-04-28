from sys import path as Path
Path.append(
    'XXXXXXXXXXXXXXXXXX')
from custom import caxes
import matplotlib.pyplot as plt
from pandas import DataFrame, read_excel, ExcelWriter, to_datetime
from datetime import timedelta, datetime
from datetime import time as timeinstance
import numpy as np


def check_dates(table, col_di, col_hi=None, col_df=None, col_hf=None):
    '''
    check da formatação da data para informação de conflito

    :param table: tabela com os apontamentos        (DataFrame)
    :param col_di: nome da coluna da Data Inicial   (str)
    :param col_hi: nome da coluna da Hora Inicial   (str)
    :param col_df: nome da coluna da Data Final     (str)
    :param col_hf: nome da coluna da Hora final     (str)
    '''
    edit_table = table.copy()

    try:
        dates = table[col_di].values
    except Exception as erro:
        print(erro)
    fmt = np.datetime64
    if not(col_hi):
        UTCtime = []
        for time in dates:
            if isinstance(time, fmt):
                UTCtime.append(to_datetime(time) + timedelta(hours=3))
    else:
        hours = edit_table[col_hi].values
        UTCtime = []
        for d, h in zip(dates, hours):
            if isinstance(d, fmt) and isinstance(h, timeinstance):
                UTCtime.append(to_datetime(d) + timedelta(
                    hours=h.hour + 3,
                    minutes=h.minute))
            if isinstance(d, fmt) and not(isinstance(h, timeinstance)):
                try:
                    hou, min, seg = h.split(':')
                    htime = timeinstance(int(hou), int(min), int(seg))
                except Exception:
                    try:
                        h, min = h.split(':')
                        htime = timeinstance(int(hou), int(min), 0)
                    except Exception:
                        try:
                            htime = timeinstance(int(h), 0, 0)
                        except Exception as erro:
                            print(erro)
                UTCtime.append(to_datetime(d) + timedelta(
                    hours=htime.hour + 3,
                    minutes=htime.minute))
    edit_table['DataInical UTC'] = UTCtime

    if col_df:
        final_times = edit_table[col_df].values
        if not(col_hf):
            UTCtime = []
            for time in final_times:
                if isinstance(time, fmt):
                    UTCtime.append(to_datetime(time) + timedelta(hours=3))
        else:
            hours = edit_table[col_hf].values
            UTCtime = []
            for d, h in zip(final_times, hours):
                if isinstance(d, fmt) and isinstance(h, timeinstance):
                    UTCtime.append(to_datetime(d) + timedelta(
                        hours=h.hour + 3,
                        minutes=h.minute))
                if isinstance(d, fmt) and not(isinstance(h, timeinstance)):
                    try:
                        hou, min, seg = h.split(':')
                        htime = timeinstance(int(hou), int(min), int(seg))
                    except Exception:
                        try:
                            h, min = h.split(':')
                            htime = timeinstance(int(hou), int(min), 0)
                        except Exception:
                            try:
                                htime = timeinstance(int(h), 0, 0)
                            except Exception as erro:
                                print(erro)
                    UTCtime.append(to_datetime(d) + timedelta(
                        hours=htime.hour + 3,
                        minutes=htime.minute))
        edit_table['DataFinal UTC'] = UTCtime
    else:
        edit_table['DataFinal UTC'] = edit_table['DataInical UTC']
    return edit_table


def ajusta_ciem2_table(table, all_lines=True):
    '''
    Ajusta tabela de atividades realizadas retirada do ciem2, com objetivo de
    criar coluna de data inicial e final em UTC e retirar as linhas que o
    usuário não tenha interesse.

    :param table:   DataFrame com as informações lidas da tabela de atividades
    :param all_lines:   bool    (   True - não retira nenhuma linha da tabela
                                    False - retira as linhas não operacionais)
    '''
    output = table.copy()
    dti = [datetime.strptime(x, '%d/%m/%Y %H:%M') for x in output['Início']]
    output['DataInical UTC'] = [x + timedelta(hours=3) for x in dti]
    dtf = [datetime.strptime(x, '%d/%m/%Y %H:%M') for x in output['Término']]
    output['DataFinal UTC'] = [x + timedelta(hours=3) for x in dtf]
    if not all_lines:
        output = output[output['Duração'] != '0:00']
        droplines = output[output['Tipo Atividade'].str.contains(
            '{}{}'.format(
                'ABASTECENDO|AGUARDANDO|ALMOÇO|EMBARQUE|DESEMBARQUE|',
                'NAVEGAÇÃO|REPOUSO|TROCA DE TURMA'))].copy()
        str_aguardando = 'AGUARDANDO CONDIÇÕES METEOCEANOGRÁFICAS'
        droplines = droplines[droplines['Tipo Atividade'] != str_aguardando]
        output = output.drop(droplines.index, axis=0)
    return output


def ajusta_output_com_dados_ciem2(table):
    '''
        Função criada para ajustar a tabela de atividades realizadas do
        ciem2 com os dados do OCEANOP para mesclar tabelas de parametros
        diferentes.

        :param table:   MultiIndex

        return MultiIndex
    '''
    try:
        table = table.droplevel(None)
    except Exception:
        pass
    new_table = table.copy()
    lixo = []
    for x in new_table.index.names:
        try:
            if 'Unnamed' in x or 'None' in x:
                lixo.append(x)
        except Exception:
            continue
    lixo.extend(['Escala', 'Agrupador', 'Status Serviço'])
    new_table = new_table.droplevel(lixo)

    # ordenando colunas da melhor forma
    new_table = new_table.reorder_levels([
        'id', 'Ref. Medição', 'UO', 'Conclusão da OS',
        'Relatório de Serviço', 'Tipo Localização', 'Campo',
        'Serviço Paralelo\n', 'Atividade Paralela', 'Descrição Demanda',
        'Duração Programada', 'Duração Planejada', 'Observação',
        'Operacionalidade', 'Conf. Custo', 'Eficiência Nível 2',
        'Eficiência Nível 1', 'Tipo Atividade', 'Cód. Atividade',
        'Descrição Serviço', 'Recurso', 'Tipo Recurso', 'Gerência',
        'Classe Serviço', 'Classe Demanda', 'Entrega', 'Classe Entrega',
        'Grupo Técnico', 'Nr Serviço', 'Localização', 'Merid. Central',
        'Coord. Leste', 'Coord. Norte' , 'Duração', 'Início',
        'Término', 'DT_DATA'])

    return new_table


def include_column_Fidelis(table):
    new_table = table.copy()
    new_table['Duracao/Namostral (s)'] = np.nan
    for idx in set(new_table.index.get_level_values(0)):
        slc = new_table.loc[idx]

        # Dividindo a duração total pelo número de de registros
        duracao_horas = int(list(set(
            slc.index.get_level_values('Duração')))[0].split(':')[0])

        duracao_minutos = int(list(set(
            slc.index.get_level_values('Duração')))[0].split(':')[1])
        total_seconds = ((duracao_horas * 3600) + (duracao_minutos * 60))

        # Adicionando à tabela
        new_table.loc[
            idx, 'Duracao/Namostral (s)'] = total_seconds / slc.shape[0]
    return new_table


def plot_recursos_ciem2(wdtb, wvtb, crtb, path):
    plt.ioff()
    for recurso in set(wdtb.index.get_level_values('Recurso')):
        # Plota vento
        wdplot = wdtb.xs(recurso, level='Recurso')
        wdplot.index = wdplot.index.get_level_values('DT_DATA')
        wdplot = wdplot.sort_index() 
        fig, ax = plt.subplots(2, 1, figsize = (15, 10))
        wdplot['INT_VENTO (m/s)'].plot(ax=ax[0], marker='o')
        ax[0].set_ylabel('Intensidade do vento (m/s)')
        wdplot['DIR_VENTO (°)'].plot(ax=ax[1], marker='o')
        caxes.direction_yaxis(ax[1])
        ax[1].set_ylabel('Direção do vento (°)')
        plt.subplots_adjust(hspace=.35)
        plt.suptitle(recurso)
        fig.savefig(f'{path}\\{recurso}_vento.png',
                    format='png',
                    bbox_inches='tight',
                    dpi=600)

        # Plota corrente
        crplot = crtb.xs(recurso, level='Recurso')
        crplot.index = crplot.index.get_level_values('DT_DATA')
        crplot = crplot.sort_index() 
        fig, ax = plt.subplots(2, 1, figsize = (15, 10))
        crplot['INT_COR (m/s)'].plot(ax=ax[0], marker='o')
        ax[0].set_ylabel('Intensidade da corrente (m/s)')
        crplot['DIR_COR (°)'].plot(ax=ax[1], marker='o')
        caxes.direction_yaxis(ax[1])
        ax[1].set_ylabel('Direção da corrente (°)')
        plt.subplots_adjust(hspace=.35)
        plt.suptitle(recurso)
        fig.savefig(f'{path}\\{recurso}_corrente.png',
                    format='png',
                    bbox_inches='tight',
                    dpi=600)

        # Plota onda
        wvplot = wvtb.xs(recurso, level='Recurso')
        wvplot.index = wvplot.index.get_level_values('DT_DATA')
        wvplot = wvplot.sort_index() 
        fig, ax = plt.subplots(3, 1, figsize = (15, 10))
        wvplot['HS_ONDA (m)'].plot(
            ax=ax[0],
            marker='o',
            markersize=3,
            linewidth=0)
        wvplot[wvplot['HS_ONDA (m)'] >= 2.5]['HS_ONDA (m)'] .plot(
            ax=ax[0],
            marker='o',
            color='r',
            linewidth=0,
            markersize=3)
        wvplot['HS_ONDA (m)'].plot(color='b', ax=ax[0], alpha=.3)
        ax[0].set_ylabel('Altura significativa de onda (m)', fontsize=8)
        ax[0].grid('on')
        wvplot['DIR_ONDA (°)'].plot(ax=ax[1], marker='o')
        # Calculando registros acima de 2,5 m
        stw = (
            wvplot[wvplot['HS_ONDA (m)'] >= 2.5].count()[0] /
            wvplot.count()[0]) * 100
        nstw = (
            wvplot[wvplot['HS_ONDA (m)'] < 2.5].count()[0] /
            wvplot.count()[0]) * 100 
        ax[0].legend(
            labels=[
                f'Hs < 2,5 m: {round(nstw, 1)}%',
                f'Hs \u2265 2,5 m: {round(stw, 1)}%'],
            fontsize=11,
            loc='upper right',
            bbox_to_anchor=(0.4, 1.3),
            ncol=2)
        ax[1].set_ylabel('Direção preferencial (°)', fontsize=8)
        ax[1].grid('on')
        caxes.direction_yaxis(ax[1])
        wvplot['PER. ONDA (s)'].plot(ax=ax[2])
        ax[2].set_ylabel('Período de pico primário (°)', fontsize=8)
        ax[2].grid('on')
        plt.subplots_adjust(hspace=.6)
        plt.suptitle(recurso)

        fig.savefig(f'{path}\\{recurso}_onda.png',
                    format='png',
                    bbox_inches='tight',
                    dpi=600)
    plt.close('all')


def ajusta_colunas_oracledb(table):
    '''
    Ajusta colunas da tabela extraída do banco oracle do ciem2 para ficarem
    iguais às colunas da tabela "Atividades Realizadas" exportada no ciem2. E adiciona as colunas de tempo inicial e final em UTC.

    :param table: DataFrame
    '''
    output = table.copy()
    output = output.rename(columns={
        'Coordenada Leste': 'Coord. Leste',
        'Coordenada Norte': 'Coord. Norte',
        'Meridiano Central': 'Merid. Central',
        'Início Tarefa': 'Início',
        'Término Tarefa': 'Término',
        'Unnamed: 0': 'id'})

    dti = [datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in output['Início']]
    output['DataInical UTC'] = [x + timedelta(hours=3) for x in dti]
    dtf = [datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in output['Término']]
    output['DataFinal UTC'] = [x + timedelta(hours=3) for x in dtf]

    return output
