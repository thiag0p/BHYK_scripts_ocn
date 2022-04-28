from matplotlib.dates import DateFormatter
from matplotlib.dates import HourLocator, DayLocator, MonthLocator, YearLocator
import numpy as np


def direction_yaxis(axes):

    '''
        Plota background com sessões para cada direção
    '''

    yticks = np.linspace(0., 360., 9)
    dirlbl = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO', 'N']

    for y, d in zip(yticks, dirlbl):
        axes.text(
            1.01,
            y / 360,
            d,
            fontsize=8,
            ha="left",
            va='center',
            transform=axes.transAxes)

    for y in yticks[1:-1:2]:
        axes.axhspan(
            y - 22.5, y + 22.5,
            facecolor=[.9, .9, .9],
            ec='None', zorder=-1)


def fmt_time_axis(axes):

    axes.fmt_xdata = DateFormatter('%d/%m/%y %H:%M')
    x_lim = axes.get_xlim()
    time_diff = abs(x_lim[0] - x_lim[-1])

    # Escala temporal: ]0, 5[ dias.
    if time_diff < 2:
        axes.xaxis.set_major_locator(DayLocator())
        axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
        axes.xaxis.set_minor_locator(HourLocator(byhour=np.arange(0, 24)))
        axes.xaxis.set_minor_formatter(DateFormatter('%H:%M'))

    # Escala temporal: ]0, 5[ dias.
    elif 2 <= (time_diff) < 5:
        axes.xaxis.set_major_locator(DayLocator())
        axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
        axes.xaxis.set_minor_locator(HourLocator(byhour=(3, 6, 9, 12, 15,
                                                         18, 21)))
        axes.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
    # Escala temporal: [5, 11[ dias.
    elif 5 <= (time_diff) < 11:
        axes.xaxis.set_major_locator(DayLocator())
        axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
        axes.xaxis.set_minor_locator(HourLocator(byhour=(6, 12, 18)))
        axes.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
    # Escala temporal: [11, 45[ dias.
    elif 11 <= (time_diff) < 45:
        axes.xaxis.set_major_locator(DayLocator())
        axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
        axes.xaxis.set_minor_locator(HourLocator(byhour=(12)))
        axes.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
    # Escala temporal: [45, 183[ dias.
    elif 45 <= (time_diff) < 183:
        axes.xaxis.set_major_locator(MonthLocator())
        axes.xaxis.set_major_formatter(DateFormatter('%m/%y'))
        axes.xaxis.set_minor_locator(DayLocator(bymonthday=(5, 10, 15, 20,
                                                            25)))
        axes.xaxis.set_minor_formatter(DateFormatter('%d'))
    # Escala temporal: [183, 365[ dias.
    elif 183 <= (time_diff) < 365:
        axes.xaxis.set_major_locator(MonthLocator())
        axes.xaxis.set_major_formatter(DateFormatter('%m/%Y'))
        axes.xaxis.set_minor_locator(DayLocator())
        axes.xaxis.set_minor_formatter(DateFormatter(''))
    # Escala temporal: >= 365 dias.
    else:
        axes.xaxis.set_major_locator(YearLocator())
        axes.xaxis.set_major_formatter(DateFormatter('%Y'))
        axes.xaxis.set_minor_locator(MonthLocator())
        axes.xaxis.set_minor_formatter(DateFormatter('%m'))
    for label in axes.xaxis.get_majorticklabels():
        label.set_fontsize(9)
        label.set_ha('right')
        label.set_rotation(45)
    for label in axes.xaxis.get_minorticklabels():
        label.set_fontsize(8)
        label.set_ha('right')
        label.set_rotation(45)
