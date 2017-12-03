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
        DoRabi                = False,
        RF_generation_method  = 'AWG'):

    m = DD.NuclearRabiWithDirectRF(name)
    funcs.prepare(m)

    ### Parameters
    m.params['RF_generation_method']    = RF_generation_method
    m.params['reps_per_ROsequence']     = 500
    m.params['C13_MBI_threshold_list']  = [1]

    if el_after_init == '1': 
        centerfreq = m.params['C' + str(carbon_nr) + '_freq_1_m1']
    if el_after_init == '0':
        centerfreq = m.params['C' + str(carbon_nr) + '_freq_0']

    if DoRabi: 
        m.params['RF_pulse_durations'] = np.linspace(100e-6,100e-6,1) + 3e-6
        m.params['pts'] = len(m.params['RF_pulse_durations'])
        m.params['RF_pulse_frqs'] = np.ones(m.params['pts']) * centerfreq 
        m.params['sweep_name'] = 'RF_pulse_length (us)'
        m.params['sweep_pts']  =  m.params['RF_pulse_durations'] / 1e-6 
    elif Sweep_C_RO_phase: 
        m.params['C_RO_phase'] = [i for i in np.linspace(0,90,21)]#np.linspace(0,180,21)       
        m.params['pts'] = len(m.params['C_RO_phase'])
        m.params['RF_pulse_durations'] = np.ones(m.params['pts']) * 10e-6
        m.params['RF_pulse_frqs'] = np.ones(m.params['pts']) * centerfreq 
        m.params['sweep_name'] = 'RF_pulse_length (us)'
        m.params['sweep_pts']  =  m.params['C_RO_phase'] 
    else: 
        m.params['RF_pulse_frqs'] = np.linspace(centerfreq-100e3,centerfreq+100e3,21)
        m.params['pts'] = len(m.params['RF_pulse_frqs'])
        m.params['RF_pulse_durations'] = np.ones(m.params['pts']) * 4e-6
        m.params['sweep_name'] = 'RF_freq (kHz)'
        m.params['sweep_pts']  =  m.params['RF_pulse_frqs'] / 1e3    

    m.params['RF_pulse_phases'] = np.ones(m.params['pts']) * 180. 
    m.params['RF_pulse_amps'] = np.ones(m.params['pts']) * 0.7       

    m.params['C13_init_method'] = 'swap' #C13_init_method
    m.params['C_RO_phase'] = ['Z']#[0] #['X'] # np.ones(m.params['pts'] )*0 # m.params['pts']*['X'] 


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
    Sweep_C_RO_phase = False
    CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C'+str(carbon_nr)+'_el1_positive_' +str(i)+'run',
                            carbon_nr = carbon_nr, el_RO= 'positive', el_after_init=el_after_init, 
                            DoRabi=DoRabi, RF_generation_method = 'AWG_Long', debug=True)
