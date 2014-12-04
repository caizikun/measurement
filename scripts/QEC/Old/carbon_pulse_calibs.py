'''
Scripts for calibrating carbon pulses 
Because matplotlib cannot be used in conjunction with qtlab manual fitting is used with prompts 
'''

import numpy as np
import qt
import msvcrt
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs


import measurement.scripts.QEC.dynamical_decoupling_script_sweep_tau as swp_tau 
import measurement.scripts.QEC.dynamical_decoupling_script_sweep_N as swp_N

reload(swp_tau)
reload(swp_N)

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def calibrate_carbon_rabi(name):
	#Initial broad scan to find dip 
	print 'Starting course tau sweep (resolution 10ns)'
	tau_min = float(raw_input('scan from?  (input in s): \n'))
	tau_max = float(raw_input('scan to? (input in s): \n'))
	N = int(raw_input('N?: \n'))
	swp_tau.SimpleDecoupling_swp_tau(SAMPLE+'sweep_tau',tau_min,tau_max,10e-9,N)
	cont = raw_input ('Do the fitting for sweep_tau... to abort press q: \n')
	if cont =='q':
	    return 

	print 'Starting fine tau sweep (resolution 2ns)'
	tau_min = float(raw_input('scan from  (input in s): \n'))
	tau_max = float(raw_input('scan to (input in s): \n'))
	swp_tau.SimpleDecoupling_swp_tau(SAMPLE+'sweep_tau',tau_min,tau_max,2e-9,N)
	cont = raw_input ('Do the fitting for sweep_tau... to abort press q: \n')
	if cont =='q':
	    return     

	print 'Starting sweep N (step size 4 pulses)'
	tau = float(raw_input('scan at tau = ?  (input in s): \n'))
	swp_N.SimpleDecoupling_swp_N(SAMPLE+'sweep_N',tau, reps_per_ROsequence = 500)
	cont = raw_input ('Do the fitting for sweep_N... to abort press q: \n')
	if cont =='q':
	    return     

	print 'Starting fine tau sweep (resolution 2ns)'
	N = int(raw_input('N for a pi_pulse? (must be even): \n'))
	swp_tau.SimpleDecoupling_swp_tau(SAMPLE+'sweep_tau',tau_min,tau_max,2e-9,N)

	print 'Starting sweep N (step size 4 pulses)'
	tau = float(raw_input('scan at tau = ?  (input in s): \n'))
	swp_N.SimpleDecoupling_swp_N(SAMPLE+'sweep_N',tau, reps_per_ROsequence = 500)
	cont = raw_input ('Do the fitting for sweep_N... to abort press q: ')
	if cont =='q':
	    return     

	return



if __name__ == '__main__':
    calibrate_carbon_rabi(SAMPLE)