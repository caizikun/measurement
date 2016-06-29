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


### default process settings

joint_params['LDE_final_mw_phase'] = qt.exp_params['protocols'][name]['pulses']['X_phase']
print joint_params['LDE_final_mw_phase']
### joint carbon parameters. Need to be updated by hand.
joint_params['slave_N'] = [12]
joint_params['slave_tau'] = [10.886e-6]
joint_params['slave_eigen_phase'] = 55.85
joint_params['slave_freq_0'] = 447940.23
joint_params['slave_freq_1'] = 425530.23
joint_params['slave_freq'] = 434615.6
joint_params['slave_min_phase_correct'] = 2
joint_params['slave_min_dec_tau'] = 30e-9 + 100e-9
joint_params['slave_max_dec_tau'] = 0.255e-6
joint_params['slave_dec_pulse_multiple'] = 4
joint_params['slave_carbon_init_RO_wait'] = 75e-6

joint_params['master_N'] = [28]
joint_params['master_tau'] = [6.36e-6]
joint_params['master_eigen_phase'] = 96.77
joint_params['master_freq_0'] = 446128.33
joint_params['master_freq_1'] = 419820.5
joint_params['master_freq'] = (419823.82+ 446122.14)/2
joint_params['master_min_phase_correct'] = 2
joint_params['master_min_dec_tau'] = 2.1e-6
joint_params['master_max_dec_tau'] = 2.4e-6
joint_params['master_dec_pulse_multiple'] = 4
joint_params['master_carbon_init_RO_wait'] = 90e-6


### parameters for LDE timing:
joint_params['TPQI_normalisation_measurement'] = False
joint_params['initial_delay']           = 10e-9 #DONT CHANGE THIS
joint_params['do_final_mw_LDE']         = 0 # only used for B&K

joint_params['opt_pi_pulses'] = 1
joint_params['opt_pulse_separation']    = 2.5e-6#250e-9 #350e-9 changed for higher visibility of 

joint_params['LDE_attempts'] = 250 # 1000 for tpqi seems ok

joint_params['LDE_element_length'] = 7e-6 #DO NOT CHANGE THIS


#change params to LT3 and LT4 later on.
joint_params['master_LDE_decouple_time']    = params_lt4.params_lt4['LDE_decouple_time']
joint_params['master_average_repump_time']  = params_lt4.params_lt4['average_repump_time']

joint_params['slave_LDE_decouple_time']     = params_lt3.params_lt3['LDE_decouple_time']
joint_params['slave_average_repump_time']   = params_lt3.params_lt3['average_repump_time']


### everything PQ is stored in local parameters
# joint_params['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
# joint_params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
# joint_params['MIN_SYNC_BIN'] =       0
# joint_params['MAX_SYNC_BIN'] =       20000
# joint_params['MIN_HIST_SYNC_BIN'] =  1
# joint_params['MAX_HIST_SYNC_BIN'] =  15000
# joint_params['TTTR_RepetitiveReadouts'] =  10 #
# joint_params['TTTR_read_count'] = 	1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
# joint_params['measurement_abort_check_interval']    = 2. #sec
# joint_params['wait_for_late_data'] = 5 #in units of measurement_abort_check_interval
# joint_params['use_live_marker_filter']=True