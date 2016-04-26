'''
contains all necessary parameters for remote measurements
'''
import qt
import params_lt1 #impot lt3 and l4 later on.
name = qt.exp_params['protocols']['current']


joint_params = {}
###
joint_params['master_setup'] = 'lt1'


### default process settings

joint_params['LDE_final_mw_phase'] = qt.exp_params['protocols'][name]['pulses']['X_phase']




### joint carbon parameters. Need to be updated by hand atm.
joint_params['slave_N'] = [10]
joint_params['slave_tau'] = [3.75e-6]
joint_params['slave_eigen_phase'] = 0.0
joint_params['slave_freq_0'] = 447968.42
joint_params['slave_freq_1'] = 483714
joint_params['slave_freq'] = (447968.42+ 483714)/2.
joint_params['slave_min_phase_correct'] = 2
joint_params['slave_min_dec_tau'] = 2.1e-6
joint_params['slave_max_dec_tau'] = 2.4e-6
joint_params['slave_dec_pulse_multiple'] = 4
joint_params['slave_carbon_init_RO_wait'] = 70e-6

joint_params['master_N'] = [28]
joint_params['master_tau'] = [8.81e-6]
joint_params['master_eigen_phase'] = -19.64
joint_params['master_freq_0'] = 438757.84
joint_params['master_freq_1'] = 413107.0
joint_params['master_freq'] = (438753.54 + 413107.0)/2.
joint_params['master_min_phase_correct'] = 2
joint_params['master_min_dec_tau'] = 2.1e-6
joint_params['master_max_dec_tau'] = 2.4e-6
joint_params['master_dec_pulse_multiple'] = 4
joint_params['master_carbon_init_RO_wait'] = 70e-6

### parameters for LDE timing:
joint_params['TPQI_normalisation_measurement'] = False
joint_params['initial_delay']           = 10e-9 #DONT CHANGE THIS
joint_params['do_final_mw_LDE']         = 0 # only changed for B&K

joint_params['opt_pi_pulses'] = 1
joint_params['opt_pulse_separation']    = 250e-9 #350e-9 changed for higher visibility of 

joint_params['LDE_attempts_before_CR'] = 250 # 1000 for tpqi seems ok

joint_params['LDE_element_length'] = 10e-6 #needs to be set accordingly.

### mw timing for LDE and for keeping coherence afterwards

#XXX
#change params to LT3 and LT4 later on.
joint_params['master_LDE_decouple_time']    = params_lt1.params_lt1['LDE_decouple_time']
joint_params['master_average_repump_time']  = params_lt1.params_lt1['average_repump_time']

joint_params['slave_LDE_decouple_time']     = params_lt1.params_lt1['LDE_decouple_time']
joint_params['slave_average_repump_time']   = params_lt1.params_lt1['average_repump_time']