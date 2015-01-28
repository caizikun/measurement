"""
Written by MB
Script for a single Nuclear Rabi
Initialization:
- Initializes in the nuclear |0> state using SWAP

Rabi
- Sweep the pulse of an RF length

Readout
- Readout in Z basis

Copy from nitogen_rabipy in lt2_scripts/adwin_ssro/BSM
Copy from BSM.py in lt2_scripts/adwin_ssro/BSM

"""


import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def CarbonRabiWithDirectRF(name, 
        carbon_nr             = 5,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = False,
        C13_init_method       = 'swap', 
        C13_MBI_RO_state      = 0,
        el_after_init         = '1'):
        

    m = DD.NuclearRabiWithDirectRF(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence']     = 500
    m.params['C13_MBI_RO_state']        = C13_MBI_RO_state     
    m.params['C13_MBI_threshold_list']  = [1] 

    #!!!! STILL OLD
    m.params['RF_pulse_durations'] = np.linspace(10e-6, 250e-6, 25)
    m.params['pts'] = len(m.params['RF_pulse_durations'])
    m.params['RF_pulse_amps'] = np.ones(m.params['pts']) * 0.02
    m.params['RF_pulse_frqs'] = np.ones(m.params['pts']) * m.params['C' + str(carbon_nr) + '_freq_' + str(C13_MBI_RO_state)]
    
    
    m.params['C_RO_phase'] = m.params['pts']*['Z']        

    m.params['sweep_name'] = 'RF_pulse_length (us)'
    m.params['sweep_pts']  =  m.params['RF_pulse_durations'] * 1e-6 
    

    m.params['C13_init_method'] = C13_init_method
    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['el_after_init']                = el_after_init

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

  
    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':
    CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C5_el1_positive', carbon_nr=5, el_RO= 'positive', el_after_init=1)

    
