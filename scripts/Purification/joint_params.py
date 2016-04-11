'''
contains all necessary parameters for remote measurements
'''
import qt
name = qt.exp_params['protocols']['current']


joint_params = {}
###
joint_params['master_setup'] = 'lt4'


### default process settings

joint_params['do_final_mw_LDE'] = 0
joint_params['LDE_final_mw_phase'] = qt.exp_params['protocols'][name]['pulses']['X_phase'] #for YY -> Y_phase

joint_params['opt_pi_pulses'] = 1
joint_params['LDE_attempts_before_CR'] = 250 # 1000 for tpqi seems ok
joint_params['initial_delay']           = 10e-9#10e-9 #Should be set once and then kept!
joint_params['opt_pulse_separation']    = 250e-9 #350e-9 changed for higher visibility of 
joint_params['TPQI_normalisation_measurement'] = False

joint_params['LDE_element_length'] = 4e-6 #needs to be set accordingly.

#### beware these elements change with every
# joint_params['slave_init_duration'] = 24*10.328e-6*2*2+

