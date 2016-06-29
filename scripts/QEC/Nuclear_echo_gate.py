"""
Script for a carbon Rabi sequence
"""
import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Echo_gate(name, C13_init_method = 'swap', carbon_nr = 5,C13_init_state='up'):

    m = DD.EchoGate(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['Carbon_nr'] = carbon_nr    
    
    m.params['reps_per_ROsequence'] = 100 
    m.params['C13_init_state']      = C13_init_state
    m.params['C13_init_method']     = C13_init_method
    m.params['sweep_name']          = 'waiting time (us)'
    m.params['e_ro_orientation']    = 'positive'

    m.params['E_superposition'] = True ### This boolean inserts an initial and final pi/2 pulse on the electronic state.

#     ### Sweep parameters
    m.params['waiting_times'] = np.arange(10e-6,400e-6,10e-6)
    m.params['do_carbon_pi'] = True
    m.params['No_of_pulses'] = np.arange(8,101,8)
    #m.params['waiting_times'] = np.arange(10e-6,400e-6,10e-6)
    m.params['pts'] = len(m.params['waiting_times']) 

    m.params['sweep_pts'] = [x*2*10**6 for x in m.params['waiting_times']] ## rescale to microseconds

    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0
    
    funcs.finish(m, upload =True, debug=False)

def Bath_Freeze(name, C13_init_method = 'swap', carbon_nr = 5,C13_init_state='up'):
    
    """
    Sweeps the number of pulses in the unconditional rotation.
    Go off resonance in order to estimate how well we freeze the bath.
    """

    m = DD.EchoGate(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    

    ### Overwrrite tau to be off resonance.
    m.params['C'+str(carbon_nr)+'_uncond_tau']=[9.21e-6]
    m.params['Carbon_nr'] = carbon_nr    
    
    m.params['reps_per_ROsequence'] = 300
    m.params['C13_init_state']      = C13_init_state
    m.params['C13_init_method']     = C13_init_method
    m.params['sweep_name']          = 'Number of pulses'
    m.params['e_ro_orientation']    = 'positive'

    m.params['E_superposition'] = True ### This boolean inserts an initial and final pi/2 pulse on the electronic state.

#     ### Sweep parameters
    m.params['Number_of_pulses'] = np.arange(8,409,50)#[9,400,3000]
    m.params['waiting_times'] = [3e-6]*len(m.params['Number_of_pulses']) ### shortest possible waiting time.
    m.params['do_carbon_pi'] = False
    
    #m.params['waiting_times'] = np.arange(10e-6,400e-6,10e-6)
    m.params['pts'] = len(m.params['Number_of_pulses']) 

    m.params['sweep_pts'] = m.params['Number_of_pulses']

    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0
    
    funcs.finish(m, upload =True, debug=False)


if __name__ == '__main__':
    #Echo_gate(SAMPLE + '_C5_pZ_eROX',carbon_nr = 5,C13_init_state='up')
    #Echo_gate(SAMPLE + '_C5_mZ_eROX',carbon_nr = 5,C13_init_state='down')

    ##############################################


    Bath_Freeze(SAMPLE + 'BathFreeze_C5_pZ_wait_3us',carbon_nr = 5,C13_init_state='up',C13_init_method='swap')
       






