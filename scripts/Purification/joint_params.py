'''
contains all necessary parameters for remote measurements
'''
import qt
import params_lt4
import params_lt3
reload(params_lt4)
reload(params_lt3)
name = qt.exp_params['protocols']['current']


joint_params = {}
###
joint_params['master_setup'] = 'lt4'
joint_params['control_slave'] = False

### default process settings

joint_params['LDE_final_mw_phase'] = qt.exp_params['protocols'][name]['pulses']['X_phase']
print joint_params['LDE_final_mw_phase']
### joint carbon parameters. Need to be updated by hand.
joint_params['slave_N'] = [12]
joint_params['slave_tau'] = [10.886e-6]
joint_params['slave_eigen_phase'] = 45.81
joint_params['slave_freq_0'] = 447823.6
joint_params['slave_freq_1'] = 425435.49
joint_params['slave_freq'] = 434615.6
joint_params['slave_min_phase_correct'] = 2
joint_params['slave_min_dec_tau'] = 30e-9 + 90e-9
joint_params['slave_max_dec_tau'] = 0.255e-6
joint_params['slave_dec_pulse_multiple'] = 4
joint_params['slave_carbon_init_RO_wait'] = 90e-6 #50 us + C13_MBI RO duration
joint_params['slave_fast_pi_duration'] = 90e-9
joint_params['slave_fast_pi2_duration'] = 46e-9

joint_params['master_N'] = [34]
joint_params['master_tau'] = [6.406e-6]
joint_params['master_eigen_phase'] = 143.74
joint_params['master_freq_0'] =  443241.12
joint_params['master_freq_1'] = 416645.12
joint_params['master_freq'] = (  416645.12 + 443241.12)/2
joint_params['master_min_phase_correct'] = 2
joint_params['master_min_dec_tau'] = 2.0e-6
joint_params['master_max_dec_tau'] = 2.5e-6
joint_params['master_dec_pulse_multiple'] = 4
joint_params['master_carbon_init_RO_wait'] = 90e-6
joint_params['master_fast_pi_duration'] = 94e-9
joint_params['master_fast_pi2_duration'] = 50e-9

joint_params['master_slave_AWG_first_element_delay'] = 500e-9 #DON'T CHANGE THIS! HIGHLY DEPENDENT ON DELAYS

### parameters for LDE timing:
joint_params['TPQI_normalisation_measurement'] = False
joint_params['initial_delay']           = 10e-9 #DONT CHANGE THIS
joint_params['do_final_mw_LDE']         = 0 # only used for B&K

joint_params['opt_pi_pulses'] = 1
joint_params['opt_pulse_separation']    = 2.5e-6#250e-9 #350e-9 changed for higher visibility of 

joint_params['LDE_attempts'] = 250 # 1000 for tpqi seems ok

joint_params['LDE_element_length'] = 7.0e-6 #DO NOT CHANGE THIS


#change params to LT3 and LT4 later on.
joint_params['master_LDE_decouple_time']    = params_lt4.params_lt4['LDE_decouple_time']
joint_params['master_average_repump_time']  = params_lt4.params_lt4['average_repump_time']

joint_params['slave_LDE_decouple_time']     = params_lt3.params_lt3['LDE_decouple_time']
joint_params['slave_average_repump_time']   = params_lt3.params_lt3['average_repump_time']
