'''
contains all necessary parameters for remote measurements
'''
import qt
import sce_expm_params_lt4 as params_lt4
import sce_expm_params_lt3 as params_lt3
# reload(params_lt4)
# reload(params_lt3)
name = qt.exp_params['protocols']['current']


joint_params = {}
###
joint_params['master_setup'] = 'lt4'
joint_params['control_slave'] = True

### default process settings

### parameters for LDE timing:
#joint_params['TPQI_normalisation_measurement'] = False # does not exist anymore
joint_params['initial_delay']           = 10e-9 #DONT CHANGE THIS
joint_params['do_final_mw_LDE']         = 0

joint_params['opt_pi_pulses'] = 1
joint_params['opt_pulse_separation']    = 0.5e-6#250e-9 #350e-9 changed for higher visibility of 

joint_params['LDE_attempts'] = 1000 

joint_params['LDE_element_length'] = 10e-6#3e-6 #DO NOT CHANGE THIS

joint_params['LDE_attempts_before_yellow']  = 200
joint_params['Yellow_AWG_duration']			= 300e-6