"""
Code used for analysis in "The Probability of the May 2024 Solar Superstorm" by Elvidge and Themens 2024
"""

import numpy as np
import pandas as pd
from pyextremes import EVA

########################################################################################################################
def GEV_exceedance_probability(xi, mu, sigma, Z):
    """

    Parameters
    ----------
    xi : shape parameter
    mu : mu/loc/mean parameter
    sigma : sigma/scale/std. dev parameter
    Z : return value

    Returns
    -------
    Return period
    """
    if xi != 0:
        P = 1 - np.exp(-(1 + xi * (Z - mu) / sigma) ** (-1 / xi))
    else:
        P = 1 - np.exp(-np.exp(-(Z - mu) / sigma))

    return 1/P

########################################################################################################################
def GPD_exceedance_probability(xi, sigma, u, n, N, Z):
    """

    Parameters
    ----------
    xi : shape parameter
    sigma : sigma/scale/std. dev parameter
    u : threshold
    n : number of distinct events (declustered peaks)
    N : years of data
    Z : return level

    Returns
    -------
    Return period
    """
    # Calculate exceedance probability for the return level Z
    def xiFunc(xi, sigma, Z, u):
        if xi != 0:
            P = (1 + xi * (Z - u) / sigma) ** (-1 / xi)
        else:
            P = np.exp(-(Z - u) / sigma)
        return P

    # Rate of exceedance
    lambda_exceedance = n / N

    # Calculate return period
    T = 1 / (lambda_exceedance * xiFunc(xi, sigma, Z, u))

    return T


########################################################################################################################
def EVT_GEV_Rtn(index):
    """
    Calculate the EVT GEV Gumbel fits.

    index should be one of: 'rAp', 'ap', 'ap30', 'ap60'

    """
    if index == 'rAp':
        fn = 'spwx_indices.csv'
        # rAp data should be downloaded from: serene.bham.ac.uk/resources/download/spwx_indices.csv
        Z = 301 # peak storm value
    elif index == 'ap':
        fn = 'spwx_indices.csv'
        # ap data should be downloaded from: https://kp.gfz-potsdam.de/en/data
        Z = 400 # peak storm value
    elif index == 'ap30':
        fn = 'ap30_data.csv'
        # ap data should be downloaded from: https://kp.gfz-potsdam.de/en/data
        Z = 534  # peak storm value
    elif index == 'ap60':
        fn = 'ap60_data.csv'
        # ap data should be downloaded from: https://kp.gfz-potsdam.de/en/data
        Z = 456  # peak storm value

    df = pd.read_csv(fn, delimiter=',')

    extreme_value_analysis = EVA(df['rAp_24'])

    # Extract extremes
    extreme_value_analysis.get_extremes(method="BM", block_size="1Y")

    # Fit model
    fit = extreme_value_analysis.fit_model()

    print(GEV_exceedance_probability(0,extreme_value_analysis.distribution.mle_parameters['loc'],
                                 extreme_value_analysis.distribution.mle_parameters['scale'],Z))


########################################################################################################################
def EVT_GPD_Rtn(index):
    """
    Calculate the EVT GPD fits.

    index should be one of: 'SMR_min', 'SMR_hour', 'SYMH_min', 'SYMH_hour', 'Dst'
    """
    if index == 'SMR_min':
        fn = 'SMR_data.csv'
        # SMR data should be downloaded from: https://supermag.jhuapl.edu/indices
        Z = 426.6  # peak storm value
        u = 250 # threshold
        r = '48H' # decluster threshold
        minmax = -1 # multiply the data by -1 (as it is negative index, and work in that space)
    elif index == 'SMR_hour':
        fn = 'SMR_data.csv'
        # SMR data should be downloaded from: https://supermag.jhuapl.edu/indices
        Z = 382.9  # peak storm value
        u = 250  # threshold
        r = '48H'  # decluster threshold
        minmax = -1  # multiply the data by -1 (as it is negative index, and work in that space)
    elif index == 'SYMH_min':
        fn = 'SYMH_data.csv'
        # SYM-H data should be downloaded from: http://wdc.kugi.kyoto-u.ac.jp/
        Z = 518  # peak storm value
        u = 250  # threshold
        r = '48H'  # decluster threshold
        minmax = -1  # multiply the data by -1 (as it is negative index, and work in that space)
    elif index == 'SMHY_hour':
        fn = 'SYMH_data.csv'
        # SYM-H data should be downloaded from: http://wdc.kugi.kyoto-u.ac.jp/
        Z = 436  # peak storm value
        u = 250  # threshold
        r = '48H'  # decluster threshold
        minmax = -1  # multiply the data by -1 (as it is negative index, and work in that space)
    elif index == 'Dst':
        fn = 'dst_data.csv'
        # SYM-H data should be downloaded from: http://wdc.kugi.kyoto-u.ac.jp/
        Z = 412  # peak storm value
        u = 250  # threshold
        r = '48H'  # decluster threshold
        minmax = -1  # multiply the data by -1 (as it is negative index, and work in that space)

    df = pd.read_csv(fn, delimiter=',')*minmax

    extreme_value_analysis = EVA(df)

    # Extract extremes
    extreme_value_analysis.get_extremes(method="POT", threshold=u, r=r)

    # Fit model
    fit = extreme_value_analysis.fit_model(distribution='genpareto')

    timeDiff = (extreme_value_analysis.data.index[-1] - extreme_value_analysis.data.index[0])

    GPD_exceedance_probability(extreme_value_analysis.distribution.mle_parameters['c'],
                               extreme_value_analysis.distribution.mle_parameters['scale'],
                               u,
                               extreme_value_analysis.extremes.shape[0],
                               (timeDiff.seconds/(24*3600) + timeDiff.days)/365.2425, Z)


########################################################################################################################
def allComb(*tuples):
    """
    Find the weighted combination of a series of EVT estimates

    Parameters
    ----------
    tuples: Each tuple should be len 4 (value, lower bound, upper bound, years) eg 1-in-17 (14,18) with 35 years of data
            would be (17,14,18,35)
    """
    def calcVar(c_l, c_u):
        return ((c_u - c_l) / 3.92) ** 2

    def calcWeight(variances):
        inv_vars = [1/v for v in variances]
        total_inv_var = sum(inv_vars)
        return [iv / total_inv_var for iv in inv_vars]

    def calcWeight2(years):
        total_years = sum(years)
        return [y / total_years for y in years]

    variances = [calcVar(t[1], t[2]) for t in tuples]
    years = [t[3] for t in tuples]

    var_weights = calcWeight(variances)
    year_weights = calcWeight2(years)

    combined_weights = [0.5 * vw + 0.5 * yw for vw, yw in zip(var_weights, year_weights)]

    comb_return = sum(t[0] * w for t, w in zip(tuples, combined_weights))
    var_w = sum(w ** 2 * v for w, v in zip(combined_weights, variances))
    std_w = np.sqrt(var_w)

    print(f'Combination: {comb_return:.1f} ({comb_return - std_w:.1f}, {comb_return + std_w:.1f})')


########################################################################################################################
if __name__ == "__main__":

    # EVT_GEV_Rtn()
    # EVT_GPD_Rtn()
    allComb((17.2, 14.2, 20.2, 23), (5.4, 3.1, 13.6, 44), (14.6, 5.8, 23.4, 64), (22, 6, 38, 40), (16, 5.6, 26.5, 40),
            (9.3, 4.3, 14.3, 49), (10.5, 4.0, 16.1, 49), (9.8, 5.6, 29.4, 150), (11.3, 8.1, 16.8, 92),
            (16.3, 10.4, 29.7, 39), (11.1, 7.3, 18.9, 39))