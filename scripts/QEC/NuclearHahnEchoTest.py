"""
Script for a carbon Hahn echo sequence.
Initialization:
- Initializes in the 1 state using Swap
- Can set the electron state by setting the MBI succes condition

Hahn echo
- Applies two pi / 2 pulses along x-axis to apply one pi pulse

Measurement
- Measures Carbon state along X,Y,Z axis. Should allign along Z.
"""
import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def NuclearHahnWithInitialization(name, 
        carbon_nr             = 5,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = False,
        C13_init_method       = 'swap'):

    m = DD.NuclearHahnEchoWithInitialization(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500
    m.params['C13_MBI_RO_state'] = 1 #Initalize in ms_=-1 to decouple nuclear spins
    m.params['C13_MBI_threshold_list'] = [0] #Zero as we are detecting ms=-1 with laser resonance on other transition
    m.params['C13_MBI_RO_duration'] = 100 #Chaning readout laser duration to ensure m_s=-1 

    ### overwritten from msmnt params
           
 
    m.params['add_wait_gate'] = False # No wait gate as we are testing pi pulse
    m.params['pts'] = 3
    m.params['free_evolution_time'] = 10e-3 # Free evolution time in the order of 
    m.params['C_RO_phase'] = ['X','Y','Z']

    m.params['sweep_name'] = 'phase'
    m.params['sweep_pts']  = m.params['C_RO_phase']
    
    

    '''Derived and fixed parameters'''

    m.params['C13_init_method'] = C13_init_method

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

  
    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':
    NuclearHahnWithInitialization(SAMPLE)

