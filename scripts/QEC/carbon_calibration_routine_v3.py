''' Measurement set to calibrate the evolution frequencies for the different carbon spins 
plus the phases they pick up during carbon gates'''

import numpy as np
import qt
import msvcrt
from analysis.scripts.QEC import carbon_ramsey_analysis as cr 
reload(cr)

execfile(qt.reload_current_setup)

ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs
n = 1

#######################################################
###### Set which carbons and values to calibrate ######
#######################################################

Carbon_list_ms0 = [1,2,3,5,6]
Carbon_list_ms1 = [1,2,3,5,6]
Carbon_list_selfphase = [1,2,3,5,6]
Carbon_list_crossphase = [1,2,3,5,6]
cal_f_ms1 = False
cal_f_ms0 = False
cal_self_phase = True
cal_crossphase = False

# Carbon_list_ms0 = [1]
# Carbon_list_ms1 = Carbon_list_ms0
# Carbon_list_selfphase = Carbon_list_ms1
# Carbon_list_crossphase = [1,2]

detuning_basic = 0.44e3
detuning_dict = {
	'1' : detuning_basic,
	'2' : detuning_basic,
	'3' : detuning_basic*3.,
	'5' : detuning_basic,
	'6' : detuning_basic*4.}
# measure

debug = False

######

def NuclearRamseyWithInitialization_cal(name, 
        carbon_nr           = 5,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        detuning            = 0.5e3,
        el_state            = 1,
        debug               = False):
    
    m = DD.NuclearRamseyWithInitialization_v2(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500
    m.params['C13_MBI_RO_state'] = el_state
    ### overwritten from msmnt params
           
    ####################################
    ### Option 1; Sweep waiting time ###
    ####################################
    
        # 1A - Rotating frame with detuning
    m.params['add_wait_gate'] = True
    m.params['pts'] = 21
    m.params['free_evolution_time'] = 400e-6 + np.linspace(0e-6, 3*1./detuning,m.params['pts'])
    # m.params['free_evolution_time'] = 180e-6 + np.linspace(0e-6, 4*1./74e3,m.params['pts'])
    

    m.params['C'+str(carbon_nr)+'_freq_0']  += detuning
    m.params['C'+str(carbon_nr)+'_freq_1']  += detuning
    m.params['C_RO_phase'] =  np.ones(m.params['pts'] )*0  

    m.params['sweep_name'] = 'free_evolution_time'
    m.params['sweep_pts']  = m.params['free_evolution_time']

    '''Derived and fixed parameters'''
	# 
    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    # m.params['electron_after_init'] = str(el_state)
    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    funcs.finish(m, upload =True, debug=debug)

def NuclearRamseyWithInitialization_phase(name, 
        carbon_nr           = 1,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        el_state            = 0,
        debug               = False,
        nr_of_pts			= 24):

    m = DD.NuclearRamseyWithInitialization_v2(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500
    m.params['C13_MBI_RO_state'] = el_state
    
    
    m.params['pts'] = nr_of_pts
    m.params['add_wait_gate'] = False
    # m.params['free_evolution_time'] = np.ones(m.params['pts'] )*360e-6
    m.params['C_RO_phase'] = np.linspace(-60, 400,m.params['pts'])    

    m.params['sweep_name'] = 'phase'
    m.params['sweep_pts']  = m.params['C_RO_phase']

    '''Derived and fixed parameters'''

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    # m.params['electron_after_init'] = str(el_state)

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

  
    funcs.finish(m, upload =True, debug=debug)


def Crosstalk(name, C_measured = 5, C_gate = 1, RO_phase=0, RO_Z=False, 
				C13_init_method = 'MBI', N_list = np.arange(4,300,24), debug = False):
    m = DD.Crosstalk(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['Carbon_A'] = C_measured    ### Carbon spin that the Ramsey is performed on
    m.params['Carbon_B'] = C_gate        ### Carbon spin that the Rabi/Gate is performed on
    
    m.params['reps_per_ROsequence'] = 750 
    m.params['C13_init_state']      = 'up' 
    m.params['C13_init_method']     = C13_init_method
    m.params['sweep_name']          = 'Number of pulses'
	
    m.params['C13_MBI_RO_state'] 	= 0

    ### Sweep parameters
    m.params['Rabi_N_Sweep']= N_list
    m.params['pts'] = len(m.params['Rabi_N_Sweep']) 
    m.params['sweep_pts'] = m.params['Rabi_N_Sweep']

    m.params['Rabi_tau_Sweep']= m.params['C'+str(C_gate)+'_Ren_tau']*len(m.params['Rabi_N_Sweep'])

    m.params['C_RO_Z']              = RO_Z 
    m.params['C_RO_phase']          = RO_phase 
    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0 
    
    funcs.finish(m, upload =True, debug=debug)


def Crosstalk_vs2(name, C_measured = 5, C_gate = 1, RO_phase=0, RO_Z=False, C13_init_method = 'MBI', 
					N_list = np.arange(4,300,24), debug = False,el_RO= 'positive',el_state = 0):
    m = DD.Nuclear_Crosstalk_vs2(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['carbon_nr'] 			= C_measured    ### Carbon spin that the Ramsey is performed on
    m.params['Carbon_B'] 			= C_gate        ### Carbon spin that the Rabi/Gate is performed on
    
    m.params['reps_per_ROsequence'] = 500 
    m.params['init_state']      	= 'up' 

   
    m.params['pts'] 				= 15
    m.params['C_RO_phase'] 			= np.linspace(-60, 400,m.params['pts'])    

    m.params['sweep_name'] 			= 'phase'
    m.params['sweep_pts']  			= m.params['C_RO_phase']

    '''Derived and fixed parameters'''

    m.params['electron_readout_orientation'] = el_RO

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0
   
    funcs.finish(m, upload =True, debug=debug)


################################################################
###### Calibrate ms=-1 frequencies for all 3 carbon spins ######
################################################################


if n == 1 and cal_f_ms1:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 100
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 100
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 0*15e-9
	print 'Calibrate ms=-1 frequencies for all ' + str(len(Carbon_list_ms1)) + ' carbon spins'
	if not debug:
		GreenAOM.set_power(25e-6)
		adwin.start_set_dio(dio_no=4,dio_val=0)
		optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
		adwin.start_set_dio(dio_no=4,dio_val=0)

	for C_msmt in Carbon_list_ms1:
		detuning = detuning_dict[str(C_msmt)]
		NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C'+str(C_msmt), carbon_nr= C_msmt, detuning = detuning, el_state = 1)
		# fit
		f0,uf0 = cr.Carbon_Ramsey(timestamp=None, 
		              offset = 0.5, amplitude = 0.3, x0=0, decay_constant = 1e5, exponent = 2, 
		              frequency = detuning, phase =0, 
		              plot_fit = True, show_guess = False, fixed = [2,3,4],            
		              return_freq = True,
		              return_results = False,
		              title = 'msm1_freq_C'+str(C_msmt))
		#update
		qt.exp_params['samples']['111_1_sil18']['C'+str(C_msmt)+'_freq_1'] += -f0 + detuning
		print 'C'+str(C_msmt)+'_freq_1'
		print qt.exp_params['samples']['111_1_sil18']['C'+str(C_msmt)+'_freq_1']
		print '--------------------------------'
		print 'press q to stop measurement loop'
		print '--------------------------------'
		qt.msleep(5)
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
		    n = 0



###############################################################
###### Calibrate ms=0 frequencies for all 3 carbon spins ######
###############################################################

if n == 1 and cal_f_ms0:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate ms=0 frequencies for all ' + str(len(Carbon_list_ms0)) + ' carbon spins'
	if not debug:
		GreenAOM.set_power(25e-6)
		adwin.start_set_dio(dio_no=4,dio_val=0)
		optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
		adwin.start_set_dio(dio_no=4,dio_val=0)

	for C_msmt in Carbon_list_ms0:
		detuning = detuning_dict[str(C_msmt)]
		NuclearRamseyWithInitialization_cal(SAMPLE+'_msm0_freq_C'+str(C_msmt), carbon_nr= C_msmt, 
							detuning = detuning, el_state = 0)
		# fit
		f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
		              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
		              frequency = detuning, phase =0, 
		              plot_fit = True, show_guess = False,fixed = [2,3,4],            
		              return_freq = True,
		              return_results = False,
		              title = '_msm0_freq_C'+str(C_msmt))
		#update
		qt.exp_params['samples']['111_1_sil18']['C'+str(C_msmt)+'_freq_0'] += -f0 + detuning
		print 'C'+str(C_msmt)+'_freq_0'
		print qt.exp_params['samples']['111_1_sil18']['C'+str(C_msmt)+'_freq_0']
		print '--------------------------------'
		print 'press q to stop measurement loop'
		print '--------------------------------'
		qt.msleep(5)
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
		    n = 0

##################################################################
##### Calibrate extra phase for gate for all 3 carbon spins ######
#################################################################
	
if n == 1 and cal_self_phase:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate extra phase for gate for all ' + str(len(Carbon_list_selfphase)) + ' carbon spins'

	if not debug:
		GreenAOM.set_power(25e-6)
		adwin.start_set_dio(dio_no=4,dio_val=0)
		optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
		adwin.start_set_dio(dio_no=4,dio_val=0)

	for C_msmt in Carbon_list_selfphase:
		qt.exp_params['samples']['111_1_sil18']['C'+str(C_msmt)+'_Ren_extra_phase_correction_list'][C_msmt] = 0
		#measure
		NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C'+str(C_msmt), carbon_nr= C_msmt, nr_of_pts = 21)
		# fit
		phi0,u_phi_0, Amp, u_Amp= 	cr.Carbon_Ramsey(timestamp=None, 
		                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
		                       frequency = 1/360., phase =0, 
		                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
		       	            return_phase = True,
		       	            return_amp = True,
				            return_results = False,
							title = 'phase_C'+str(C_msmt))
		#update
		if Amp > 0:
			qt.exp_params['samples']['111_1_sil18']['C'+str(C_msmt)+'_Ren_extra_phase_correction_list'][C_msmt] = phi0
		elif Amp < 0:
			qt.exp_params['samples']['111_1_sil18']['C'+str(C_msmt)+'_Ren_extra_phase_correction_list'][C_msmt] = phi0+180.
		print 'C'+str(C_msmt)+'_Ren_extra_phase_correction_list['+str(C_msmt)+']'
		print qt.exp_params['samples']['111_1_sil18']['C'+str(C_msmt)+'_Ren_extra_phase_correction_list'][C_msmt]
		print '--------------------------------'
		print 'press q to stop measurement loop'
		print '--------------------------------'
		qt.msleep(5)
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
			n = 0
#################################################################
###### Calibrate crosstalk for gate for all 3 carbon spins ######
#################################################################

	
if n == 1 and cal_crossphase:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate crosstalk for gate for all ' + str(len(Carbon_list_crossphase)) + ' carbon spins'

	if not debug:
		GreenAOM.set_power(25e-6)
		adwin.start_set_dio(dio_no=4,dio_val=0)
		optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
		adwin.start_set_dio(dio_no=4,dio_val=0)

	for C_msmt in Carbon_list_crossphase:
		for C_gate in Carbon_list_crossphase:
			if C_gate != C_msmt:
				qt.exp_params['samples']['111_1_sil18']['C'+str(C_gate)+ '_Ren_extra_phase_correction_list'][C_msmt] = 0.
				#measure
				Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC' +str(C_gate)+ '_measC' + str(C_msmt), C_measured = C_msmt, C_gate = C_gate, debug = debug)

				phi0,u_phi_0, Amp, u_Amp = 	cr.Carbon_Ramsey(timestamp=None, 
				                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
				                       frequency = 1/360., phase =0, 
				                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
				       	            return_phase = True,
				       	            return_amp = True,
						            return_results = False,						title = 'phase_cal_gateC' + str(C_gate) +'_measC' + str(C_msmt))
				#update
				if Amp > 0:
					qt.exp_params['samples']['111_1_sil18']['C'+str(C_gate)+ '_Ren_extra_phase_correction_list'][C_msmt] = phi0
				elif Amp < 0:
				 	qt.exp_params['samples']['111_1_sil18']['C'+str(C_gate)+ '_Ren_extra_phase_correction_list'][C_msmt] = phi0+180.
				print 'C'+str(C_gate) +'_Ren_extra_phase_correction_list['+ str(C_msmt)+']'
				print qt.exp_params['samples']['111_1_sil18']['C' + str(C_gate) + '_Ren_extra_phase_correction_list'][C_msmt]
				print '--------------------------------'
				print 'press q to stop measurement loop'
				print '--------------------------------'
				qt.msleep(5)
				if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
				    n = 0
#################################
###### Print final results ######
#################################
print 
print 'Finished C13 calibration measurements'
print 'Values found:'
print
if cal_f_ms1:
	for C_msmt in Carbon_list_ms1:
		print 'C' + str(C_msmt) + '_freq_1'
		print qt.exp_params['samples']['111_1_sil18']['C' + str(C_msmt) + '_freq_1']

print

if cal_f_ms0:
	for C_msmt in Carbon_list_ms0:
		print 'C' + str(C_msmt) + '_freq_0'
		print qt.exp_params['samples']['111_1_sil18']['C' + str(C_msmt) + '_freq_0']

print

if cal_self_phase:
	for C_msmt in Carbon_list_selfphase:
		print 'C' + str(C_msmt) + '_Ren_extra_phase_correction_list[' + str(C_msmt) + ']'
		print qt.exp_params['samples']['111_1_sil18']['C' + str(C_msmt) + '_Ren_extra_phase_correction_list'][C_msmt]

print

if cal_crossphase:
	for C_gate in Carbon_list_crossphase:
		for C_msmt in Carbon_list_crossphase:
			if C_gate != C_msmt:
				print 'C'+str(C_gate) +'_Ren_extra_phase_correction_list['+ str(C_msmt)+']'
				print qt.exp_params['samples']['111_1_sil18']['C'+str(C_gate) +'_Ren_extra_phase_correction_list'][C_msmt]

All_carbons = list(set(Carbon_list_ms1 + Carbon_list_ms0 + Carbon_list_selfphase + Carbon_list_crossphase))

for C_gate in All_carbons:
	C_msmt = C_gate
	print
	if C_msmt in Carbon_list_ms0:
		print 'C' + str(C_msmt) + '_freq_0', qt.exp_params['samples']['111_1_sil18']['C' + str(C_msmt) + '_freq_0']
	if C_msmt in Carbon_list_ms1:
		print 'C' + str(C_msmt) + '_freq_1', qt.exp_params['samples']['111_1_sil18']['C' + str(C_msmt) + '_freq_1']
	for C_msmt in list(set(Carbon_list_selfphase + Carbon_list_crossphase)):
		print 'C'+str(C_gate) +'_Ren_extra_phase_correction_list['+ str(C_msmt)+']', qt.exp_params['samples']['111_1_sil18']['C'+str(C_gate) +'_Ren_extra_phase_correction_list'][C_msmt]
