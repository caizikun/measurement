import qt
import sce_expm_joint_params
import numpy as np
### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

params_lt4 = {}

#general sequence things. All of these are set automatically.
params_lt4['do_general_sweep']          = False
params_lt4['is_two_setup_experiment']   = 1
params_lt4['do_N_MBI']                  = 0 #practically not in use
params_lt4['MW_before_LDE']            = 0
params_lt4['LDE_is_init']             = 0
params_lt4['do_LDE']                  = 1 # we always do this.
params_lt4['record_expm_params']  = False # by default we dont record this, only useful if a long run

# LDE element
params_lt4['MW_during_LDE']             = 1 
params_lt4['AWG_SP_power']              = 150e-9
params_lt4['LDE_SP_duration']           = 1.5e-6 #1.5e-6
params_lt4['LDE_SP_delay']			    = 0e-6 ### don't change this.
params_lt4['average_repump_time'] 		= 0.3e-6
params_lt4['LDE_decouple_time']         = round(1/qt.exp_params['samples']['111no2']['C4_freq_0'],9)#2.2e-6
params_lt4['opt_pulse_start']           = 2.5e-6 #2215e-9 - 46e-9 + 4e-9 +1e-9 
params_lt4['MW_opt_puls1_separation']   = 100e-9#220e-9
params_lt4['MW_repump_distance']		= 150e-9
params_lt4['MW_final_delay_offset']		= 10e-9
params_lt4['first_mw_pulse_is_pi2']     = 0


#adwin params defs:
params_lt4['SP_duration'] = 30 #10
params_lt4['wait_after_pulse_duration'] = 1
params_lt4['do_sequences'] = 1
params_lt4['Dynamical_stop_ssro_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt4['E_RO_durations']  = [params_lt4['Dynamical_stop_ssro_duration']] # only necessary for analysis
params_lt4['Dynamical_stop_ssro_threshold'] = 1
params_lt4['MBI_attempts_before_CR'] = 1 

# channels
params_lt4['PLU_event_di_channel'] = 21
params_lt4['PLU_which_di_channel'] = 20
params_lt4['AWG_repcount_DI_channel'] = 19
params_lt4['remote_adwin_di_success_channel'] = 22
params_lt4['remote_adwin_di_fail_channel'] = 23
params_lt4['remote_adwin_do_success_channel'] = 14
params_lt4['remote_adwin_do_fail_channel'] = 15
params_lt4['remote_awg_trigger_channel'] = 13
params_lt4['invalid_data_marker_do_channel'] = 1 # currently not used

# timing and communication
params_lt4['adwin_comm_safety_cycles'] = 15
params_lt4['adwin_comm_timeout_cycles'] = 50000 # 10 ms
params_lt4['wait_for_awg_done_timeout_cycles'] = 1000000  # 10ms
params_lt4['master_slave_awg_trigger_delay'] = 9 # times 10ns, minimum is 9.


# dynamical decoupling
params_lt4['max_decoupling_reps'] = 200
params_lt4['dynamic_decoupling_N'] = 4
params_lt4['dynamic_decoupling_tau'] = 2.2e-6#round(10/qt.exp_params['samples'][]['C4_freq_0'],9) #16*2.2e-6 # 16 th larmor revival gives: 200*4*32 = 25.6 ms.
params_lt4['tomography_basis'] = 'Y' ### sets RELATIVE phase and amplitude of the last pi/2 pulse when doing decoupling.
params_lt4['decoupling_element_duration'] = 2*params_lt4['dynamic_decoupling_tau']*params_lt4['dynamic_decoupling_N']


params_lt4['sync_during_LDE']           = 1

params_lt4['PLU_during_LDE']          = 1
params_lt4['PLU_gate_duration']       = 200e-9#70e-9 # 200e-9
params_lt4['PLU_gate_3_duration']     = 40e-9
params_lt4['PLU_1_delay']             = 2e-9
params_lt4['PLU_2_delay']             = 1e-9
params_lt4['PLU_3_delay']             = 50e-9
params_lt4['PLU_4_delay']             = 200e-9

params_lt4['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_theta_amp'] #### needs to be changed back to regular pi/2 for most calibrations
params_lt4['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_theta_length']
params_lt4['mw_first_pulse_phase']    = qt.exp_params['protocols'][name]['pulses']['X_phase']
params_lt4['LDE_final_mw_amplitude']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt4['LDE_final_mw_phase'] 	  = 93.7 #qt.exp_params['protocols'][name]['pulses']['X_phase']

params_lt4['sin2_theta']			= 0.5
params_lt4['sin2_theta_fit_of']		= 1.0227049816095488
params_lt4['sin2_theta_fit_a']		= 1.7743130002675946
params_lt4['sin2_theta_fit_x0']		= 0.89525893974434934

### Everything HydraHarp
TH_HH_selector = 1#e3 #set to 1 for HH
params_lt4['MAX_DATA_LEN']        =   int(100e6)
params_lt4['BINSIZE']             =   8  #2**BINSIZE*BASERESOLUTION = 1 ps for HH
params_lt4['MIN_SYNC_BIN']        =   int(1.75e6)/TH_HH_selector #5 us 
params_lt4['MAX_SYNC_BIN']        =   int(2.5e6)/TH_HH_selector#15 us # XXX was 15us 
params_lt4['MIN_HIST_SYNC_BIN']   =   int(1.65e6)/TH_HH_selector #XXXX was 5438*1e3
params_lt4['MAX_HIST_SYNC_BIN']   =   int(2.0e6)/TH_HH_selector
params_lt4['count_marker_channel'] = 1

params_lt4['pulse_start_bin'] = 1838e3 -params_lt4['MIN_SYNC_BIN'] #2490e3 BK  #XXX
params_lt4['pulse_stop_bin'] = 1842e3 - params_lt4['MIN_SYNC_BIN'] # 2499e3 BK #XXX
params_lt4['tail_start_bin'] = 1843e3 - params_lt4['MIN_SYNC_BIN'] # 2499e3 BK #XXX
params_lt4['tail_stop_bin'] = 1873e3 - params_lt4['MIN_SYNC_BIN']  # 2570e3 BK #XXX
params_lt4['PQ_ch1_delay'] = 20e3

params_lt4['measurement_time']    =   24.*60*60 #sec = 24H
params_lt4['measurement_abort_check_interval']    = 1 #sec
params_lt4['wait_for_late_data'] = 0 #in units of measurement_abort_check_interval
params_lt4['TTTR_read_count'] = 131072#qt.instruments['HH_400'].get_T2_READMAX()
params_lt4['TTTR_RepetitiveReadouts'] =  1


params_lt4['Phase_msmt_DAC_channel'] = 12 
params_lt4['Phase_Msmt_voltage'] = 3.2 # 3.0 V = approx. 200 nW seems okay
params_lt4['Phase_Msmt_off_voltage'] = 0
params_lt4['Phase_stab_DAC_channel'] = 14 ### channel of the fibre stretcher
params_lt4['zpl1_counter_channel'] = 2
params_lt4['zpl2_counter_channel'] = 3
params_lt4['modulate_stretcher_during_phase_msmt'] = 0

params_lt4['stretcher_V_2pi'] = 2.23
params_lt4['stretcher_V_max'] = 9.5
params_lt4['Phase_Msmt_g_0'] = 0.91
params_lt4['Phase_Msmt_Vis'] = 1.47


params_lt4['PID_GAIN'] = 1.0
params_lt4['PID_Kp'] = 5.0 #10	# was 15
params_lt4['PID_Ki'] = 0.0
params_lt4['PID_Kd'] = 0.0
params_lt4['phase_setpoint'] = np.pi/2

# Relevant to PID/ ent expm
params_lt4['count_int_time_stab'] = 10000 # How long to integrate counts for in microseconds for phase stab
params_lt4['pid_points'] = 4 # How many points to sample the phase at during the PID loop
params_lt4['pid_points_to_store'] = 4 # How many points to store
params_lt4['phase_stab_max_time'] = 300000 # How long in microseconds to run the expm for after phase stabilisation

# Relevant to phase stability studies
params_lt4['sample_points'] = 10 # How many points to sample the phase at during the expm part
params_lt4['count_int_time_meas'] = 1000 # How long to integrate counts for in microseconds for phase meas


