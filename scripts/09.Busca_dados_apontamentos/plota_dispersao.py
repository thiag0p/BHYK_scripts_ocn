from pandas import read_excel
import matplotlib.pyplot as plt
# _____________________________________________________________________________
#                           MODIFICAR AQUI
# _____________________________________________________________________________

# Diretório onde estão dos dados
PATH = 'XXXXXXXXXXXXX'
# Tabela com os dados (colocar a extensão do arquivo)
FILE = 'ATIVIDADES_REALIZADAS_RV_preenchida.xlsx'
# Nome da coluna onde estão os primeiros dados de interesse
COL1 = 'INT_VENTO (m/s)'
# Nome da coluna onde estão os segundos dados de interesse
COL2 = 'HS_ONDA (m)'
# Trata-se da tabela de atividades do ciem2? Se sim, coloque True, se não False
CIEM2 = True

# _____________________________________________________________________________
#                           LENDOO DADOS
# _____________________________________________________________________________

table = read_excel(f'{PATH}\\{FILE}')

# _____________________________________________________________________________
#                           PLOTANDO
# _____________________________________________________________________________
fig, ax = plt.subplots(figsize=(10, 8))
size = 20
if not CIEM2:
    datap = table[[COL1, COL2]]
    # Plotando
    datap.plot.scatter(COL1, COL2, size, ax=ax)
else:
    # convertendo para nós os dados de intensidade do vento
    table['INT_VENTO (m/s)'] = table['INT_VENTO (m/s)'] * 1.94384449
    table = table.rename(columns={'INT_VENTO (m/s)': 'INT_VENTO (nós)'})
    COL1 = 'INT_VENTO (nós)'
    # Pegando apontamentos operacionais
    op1 = table[table['Tipo Atividade'] == 'OPERAÇÃO DE FUNDO'][[COL1, COL2]]
    op2 = table[table['Tipo Atividade'] == 'OPERAÇÃO DE SUPERFÍCIE'][
        [COL1, COL2]]
    # Pegando apontamentos não operacionais
    nop = table[
        table['Tipo Atividade'] == 'AGUARDANDO CONDIÇÕES METEOCEANOGRÁFICAS'][
            [COL1, COL2]]
    # percentual de cada parte
    divisor = table[~table[[COL1, COL2]].isnull().any(axis=1)].count()[0]
    pop1 = (op1[~op1.isnull().any(axis=1)].count()[0] / divisor) * 100
    pop2 = (op2[~op2.isnull().any(axis=1)].count()[0] / divisor) * 100
    pnop = (nop[~nop.isnull().any(axis=1)].count()[0] / divisor) * 100
    # Plotando
    fig, ax = plt.subplots(1, 2, figsize=(10, 8))
    op1.plot.scatter(
        COL1, COL2, size, ax=ax[0], color='b', alpha=.4,
        label='OPERAÇÃO DE FUNDO - {:.1f} %'.format(pop1))
    op2.plot.scatter(
        COL1, COL2, size, ax=ax[1], color='g', alpha=.4,
        label='OPERAÇÃO DE SUPERFÍCIE - {:.1f} %'.format(pop2))
    nop.plot.scatter(
        COL1, COL2, size, ax=ax[0], color='r', alpha=.4,
        label='ACM - {:.1f} %'.format(pnop))
    nop.plot.scatter(
        COL1, COL2, size, ax=ax[1], color='r', alpha=.4,
        label='ACM - {:.1f} %'.format(pnop))
    ax[0].grid('on')
    ax[1].grid('on')

fig.savefig(
    f'{PATH}\\scatter_plot.png',
    format='png',
    bbox_inches='tight',
    dpi=600)
