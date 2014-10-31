"""
Script for a carbonT1 msmnts
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

def NuclearT1(name,tau = None, carbon_state = 'up', 
            electron_RO = 'positive', carbon = 1,
            el_RO_result = 0):

    m = DD.NuclearT1(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['pts'] = 11 

    m.params['Addressed_Carbon']             = carbon
    m.params['C13_init_state']               = carbon_state
    m.params['electron_readout_orientation'] = electron_RO
    m.params['C13_MBI_RO_state'] = el_RO_result


    m.params['sweep_name'] = 'wait_times'
    m.params['wait_times'] = np.linspace(1e-3, 40e-3,m.params['pts']) #Note: wait time must be atleast carbon init time +5us 
    m.params['sweep_pts']  = m.params['wait_times']

    m.params['Nr_C13_init']         = 1

    ### MBE settings
    m.params['Nr_MBE']              = 0
    m.params['Nr_parity_msmts']     = 0


    #############################
    #!NB: These should go into msmt params
    #############################

    ##########
    # Overwrite certain params to test
    m.params['C13_MBI_threshold_list']       = [0]
        
    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':


    
    ## Carbon up and down
    NuclearT1(SAMPLE + 'up_positive_C1',carbon_state = 'up', 
            electron_RO = 'positive', carbon = 5,
            el_RO_result = 0)


    NuclearT1(SAMPLE + 'up_negative_C1',carbon_state = 'up', 
        electron_RO = 'negative', carbon = 5,
        el_RO_result = 0)