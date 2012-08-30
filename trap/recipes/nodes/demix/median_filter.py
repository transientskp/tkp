import os
import numpy as numpy
import math
from   scipy import *
import scipy.signal as signal

def median_filter(ampl_tot, half_window, threshold):

     q = 1.# 1.4826
     ampl_tot_copy = numpy.copy(ampl_tot)
     median_array = signal.medfilt(ampl_tot,half_window*2.-1)

     # find the higher peaks
     for i in range(len(median_array)):
         thr = float(threshold*median_array[i]*q)
         absvalue= abs(ampl_tot[i] -  median_array[i])
         if absvalue > thr :
             ampl_tot_copy[i] = median_array[i]

     # find the low values
     ampl_div      = 1./ampl_tot_copy
     median_array = signal.medfilt(ampl_div,half_window*2.-1)

     for i in range(len(median_array)):
         thr = float(threshold*median_array[i]*q)
         absvalue= abs(ampl_div[i] -  median_array[i])
         if absvalue > thr :
             ampl_div[i] = median_array[i]
     ampl_tot_copy = 1./ampl_div # get back

     ###### now do a second pass #######
     median_array = signal.medfilt(ampl_tot,half_window*2.-1)

     # find the higher peaks
     for i in range(len(median_array)):
         thr = float(threshold*median_array[i]*q)
         absvalue= abs(ampl_tot[i] -  median_array[i])
         if absvalue > thr :
             ampl_tot_copy[i] = median_array[i]

     # find the low values
     ampl_div      = 1./ampl_tot_copy
     median_array = signal.medfilt(ampl_div,half_window*2.-1)

     for i in range(len(median_array)):
         thr = float(threshold*median_array[i]*q)
         absvalue= abs(ampl_div[i] -  median_array[i])
         if absvalue > thr :
             ampl_div[i] = median_array[i]
     ampl_tot_copy = 1./ampl_div # get back
     #ampl_tot_copy = ampl_tot_copy*0. + 1.0
     return ampl_tot_copy


def my_solflag(ampl, half_window, threshold):
    """ Picked out the flagging part of solflag. ampl is a numpy array of
ONE series
    of amplitudes. Bad data is False --- R. Niruj Mohan"""

    import numpy as N
    import math


    ampl_tot_copy = numpy.copy(ampl)
    median_array  = signal.medfilt(ampl_tot_copy,half_window*2.-1)


    ndata = len(ampl)
    flags = N.zeros(ndata, dtype=bool)
    sol = N.zeros(ndata+2*half_window)
    sol[half_window:half_window+ndata] = ampl

    for i in range(0, half_window):
        # Mirror at left edge.
        idx = min(ndata-1, half_window-i)
        sol[i] = ampl[idx]

        # Mirror at right edge
        idx = max(0, ndata-2-i)
        sol[ndata+half_window+i] = ampl[idx]

    sol_flag = N.zeros(ndata+2*half_window, dtype=bool)
    sol_flag_val = N.zeros(ndata+2*half_window, dtype=bool)

    for i in range(half_window, half_window + ndata):
        # Compute median of the absolute distance to the median.
        window = sol[i-half_window:i+half_window+1]
        window_flag = sol_flag[i-half_window:i+half_window+1]
        window_masked = window[~window_flag]

        if len(window_masked) < math.sqrt(len(window)):
            # Not enough data to get accurate statistics.
            continue

        median = N.median(window_masked)
        q = 1.4826 * N.median(N.abs(window_masked - median))

        # Flag sample if it is more than 1.4826 * threshold * the
        # median distance away from the median.
        if abs(sol[i] - median) > (threshold * q):
            sol_flag[i] = True

    mask = sol_flag[half_window:half_window + ndata]

    for i in range(len(mask)):
        if mask[i]:
           ampl_tot_copy[i] = median_array[i]
    return ampl_tot_copy

def my_solflag_inv(ampl, half_window, threshold):
    """ Picked out the flagging part of solflag. ampl is a numpy array of
ONE series
    of amplitudes. Bad data is False --- R. Niruj Mohan"""

    import numpy as N
    import math


    ampl_tot_copy = 1./numpy.copy(ampl)
    median_array  = signal.medfilt(ampl_tot_copy,half_window*2.-1)


    ndata = len(ampl)
    flags = N.zeros(ndata, dtype=bool)
    sol = N.zeros(ndata+2*half_window)
    sol[half_window:half_window+ndata] = ampl

    for i in range(0, half_window):
        # Mirror at left edge.
        idx = min(ndata-1, half_window-i)
        sol[i] = ampl[idx]

        # Mirror at right edge
        idx = max(0, ndata-2-i)
        sol[ndata+half_window+i] = ampl[idx]

    sol_flag = N.zeros(ndata+2*half_window, dtype=bool)
    sol_flag_val = N.zeros(ndata+2*half_window, dtype=bool)

    for i in range(half_window, half_window + ndata):
        # Compute median of the absolute distance to the median.
        window = sol[i-half_window:i+half_window+1]
        window_flag = sol_flag[i-half_window:i+half_window+1]
        window_masked = window[~window_flag]

        if len(window_masked) < math.sqrt(len(window)):
            # Not enough data to get accurate statistics.
            continue

        median = N.median(window_masked)
        q = 1.4826 * N.median(N.abs(window_masked - median))

        # Flag sample if it is more than 1.4826 * threshold * the
        # median distance away from the median.
        if abs(sol[i] - median) > (threshold * q):
            sol_flag[i] = True

    mask = sol_flag[half_window:half_window + ndata]

    for i in range(len(mask)):
        if mask[i]:
           ampl_tot_copy[i] = median_array[i]
    return 1./ampl_tot_copy

