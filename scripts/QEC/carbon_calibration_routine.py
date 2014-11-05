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

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    funcs.finish(m, upload =True, debug=False)

def NuclearRamseyWithInitialization_phase(name, 
        carbon_nr           = 1,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        el_state            = 0,
        debug               = False):

    m = DD.NuclearRamseyWithInitialization_v2(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500
    m.params['C13_MBI_RO_state'] = el_state
    
    
    m.params['pts'] = 21
    m.params['add_wait_gate'] = False
    m.params['free_evolution_time'] = np.ones(m.params['pts'] )*360e-6
    m.params['C_RO_phase'] = np.linspace(-20, 400,m.params['pts'])    

    m.params['sweep_name'] = 'phase'
    m.params['sweep_pts']  = m.params['C_RO_phase']

    '''Derived and fixed parameters'''

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

  
    funcs.finish(m, upload =True, debug=debug)


def Crosstalk(name, C_measured = 5, C_gate = 1, RO_phase=0, RO_Z=False, C13_init_method = 'MBI'):
    m = DD.Crosstalk(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['Carbon_A'] = C_measured    ### Carbon spin that the Ramsey is performed on
    m.params['Carbon_B'] = C_gate        ### Carbon spin that the Rabi/Gate is performed on
    
    m.params['reps_per_ROsequence'] = 500 
    m.params['C13_init_state']      = 'up' 
    m.params['C13_init_method']     = C13_init_method
    m.params['sweep_name']          = 'Number of pulses'
    m.params['C_RO_phase']          = RO_phase 
    m.params['C_RO_Z']              = RO_Z 
    
    ### Pulse spacing (overwrite tau to test other DD times)
    
    #m.params['C4_Ren_tau'] = [6.456e-6]            
    #m.params['C4_Ren_tau'] = [3.072e-6]
    #m.params['C1_Ren_tau'] = [9.420e-6]

    ### Sweep parameters
    m.params['Rabi_N_Sweep']= np.arange(4,300,24)
    m.params['pts'] = len(m.params['Rabi_N_Sweep']) 
    m.params['sweep_pts'] = m.params['Rabi_N_Sweep']


   
    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0 
    
    funcs.finish(m, upload =True, debug=False)


################################################################
###### Calibrate ms=-1 frequencies for all 3 carbon spins ######
################################################################
print 'Calibrate ms=-1 frequencies for all 3 carbon spins'

qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 100
qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 100
qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 0*15e-9


detuning = 0.5e3
# measure
NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C1', carbon_nr= 1, detuning = detuning, el_state = 1)
# fit
f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
              frequency = detuning, phase =0, 
              plot_fit = True, show_guess = False,fixed = [2,3,4],            
              return_freq = True,
              return_results = False,
              title = 'msm1_freq_C1')
#update
qt.exp_params['samples']['111_1_sil18']['C1_freq_1'] += f0 - detuning
print 'C1_freq_1'
print qt.exp_params['samples']['111_1_sil18']['C1_freq_1']

print '--------------------------------'
print 'press q to stop measurement loop'
print '--------------------------------'
qt.msleep(5)
if msvcrt.kbhit() and msvcrt.getch() == 'q':
	n = 0
# 
if n == 1:

	#measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C2', carbon_nr= 2, detuning = detuning, el_state = 1)
	# fit
	f0,uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'msm1_freq_C2')
	#update
	qt.exp_params['samples']['111_1_sil18']['C2_freq_1'] += f0 - detuning
	print 'C2_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C2_freq_1']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0
	# 
if n == 1:
	#measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C5', carbon_nr= 5, detuning = detuning, el_state = 1)
	# fit
	f0,uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'msm1_freq_C5')
	#update
	qt.exp_params['samples']['111_1_sil18']['C5_freq_1'] += f0 - detuning
	print 'C5_freq_1'
	print qt.exp_params['samples']['111_1_sil18']['C5_freq_1']
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0
	
	
###############################################################
###### Calibrate ms=0 frequencies for all 3 carbon spins ######
###############################################################
if n == 1:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 30
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate ms=0 frequencies for all 3 carbon spins '
	# measure
	NuclearRamseyWithInitialization_cal(SAMPLE+'_msm0_freq', carbon_nr= 1, 
						detuning = detuning, el_state = 0)
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = detuning, phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'msm0_freq')
	#update
	qt.exp_params['samples']['111_1_sil18']['C1_freq_0'] += f0 - detuning
	qt.exp_params['samples']['111_1_sil18']['C2_freq_0'] += f0 - detuning
	qt.exp_params['samples']['111_1_sil18']['C5_freq_0'] += f0 - detuning
	print 'C_freq_0'
	print qt.exp_params['samples']['111_1_sil18']['C1_freq_0']
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
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 30
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	
	print 'Calibrate extra phase for gate for all 3 carbon spins'

	#set all to zero to start with
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1] = 0
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2] = 0
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5] = 0

	# measure
	NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C1', carbon_nr= 1)
	# fit
	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,
						title = 'phase_cal_C1')
	#update
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1] = phi0
	print 'C1_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1:	
	#measure
	NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C2', carbon_nr= 2)
	# fit
	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,
						title = 'phase_cal_C2')
	#update
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2] = phi0
	print 'C2_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1:
	#measure
	NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C5', carbon_nr= 5)
	# fit
	phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
	                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	                       frequency = 1/360., phase =0, 
	                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
	       	            return_phase = True,
			            return_results = False,
						title = 'phase_cal_C5')
	#update
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5] = phi0
	print 'C5_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1:
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

	# measure
	Crosstalk(SAMPLE+ '_gateC2_measC1', C_measured = 1, C_gate = 2, RO_phase=90, RO_Z=False, C13_init_method = 'MBI')
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/127., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC2_measC1')
	#update
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1] = f0*18*360
	print 'C2_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1:
	#measure
	Crosstalk(SAMPLE+ '_gateC5_measC1', C_measured = 1, C_gate = 5, RO_phase=90, RO_Z=False, C13_init_method = 'MBI')
		# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/160., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC5_measC1')

	#update
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1] = f0*38*360
	print 'C5_Ren_extra_phase_correction_list[1]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0


if n == 1:
	#measure
	Crosstalk(SAMPLE+ '_gateC1_measC2', C_measured = 2, C_gate = 1, RO_phase=90, RO_Z=False, C13_init_method = 'MBI')
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/462., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC1_measC2')

	#update
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2] = f0*34*360
	print 'C1_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1:
	# measure
	Crosstalk(SAMPLE+ '_gateC5_measC2', C_measured = 2, C_gate = 5, RO_phase=90, RO_Z=False, C13_init_method = 'MBI')
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/160., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC5_measC2')

	#update
	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2] = f0*38*360
	print 'C5_Ren_extra_phase_correction_list[2]'
	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1:
	#measure
	Crosstalk(SAMPLE+ '_gateC1_measC5', C_measured = 5, C_gate = 1, RO_phase=90, RO_Z=False, C13_init_method = 'MBI')
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/177., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC1_measC5')

	#update
	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5] = f0*34*360
	print 'C1_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5]
	print '--------------------------------'
	print 'press q to stop measurement loop'
	print '--------------------------------'
	qt.msleep(5)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
	    n = 0

if n == 1:
	#measure
	Crosstalk(SAMPLE+ '_gateC2_measC5', C_measured = 5, C_gate = 2, RO_phase=90, RO_Z=False, C13_init_method = 'MBI')
	# fit
	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
	              frequency = 1/90., phase =0, 
	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
	              return_freq = True,
	              return_results = False,
	              title = 'Crosstalk_gateC2_measC5')

	#update
	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5] = f0*18*360
	print 'C2_Ren_extra_phase_correction_list[5]'
	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5]

#################################
###### Print final results ######
#################################

print 'Finished C13 calibration measurements'
print 'Values found:'
print
print 'C1_freq_1'
print qt.exp_params['samples']['111_1_sil18']['C1_freq_1']
print 'C2_freq_1'
print qt.exp_params['samples']['111_1_sil18']['C2_freq_1']
print 'C5_freq_1'
print qt.exp_params['samples']['111_1_sil18']['C5_freq_1']
print
print 'C_freq_0'
print qt.exp_params['samples']['111_1_sil18']['C1_freq_0']
print
print 'C1_Ren_extra_phase_correction_list[1]'
print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1]
print 'C2_Ren_extra_phase_correction_list[2]'
print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2]
print 'C5_Ren_extra_phase_correction_list[5]'
print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5]
print
print 'C2_Ren_extra_phase_correction_list[1]'
print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1]
print 'C5_Ren_extra_phase_correction_list[1]'
print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1]
print 'C1_Ren_extra_phase_correction_list[2]'
print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2]
print 'C5_Ren_extra_phase_correction_list[2]'
print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2]
print 'C1_Ren_extra_phase_correction_list[5]'
print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5]
print 'C2_Ren_extra_phase_correction_list[5]'
print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5]


################################
###### Save final results ######
################################

qt.mstart()

d = qt.Data(name=SAMPLE_CFG+'_carbon_calibration')


d.add_coordinate('round')
d.add_value('C1_freq_1')
d.add_value('C2_freq_1')
d.add_value('C5_freq_1')
d.add_value('C_freq_0')
d.add_value('C1_Ren_extra_phase_correction_list[1]')
d.add_value('C2_Ren_extra_phase_correction_list[2]')
d.add_value('C5_Ren_extra_phase_correction_list[5]')
d.add_value('C2_Ren_extra_phase_correction_list[1]')
d.add_value('C5_Ren_extra_phase_correction_list[1]')
d.add_value('C1_Ren_extra_phase_correction_list[2]')
d.add_value( 'C5_Ren_extra_phase_correction_list[2]')
d.add_value( 'C1_Ren_extra_phase_correction_list[5]')
d.add_value( 'C2_Ren_extra_phase_correction_list[5]')

d.add_data_point([0], [qt.exp_params['samples']['111_1_sil18']['C1_freq_1']],
 [qt.exp_params['samples']['111_1_sil18']['C2_freq_1']],
 [qt.exp_params['samples']['111_1_sil18']['C5_freq_1']],
 [qt.exp_params['samples']['111_1_sil18']['C1_freq_0']],
 [qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1]],
 [qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][2]],
 [qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][5]],
 [qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1]],
 [qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1]],
 [qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2]],
  [qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2]],
  [qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5]],
  [qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5]])

d.create_file()
filename=d.get_filepath()[:-4]
d.close_file()
qt.mend()
