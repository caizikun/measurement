"""
Script for a simple Decoupling sequence
"""
import numpy as np
import qt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling_swp_tau(name,tau_min=9e-6,tau_max=10e-6,tau_step =50e-9, N =16):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    if N%4 == 0: 
        m.params['Final_Pulse'] ='-x'
    else:
        m.params['Final_Pulse'] ='x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    Number_of_pulses = N 
    tau_list = np.arange(tau_min,tau_max,tau_step) 
    print tau_list

    m.params['pts']              = len(tau_list)
    m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
    m.params['tau_list']         = tau_list
    m.params['sweep_pts']        = tau_list*1e6
    m.params['sweep_name']       = 'tau (us)'

    print m.params['fast_pi_duration']
    print m.params['fast_pi_amp']

    # m.params['fast_pi2_duration'] = pi_dur
    # m.params['fast_pi2_amp'] = pi_amp




    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    #SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.522e-6-0.02e-6,tau_max=6.522e-6+0.02e-6,tau_step =1e-9, N =20)
    #SimpleDecoupling_swp_tau(SAMPLE, tau_min=18.55e-6-0.03e-6,tau_max=18.55e-6+0.03e-6,tau_step =2e-9, N =32)
    #SimpleDecoupling_swp_tau(SAMPLE, tau_min=15.200e-6,tau_max=15.400e-6,tau_step =4e-9, N =64)
    # stools.turn_off_all_lt2_lasers()
    # GreenAOM.set_power(20e-6)
    # optimiz0r.optimize(dims=['x','y','z'])
    # stools.turn_off_all_lt2_lasers()
    SimpleDecoupling_swp_tau(SAMPLE, tau_min=2.7e-6,tau_max=2.78e-6,tau_step =4e-9, N =64)
    # stools.turn_off_all_lt2_lasers()
    # GreenAOM.set_power(20e-6)
    # optimiz0r.optimize(dims=['x','y','z'])
    # stools.turn_off_all_lt2_lasers()
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=8.2e-6,tau_max=8.7e-6,tau_step =5e-9, N =32, pi_dur = 136e-9, pi_amp=0.398466, pi2_dur = 68e-9, pi2_amp = 0.398571)
    # stools.turn_off_all_lt2_lasers()
    # GreenAOM.set_power(20e-6)
    # optimiz0r.optimize(dims=['x','y','z'])
    # stools.turn_off_all_lt2_lasers()
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=8.2e-6,tau_max=8.7e-6,tau_step =5e-9, N =32, pi_dur = 168e-9, pi_amp=0.313663, pi2_dur = 84e-9, pi2_amp = 0.314146)


