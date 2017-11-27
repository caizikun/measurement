# """
# Written by MAB
# Script for a single Nuclear Rabi
# Initialization:
# - Initializes in the nuclear |0> state using SWAP

# Rabi
# - Sweep the pulse of an RF length

# Readout
# - Readout in Z basis

# Copy from nitogen_rabipy in lt2_scripts/adwin_ssro/BSM
# Copy from BSM.py in lt2_scripts/adwin_ssro/BSM

# Copy created by Joe 10-11-17

# """


# import numpy as np
# import qt 
# import msvcrt

# #reload all parameters and modules
# execfile(qt.reload_current_setup)
# import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
# import measurement.scripts.mbi.mbi_funcs as funcs

# SAMPLE = qt.exp_params['samples']['current']
# SAMPLE_CFG = qt.exp_params['protocols']['current']

# def CarbonRabiWithDirectRF(name,
#         carbon_nr             = 5,               
#         carbon_init_state     = 'up', 
#         el_RO                 = 'positive',
#         debug                 = True,
#         C13_init_method       = 'swap', 
#         el_after_init         = '1',
#         DoRabi                = False):

#     m = DD.NuclearRabiWithDirectRF(name)
#     funcs.prepare(m)


#     '''Set parameters'''

#     ### Parameters
#     m.params['reps_per_ROsequence']     = 400
#     m.params['C13_MBI_threshold_list']  = [0]
#     if el_after_init == '1': 
#         centerfreq = m.params['C' + str(carbon_nr) + '_freq_1_m1']
#     if el_after_init == '0':
#         centerfreq = m.params['C' + str(carbon_nr) + '_freq_0']

#     if DoRabi: 
#         m.params['RF_pulse_durations'] = 10e-6 + np.linspace(0e-6,800e-6,21)
#         m.params['pts'] = len(m.params['RF_pulse_durations'])
#         m.params['RF_pulse_frqs'] = np.ones(m.params['pts']) * centerfreq 
#         m.params['sweep_name'] = 'RF_pulse_length (us)'
#         m.params['sweep_pts']  =  m.params['RF_pulse_durations'] / 1e-6 
#     else: 
#         m.params['RF_pulse_frqs'] = np.linspace(centerfreq-0e3,centerfreq+2e3,1)
#         m.params['pts'] = len(m.params['RF_pulse_frqs'])
#         m.params['RF_pulse_durations'] = np.ones(m.params['pts']) * 410e-6
#         m.params['sweep_name'] = 'RF_freq (kHz)'
#         m.params['sweep_pts']  =  m.params['RF_pulse_frqs'] / 1e3       

#     m.params['RF_pulse_phases'] = np.ones(m.params['pts']) * 0 
#     m.params['RF_pulse_amps'] = np.ones(m.params['pts']) * 0
#     m.params['C_RO_phase'] = m.params['pts']*['Z'] #np.ones(m.params['pts'] )*0 #m.params['pts']*['Z']

#     m.params['C13_init_method'] = 'swap' #C13_init_method
#     m.params['electron_readout_orientation'] = el_RO
#     m.params['carbon_nr']                    = carbon_nr
#     m.params['init_state']                   = 'up' #carbon_init_state  
#     m.params['el_after_init']                = el_after_init

#     m.params['Nr_C13_init']       = 1 
#     m.params['Nr_MBE']            = 0 
#     m.params['Nr_parity_msmts']   = 0

#     funcs.finish(m, upload =True, debug=debug)

# if __name__ == '__main__':
#     carbon_nr = 1
#     i = 0
#     el_after_init = '1'
#     DoRabi = True
#     CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C'+str(carbon_nr)+'_el1_positive_' +str(i)+'run', carbon_nr = carbon_nr, el_RO= 'positive', el_after_init=el_after_init, DoRabi=DoRabi, debug=False)

"""
Written by MAB
Script for a single Nuclear Rabi
Initialization:
- Initializes in the nuclear |0> state using SWAP

Rabi
- Sweep the pulse of an RF length

Readout
- Readout in Z basis

Copy from nitogen_rabipy in lt2_scripts/adwin_ssro/BSM
Copy from BSM.py in lt2_scripts/adwin_ssro/BSM

Copy created by Joe 10-11-17

"""


import numpy as np
import qt 
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def CarbonRabiWithDirectRF(name,
        carbon_nr             = 5,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = True,
        C13_init_method       = 'swap', 
        el_after_init         = '1',
        DoRabi                = False):

    m = DD.NuclearRabiWithDirectRF(name)
    funcs.prepare(m)


    '''Set parameters'''

    ### Parameters
    m.params['reps_per_ROsequence']     = 500
    m.params['C13_MBI_threshold_list']  = [0]
    if el_after_init == '1': 
        centerfreq = m.params['C' + str(carbon_nr) + '_freq_1_m1']
    if el_after_init == '0':
        centerfreq = m.params['C' + str(carbon_nr) + '_freq_0']

    if DoRabi: 
        m.params['RF_pulse_durations'] = 300e-6 + np.linspace(0e-6,10e-6,21)
        m.params['pts'] = len(m.params['RF_pulse_durations'])
        m.params['RF_pulse_frqs'] = np.ones(m.params['pts']) * centerfreq 
        m.params['sweep_name'] = 'RF_pulse_length (us)'
        m.params['sweep_pts']  =  m.params['RF_pulse_durations'] / 1e-6 
    else: 
        m.params['RF_pulse_frqs'] = np.linspace(centerfreq-0e3,centerfreq+2e3,1)
        m.params['pts'] = len(m.params['RF_pulse_frqs'])
        m.params['RF_pulse_durations'] = np.ones(m.params['pts']) * 410e-6
        m.params['sweep_name'] = 'RF_freq (kHz)'
        m.params['sweep_pts']  =  m.params['RF_pulse_frqs'] / 1e3       

    m.params['RF_pulse_phases'] = np.ones(m.params['pts']) * 0 
    m.params['RF_pulse_amps'] = np.ones(m.params['pts']) * 1
    m.params['C_RO_phase'] = np.ones(m.params['pts'] )*0,#[0] #['X'] # np.ones(m.params['pts'] )*0 # m.params['pts']*['X'] 

    m.params['C13_init_method'] = C13_init_method
    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = 'up' #carbon_init_state  
    m.params['el_after_init']                = el_after_init

    m.params['Nr_C13_init']       = 1 
    m.params['Nr_MBE']            = 0 
    m.params['Nr_parity_msmts']   = 0

    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':
    carbon_nr = 1
    i = 0
    el_after_init = '1'
    DoRabi = True
    CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C'+str(carbon_nr)+'_el1_positive_' +str(i)+'run', carbon_nr = carbon_nr, el_RO= 'positive', C13_init_method = 'MBI', el_after_init=el_after_init, DoRabi=DoRabi, debug=False)
