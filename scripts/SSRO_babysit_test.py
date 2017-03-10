import msvcrt
import qt
import numpy as np
import time
import logging

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
# reload all parameters and modules
execfile(qt.reload_current_setup)

def optimize():
	print 'Starting to optimize.'

	powers_ok=False
	for i in range(5):
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
			break
		if bell_check_powers():
			powers_ok=True
			print 'All powers are ok.'
			break
	if not powers_ok:
		print 'Could not get good powers!'
		return False
   
	qt.msleep(3)
	print 'mash q now to stop the measurement'
	optimize_ok = False
	for i in range(1):
		print 'press q now to stop measuring!'
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
			break
		if qt.current_setup=='lt4':
			qt.instruments['optimiz0r'].optimize(dims=['y','x'],cnt=1, int_time=100, cycles =1)
			optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=100, cycles =2)
		else:
			qt.instruments['optimiz0r'].optimize(dims=['x','y'],cnt=1, int_time=50, cycles =1)
			optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=50, cycles =2)
		qt.msleep(1)
	if not(optimize_ok):
		print 'Not properly optimized position'
		return False
	else: 
		print 'Position is optimized!'
	qt.msleep(3)
	
	return True
	
def bell_check_powers():

	prot_name = qt.exp_params['protocols']['current']

	names=['MatisseAOM', 'NewfocusAOM','YellowAOM']
	setpoints = [qt.exp_params['protocols'][prot_name]['AdwinSSRO']['Ex_RO_amplitude'],
				700e-9, # The amount for repumping in purification
				qt.exp_params['protocols']['AdwinSSRO']['yellow_repump_amplitude']] #XXXXXXXXXXXXXXX #LT3 Yellow power fluctuates with setup steering LT3
	relative_thresholds = [0.15,0.15,0.15]
	qt.instruments['PMServo'].move_in()
	qt.msleep(2)
	qt.stools.init_AWG()
	qt.stools.turn_off_all_lasers()

	all_fine=True
	for n,s,t in zip(names, setpoints,relative_thresholds):
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
			break
		setpoint, value = qt.stools.check_power(n, s, 'adwin', 'powermeter', 'PMServo', False)
		deviation =np.abs(1-setpoint/value)
		print 'deviation', deviation
		if deviation>t:
			all_fine=False
			qt.stools.recalibrate_laser(n, 'PMServo', 'adwin')
			if n == 'NewfocusAOM':
				qt.stools.recalibrate_laser(n, 'PMServo', 'adwin',awg=True)
			break
	qt.instruments['PMServo'].move_out()
	return all_fine

SAMPLE_CFG = qt.exp_params['protocols']['current']

def ssrocalibration(name, **additional_params):
	m = ssro.AdwinSSRO('SSROCalibration_'+name)

	m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
	m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
	
	m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
	m.params.from_dict(additional_params)
	print m.params['repump_mod_control_offset']
	# ms = 0 calibration
	m.params['SP_duration'] = m.params['SP_duration_ms0']
	m.params['Ex_SP_amplitude'] = 0.
	m.params['A_SP_amplitude'] = m.params['A_SP_amplitude']
	m.params['SSRO_repetitions'] = 5000
	if m.run():
		m.save('ms0')
		qt.msleep(2.)
		# ms = 1 calibration
		m.params['SP_duration'] = m.params['SP_duration_ms1']
		m.params['A_SP_amplitude'] = 0.
		m.params['Ex_SP_amplitude'] = m.params['Ex_SP_calib_amplitude']
		m.run()
		m.save('ms1')

	m.finish()

if __name__ == '__main__':
	while True:
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
			break

		# SSRO for 1000 cycles, with babysitter on
		qt.instruments['purification_optimizer'].set_pidgate_running(True)
		qt.instruments['purification_optimizer'].set_pidyellowfrq_running(True)

		stools.turn_off_all_lasers()
		last_time = time.time()
		for i in range(1000):
			qt.instruments['purification_optimizer'].start_babysit()
			ssrocalibration(SAMPLE_CFG)
			qt.instruments['purification_optimizer'].stop_babysit()
			if time.time()-last_time > 15*60:
				qt.instruments['purification_optimizer'].stop_optimize_now()
				break
			qt.msleep(1.)	
			if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
				qt.instruments['purification_optimizer'].stop_optimize_now()
				break

		# Re-optimize if needed
		execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py')
		optimize()




