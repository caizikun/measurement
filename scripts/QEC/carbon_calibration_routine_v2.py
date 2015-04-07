''' Measurement set to calibrate the evolution frequencies for the different carbon spins 
plus the phases they pick up during carbon gates'''

import io,sys
import numpy as np
import qt
import msvcrt
from analysis.scripts.QEC import carbon_ramsey_analysis as cr 
reload(cr)

# execfile(qt.reload_current_setup)

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

carbons = [1,5]

#######################################################
######      Set the tasks you want performed     ######
#######################################################

"""
The crosstalk option has been excluded from this script, since every fit needs its own frequency.
Therefore the modularity is not increased.
(But it might be increased by finding stable input parameters for the fits for certain carbon combinations.)

AFTER THE CALIBRATION IS DONE:

The measured values are directly written into msmt_params.py
"""

f_ms0 = True

f_ms1 = True

#c_cross_talk = True ### Not in use yet.

self_phase_calibration = True

cross_phase_calibration = True

debug = False

with open(r'D:/measuring/measurement/scripts/lt2_scripts/setup/msmt_params.py','r') as param_file:
    dataTest = param_file.readlines()

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
        debug               = False):

    m = DD.NuclearRamseyWithInitialization_v2(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 200
    m.params['C13_MBI_RO_state'] = el_state
    
    
    m.params['pts'] = 24
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


def write_to_msmt_params(carbons,f_ms0,f_ms1,self_phase,cross_phase,debug):

    """
    This routine automatically takes the measured values and writes them to the measurement parameters.
    Takes a list of carbons as input and the booleans which decode which calibrations have been done.
    """

    if not debug:
        with open(r'D:/measuring/measurement/scripts/lt2_scripts/setup/msmt_params.py','r') as param_file:
            data = param_file.readlines()

        for c in carbons:
            if f_ms0:

                search_string = 'C'+str(c)+'_freq_0'
                data = write_to_file_subroutine(data,search_string)

            if f_ms1:

                search_string = 'C'+str(c)+'_freq_1'
                data = write_to_file_subroutine(data,search_string)

            if self_phase or cross_phase:

                search_string = 'C'+str(c)+'_Ren_extra_phase_correction_list'
                data = write_to_file_subroutine(data,search_string)


        ### after compiling the new msmt_params, the are flushed to the python file.
        f = open(r'D:/measuring/measurement/scripts/lt2_scripts/setup/msmt_params.py','w')
        f.writelines(data)
        f.close()


def write_to_file_subroutine(data,search_string):
    """
    Takes a list of read file lines and a search string.
    Scans the file for uncommented lines with this specific string in it.
    It is assumed that the string occurs within the dictionary part of msmt_params.
    Beware: Will delete any comments attached to the specific parameter.
    """
    params = qt.exp_params['samples']['111_1_sil18'][search_string]

    for ii,x in enumerate(data):
        if search_string in x and not '#' in x[:5]:

            ### detect if we must write a list to the msmt_params or an integer
            if type(params) == list or type(params) == np.ndarray:
                array_string = 'np.array('

                for i,phi in enumerate(params):
                    if i+1 == len(params):
                        array_string += '['+str(round(phi,2))+']),\n'

                    else:
                        array_string += '['+str(round(phi,2))+'] + '

            else:
                array_string = str(round(params,2))+',\n'

            fill_in = x[:len(search_string)+2] + ' : ' + array_string

            # print fill_in
            data[ii] = fill_in

        ### we have reached the parameters for the wrong NV center.
        if ii>400 and 'Hans' in x:
            break
    ### return the contents of msmt_params.py
    return data

            
            

################################################################
###### 				Calibrate ms=-1 frequencies 	      ######
################################################################
print 'Calibrate ms=-1 frequencies for all 3 carbon spins'

qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 100
qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 100
qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 0*15e-9


detuning = 0.44e3
# measure
if f_ms1 and n == 1:

	for c in carbons:

		if n == 1:

			NuclearRamseyWithInitialization_cal(SAMPLE+'_msm1_freq_C'+str(c), carbon_nr= c, detuning = detuning, el_state = 1)
			# fit
			f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
			              offset = 0.5, amplitude = 0.3, x0=0, decay_constant = 1e5, exponent = 2, 
			              frequency = detuning, phase =0, 
			              plot_fit = True, show_guess = False,fixed = [2,3,4],            
			              return_freq = True,
			              return_results = False,
			              title = 'msm1_freq_C'+str(c))
			#update
			qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_freq_1'] += -f0 + detuning
			print 'press q to stop measurement loop'
			print '--------------------------------'
			qt.msleep(5)
			if msvcrt.kbhit() and msvcrt.getch() == 'q':
				n = 0
	
	
###############################################################
###### 				Calibrate ms=0 frequencies 	 		 ######
###############################################################
if n == 1 and f_ms0:
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	print 'Calibrate ms=0 frequencies'
	# measure
	for c in carbons:
		if n == 1:
			NuclearRamseyWithInitialization_cal(SAMPLE+'_msm0_freq_C'+str(c), carbon_nr= c, 
								detuning = detuning, el_state = 0)
			# fit
			f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
			              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
			              frequency = detuning, phase =0, 
			              plot_fit = True, show_guess = False,fixed = [2,3,4],            
			              return_freq = True,
			              return_results = False,
			              title = '_msm0_freq_C'+str(c))
			#update
			qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_freq_0'] += -f0 + detuning
			print 'C'+str(c)+'_freq_0'
			print qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_freq_0']
			print '--------------------------------'
			print 'press q to stop measurement loop'
			print '--------------------------------'
			qt.msleep(5)
			if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
			    n = 0

##################################################################
##### Calibrate extra phase for gate for all 3 carbon spins ######
#################################################################
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
	qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
	
	print 'Calibrate extra phase for gate for all 3 carbon spins'

	#set all to zero to start with


if n == 1 and self_phase_calibration:
	for c in carbons:
		if n == 1:
			qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_Ren_extra_phase_correction_list'][c] = 0
			# measure
			NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C'+str(c), carbon_nr= c)
			# fit
			phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
			                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
			                       frequency = 1/360., phase =0, 
			                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
			       	            return_phase = True,
					            return_results = False,						title = 'phase_C'+str(c))
			#update
			# if A > 0:
			#### hot fix for the phase correction. carbons which show wrong fit results can be added manually by expanding the list below.
			if c in [2]:
				qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_Ren_extra_phase_correction_list'][c] = phi0+180
			else:
				qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_Ren_extra_phase_correction_list'][c] = phi0
		# elif A < 0:
			# 	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][1] = phi0+180
			print 'C'+str(c)+'_Ren_extra_phase_correction_list['+str(c)+']'
			print qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_Ren_extra_phase_correction_list'][c]
			print '--------------------------------'
			print 'press q to stop measurement loop'
			print '--------------------------------'
			qt.msleep(5)
			if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
			    n = 0

#################################################################
###### Calibrate crosstalk for gate for all 3 carbon spins ######
#################################################################
# print 'Calibrate crosstalk for gate for all 3 carbon spins'

"""
The crosstalk option has been excluded from this script, since every fit needs its own frequency.
Therefore the modularity is not increased.
(But it might be increased by finding stable input parameters for the fits for certain carbon combinations.)
"""

# if n == 1 and Carbon_2to1_crosstalk:
# 	# measure
# 	Crosstalk(SAMPLE+ '_Crosstalk_gateC2_measC1', C_measured = 1, C_gate = 2, RO_phase=90, RO_Z=False, C13_init_method = 'MBI', debug = debug)
# 	# fit
# 	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
# 	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
# 	              frequency = 1/127., phase =0, 
# 	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
# 	              return_freq = True,
# 	              return_results = False,
# 	              title = 'Crosstalk_gateC2_measC1')
# 	#update
# 	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C2_Ren_N'][0]
# 	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1] = abs(f0)*nr_of_pulses*360
# 	print 'C2_Ren_extra_phase_correction_list[1]'
# 	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][1]
# 	print '--------------------------------'
# 	print 'press q to stop measurement loop'
# 	print '--------------------------------'
# 	qt.msleep(5)
# 	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
# 	    n = 0

# if n == 1 and Carbon_5to1_crosstalk:
# 	#measure
# 	Crosstalk(SAMPLE+ '_Crosstalk_gateC5_measC1', C_measured = 1, C_gate = 5, RO_phase=90, RO_Z=False, C13_init_method = 'MBI', debug = debug)
# 		# fit
# 	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
# 	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
# 	              frequency = 1/160., phase =0, 
# 	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
# 	              return_freq = True,
# 	              return_results = False,
# 	              title = 'Crosstalk_gateC5_measC1')

# 	#update
# 	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C5_Ren_N'][0]
# 	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1] = abs(f0)*nr_of_pulses*360
# 	print 'C5_Ren_extra_phase_correction_list[1]'
# 	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][1]
# 	print '--------------------------------'
# 	print 'press q to stop measurement loop'
# 	print '--------------------------------'
# 	qt.msleep(5)
# 	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
# 	    n = 0


# if n == 1 and Carbon_1to2_crosstalk:
# 	#measure
# 	Crosstalk(SAMPLE+ '_Crosstalk_gateC1_measC2', C_measured = 2, C_gate = 1, RO_phase=90, 
# 		RO_Z=False, C13_init_method = 'MBI', debug = debug, N_list = np.arange(4,600,72))
# 	# fit
# 	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
# 	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
# 	              frequency = 1/462., phase =0, 
# 	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
# 	              return_freq = True,
# 	              return_results = False,
# 	              title = 'Crosstalk_gateC1_measC2')

# 	#update
# 	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C1_Ren_N'][0]
# 	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2] = abs(f0)*nr_of_pulses*360
# 	print 'C1_Ren_extra_phase_correction_list[2]'
# 	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][2]
# 	print '--------------------------------'
# 	print 'press q to stop measurement loop'
# 	print '--------------------------------'
# 	qt.msleep(5)
# 	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
# 	    n = 0

# if n == 1 and Carbon_5to2_crosstalk:
# 	# measure
# 	Crosstalk(SAMPLE+ '_Crosstalk_gateC5_measC2', C_measured = 2, C_gate = 5, RO_phase=90, RO_Z=False, C13_init_method = 'MBI', debug = debug)
# 	# fit
# 	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
# 	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
# 	              frequency = 1/160., phase =0, 
# 	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
# 	              return_freq = True,
# 	              return_results = False,
# 	              title = 'Crosstalk_gateC5_measC2')

# 	#update
# 	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C5_Ren_N'][0]
# 	qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2] = abs(f0)*nr_of_pulses*360
# 	print 'C5_Ren_extra_phase_correction_list[2]'
# 	print qt.exp_params['samples']['111_1_sil18']['C5_Ren_extra_phase_correction_list'][2]
# 	print '--------------------------------'
# 	print 'press q to stop measurement loop'
# 	print '--------------------------------'
# 	qt.msleep(5)
# 	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
# 	    n = 0

# if n == 1 and Carbon_1to5_crosstalk:
# 	#measure
# 	Crosstalk(SAMPLE+ '_Crosstalk_gateC1_measC5', C_measured = 5, C_gate = 1, RO_phase=90, RO_Z=False, C13_init_method = 'MBI', debug = debug)
# 	# fit
# 	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
# 	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
# 	              frequency = 1/177., phase =0, 
# 	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
# 	              return_freq = True,
# 	              return_results = False,
# 	              title = 'Crosstalk_gateC1_measC5')

# 	#update
# 	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C1_Ren_N'][0]
# 	qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5] = abs(f0)*nr_of_pulses*360
# 	print 'C1_Ren_extra_phase_correction_list[5]'
# 	print qt.exp_params['samples']['111_1_sil18']['C1_Ren_extra_phase_correction_list'][5]
# 	print '--------------------------------'
# 	print 'press q to stop measurement loop'
# 	print '--------------------------------'
# 	qt.msleep(5)
# 	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
# 	    n = 0

# if n == 1 and Carbon_2to5_crosstalk:
# 	#measure
# 	Crosstalk(SAMPLE+ '_Crosstalk_gateC2_measC5', C_measured = 5, C_gate = 2, RO_phase=90, RO_Z=False, C13_init_method = 'MBI',N_list = np.arange(4,160,12), debug = debug)
# 	# fit
# 	f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
# 	              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
# 	              frequency = 1/90., phase =0, 
# 	              plot_fit = True, show_guess = False,fixed = [2,3,4],            
# 	              return_freq = True,
# 	              return_results = False,
# 	              title = 'Crosstalk_gateC2_measC5')

# 	#update
# 	nr_of_pulses = qt.exp_params['samples']['111_1_sil18']['C2_Ren_N'][0]
# 	qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5] = abs(f0)*nr_of_pulses*360
# 	print 'C2_Ren_extra_phase_correction_list[5]'
# 	print qt.exp_params['samples']['111_1_sil18']['C2_Ren_extra_phase_correction_list'][5]

########################
########################
########################

if cross_phase_calibration and n ==1:
    #set all cross-phases to zero to start with
    for c in carbons:
    	# remove that specific carbon from the list
    	carbons_cross = carbons
    	carbons_cross.remove(c)
    	# reset phases to 0
    	for c_cross in carbons_cross:
    		qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_Ren_extra_phase_correction_list'][c_cross] = 0.

if n == 1 and cross_phase_calibration and len(carbons)>1:
	for c in carbons:
		# remove that specific carbon from the list
		carbons_cross = carbons
		carbons_cross.remove(c)
		for cross_c in carbons_cross:

			#measure
			Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC'+str(cross_c)+'_measC'+str(c), C_measured = c, C_gate =cross_c ,debug = debug)

			phi0,u_phi_0 = 	cr.Carbon_Ramsey(timestamp=None, 
			                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
			                       frequency = 1/360., phase =0, 
			                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
			       	            return_phase = True,
					            return_results = False,
								title = 'phase_cal_gateC'+str(cross_c)+'_measC'+str(c))
			#update
			qt.exp_params['samples']['111_1_sil18']['C'+str(cross_c)+'_Ren_extra_phase_correction_list'][c] = phi0
			print 'C'+str(cross_c)+'_Ren_extra_phase_correction_list['+str(c)+']'
			print qt.exp_params['samples']['111_1_sil18']['C'+str(cross_c)+'_Ren_extra_phase_correction_list'][c]

#################################
###### Print final results ######
#################################
print 
print 'Finished C13 calibration measurements'
print 'Values found:'
print

if f_ms1:
	print '#########################'
	print 'ms = 1 frequencies'
	for c in carbons:
		print 'Carbon '+str(c)
		print qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_freq_1']
	print
	print '#########################'

print

if f_ms0:
	print '#########################'
	print 'ms = 0 frequencies'
	print
	for c in carbons:
		print 'Carbon '+str(c)
		print qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_freq_0']
	print
	print '#########################'
print

if self_phase_calibration:
	print '#########################'
	print 'self phases'
	print
	for c in carbons:
		print 'C'+str(c)+'_Ren_extra_phase_correction_list['+str(c)+']'
		print qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_Ren_extra_phase_correction_list'][c]
	print
	print '#########################'
print

if cross_phase_calibration and len(carbons)>1:
	print '#########################'
	print 'cross phases'
	print
	for c in carbons:
		carbons_cross = carbons
		carbons_cross.remove(c)
		for cross_c in carbons_cross:
			print 'C'+str(c)+'_Ren_extra_phase_correction_list['+str(cross_c)+']'
			print qt.exp_params['samples']['111_1_sil18']['C'+str(c)+'_Ren_extra_phase_correction_list'][cross_c]


write_to_msmt_params(carbons,f_ms0,f_ms1,self_phase_calibration,cross_phase_calibration,debug)