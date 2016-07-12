"""
Script for a carbon Rabi sequence

Carbon A and B are the same guy.
Address A on resonance, B on unconditional resonance
"""
import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Crosstalk(name, RO_phase=0, RO_Z=False, C13_init_method = 'swap', carbon_A = 1, carbon_B = 5,  
    N = np.arange(4,100,8), tau_list= None):

    m = DD.Crosstalk(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['Carbon_A'] = carbon_A    ### Carbon spin that the Ramsey is performed on
    m.params['Carbon_B'] = carbon_B    ### Carbon spin that the Rabi/Gate is performed on
    
    m.params['reps_per_ROsequence'] = 150
    m.params['C13_init_state']      = 'up'
    m.params['C13_init_method']     = C13_init_method
    m.params['sweep_name']          = 'Number of pulses'
    m.params['C_RO_phase']          = RO_phase 
    m.params['C_RO_Z']              = RO_Z 

#     ### Sweep parameters
    m.params['Rabi_N_Sweep']= [0] + N
    
    if tau_list == None:
        tau_list = m.params['C'+str(carbon_B)+'_Ren_tau']*len(N)

    m.params['Rabi_tau_Sweep']= tau_list

    m.params['pts'] = len(m.params['Rabi_N_Sweep']) 

    m.params['sweep_pts'] = m.params['Rabi_N_Sweep']

    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0
    
    funcs.finish(m, upload =True, debug=False)


if __name__ == '__main__':


    # N_list=np.arange(2,100,16)
    # N_list=[32]
    tau_list = np.arange(2.1e-6,2.5e-6,4e-9)
    N_list = [32]*len(tau_list)
    Crosstalk(SAMPLE + '_condGate_C1_tau_'+str(tau_list[0]),
        RO_phase = 0, 
        RO_Z =True, 
        carbon_A = 1, 
        carbon_B = 1, 
        tau_list=tau_list,
        N=N_list)
 



