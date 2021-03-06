"""
Script for a simple Decoupling sequence
"""
import numpy as np
import qt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling_swp_tau(name,tau_min=9e-6,tau_max=10e-6,tau_step =50e-9, N =16, reps_per_ROsequence=250):

    m = DD.SimpleDecoupling(name+'_tau_'+str(tau_min*1e9))

    # print 'threshold =' + str(m.params['MBI_threshold'])
    # print 'pulse_shape = ' +str(m.params['pulse_shape'])
    # NOTE: ADDED from ElectronT1_Hermite on 23-04-2015
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    funcs.prepare(m)

    if False: ### if you don't want to do MBI for this script.
        m.params['MBI_threshold'] = 0
        m.params['Ex_SP_amplitude'] = 0.
        m.params['Ex_MBI_amplitude'] = 0.
        m.params['SP_E_duration'] = 50 
        
        m.params['repump_after_MBI_A_amplitude'] = [12e-9] #20e-9
        m.params['repump_after_MBI_duration'] = [200] # 50  


    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = reps_per_ROsequence
    m.params['Initial_Pulse'] ='x'

    m.params['Final_Pulse'] ='-x'

    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'
    # m.params['Decoupling_sequence_scheme'] = 'single_block'
    Number_of_pulses = N 
    tau_list = np.arange(tau_min,tau_max,tau_step) 
    print tau_list

    m.params['pts']              = len(tau_list)
    m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
    m.params['tau_list']         = tau_list
    m.params['sweep_pts']        = tau_list*1e6
    m.params['sweep_name']       = 'tau (us)'

    m.params['DD_in_eigenstate'] = False



    m.autoconfig()
    funcs.finish(m, upload = True, debug=False)

if __name__ == '__main__':

    center_tau = 3.692e-6
    tau_step = 2e-9
    steps = 20 #has to be divisble by two.

    SimpleDecoupling_swp_tau(SAMPLE, 
        tau_min=center_tau - (steps/2)*tau_step,
        tau_max=center_tau + (steps/2)*tau_step,
        tau_step = tau_step,
        N=66,
        reps_per_ROsequence = 250)
