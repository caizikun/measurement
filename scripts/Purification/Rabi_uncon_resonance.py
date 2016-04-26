"""
Script for a carbon Rabi sequence

1) Carbon A is initialized
2) Carbon B is the guy who gets the RABI

Allows varying of tau and N of the RABI
"""


import numpy as np
import qt
import msvcrt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD
import measurement.scripts.mbi.mbi_funcs as funcs
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)
reload(funcs)
reload(DD)

ins_counters = qt.instruments['counters']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def unconditional_rabi(name, 
    C13_init_method = 'MBI', 
    carbon_A    = 1, 
    carbon_B    = 1,  
    N_list      = np.arange(4,100,8), 
    tau_list    = None,
    electron_readout_orientation = 'positive',
    tomo_basis = 'X'):

    m = DD.Crosstalk(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['carbon_nr'] = carbon_A  ### Carbon spin that is prepared via MBI
    m.params['Carbon_B']  = carbon_B  ### Carbon spin that the Rabi/Gate is performed on
    m.params['reps_per_ROsequence'] = 500

    ###############
    # Carbon INIT #
    ###############
    m.params['Nr_C13_init']         = 1
    m.params['C13_init_method']     = C13_init_method
    m.params['C13_init_state']      = 'up'
    m.params['el_after_init']       = '0'
    
    ###############
    # Rabi params #
    ###############
    m.params['Carbon_B']            = carbon_B
    m.params['Rabi_N_Sweep']        = N_list
    if tau_list == None:
        tau_list = m.params['C'+str(carbon_B)+'_Ren_tau']*len(N_list)
    m.params['Rabi_tau_Sweep']      = tau_list
    m.params['pts'] = len(m.params['Rabi_N_Sweep']) 

    ###############
    # tomo params #
    ###############
    m.params['Tomography Bases']    = tomo_basis
    m.params['electron_readout_orientation'] = electron_readout_orientation

    # sweep stuff
    if len(set(N_list)) != 1:
        print 'SWEEPING N'
        m.params['sweep_name']          = 'Number of pulses'
        m.params['sweep_pts']           = m.params['Rabi_N_Sweep']
    elif len(set(tau_list)) != 1:
        print 'SWEEPING tau'
        m.params['sweep_name']          = 'Rabi tau'
        m.params['sweep_pts']           = m.params['Rabi_tau_Sweep']

    
    #### parity and mbe settings
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0
    
    funcs.finish(m, upload =True, debug=False)


if __name__ == '__main__':


    N_list      =   np.arange(2,100,4)
    tau_list    =   [(9.16)*1e-6] *len(N_list)

    # tau_range = 0.1e-6
    # tau_list = np.arange(9.18e-6-tau_range,9.18e-6+tau_range,4e-9) #steps of 2e-9
    # N_list = [20]*len(tau_list)

    unconditional_rabi(SAMPLE + '_uncondGate_tau_'+str(tau_list[0]),
        C13_init_method = 'swap',
        carbon_A        = 1, 
        carbon_B        = 1, 
        tau_list        = tau_list,
        N_list          =  N_list,
        electron_readout_orientation = 'positive',
        tomo_basis      = 'Z')
 



