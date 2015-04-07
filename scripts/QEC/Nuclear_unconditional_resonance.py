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

    m.params['Rabi_tau_Sweep']= m.params['C'+str(carbon_B)+'_Ren_tau'] +  tau_list

    m.params['pts'] = len(m.params['Rabi_N_Sweep']) 

    m.params['sweep_pts'] = m.params['Rabi_N_Sweep']

    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0
    
    funcs.finish(m, upload =True, debug=False)


if __name__ == '__main__':
    # N_list=np.arange(30,70,4)
    # tau_list = [(9.098)*1e-6]*len(N_list)
    # Crosstalk(SAMPLE + '_uncondGate_C3_tau_'+str(tau_list[1]),RO_phase = 0, RO_Z =True, carbon_A = 3, carbon_B = 3, tau_list=tau_list,N=N_list)
    
    # N_list=np.arange(40,100,4)
    # tau_list = [(6.824)*1e-6]*len(N_list)
    # Crosstalk(SAMPLE + '_uncondGate_C3_tau_'+str(tau_list[1]),RO_phase = 0, RO_Z =True, carbon_A = 3, carbon_B = 3, tau_list=tau_list,N=N_list)
    
    # N_list=np.arange(2,60,8)
    # tau_list = [(11.944)*1e-6]*len(N_list)
    # Crosstalk(SAMPLE + '_condGate_C3_tau_'+str(tau_list[1]),RO_phase = 0, RO_Z =True, carbon_A = 3, carbon_B = 3, tau_list=tau_list,N=N_list)
    

    # N_list=np.arange(2,100,16)
    # # N_list=[24,28,32]
    # tau_list = [(7.22)*1e-6]*len(N_list)
    # Crosstalk(SAMPLE + '_condGate_C5_tau_'+str(tau_list[0]),RO_phase = 0, RO_Z =True, carbon_A = 1, carbon_B = 1, tau_list=tau_list,N=N_list)
    

    N_list=np.arange(2,100,16)
    # N_list=[24,28,32]
    tau_list = [(9.444)*1e-6]*len(N_list)
    Crosstalk(SAMPLE + '_condGate_C5_tau_'+str(tau_list[0]),RO_phase = 0, RO_Z =True, carbon_A = 1, carbon_B = 1, tau_list=tau_list,N=N_list)
    
    # N_list=np.arange(2,60,8)
    # tau_list = [(16.5)*1e-6]*len(N_list)
    # Crosstalk(SAMPLE + '_condGate_C3_tau_'+str(tau_list[1]),RO_phase = 0, RO_Z =True, carbon_A = 3, carbon_B = 3, tau_list=tau_list,N=N_list)

    # N_list=np.arange(80,120,4)
    # tau_list = [(5.688)*1e-6]*len(N_list)
    # Crosstalk(SAMPLE + '_uncondGate_C3_tau_'+str(tau_list[1]),RO_phase = 0, RO_Z =True, carbon_A = 3, carbon_B = 3, tau_list=tau_list,N=N_list)
       









