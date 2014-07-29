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

def Crosstalk(name, RO_phase=0, RO_Z=False):

    m = DD.Crosstalk(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['Carbon_A'] = 3    ### Carbon spin that the Ramsey is performed on
    m.params['Carbon_B'] = 1    ### Carbon spin that the Rabi/Gate is performed on
    
    m.params['reps_per_ROsequence'] = 350 
    m.params['C13_init_state']      = 'up' 
    m.params['sweep_name']          = 'Number of pulses'
    m.params['C_RO_phase']          = RO_phase 
    m.params['C_RO_Z']              = RO_Z 
    
    ### Pulse spacing (overwrite tau to test other DD times)
    
    #m.params['C4_Ren_tau'] = [6.456e-6]            
    #m.params['C4_Ren_tau'] = [3.072e-6]
    #m.params['C1_Ren_tau'] = [9.420e-6]

    ### Sweep parameters
    m.params['Rabi_N_Sweep']= np.arange(2,40,2)
    m.params['pts'] = len(m.params['Rabi_N_Sweep']) 
    m.params['sweep_pts'] = m.params['Rabi_N_Sweep']

    ### Overwrite certain params to test
    m.params['C13_MBI_threshold']       = 1
    m.params['MBI_threshold']           = 1
    
    m.params['C13_MBI_RO_duration']     = 30 
    m.params['E_C13_MBI_amplitude']     = 1e-9

    m.params['SP_duration_after_C13']   = 50
    m.params['A_SP_amplitude_after_C13_MBI']  = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 
    
    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
      # Tomography 
    Crosstalk(SAMPLE, RO_phase = 0, RO_Z = False)
    Crosstalk(SAMPLE,RO_phase = 90, RO_Z = False)
    Crosstalk(SAMPLE,RO_phase = 0, RO_Z = True)








