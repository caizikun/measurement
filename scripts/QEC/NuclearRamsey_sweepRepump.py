"""
Script for a carbon ramsey sequence.
Initialization:
- Initializes in the +/- X state using C13 MBI
- Can set the electron state by setting the MBI succes condition

Ramsey
- Sweeps a wait time after initialization or RO phase at a fixed time
"""
import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def NuclearRamseyWithInitialization(name, 
        carbon_nr             = 3,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = False,
        C13_init_method       = 'MBI',
        C13_sp_duration       = 300):

    m = DD.NuclearRamseyWithInitialization_v2(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 300
    m.params['C13_MBI_RO_state'] = 1

    ### overwritten from msmnt params
           
    ####################################
    ### Option 1; Sweep waiting time ###
    ####################################
    
        # 1A - Rotating frame with detuning
    # detuning = 0.5e3
    # m.params['add_wait_gate'] = True
    # m.params['pts'] = 21
    # m.params['free_evolution_time'] = 400e-6 + np.linspace(0e-6, 3*1./detuning,m.params['pts'])
    # # m.params['free_evolution_time'] = 180e-6 + np.linspace(0e-6, 4*1./74e3,m.params['pts'])
    

    # m.params['C'+str(carbon_nr)+'_freq_0']  += detuning
    # m.params['C'+str(carbon_nr)+'_freq_1']  += detuning
    # m.params['C_RO_phase'] =  np.ones(m.params['pts'] )*0  

    # m.params['sweep_name'] = 'free_evolution_time'
    # m.params['sweep_pts']  = m.params['free_evolution_time']
    
        ### 1B - Lab frame
    m.params['add_wait_gate'] = True
    m.params['pts'] = 37
    m.params['free_evolution_time'] = np.linspace(510e-6, 528e-6,m.params['pts'])
    m.params['C_RO_phase'] = m.params['pts']*['reset']
    # m.params['C_RO_phase'] = m.params['pts']*['X']        

    m.params['sweep_name'] = 'free_evolution_time'
    m.params['sweep_pts']  = m.params['free_evolution_time']
    
    ############################################
    ### Option 2; Sweep RO phase at set time ###
    ############################################
    # m.params['pts'] = 21
    # m.params['add_wait_gate'] = False
    # m.params['free_evolution_time'] = np.ones(m.params['pts'] )*360e-6
    # m.params['C_RO_phase'] = np.linspace(-20, 400,m.params['pts'])    

    # m.params['sweep_name'] = 'phase'
    # m.params['sweep_pts']  = m.params['C_RO_phase']

    '''Derived and fixed parameters'''

    m.params['C13_init_method'] = C13_init_method

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    m.params['SP_duration_after_C13']=C13_sp_duration 
    m.params['C13_MBI_RO_duration']=100
    m.params['electron_after_init']='0'

    if C13_sp_duration==0:
        m.params['A_SP_amplitude_after_C13_MBI']=0

    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':

    for length in [20]:#[0,2,5,7,10,15,20,25,30,35,40,50,70,85,100,125,150]:
        NuclearRamseyWithInitialization(SAMPLE+'_SP_length_'+str(length),C13_sp_duration=length)

