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

Carbon_1_f_ms0  		= False
Carbon_2_f_ms0  		= False
Carbon_5_f_ms0  		= False

Carbon_3_f_ms0  		= False
Carbon_6_f_ms0  		= False

Carbon_1_f_msm1  		= False
Carbon_2_f_msm1  		= False
Carbon_5_f_msm1  		= False

Carbon_3_f_msm1  		= False
Carbon_6_f_msm1  		= False


Carbon_1_self_phase		= False
Carbon_2_self_phase		= False
Carbon_5_self_phase		= False

Carbon_3_self_phase		= False
Carbon_6_self_phase		= False

Carbon_1to2_crosstalk	= False
Carbon_1to5_crosstalk	= False
Carbon_2to1_crosstalk	= False
Carbon_2to5_crosstalk	= False
Carbon_5to1_crosstalk	= False
Carbon_5to2_crosstalk	= False

Carbon_phase_cal_1to2	= False
Carbon_phase_cal_1to5	= False
Carbon_phase_cal_2to1	= False
Carbon_phase_cal_2to5	= False
Carbon_phase_cal_5to1	= False
Carbon_phase_cal_5to2	= False

Carbon_phase_cal_1to3	= False
Carbon_phase_cal_3to1	= False
Carbon_phase_cal_1to3	= False
Carbon_phase_cal_3to1	= False
Carbon_phase_cal_1to6	= True
Carbon_phase_cal_6to1	= True

debug 					= False

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
    m.params['reps_per_ROsequence'] = 200
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
    
    m.params['reps_per_ROsequence'] = 500 
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
    
    m.params['reps_per_ROsequence'] = 300 
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
print 'Calibrate ms=-1 frequencies for all 3 carbon spins'

qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 100
qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 100
qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 0*15e-9

if n == 1 and (Carbon_1_f_msm1 or Carbon_2_f_msm1 or Carbon_3_f_msm1 or Carbon_5_f_msm1 or Carbon_6_f_msm1):	
	GreenAOM.set_power(25e-6)
	adwin.start_set_dio(dio_no=4,dio_val=0)
	optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
	adwin.start_set_dio(dio_no=4,dio_val=0)

detuning = 0.44e3
# measure
if n == 1 and Carbon_1_f_msm1:
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C1', carbon_nr= 1, detuning = detuning, el_state = 1)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.3, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'msm1_freq_C1')
	#update
	qt.exp_params['samples']['111_1_sil18']['C1_freq_1'] += -f0 + detuning
	print 'C1_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C1_freq_1']

	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if msvcrt.kbhit() and msvcrt.getch() == 'q':
		n = 0
	# 
if n == 1 and Carbon_2_f_msm1:

	#measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C2', carbon_nr= 2, detuning = detuning, el_state = 1)
	# fit
	f0,uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.3, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'msm1_freq_C2')
	#update
	qt.exp_params['samples']['111_1_sil18']['C2_freq_1'] += -f0 + detuning
	print 'C2_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C2_freq_1']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0
	# 

if n == 1 and Carbon_3_f_msm1:
	#measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C3', carbon_nr= 3, detuning = detuning*2.2, el_state = 1)
	# fit
	f0,uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.3, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning*2.2, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'msm1_freq_C3')
	#update
	qt.exp_params['samples']['111_1_sil18']['C3_freq_1'] += -f0 + detuning*2.2
	print 'C3_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C3_freq_1']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0


if n == 1 and Carbon_5_f_msm1:
	#measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C5', carbon_nr= 5, detuning = detuning, el_state = 1)
	# fit
	f0,uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.3, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'msm1_freq_C5')
	#update
	qt.exp_params['samples']['111_1_sil18']['C5_freq_1'] += -f0 + detuning
	print 'C5_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C5_freq_1']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_6_f_msm1:
	#measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C6', carbon_nr= 6, detuning = detuning*2.8, el_state = 1)
	# fit
	f0,uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.3, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning*2.8, phase =0, 
	              plot_fit = True, show_guess = False, fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'msm1_freq_C6')
	#update
	qt.exp_params['samples']['111_1_sil18']['C6_freq_1'] += -f0 + detuning*2.8
	print 'C6_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C6_freq_1']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and (Carbon_1_f_ms0 or Carbon_2_f_ms0 or Carbon_3_f_ms0 or Carbon_5_f_ms0 or Carbon_6_f_ms0):	
	GreenAOM.set_power(25e-6)
	adwin.start_set_dio(dio_no=4,dio_val=0)
	optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
	adwin.start_set_dio(dio_no=4,dio_val=0)

###############################################################
###### Calibrate ms=0 frequencies for all 3 carbon spins ######
###############################################################
if n == 1 and Carbon_1_f_ms0:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate ms=0 frequencies for all 3 carbon spins '
	# measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm0_freq_C1', carbon_nr= 1, 
						detuning = detuning, el_state = 0)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = '_msm0_freq_C1')
	#update
	qt.exp_params['samples']['111_1_sil18']['C1_freq_0'] += -f0 + detuning
	print 'C1_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C1_freq_0']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_2_f_ms0:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate ms=0 frequencies for all 3 carbon spins '
	# measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm0_freq_C2', carbon_nr= 2, 
						detuning = detuning, el_state = 0)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = '_msm0_freq_C2')
	#update
	qt.exp_params['samples']['111_1_sil18']['C2_freq_0'] += -f0 + detuning
	print 'C2_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C2_freq_0']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_3_f_ms0:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 230
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate ms=0 frequencies for all 3 carbon spins '
	# measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm0_freq_C3', carbon_nr= 3, 
						detuning = detuning*2.2, el_state = 0)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning*2.2, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = '_msm0_freq_C3')
	#update
	qt.exp_params['samples']['111_1_sil18']['C3_freq_0'] += -f0 + detuning*2.2
	print 'C3_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C3_freq_0']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_5_f_ms0:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate ms=0 frequencies for all 3 carbon spins '
	# measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm0_freq_C5', carbon_nr= 5, 
						detuning = detuning, el_state = 0)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = '_msm0_freq_C5')
	#update
	qt.exp_params['samples']['111_1_sil18']['C5_freq_0'] += -f0 + detuning
	print 'C5_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C5_freq_0']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_6_f_ms0:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate ms=0 frequencies for all 3 carbon spins '
	# measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm0_freq_C6', carbon_nr= 6, 
						detuning = detuning*2.8, el_state = 0)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning*2.8, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = '_msm0_freq_C6')
	#update
	qt.exp_params['samples']['111_1_sil18']['C6_freq_0'] += -f0 + detuning*2.8
	print 'C6_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C6_freq_0']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0


if n == 1:
##################################################################
##### Calibrate extra phase for gate for all 3 carbon spins ######
#################################################################
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	
	print 'Calibrate extra phase for gate for all 3 carbon spins'

	#set all to zero to start with
	if (Carbon_1_self_phase or Carbon_2_self_phase or Carbon_3_self_phase or Carbon_5_self_phase or Carbon_6_self_phase):
		GreenAOM.set_power(25e-6)
		adwin.start_set_dio(dio_no=4,dio_val=0)
		optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
		adwin.start_set_dio(dio_no=4,dio_val=0)

if n == 1 and Carbon_1_self_phase:
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1] = 0
	# measure
	NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C1', carbon_nr= 1)
	# fit
	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,						title = 'phase_C1')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1] = phi0
# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1] = phi0+180
	print 'C1_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_2_self_phase:	
	#measure
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2] = 0
	NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C2', carbon_nr= 2)

	# fit
	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,
						title = 'phase_C2')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2] = phi0 + 180.
	# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2] = phi0+180
	print 'C2_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0


#Added by Michiel
if n == 1 and Carbon_3_self_phase:
	qt.exp_params['samples']['111_1_sil18']['C3_Ren_extra_phase_correction_list'][3] = 0
	#measure
	NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C3', carbon_nr= 3)
	# fit
	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,
						title = 'phase_C3')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C3_Ren_extra_phase_correction_list'][3] = phi0
	# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5] = phi0+180
	print 'C5_Ren_extra_phase_correction_list[3]'
	print qt.exp_params['samples']['111_1_sil18']['C3_Ren_extra_phase_correction_list'][5]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0



if n == 1 and Carbon_5_self_phase:
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5] = 0
	#measure
	NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C5', carbon_nr= 5)
	# fit
	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,
						title = 'phase_C5')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5] = phi0
	# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5] = phi0+180
	print 'C5_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_6_self_phase:
	qt.exp_params['samples']['111_1_sil18']['C6_Ren_extra_phase_correction_list'][6] = 0
	#measure
	NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C6', carbon_nr= 6, nr_of_pts = 21)
	# fit
	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,
						title = 'phase_C6')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C6_Ren_extra_phase_correction_list'][6] = phi0
	# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C6_Ren_extra_phase_correction_list'][6] = phi0+180
	print 'C6_Ren_extra_phase_correction_list[6]'
	print qt.exp_params['samples']['111_1_sil18']['C6_Ren_extra_phase_correction_list'][6]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0
#################################################################
###### Calibrate crosstalk for gate for all 3 carbon spins ######
#################################################################
print 'Calibrate crosstalk for gate for all 3 carbon spins'

#set all to zero to start with
qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2] = 0
qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5] = 0
qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1] = 0
qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5] = 0
qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1] = 0
qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2] = 0

# if n == 1:	
# 	GreenAOM.set_power(25e-6)
# 	adwin.start_set_dio(dio_no=4,dio_val=0)
# 	optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
# 	adwin.start_set_dio(dio_no=4,dio_val=0)

if n == 1 and Carbon_2to1_crosstalk:
	# measure
	Crosstalk(SAMPLE+ '_Crosstalk_gateC2_measC1', C_measured = 1, C_gate = 2, RO_phase=90, RO_Z=False, C13_init_method = 'MBI', debug = debug)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/127., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC2_measC1')
	#update
	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C2_Ren_N'][0]
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1] = abs(f0)*nr_of_pulses*360
	print 'C2_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_5to1_crosstalk:
	#measure
	Crosstalk(SAMPLE+ '_Crosstalk_gateC5_measC1', C_measured = 1, C_gate = 5, RO_phase=90, RO_Z=False, C13_init_method = 'MBI', debug = debug)
		# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/160., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC5_measC1')

	#update
	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C5_Ren_N'][0]
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1] = abs(f0)*nr_of_pulses*360
	print 'C5_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0


if n == 1 and Carbon_1to2_crosstalk:
	#measure
	Crosstalk(SAMPLE+ '_Crosstalk_gateC1_measC2', C_measured = 2, C_gate = 1, RO_phase=90, 
		RO_Z=False, C13_init_method = 'MBI', debug = debug, N_list = np.arange(4,600,72))
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/462., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC1_measC2')

	#update
	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C1_Ren_N'][0]
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2] = abs(f0)*nr_of_pulses*360
	print 'C1_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_5to2_crosstalk:
	# measure
	Crosstalk(SAMPLE+ '_Crosstalk_gateC5_measC2', C_measured = 2, C_gate = 5, RO_phase=90, RO_Z=False, C13_init_method = 'MBI', debug = debug)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/160., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC5_measC2')

	#update
	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C5_Ren_N'][0]
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2] = abs(f0)*nr_of_pulses*360
	print 'C5_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_1to5_crosstalk:
	#measure
	Crosstalk(SAMPLE+ '_Crosstalk_gateC1_measC5', C_measured = 5, C_gate = 1, RO_phase=90, RO_Z=False, C13_init_method = 'MBI', debug = debug)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/177., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC1_measC5')

	#update
	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C1_Ren_N'][0]
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5] = abs(f0)*nr_of_pulses*360
	print 'C1_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1 and Carbon_2to5_crosstalk:
	#measure
	Crosstalk(SAMPLE+ '_Crosstalk_gateC2_measC5', C_measured = 5, C_gate = 2, RO_phase=90, RO_Z=False, C13_init_method = 'MBI',N_list = np.arange(4,160,12), debug = debug)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/90., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC2_measC5')

	#update
	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C2_Ren_N'][0]
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5] = abs(f0)*nr_of_pulses*360
	print 'C2_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5]

if n == 1 and Carbon_phase_cal_2to1:
	#measure
	Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC2_measC1', C_measured = 1, C_gate =2 ,debug = debug)

	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,
						title = 'phase_cal_gateC2_measC1')
	#update
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1] = phi0
	print 'C2_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1]

########################
########################
########################

if n == 1:	
	GreenAOM.set_power(25e-6)
	adwin.start_set_dio(dio_no=4,dio_val=0)
	optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
	adwin.start_set_dio(dio_no=4,dio_val=0)

if n == 1 and Carbon_phase_cal_5to1:
	#measure
	Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC5_measC1', C_measured = 1, C_gate =5 ,debug = debug)

	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,
						title = 'phase_cal_gateC5_measC1')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1] = phi0
	# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1] = phi0+180
	print 'C5_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1]

if n == 1 and Carbon_phase_cal_1to2:
	#measure
	Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC1_measC2', C_measured = 2, C_gate =1 ,debug = debug)

	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,						title = 'phase_cal_gateC1_measC2')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2] = phi0
# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2] = phi0+180
	print 'C1_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2]

if n == 1 and Carbon_phase_cal_5to2:
	#measure
	Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC5_measC2', C_measured = 2, C_gate =5 ,debug = debug)

	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,						title = 'phase_cal_gateC5_measC2')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2] = phi0
# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2] = phi0+180
	print 'C5_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2]


if n == 1 and Carbon_phase_cal_1to5:
	#measure
	Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC1_measC5', C_measured = 5, C_gate = 1, debug = debug)

	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,						title = 'phase_cal_gateC1_measC5')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5] = phi0
# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5] = phi0+180
	print 'C1_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5]

if n == 1 and Carbon_phase_cal_2to5:
	#measure
	Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC2_measC5', C_measured = 5, C_gate = 2, debug = debug)

	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,						title = 'phase_cal_gateC2_measC5')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5] = phi0
# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5] = phi0+180
	print 'C2_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5]

if n == 1 and Carbon_phase_cal_1to6:
	#measure
	Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC1_measC6', C_measured = 6, C_gate = 1, debug = debug)

	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,						title = 'phase_cal_gateC1_measC6')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][6] = phi0
# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][6] = phi0+180
	print 'C1_Ren_extra_phase_correction_list[6]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][6]


if n == 1 and Carbon_phase_cal_6to1:
	#measure
	Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC6_measC1', C_measured = 1, C_gate = 6, debug = debug)

	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,						title = 'phase_cal_gateC6_measC1')
	#update
	# if A > 0:
	qt.exp_params['samples']['111_1_sil18']['C6_Ren_extra_phase_correction_list'][1] = phi0
# elif A < 0:
	# 	qt.exp_params['samples']['111_1_sil18']['C6_Ren_extra_phase_correction_list'][1] = phi0+180
	print 'C6_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C6_Ren_extra_phase_correction_list'][1]

#################################
###### Print final results ######
#################################
print 
print 'Finished C13 calibration measurements'
print 'Values found:'
print

if Carbon_1_f_msm1:
	print 'C1_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C1_freq_1']
if Carbon_2_f_msm1:
	print 'C2_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C2_freq_1']
if Carbon_3_f_msm1:
	print 'C3_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C3_freq_1']
if Carbon_5_f_msm1:
	print 'C5_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C5_freq_1']
if Carbon_6_f_msm1:
	print 'C6_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C6_freq_1']	

print

if Carbon_1_f_ms0:
	print 'C1_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C1_freq_0']
if Carbon_2_f_ms0:
	print 'C2_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C2_freq_0']
if Carbon_3_f_ms0:
	print 'C3_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C3_freq_0']
if Carbon_5_f_ms0:
	print 'C5_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C5_freq_0']
if Carbon_6_f_ms0:
	print 'C6_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C6_freq_0']

print
if Carbon_1_self_phase:
	print 'C1_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1]
if Carbon_2_self_phase:
	print 'C2_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2]
if Carbon_3_self_phase:
	print 'C3_Ren_extra_phase_correction_list[3]'
	print qt.exp_params['samples']['111_1_sil18']['C3_Ren_extra_phase_correction_list'][3]
if Carbon_5_self_phase:
	print 'C5_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5]
if Carbon_6_self_phase:
	print 'C6_Ren_extra_phase_correction_list[6]'
	print qt.exp_params['samples']['111_1_sil18']['C6_Ren_extra_phase_correction_list'][6]
print

if Carbon_phase_cal_2to1:
	print 'C2_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1]
if Carbon_phase_cal_5to1:
	print 'C5_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1]
if Carbon_phase_cal_1to2:
	print 'C1_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2]
if Carbon_phase_cal_5to2:
	print 'C5_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2]
if Carbon_phase_cal_1to5:
	print 'C1_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5]
if Carbon_phase_cal_2to5:
	print 'C2_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5]
if Carbon_phase_cal_1to5:
	print 'C1_Ren_extra_phase_correction_list[6]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][6]
if Carbon_phase_cal_6to1:
	print 'C6_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C6_Ren_extra_phase_correction_list'][1]

