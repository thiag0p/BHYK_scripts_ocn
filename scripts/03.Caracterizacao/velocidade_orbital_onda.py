'''
Encontra velocidade orbital da onda em diversas profundidades
usando o método metodo Newton-Raphson para calculo do número de onda e
aplicando valores na equação geral de dispersão de onda.
'''
from math import tanh, pi, cosh, sin, sinh, cos
import numpy as np

# _____________________________________________________________________________
#                   MODIFICAR AQUI
# _____________________________________________________________________________
# Diretório onde será salvo o resultado
PATH = "XXXXXXXXXXXXXXXXXXXXXXX"
# Altura significativa de onda
ALTSIGN = 2.2

# Período de pico primário da onda
PERIODO = 9.7

# Profundidade local
PROFUND = 1000

# Profundidades de interesse para o calculo da velocidade orbital
Z = [0, -5, -10]

# _____________________________________________________________________________
# -----------------------------------------------------------------------------
# _____________________________________________________________________________

GRAVIDADE = 9.8
ALTMAX = ALTSIGN * 1.8
# Equação para calculo do comprimento da onda em água profunda
L0 = 1.56 * (PERIODO ** 2)
# KO numero de onda em agua profunda x profundidade local
KOH = (2 * pi / L0) * PROFUND
# Omega ao quadrado
OMEGAQ = (2 * pi / PERIODO) ** 2
# numero de iteracoes
INT = 500000
# tolerancia para convergencia
TOL = .0001

# Método Newton - Raphson
# chute inicial x0 = KOH
x = [KOH]
# definindo o primeiro valor de f
f = [(x[0] * tanh(x[0])) - KOH]
# definindo o primeiro valor de fl
fl = [tanh(x[0]) + (x[0] * (1 - (tanh(x[0]))**2))]
# variavel para verificar convergencia
conv = 0

# loop do metodo de Newton-Raphson
for i in np.arange(1, INT + 1):
    x.append(x[i - 1] - (f[i - 1] / fl[i - 1]))
    f.append(x[i] * tanh(x[i]) - KOH)
    fl.append(tanh(x[i]) + (x[i] * (1 - tanh(x[i])**2)))

    # dispersão
    fdireta = GRAVIDADE * x[i] / PROFUND * tanh(x[i])

    # checando a convergencia entre  os dois termos da equacao de dispersao 
    # [ (2pi/T)^2 ]   =   [ gk*tanh(kh) ]
    if abs(OMEGAQ - fdireta) <= TOL: 
        conv = 1
        print(f'Método convergiu em {i-1} interacoes.')
        Lfinal = 2 * pi * PROFUND / x[i]
        break
if conv == 0:
    print('Método nao convergiu')

# _____________________________________________________________________________
#       Calculando velocidades e acelerações
# _____________________________________________________________________________
# NÚMERO DE ONDA FINAL ENCONTRADO PARA A PROFUNDIDADE FORNECIDA
K = 2 * pi / Lfinal
# DISPERSÃO PARA A PROFUNDIDADE FORNECIDA
OMEGA = np.sqrt(GRAVIDADE * K * (tanh(K * PROFUND)))
phi = np.arange(0, 2 * pi + .01, pi / 2)

P1 = (ALTSIGN / 2) * GRAVIDADE * K
P3 = cosh(K * PROFUND)
arqtxt = open(f'{PATH}\\velocidade_orbital.txt', 'w')
for dep in Z:
    u, w, ax, az = [], [], [], []
    P2 = cosh(K * (PROFUND + dep))
    P5 = sinh(K * (PROFUND + dep))

    for jj in range(5):
        P4 = sin(phi[jj])
        P6 = cos(phi[jj])

        u.append(((P1 / OMEGA) * (P2 / P3)) * P4)
        w.append((((P1 / OMEGA) * (P5 / P3)) * P6) * (-1))
        ax.append(((P1 * (P2 / P3)) * P6) * (-1))
        az.append(((P1 * (P5 / P3)) * P4) * (-1))

    arqtxt.write('Valores de velocidade em m/s\n\n')
    arqtxt.write(f'Prof: {dep} m\n')
    arqtxt.write(f'Pontos: {phi} rad\n')
    arqtxt.write(f'u: {u}\n')
    arqtxt.write(f'w: {w}\n\n\n')
arqtxt.close()
