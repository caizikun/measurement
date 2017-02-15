'''
contains all necessary parameters for remote measurements
'''
import qt
import single_click_ent_expm_params_lt4 as params_lt4
import single_click_ent_expm_params_lt3 as params_lt3
reload(params_lt4)
reload(params_lt3)
name = qt.exp_params['protocols']['current']


joint_params = {}
###
joint_params['master_setup'] = 'lt4'
joint_params['control_slave'] = True

### default process settings

joint_params['LDE_final_mw_phase'] = qt.exp_params['protocols'][name]['pulses']['X_phase']

joint_params['master_slave_AWG_first_element_delay'] = 500e-9 #DON'T CHANGE THIS! HIGHLY DEPENDENT ON DELAYS

### parameters for LDE timing:
joint_params['TPQI_normalisation_measurement'] = False
joint_params['initial_delay']           = 10e-9 #DONT CHANGE THIS
joint_params['do_final_mw_LDE']         = 0 # only used for B&K

joint_params['opt_pi_pulses'] = 1
joint_params['opt_pulse_separation']    = 2.5e-6#250e-9 #350e-9 changed for higher visibility of 

joint_params['LDE_attempts'] = 1000 

joint_params['LDE_element_length'] = 7.0e-6 #DO NOT CHANGE THIS

joint_params['Phase_msmt_DAC_channel'] = 2 
joint_params['Phase_Msmt_voltage'] = 0.8
joint_params['Phase_Msmt_off_voltage'] = 0.8
joint_params['PID_GAIN'] = 1.0
joint_params['PID_Kp'] = 0.002
joint_params['PID_Ki'] = 0.0
joint_params['PID_Kd'] = 0.0

joint_params['count_int_cycles'] = 25 # How many cycles to integrate counts for
joint_params['pid_points'] = 10 # How many points to sample the phase at during the PID loop
joint_params['sample_points'] = 100 # How many points to sample the phase at during the expm part

