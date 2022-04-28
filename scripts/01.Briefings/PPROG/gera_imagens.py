PATH = 'M:\\Previsao\\1.Briefings\\PPROG\\imagens'
# _____________________________________________________________________________
#                               MODIFICAR AQUI
# _____________________________________________________________________________
PPROGS = {
    'UNIDADE': {
        'PATH': PATH,
        'UCD': 'UNIDADE',
        'ALTURAS_DE_TRABALHO': [81],
        'ucdwind': ['UNIDADE'],
        'ucdwave': ['UNIDADE'],
        'ucdcurr': ['UNIDADE'],
        'tipo_plot_precipitacao': 1
    },
}

# _____________________________________________________________________________
#                         IMPORTANDO BIBLIOTECAS
# _____________________________________________________________________________

from sys import path
brpath = 'M:\\Rotinas\\python\\scripts\\01.Briefings\\PPROG'
path.append(brpath)
from db import db
from plot import make
from warnings import filterwarnings
filterwarnings('ignore')
# _____________________________________________________________________________
#                         LENDO E PLOTANDO PREVISÃO
# _____________________________________________________________________________

for name, pprog in PPROGS.items():

    print('Elaborando imagens da Previsão:')
    print(f'Lendo {name}')

    forecast = db.get_forecast(pprog['UCD'])

    make.plot_wind(
        forecast=forecast,
        wkheight=pprog['ALTURAS_DE_TRABALHO'],
        PATH='{}\\{}'.format(pprog['PATH'], pprog['UCD']),
        UCD=pprog['UCD'])
    make.plot_wave(
        forecast=forecast,
        PATH='{}\\{}'.format(pprog['PATH'], pprog['UCD']),
        UCD=pprog['UCD'])
    make.plot_rain(
        forecast=forecast,
        PATH='{}\\{}'.format(pprog['PATH'], pprog['UCD']),
        UCD=pprog['UCD'],
        wkheight=pprog['ALTURAS_DE_TRABALHO'][-1],
        tipo=pprog['tipo_plot_precipitacao'])
    make.pcolor_gust(
        forecast=forecast,
        wkheight=pprog['ALTURAS_DE_TRABALHO'],
        PATH='{}\\{}'.format(pprog['PATH'], pprog['UCD']),
        UCD=pprog['UCD'])
print('Previsão ok!')

# _____________________________________________________________________________
#                         LENDO E PLOTANDO DADOS MEDIDOS
# _____________________________________________________________________________
for name, pprog in PPROGS.items():
    print('Elaborando imagens dados medidos 24h:')
    print(f'Lendo {name}')

    data = db.get_data24h(pprog['ucdwind'], pprog['ucdwave'], pprog['ucdcurr'])

    wind, wave, curr = data

    make.plot_data24h(
        wind=wind,
        wave=wave,
        curr=curr,
        wkheight=pprog['ALTURAS_DE_TRABALHO'][-1],
        PATH='{}\\{}'.format(pprog['PATH'], pprog['UCD'])
    )
