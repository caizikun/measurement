'''
contains all necessary parameters for remote measurements
'''
import qt
name = qt.exp_params['protocols']['current']


joint_params = {}
###
joint_params['master_setup'] = 'lt1'


### default process settings
joint_params['RO_during_LDE'] = 1 #0=adwin, 1=timeharp

joint_params['do_final_mw'] = 1
joint_params['LDE_final_mw_phase'] = qt.exp_params['protocols'][name]['pulses']['X_phase']

joint_params['opt_pi_pulses'] = 2
joint_params['LDE_attempts_before_CR'] = 250 # 1000 for tpqi seems ok
joint_params['initial_delay']           = 10e-9 #DONT CHANGE THIS
joint_params['opt_pulse_separation']    = 250e-9 #350e-9 changed for higher visibility of 
joint_params['TPQI_normalisation_measurement'] = False

joint_params['LDE_element_length'] = 5e-6 #needs to be set accordingly.


### joint carbon parameters. Need to be updated by hand atm.
joint_params['slave_carbon_N'] = 10
joint_params['slave_carbon_tau'] = 3.75e-6
joint_params['slave_carbon_eigen_phase'] = 0.0
joint_params['slave_freq_0'] = 447968.42
joint_params['slave_freq_1'] = 483714
joint_params['slave_freq'] = (447024.+ 483714)/2.

joint_params['master_carbon_N'] = 28
joint_params['master_carbon_tau'] = 8.81e-6
joint_params['master_carbon_eigen_phase'] = -19.64
joint_params['master_freq_0'] = 438757.84
joint_params['master_freq_1'] = 413107.0
joint_params['master_freq'] = (438753.54 + 413107.0)/2.,