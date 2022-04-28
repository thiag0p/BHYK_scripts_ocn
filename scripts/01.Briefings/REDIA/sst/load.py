import xarray


def sst_seBR(date):
    '''
    Carrega dados de TSM do MUR na região sudeste do Brasil

    :param date:     data de interesse    (str - d/m/y)

    :return df:     DataFrame
    '''

    opendap = xarray.open_dataset('{}{}'.format(
        'http://XXXXXXX'))

    try:
        xy_sel = opendap.sel(
            latitude=slice(-30, -18),
            longitude=slice(-50, -38))
        tp_sel = xy_sel.sel(
            time=date,
            method='nearest')

        TSM = tp_sel.sw_temp_srfc
    except Exception:
        print("+++ SEM DADOS DE TSM NO OPENDAP +++")
        TSM = None
    return TSM
