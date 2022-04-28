import numpy as np


def calc_wind_10m(COTA, WIND):                           # AL4N
    '''
    Corrige a intensidade do vento medido na cota de instalação do sensor
    (COTA) para a altura de 10m

    * Atributos __________________________________________________________
        COTA    |   int ou float 
        WIND    |   list ou tuple
    '''
    WND10m = np.asarray(WIND) / (1 + 0.137 *
                                 np.log(np.asarray(COTA) / 10.))

    return WND10m
