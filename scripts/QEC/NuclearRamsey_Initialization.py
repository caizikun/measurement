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
        carbon_nr             = 5,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = False,
        C13_init_method       = 'MBI',
        C13_MBI_RO_state      = 1,
        dyn_dec=False):

    m = DD.NuclearRamseyWithInitialization_v2(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 150
    m.params['C13_MBI_RO_state'] = 1
    #m.params['C13_MBI_threshold_list']=[0]

    # ### overwritten from msmnt params
           
    ###################################
    ## Option 1; Sweep waiting time ###
    ###################################
    
    #      1A - Rotating frame with detuning
    detuning_basic = 0.100e3
    detuning_dict = {
    '1' : detuning_basic,
    '2' : detuning_basic,
    '3' : detuning_basic*3.,
    '5' : detuning_basic,
    '6' : detuning_basic*4.}

    detuning = detuning_dict[str(carbon_nr)] 
    m.params['add_wait_gate'] = True
    m.params['pts'] = 21
    m.params['free_evolution_time'] = 400e-6 + np.linspace(0e-6, 3*1./detuning,m.params['pts'])
    # m.params['free_evolution_time'] = 180e-6 + np.linspace(0e-6, 4*1./74e3,m.params['pts'])
    

    m.params['C'+str(carbon_nr)+'_freq_0']  += detuning
    m.params['C'+str(carbon_nr)+'_freq_1'+m.params['electron_transition']]  += detuning
    m.params['C_RO_phase'] =  np.ones(m.params['pts'] )*0  

    m.params['sweep_name'] = 'free_evolution_time'
    m.params['sweep_pts']  = m.params['free_evolution_time']
        
    #     # 1B - Lab frame
    # m.params['add_wait_gate'] = True
    # m.params['pts'] = 20
    # m.params['free_evolution_time'] = np.linspace(385e-6, 389e-6,m.params['pts'])
    # m.params['C_RO_phase'] = m.params['pts']*['reset']
    # # m.params['C_RO_phase'] = m.params['pts']*['X']        

    # m.params['sweep_name'] = 'free_evolution_time'
    # m.params['sweep_pts']  = m.params['free_evolution_time']
    
    ############################################
    ### Option 2; Sweep RO phase at set time ###
    ############################################
    # m.params['pts'] = 15
    # m.params['add_wait_gate'] = True
    # m.params['free_evolution_time'] = np.ones(m.params['pts'] )*465e-6
    # m.params['C_RO_phase'] = np.linspace(-20, 800,m.params['pts'])    

    # m.params['sweep_name'] = 'phase'
    # m.params['sweep_pts']  = m.params['C_RO_phase']

    '''Derived and fixed parameters'''

    # m.params['C13_init_method'] = C13_init_method

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

  
    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':
    NuclearRamseyWithInitialization(SAMPLE+'_positive__ms1',debug=False,carbon_nr =1,el_RO='postive',C13_MBI_RO_state=0)
    #NuclearRamseyWithInitialization(SAMPLE+'_positive__ms0',debug=False,carbon_nr =1,el_RO='postive',C13_MBI_RO_state=0)
    #NuclearRamseyWithInitialization(SAMPLE+'_negative__ms1',debug=False,carbon_nr =1,el_RO='negative',C13_MBI_RO_state=1)
    #NuclearRamseyWithInitialization(SAMPLE+'_negative__ms0',debug=False,carbon_nr =1,el_RO='negative',C13_MBI_RO_state=0)


