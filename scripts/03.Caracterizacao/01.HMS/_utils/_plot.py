from matplotlib.dates import DateFormatter
from matplotlib.ticker import AutoMinorLocator
import matplotlib.pyplot as plt
from ocnpylib import name_byid_local, id_local_byname
from numpy import diff

from sys import path
path.append('M:\\Rotinas\\python\\graph')
from custom import caxes
from numpy import asarray


def timexfmt(ax):
    '''
    Função de formatação do eixo x do gráfico de série temporal

    :param ax: axis from matplotlib.pyploy.subplots

    '''
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    dt_fmt = '%d/%m\n%H:%M:%S' if diff(
        ax.xaxis.get_data_interval()) < 1 else '%d/%m/%y\n%H:%M'
    ax.xaxis.set_major_formatter(DateFormatter(dt_fmt))
    [l.set_rotation(45) for l in ax.xaxis.get_majorticklabels()]


def plot_hms_young_raw(
    HMSDATA, rmdata, mdata, INTCOTA, INTCOTA2MIN,
    INTRMCOTA10MIN, INTMCOTA10MIN, DIR,
    cota, xaxin, xaxfn, UCDNAME, PATH):

    '''
    Plota dados brutos do young
    '''

    fig, ax = plt.subplots(2, 1, figsize=(15, 12))
    HMSDATA[INTCOTA].rename('Instantânea').plot(
        ax=ax[0],
        x_compat=True,
        color='gray',
        alpha=.3)
    HMSDATA[INTCOTA2MIN].rename('2min').plot(
        ax=ax[0],
        x_compat=True)
    rmdata[INTRMCOTA10MIN].rename('Média móvel 10 min').plot(
        linewidth=.5,
        marker='o',
        markersize=1,
        color='#334fff',
        ax=ax[0])
    mdata[INTMCOTA10MIN].rename('Média 10 min').plot(
        linewidth=2,
        marker='o',
        markersize=1,
        color='#ff4f33',
        ax=ax[0])

    HMSDATA[DIR].rename('Instantânea').plot(
        ax=ax[1],
        x_compat=True,
        color='gray',
        alpha=.3)
    HMSDATA['Direcao 2min (deg m)'].rename('2min').plot(
        ax=ax[1],
        x_compat=True)
    rmdata['Direcao media movel (10 min)'].rename(
        'Média móvel (10 min)').plot(
            linewidth=.5,
            marker='o',
            markersize=1,
            color='#334fff',
            ax=ax[1])
    mdata['Direcao media (10 min)'].rename('Média 10 min').plot(
        linewidth=2,
        marker='o',
        markersize=1,
        color='#ff4f33',
        ax=ax[1])

    ax[0].set_ylabel('Intensidade à {} m (nós)'.format(cota), fontsize=16)
    timexfmt(ax[0])
    ax[0].set_xlim([xaxin, xaxfn])
    ax[0].tick_params(axis='both', which='major', labelsize=12)

    ax[0].grid('on')
    ax[0].legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
                ncol=2, mode="expand", borderaxespad=0., fontsize=14)

    ax[1].set_ylabel('Direção mag. (°)', fontsize=16)
    timexfmt(ax[1])
    ax[1].set_xlim([xaxin, xaxfn])
    ax[1].tick_params(axis='both', which='major', labelsize=12)
    ax[1].grid('on')
    ax[1].legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
                ncol=2, mode="expand", borderaxespad=0., fontsize=14)
    caxes.direction_yaxis(ax[1])

    fig.suptitle(name_byid_local(id_local_byname(UCDNAME))[0], fontsize=20)
    plt.subplots_adjust(wspace=None, hspace=.6)

    fig.savefig('{}\\{}_tela_radio_operador_HMS.png'.format(PATH, 'Vento'),
                format='png',
                bbox_inches='tight',
                dpi=600)


def plot_hms_young_10m(
    HMSDATA, rmdata, mdata, INT10M, INT10M2MIN,
    INTRM10M10MIN, INTM10M10MIN, DIR, RMDIR, MDIR,
    cota, decm, xaxin, xaxfn, UCDNAME, PATH):
    '''
    Plotando dados de young convertidos à 10m de altitude e com direção
    verdadeira
    '''

    fig, ax = plt.subplots(2, 1, figsize=(15, 12))

    HMSDATA[INT10M].rename('Instantânea').plot(
        ax=ax[0],
        x_compat=True,
        color='gray',
        alpha=.3)
    HMSDATA[INT10M2MIN].rename('2min').plot(
        ax=ax[0],
        x_compat=True)

    rmdata[INTRM10M10MIN].rename('Média móvel (10 min)').plot(
        linewidth=.5,
        marker='o',
        markersize=1,
        color='#334fff',
        ax=ax[0])
    mdata[INTM10M10MIN].rename('Média 10 min').plot(
        linewidth=2,
        marker='o',
        markersize=1,
        color='#ff4f33',
        ax=ax[0])
    HMSDATA[DIR].apply(lambda x: (x + decm) % 360).rename('Instantânea').plot(
        ax=ax[1],
        x_compat=True,
        color='gray',
        alpha=.3)
    HMSDATA['Direcao 2min (deg m)'].apply(lambda x: (x + decm) % 360).rename(
        '2min').plot(
            ax=ax[1],
            x_compat=True)
    RMDIR['Direcao media movel (10 min)'].rename('Média móvel (10 min)').plot(
        linewidth=.5,
        marker='o',
        markersize=1,
        color='#334fff',
        ax=ax[1])
    MDIR.rename('Média de 10 min').plot(
        linewidth=2,
        marker='o',
        markersize=1,
        color='#ff4f33',
        ax=ax[1])

    ax[0].set_ylabel('Intensidade à 10 m (nós)', fontsize=16)
    timexfmt(ax[0])
    ax[0].set_xlim([xaxin, xaxfn])
    ax[0].tick_params(axis='both', which='major', labelsize=12)

    ax[0].grid('on')
    ax[0].legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
                ncol=2, mode="expand", borderaxespad=0., fontsize=14)
    ax[1].set_ylabel('Direção (°)', fontsize=16)
    timexfmt(ax[1])
    ax[1].set_xlim([xaxin, xaxfn])
    ax[1].tick_params(axis='both', which='major', labelsize=12)
    ax[1].grid('on')
    ax[1].legend(
        bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
        ncol=2, mode="expand", borderaxespad=0., fontsize=14)
    caxes.direction_yaxis(ax[1])

    fig.suptitle(name_byid_local(id_local_byname(UCDNAME))[0], fontsize=20)
    plt.subplots_adjust(wspace=None, hspace=.6)

    fig.savefig('{}\\{}_padrao_ocn_HMS.png'.format(PATH, 'Vento'),
                format='png',
                bbox_inches='tight',
                dpi=600)


def plot_hms_scalar(HMSDATA, xaxin, xaxfn, UCDNAME, PATH):
    '''
    Plota parametros escalares do young

    '''
    fig, ax = plt.subplots(3, 1, figsize=(15, 12))
    HMSDATA['Temperatura 2min (oc)'].plot(ax=ax[0], x_compat=True)
    HMSDATA['P.Orvalho 2min (oc)'].plot(ax=ax[1], x_compat=True)
    HMSDATA['Umidade 2min (%r)'].plot(ax=ax[2], x_compat=True)

    ax[0].set_ylabel('Temperatura 2min (oc)', fontsize=16)
    ax[1].set_ylabel('P.Orvalho 2min (oc)', fontsize=16)
    ax[2].set_ylabel('Umidade 2min (%r)', fontsize=16)

    for sbp in range(3):
        ax[sbp].grid('on')
        timexfmt(ax[sbp])
        ax[sbp].set_xlim([xaxin, xaxfn])

        ax[sbp].tick_params(axis='both', which='major', labelsize=12)

    ax[0].set_title(name_byid_local(id_local_byname(UCDNAME))[0], fontsize=20)
    plt.subplots_adjust(wspace=None, hspace=.4)

    fig.savefig('{}\\{}_HMS.png'.format(PATH, 'Escalares'),
                format='png',
                bbox_inches='tight',
                dpi=600)


def plot_hms_atitude(HMSDATA, xaxin, xaxfn, UCDNAME, PATH, PARAMS):
    
    limites_pouso = {
        'Pitch inst. (deg)': ['C.Aeronave pesada=0 (média=1)', 3, 4],
        'Roll inst. (deg)': ['C.Aeronave pesada=0 (média=1)', 3, 4],
        'Incl inst. (deg)': ['C.Aeronave pesada=0 (média=1)', -3.5, -4.5],
        'Heave inst. (m)': ['Dia/Noite dia=0 (noite=1)', 5, 4],
        'Heave Vel.M. 20min (m/s)': ['Dia/Noite dia=0 (noite=1)', -1.3, -1]}

    sufix = ['Pou', 'Pit', 'Rol', 'Inc', 'Hea']
    atitu = [x for x in PARAMS if x[:3] in sufix]

    HMSatitu = HMSDATA[atitu].copy()

    # Retirando falha de cota para o heave
    # HMSatitu['Heave inst. (m)'] = HMSatitu[
    #     'Heave inst. (m)'] - HMSatitu['Heave inst. (m)'].mean()

    select_plot = [
        'Pitch inst. (deg)', 'Roll inst. (deg)', 'Incl inst. (deg)',
        'Heave inst. (m)', 'Heave Vel.M. 20min (m/s)']

    fig, ax = plt.subplots(len(select_plot), 1, figsize=(15, 12))

    for sbp, cl in enumerate(select_plot):

        HMSatitu[cl].plot(ax=ax[sbp], x_compat=True)

        if cl == 'Pitch inst. (deg)':
            HMSDATA['Pitch D.M. 20min (deg)'].plot(
                ax=ax[sbp],
                color='k',
                linewidth=1.5,
                alpha=.4,
                x_compat=True)
            HMSDATA['Pitch U.M. 20min (deg)'].plot(
                ax=ax[sbp],
                color='k',
                linewidth=1.5,
                alpha=.4,
                x_compat=True)

        if cl == 'Roll inst. (deg)':
            HMSDATA['Roll P.M. 20min (deg)'].plot(
                ax=ax[sbp],
                color='k',
                linewidth=1.5,
                alpha=.4,
                x_compat=True)

            HMSDATA['Roll S.M. 20min (deg)'].plot(
                ax=ax[sbp],
                color='k',
                linewidth=1.5,
                alpha=.4,
                x_compat=True)

        # Plotando limites de pouso para informações de atitude
        if cl in limites_pouso.keys():
            kw = {'facecolor': 'green', 'alpha': 0.2}
            prm, limit1, limit2 = limites_pouso[cl]
            val = asarray(
                [limit2 if x == 1 else limit1 for x in HMSDATA[prm].values])
            ax[sbp].fill_between(
                HMSatitu.index,
                -(abs(val) + val) / 2,
                abs(val), **kw)

        ax[sbp].grid('on')
        if sbp == len(select_plot) - 1:
            timexfmt(ax[sbp])
        else:
            ax[sbp].set_xticklabels([])

        if sbp != len(select_plot) - 1:
            ax[sbp].set_xticklabels([])

        ax[sbp].set_xlim([xaxin, xaxfn])

        ax[sbp].tick_params(axis='both', which='major', labelsize=12)
        if cl == 'Heave Vel.M. 20min (m/s)':
            ax[sbp].set_ylabel('Heave Vel.M.\n20min (m/s)', fontsize=12)
        else:
            ax[sbp].set_ylabel(cl, fontsize=12)

    ax[0].set_title(name_byid_local(id_local_byname(UCDNAME))[0], fontsize=20)

    fig.savefig('{}\\{}_HMS.png'.format(PATH, 'Atitude'),
                format='png',
                bbox_inches='tight',
                dpi=600)


def plot_epta_young_raw(
    EPTADATA, INT, INT2MIN,
    DIR, xaxin, xaxfn, UCDNAME, PATH):

    # Plotando dados dispostos na tela do radio operador.
    fig, ax = plt.subplots(2, 1, figsize=(15, 12))
    EPTADATA[INT].rename('Instantânea').plot(
        ax=ax[0],
        x_compat=True,
        color='gray',
        alpha=.3)
    EPTADATA[INT2MIN].rename('2min').plot(
        ax=ax[0],
        x_compat=True)

    EPTADATA[DIR].rename('Instantânea').plot(
        ax=ax[1],
        x_compat=True,
        color='gray',
        alpha=.3)
    EPTADATA['Direção 2min (deg m)'].rename('2min').plot(
        ax=ax[1],
        x_compat=True)

    ax[0].set_ylabel('Intensidade (nós)', fontsize=16)
    timexfmt(ax[0])
    ax[0].set_xlim([xaxin, xaxfn])
    ax[0].tick_params(axis='both', which='major', labelsize=12)

    ax[0].grid('on')
    ax[0].legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
                ncol=2, mode="expand", borderaxespad=0., fontsize=14)

    ax[1].set_ylabel('Direção mag. (°)', fontsize=16)
    timexfmt(ax[1])
    ax[1].set_xlim([xaxin, xaxfn])
    ax[1].tick_params(axis='both', which='major', labelsize=12)
    ax[1].grid('on')
    ax[1].legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
                ncol=2, mode="expand", borderaxespad=0., fontsize=14)
    caxes.direction_yaxis(ax[1])

    fig.suptitle(name_byid_local(id_local_byname(UCDNAME))[0], fontsize=20)
    plt.subplots_adjust(wspace=None, hspace=.6)

    fig.savefig(f'{PATH}\\Vento_EPTA.png',
                format='png',
                bbox_inches='tight',
                dpi=600)


def plot_epta_scalar(EPTADATA, xaxin, xaxfn, UCDNAME, PATH):

    fig, ax = plt.subplots(3, 1, figsize=(15, 12))
    EPTADATA['Temperatura 2min (oc)'].plot(ax=ax[0], x_compat=True)
    EPTADATA['P.Orvalho 2min (oc)'].plot(ax=ax[1], x_compat=True)
    EPTADATA['Umidade 2min (%r)'].plot(ax=ax[2], x_compat=True)

    ax[0].set_ylabel('Temperatura 2min (oc)', fontsize=16)
    ax[1].set_ylabel('P.Orvalho 2min (oc)', fontsize=16)
    ax[2].set_ylabel('Umidade 2min (%r)', fontsize=16)

    for sbp in range(3):
        ax[sbp].grid('on')
        timexfmt(ax[sbp])
        ax[sbp].set_xlim([xaxin, xaxfn])

        ax[sbp].tick_params(axis='both', which='major', labelsize=12)

    ax[0].set_title(name_byid_local(id_local_byname(UCDNAME))[0], fontsize=20)
    plt.subplots_adjust(wspace=None, hspace=.4)

    fig.savefig('{}\\{}_EPTA.png'.format(PATH, 'Escalares'),
                format='png',
                bbox_inches='tight',
                dpi=600)
