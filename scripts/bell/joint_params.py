joint_params = {}

### default process settings
joint_params['RO_during_LDE'] = 0

joint_params['opt_pi_pulses'] = 2
joint_params['LDE_attempts_before_CR'] = 250 # 1000 for tpqi seems ok
joint_params['initial_delay']           = 10e-9 ## 2014-06-07 initial delay used to be a joint param. i made it setup specific, to overlap the pulses
joint_params['opt_pulse_separation']    = 600e-9

joint_params['RND_during_LDE'] = 0 
joint_params['do_echo'] = 0
joint_params['do_final_MW_rotation'] = 0
joint_params['wait_for_1st_revival'] = 0
joint_params['DD_number_pi_pulses'] = 2 # the maximum number of pi pulses is 3 !!!

joint_params['LDE_element_length']     = 16.e-6+(joint_params['opt_pi_pulses']-2)*joint_params['opt_pulse_separation']  # 9e-6 for TPQI with 5 pulses
joint_params['LDE_RO_duration'] = 4e-6
joint_params['separate_RO_element'] =  True

joint_params['MAX_DATA_LEN'] =       int(100e6)
joint_params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
joint_params['MIN_SYNC_BIN'] =       0 #WRONG / TODO
joint_params['MAX_SYNC_BIN'] =       7000
joint_params['TTTR_read_count'] = 	 1000 #s
joint_params['measurement_abort_check_interval']    = 1. #sec
