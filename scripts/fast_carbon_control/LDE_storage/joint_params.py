'''
contains all necessary parameters for remote measurements
'''
import qt
import params_lt4
reload(params_lt4)
name = qt.exp_params['protocols']['current']


joint_params = {}
joint_params['master_setup'] = None

### default process settings

joint_params['LDE_final_mw_phase'] = qt.exp_params['protocols'][name]['pulses']['X_phase']
print joint_params['LDE_final_mw_phase']
### joint carbon parameters. Need to be updated by hand.
joint_params['slave_N'] = [12]
joint_params['slave_tau'] = [10.886e-6]
joint_params['slave_eigen_phase'] = 36.64
joint_params['slave_freq_0'] =   447747.11
joint_params['slave_freq_1'] = 425341.4
joint_params['slave_freq'] =   (447747.11+425341.4)/2
joint_params['slave_min_phase_correct'] = 2
joint_params['slave_min_dec_tau'] = 30e-9 + 90e-9
joint_params['slave_max_dec_tau'] = 0.255e-6
joint_params['slave_dec_pulse_multiple'] = 4
joint_params['slave_carbon_init_RO_wait'] = 90e-6 #50 us + C13_MBI RO duration
joint_params['slave_fast_pi_duration'] = 90e-9
joint_params['slave_fast_pi2_duration'] = 46e-9

joint_params['master_N'] = [34]
joint_params['master_tau'] = [6.406e-6]
joint_params['master_eigen_phase'] = 130.41
joint_params['master_freq_0'] =  443141.64
joint_params['master_freq_1'] = 416544.29
joint_params['master_freq'] = (443141.64 + 416544.29)/2
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

joint_params['LDE1_attempts'] = 1000 
joint_params['LDE2_attempts'] = 500

joint_params['LDE_element_length'] = 7e-6 #3*params_lt4.params_lt4['LDE_decouple_time'] #6.75e-6 #DO NOT CHANGE THIS # JS: did so anyway (2017-07-18)


# #change params to LT3 and LT4 later on.
# joint_params['master_LDE_decouple_time']    = params_lt2.params_lt2['LDE_decouple_time']
# joint_params['master_average_repump_time']  = params_lt2.params_lt2['average_repump_time']
#
# joint_params['slave_LDE_decouple_time']     = params_lt2.params_lt2['LDE_decouple_time']
# joint_params['slave_average_repump_time']   = params_lt2.params_lt2['average_repump_time']
