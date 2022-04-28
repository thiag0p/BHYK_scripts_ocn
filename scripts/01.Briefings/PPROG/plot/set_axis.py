import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator
import locale
locale.setlocale(locale.LC_TIME, '')


def plot_days_hours(ax):
    '''
        Plota dias e horas acima do gráfico

        :param ax: axis do plot from matplotlib.pyplot
    '''
    ax2 = ax.twiny()
    # HORAS
    ax.xaxis.set_major_locator(HourLocator(byhour=(0)))
    ax.xaxis.set_major_formatter(DateFormatter('%H'))
    ax.xaxis.set_minor_locator(HourLocator(byhour=(12)))
    ax.xaxis.set_minor_formatter(DateFormatter('%H'))

    # DIAS
    ax2.set_xlim(ax.get_xlim())
    ax2.xaxis.set_major_locator(HourLocator(byhour=(12)))
    ax2.xaxis.set_major_formatter(DateFormatter('%a %d/%m'))

    # GRID LINES
    ax.grid(which='major', axis='x', linewidth=1.5, alpha=.4)
    ax.grid(which='both', axis='y', linewidth=.2, alpha=.2)


def plot_vetores(xticks, centro, u, v, clr):
    '''
        Plota vetores abaixo do eixo do tempo

        :param xticks: xticks onde serão dispostos vetores
        :param centro: ponto central dos vetores (list)
        :param u: valor da componente zonal de velocidade (array)
        :param v: valor da componente meridional de velocidade (array)
        :param clr: cor do vetor
    '''
    plt.subplots_adjust(bottom=0.12, top=0.8)
    axv = plt.axes([0.092, 0.02, .848, 0.06], frameon=False)
    axv.quiver(
        xticks, centro, u, v,
        width=.0025, scale=58, headwidth=3.8,
        pivot="middle", headlength=4.5, color=clr)
    plt.xticks([])
    plt.yticks([])
