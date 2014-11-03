"""
Cython-based fast data analysis for raw data obtained with the HH or TH in T2 mode.

authors:
Gerwin Koolstra
Wolfgang Pfaff

2014: Bas Hensen :
    - NOTE THESE FILES DO NOT WORK FOR THE PicoHARP instrument.
Bell: 
    - Combined Histogramming and T2 measurement
"""
 
import cython
#import time
import numpy as np
#from cython.view cimport array as cvarray
cimport numpy as cnp
#from libc.math cimport floor
 
@cython.boundscheck(False)
@cython.wraparound(False)
def Bell_live_filter(
    cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] time not None,
    cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] channel not None,
    cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] special not None,
    cnp.ndarray[cnp.uint32_t, ndim=2, mode='c'] hist not None,
    cnp.uint64_t t_ofl,
    cnp.uint64_t t_lastsync,
    cnp.uint32_t last_sync_number,
    cnp.uint64_t min_sync_time,
    cnp.uint64_t max_sync_time,
    cnp.uint64_t min_hist_sync_time,
    cnp.uint64_t max_hist_sync_time,
    cnp.uint64_t wraparound,
    cnp.uint64_t t2_time_factor):
    """
    This is a specialized form of PQ data recording, alowing to receive part of the data 
    in a histogrammed form (the data arriving between min_hist_sync_time and max_hist_sync_time), 
    and part of the data (between min_sync_time and max_sync_time) in standard - per event - 
    form. The two regions are allowed to overlap.
    This function expects as input decoded HH data:
    - an array with time information,
    - an array for the channel,
    - an array containing the special bit,
    - 1 x (N x 2) array to histogram the data in. N = max_hist_sync_time - min_hist_sync_time.
    and overflow information: 
    - the current overflow time,
    - and the time of the last sync. (both start with zero and get updated by
        calls of this function).
    - the last sync number
    
    Returns for each event (syncs and overflows are not in the data anymore)
    - the absolute time since msmt start (in bins)
    - channel
    - special bit,
    - the updated (N x 2) histrogram array
    - relative time to the last previous sync (in bins)
    and overflow information (absolute overflow time and time of the last sync).
    """

    cdef cnp.uint64_t EntanglementMarkers =0
    cdef cnp.uint64_t k
    cdef cnp.uint64_t l = 0
    cdef cnp.uint64_t Hist_SyncTimediff
    cdef cnp.uint64_t length = time.shape[0]
    cdef cnp.ndarray[cnp.uint64_t, ndim=1, mode='c'] sync_time = np.empty((length,), dtype='u8')
    cdef cnp.ndarray[cnp.uint64_t, ndim=1, mode='c'] hhtime = np.empty((length,), dtype='u8')
    cdef cnp.ndarray[cnp.uint8_t, ndim=1, mode='c'] hhchannel = np.empty((length,), dtype='u1')
    cdef cnp.ndarray[cnp.uint8_t, ndim=1, mode='c'] hhspecial = np.empty((length,), dtype='u1')
    cdef cnp.ndarray[cnp.uint32_t, ndim=1, mode='c'] sync_number = np.empty((length,), dtype='u4')

    for k in range(length):
        if channel[k] == 63:
            t_ofl += wraparound
            continue

        if special[k] == 1 and channel[k] == 0: # This is a SYNC event
            t_lastsync = (time[k] + t_ofl) / t2_time_factor      #the t2_time_factor comes from an extra bit for the HH. see HH docs.
            last_sync_number += 1
            continue

        _sync_time = (t_ofl + time[k]) / t2_time_factor  - t_lastsync           

        # now calculate the histogram (note that only photons are saved, but no markers)
        if special[k] == 0 and _sync_time > min_hist_sync_time and _sync_time < max_hist_sync_time:
            hist[_sync_time - min_hist_sync_time,channel[k]] += 1

        if special[k] == 1 or (_sync_time > min_sync_time and _sync_time < max_sync_time):  # write all markers and photons in ROI
            if channel == 4:
                EntanglementMarkers += 1
            hhtime[l] = (t_ofl + time[k]) / t2_time_factor
            hhchannel[l] = channel[k]
            hhspecial[l] = special[k]
            sync_time[l] = _sync_time
            sync_number[l] = last_sync_number
            l += 1
            continue

        

    return hhtime[:l], hhchannel[:l], hhspecial[:l], sync_time[:l], hist, sync_number[:l], l, t_ofl, t_lastsync, last_sync_number, EntanglementMarkers
