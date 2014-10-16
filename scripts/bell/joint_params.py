joint_params = {}

### default process settings
joint_params['RO_during_LDE'] = 1

joint_params['opt_pi_pulses'] = 2
joint_params['LDE_attempts_before_CR'] = 250 # 1000 for tpqi seems ok
joint_params['initial_delay']           = 10e-9 #DONT CHANGE THIS
joint_params['opt_pulse_separation']    = 600e-9
joint_params['TPQI_normalisation_measurement'] = True

joint_params['RND_during_LDE'] = 1 
joint_params['do_echo'] = 1
joint_params['do_final_MW_rotation'] = 1
joint_params['wait_for_1st_revival'] = 0
joint_params['DD_number_pi_pulses'] = 2 # the maximum number of pi pulses is 3 !!!

joint_params['LDE_element_length']     = 16.e-6+(joint_params['opt_pi_pulses']-2)*joint_params['opt_pulse_separation']+1e-6  # 9e-6 for TPQI with 5 pulses
joint_params['LDE_RO_duration'] = 4e-6

joint_params['MAX_DATA_LEN'] =       int(100e6)
joint_params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
joint_params['MIN_SYNC_BIN'] =       7000 #WRONG / TODO
joint_params['MAX_SYNC_BIN'] =       7005
joint_params['MIN_HIST_SYNC_BIN'] =  1
joint_params['MAX_HIST_SYNC_BIN'] =  15000
joint_params['TTTR_read_count'] = 	 1000 #s
joint_params['measurement_abort_check_interval']    = 1. #sec
joint_params['RND_start'] = 9969e-9+200e-9# = dt(f,BC)-dt(AC) + margin
