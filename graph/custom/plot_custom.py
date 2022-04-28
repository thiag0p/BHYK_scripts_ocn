#!/usr/bin/env python

'''
    Biblioteca de funções de configuração de imagens

    Autores: Francisco Thiago Franca Parente (BHYK)

    * Obs.: Qualquer dúvida entrar em contato com o(s) autor(es) das funções, indicados
    ao lado de cada uma delas.

'''

import matplotlib.pyplot as plt
import numpy as np


def temp_serie_config():

    plt.rcParams['legend.fancybox'] = True
    plt.rcParams['legend.fontsize'] = 'x-small'
    plt.rcParams['lines.markersize'] = 4
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['grid.linestyle'] = '-'
    plt.rcParams['grid.color'] = [.7, .7, .7, .3]
