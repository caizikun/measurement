"""
Takes hardcoded gate parameters for one carbon and sweeps these parameters. 
Scans a large range!
Now even larger and works for a list of taus ~SK 2016

Similar to the script search_optimal_carbon_gates

NK 2015
"""

import numpy as np
import qt
import msvcrt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD
import measurement.scripts.mbi.mbi_funcs as funcs
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)
reload(funcs)
reload(DD)

ins_counters = qt.instruments['counters']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def put_sweep_together(Ns,taus):
	### put together into one sweep parameter
	px_list = ['X_'+str(Ns[i])+'_'+str(taus[i]) for i in range(len(Ns))]
	py_list = ['Y_'+str(Ns[i])+'_'+str(taus[i]) for i in range(len(Ns))]


	## having fun with slices
	com_list = px_list + py_list

	tomos = len(px_list)*['X']+len(py_list)*['Y']
	print tomos
	print com_list

	print 'len taus in put sweep together: ',len(taus) 
	print 'taus: ', taus
	print 'len Ns in put sweep together: ',len(Ns) 
	print 'Ns: ', Ns
	return com_list,np.concatenate((Ns,Ns)),np.concatenate((taus,taus)),tomos


def SweepGates(name,**kw):

	debug = kw.pop('debug',False)
	carbon = kw.pop('carbon',False)
	el_RO = kw.pop('el_RO','positive')
	tau_list = kw.pop('tau_list',None)
	N_list = kw.pop('N_list',None)


	m = DD.Sweep_Carbon_Gate(name)
	funcs.prepare(m)

	m.params['C13_MBI_threshold_list'] = [1]
	m.params['el_after_init'] = '0'



	''' set experimental parameters '''

	m.params['reps_per_ROsequence'] = 1000

	### Carbons to be used
	m.params['carbon_list']         =[carbon]

	########################################
	### Carbon Initialization settings #####
	########################################

	m.params['carbon_init_list']    = [carbon]
	m.params['init_method_list']    = ['MBI']    
	m.params['init_state_list']     = ['up']
	m.params['Nr_C13_init']         = 1


	##################################
	### RO bases,timing and number of pulses (sweep parameters) ###
	##################################

	# print m.params['electron_transition']
	if N_list == None or tau_list == None:
		# takes from msts.params
		com_list,m.params['N_list'],m.params['tau_list'],m.params['Tomography Bases'] = put_sweep_together(m.params['C'+str(carbon)+
			'_gate_optimize_N_list'+m.params['electron_transition']],m.params['C'+str(carbon)+'_gate_optimize_tau_list'+m.params['electron_transition']])
		
 	else:
 		com_list,m.params['N_list'],m.params['tau_list'],m.params['Tomography Bases'] = put_sweep_together(N_list,tau_list)
 
	####################
	### MBE settings ###
	####################

	m.params['Nr_MBE']              = 0 
	m.params['MBE_bases']           = []
	m.params['MBE_threshold']       = 1
	
	###################################
	### Parity measurement settings ###
	###################################

	m.params['Nr_parity_msmts']     = 0
	m.params['Parity_threshold']    = 1

	# print com_list

	### Derive other parameters
	m.params['pts']                 = len(com_list)
	#another init param
	m.params['init_phase_list']		= [0]*m.params['pts'] #someone hardcoded a swap phase in there. We dont do swap -> put it to whatever
	m.params['sweep_name']          = 'Tomo N and tau' 
	m.params['sweep_pts']           = com_list
	
	### RO params
	m.params['electron_readout_orientation'] = el_RO
	
	funcs.finish(m, upload =True, debug=debug)

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def optimize():
    GreenAOM.set_power(10e-6)
    counters.set_is_running(1)
    optimiz0r.optimize(dims = ['x','y','z','y','x'])
    GreenAOM.set_power(0e-6)


def add_carbon_dictionary(C_taus = None, C_tau_rng = 10e-9, C_N = [24], C_N_steps = 10, carbon = 5):


	if C_taus == None:
		print 'No C_taus supplied, please find the resonant carbon tau values first'
		return

	##### Error catching, not functional yet
	# if C_tau_rng%(2e-9) !=0 or C_N_steps%2 !=0:
	# 	return 'Either C_tau_rng or C_N_steps is not of step size 2e-9 or 2 respectively'
		

	# if len(C_N) != len(C_taus):
	# 	return 'Need an equal amount of taus and N'
		


	# Build N_list
	# raw_N_list = np.linspace(C_N-C_N_steps,C_N+C_N_steps,C_N_steps+1)
	# N_list = []
	# for i in range(int(C_tau_rng/2e-9*2)+1):
	# 	N_list = np.concatenate((N_list,raw_N_list))

	# multi_tau_carbon_dict['C' + str(c)]['N_list'] = N_list	

	# Build tau_lists and N_list
	for j, t in enumerate(C_taus):	
		## make this a function that returns a custom msmt dict for each carbon
		raw_tau_list = np.linspace(C_taus[j]-C_tau_rng,C_taus[j]+C_tau_rng,C_tau_rng*1e9+1)
		raw_N_list = np.linspace(C_N[j]-C_N_steps,C_N[j]+C_N_steps,C_N_steps+1)
		#put complete list together.
		tau_list = []
		N_list = []
		
		for i in range(len(raw_tau_list)):
			tau_list = tau_list + [raw_tau_list[i]]*(C_N_steps+1)
			N_list = np.concatenate((N_list,raw_N_list))

		## every msmt consists of 9 gate configurations. 
		## One can refine this with an additional parameter and add it to the dictionary.
		## This would guarantee most efficient AWG loading.	
		multi_tau_carbon_dict['C' + str(c)]['tau_list' + str(j)] = tau_list
		multi_tau_carbon_dict['C' + str(c)]['N_list' + str(j)] = N_list	

	# Number of measurements blocks for all taus in total. They are devided in blocks of 9 (after linking tau and N together)
	Msmts_for_single_tau = int((len(raw_tau_list)*len(raw_N_list))/9.)\

	if (len(raw_tau_list)*len(raw_N_list))%9 !=0:
		Msmts_for_single_tau +=1 
	print 'Number of measurement blocks of 9 per single tau: ' +str(Msmts_for_single_tau)
	print 'len(raw_tau_list): ' + str(len(raw_tau_list))
	print 'len(raw_N_list): ' + str(len(raw_N_list))
	print 'raw_tau: ' + str(raw_tau_list)
	print 'raw_N_list: ' + str(raw_N_list)
	print tau_list
	print N_list

	multi_tau_carbon_dict['C' + str(c)]['nr_of_blocks_single_tau'] = Msmts_for_single_tau
	Msmts_for_C = len(C_taus)*Msmts_for_single_tau	

	multi_tau_carbon_dict['C' + str(c)]['nr_of_measurements'] = Msmts_for_C 




if __name__ == '__main__':


	''' '''
	''' Specify parameters for each carbon here: C_taus = central taus for sweep, C_tau_rng = tau range
													 C_N = central N's for sweep, C_N_steps = N range

     	Warning: Give tau_rng in multiples of 2e-9 and C_N_steps in multiples of 2
     	Warning: Make C_taus and C_N of the same length
	'''

	### Enter sweep parameters for each Carbon
	multi_tau_carbon_dict = {}
	if qt.current_setup == 'lt3':


		#######################
		#### SIL 1 ###########
		#####################
		# multi_tau_carbon_dict['C2'] = {'C_taus' 	: [4.51e-6], 
		# 								'C_tau_rng'  :10e-9, # steps of 2e-9
		# 								'C_N' 		: [48],
		# 								'C_N_steps' : 8} # steps of 2 	


		# multi_tau_carbon_dict['C3'] = {'C_taus' 	: [7.144e-6],#,8.244e-6,9.34e-6,12.638e-6,21.428e-6], 
		# 								'C_tau_rng'  :0e-9, # steps of 2e-9
		# 								'C_N' 		: [38],
		# 								'C_N_steps' : 8} # steps of 2 	

		# #sweep parameters C4
		# # multi_tau_carbon_dict['C4'] = {'C_taus' 	: [9.3e-6, 14.77e-6,16.96e-6,18.053e-6],
		# # 								'C_tau_rng'  :20e-9, # steps of 2e-9
		# # 								'C_N' 		: [28],
		# # 								'C_N_steps' : 12} # steps of 2 	


		# # sweep parameters C5
		# multi_tau_carbon_dict['C5'] = {'C_taus' 	: [7.08e-6], #6.25e-6, 9.66e-6, 15.345e-6, 19.920e-6],#22.165e-6], # m1[7.108e-6],#[9.3e-6, 14.77e-6,16.96e-6,18.053e-6],
		# 								'C_tau_rng'  :10e-9, # steps of 2e-9
		# 								'C_N' 		: [28],
		# 								'C_N_steps' : 8} # steps of 2 	


		# #sweep parameters C6
		# multi_tau_carbon_dict['C6'] = {'C_taus' 	: [16.065e-6],#[6.17e-6,9.355e-6,19.625e-6],#[17.175e-6, 19.395e-6, 23.838e-6 ,24.940e-6],
		#  								'C_tau_rng' : 10e-9,
		# 								'C_N' 		: [24], 
		# 								'C_N_steps' : 8} 

		# #sweep parameters C7
		# multi_tau_carbon_dict['C7'] = {'C_taus' 	: [8.628e-6],
		#  								'C_tau_rng' : 10e-9,
		# 								'C_N' 		: [24], 
		# 								'C_N_steps' : 8} 

		# multi_tau_carbon_dict['C8'] = {'C_taus' 	: [4.818e-6],
		#  								'C_tau_rng' : 10e-9,
		# 								'C_N' 		: [20], 
		# 								'C_N_steps' : 8} 

		#######################
		#### SIL 2 ###########
		#####################
		multi_tau_carbon_dict['C1'] = {'C_taus' 	: [10.884e-6],#[8.592e-6, 10.884e-6,6.3e-6,7.476e-6,9.76e-6,13.142e-6, 15.46e-6], 
										'C_tau_rng' : 14e-9, # steps of 2e-9
										'C_N' 		: [12],#[10,10,10,10,10,10,14],
										'C_N_steps' : 6} # steps of 2 	

		multi_tau_carbon_dict['C2'] = {'C_taus' 	: [9.318e-6,10.786e-6,11.92e-6,13.05e-6,14.19e-6,16.46e-6,22.14e-6], 
										'C_tau_rng' : 12e-9, # steps of 2e-9
										'C_N' 		: [24,24,22,24,26,26,42],
										'C_N_steps' : 10} # steps of 2 	
	
	elif qt.current_setup == 'lt4':
		

		# multi_tau_carbon_dict['C1'] = {'C_taus' 	: [5.97e-6], 
		# 								'C_tau_rng'  :10e-9, # steps of 2e-9
		# 								'C_N' 		: [28],
		# 								'C_N_steps' : 8} # steps of 2 	


		# multi_tau_carbon_dict['C3'] = {'C_taus' 	: [3.66e-6], 
		# 								'C_tau_rng'  :10e-9, # steps of 2e-9
		# 								'C_N' 		: [50],
		# 								'C_N_steps' : 8} # steps of 2 	

		
		multi_tau_carbon_dict['C4'] = {'C_taus' 	: [6.394e-6],#,5.230e-6,7560e-9,8720e-9],#[5.274e-6, 6.464e-6, 7.64e-6, 8.82e-6], 
										'C_tau_rng'  :10e-9, # steps of 2e-9
										'C_N' 		: [34],#,24,26,30], 
										'C_N_steps' : 14} # steps of 2 	


		multi_tau_carbon_dict['C5'] = {'C_taus' 	: [8.58e-6],#[5.22e-6],#[6.4e-6, 8.73e-6]
										'C_tau_rng'  :16e-9, # steps of 2e-9
										'C_N' 		: [42],#[36,44], # 34,
										'C_N_steps' : 12} # steps of 2 	


		# multi_tau_carbon_dict['C6'] = {'C_taus' 	: [3.725e-6],#[6.17e-6,9.355e-6,19.625e-6],#[17.175e-6, 19.395e-6, 23.838e-6 ,24.940e-6],
		#  								'C_tau_rng' : 10e-9,
		# 								'C_N' 		: [66], 
		# 								'C_N_steps' : 8} 


		multi_tau_carbon_dict['C8'] = {'C_taus' 	: [4.86e-6], #[3.834e-6, 4.944e-6, 6.04e-6, 7.14e-6], # 3.83e-6, 6.04e-6,
		 								'C_tau_rng' : 16e-9,
										'C_N' 		: [38],  #34, 42,
										'C_N_steps' : 12} 

	### choose your carbons.
	carbons = [1]

	### msmt loop begins here.
	breakst = False
	for c in carbons:

		#get on NV before we start
		# optimize()

		breakst = show_stopper()
		if breakst: break
		# add all carbon parameters to the dictionary. Parameters can be defined above.
		add_carbon_dictionary(C_taus = multi_tau_carbon_dict['C'+ str(c)]['C_taus'], 
									C_tau_rng = multi_tau_carbon_dict['C'+ str(c)]['C_tau_rng'], 
									C_N = multi_tau_carbon_dict['C'+ str(c)]['C_N'], 
									C_N_steps = multi_tau_carbon_dict['C'+ str(c)]['C_N_steps'], 
									carbon = c)

		print '---------------------------------------------------------------------------------------------------'
		# print 'loaded dictionary: ' + str(multi_tau_carbon_dict)
		print 'Number of measurement blocks (each block is 9 individual measurements) for carbon' +str(c) + ': ' + str(multi_tau_carbon_dict['C' + str(c)]['nr_of_measurements'])
		print '---------------------------------------------------------------------------------------------------'
		

		for j, t in enumerate(multi_tau_carbon_dict['C'+ str(c)]['C_taus']):	

			breakst = show_stopper()
			if breakst: break

			#	start the measurement
			print 'Starting measurement for tau = ' + str(multi_tau_carbon_dict['C'+ str(c)]['C_taus'][j])
			
			# Rename msmt params locally for shorter access
			No_of_msmts = multi_tau_carbon_dict['C' + str(c)]['nr_of_blocks_single_tau']
			tau_list =	 multi_tau_carbon_dict['C'+str(c)]['tau_list' + str(j)]
			N_list = 	multi_tau_carbon_dict['C'+str(c)]['N_list' + str(j)]

			#gate_configs_per_msmt = msmt_dict['C'+str(c)][3] ## to be added for efficient AWG loading.

			# print 'len tau', len(tau_list)
			# print 'len N', len(N_list)
			for i in range(No_of_msmts):
				breakst = show_stopper()
				if breakst: break

				print '---------------------------------------------------------------------------------------------------'
				print 'Now @ tau: ' + str(j+1) + ' out of ' + str(len(multi_tau_carbon_dict['C' + str(c)]['C_taus']))
				print '---------------------------------------------------------------------------------------------------'
				print '----------------------------------------------------------------------------'
				print 'Progress in measurement blocks @: ' + str(i+1) + ' out of ' + str(No_of_msmts)
				print '----------------------------------------------------------------------------'
				
				# print 'Total long N_list: ' + str(N_list)
				# print 'Total long tau_list: ' + str(tau_list)
				

				# Chop it up
				if i!= No_of_msmts-1:
					#cut out 9 values from the long tau and N lists.
					current_N_list = N_list[i*9:i*9+9]
					current_tau_list = tau_list[i*9:i*9+9]

				else:
					current_N_list = N_list[i*9:]
					current_tau_list = tau_list[i*9:]
					
				print 'Current_N_list, i.e. chopped up: ' + str(current_N_list)
				print 'Current_tau_list, i.e. chopped up: ' + str(current_tau_list)

				for el_RO in ['positive','negative']:
					print '@el_ro: ' + el_RO
					breakst = show_stopper()
					if breakst: break

					SweepGates('_C'+str(c)+ '_' + el_RO + '_tau' + str(j) + '_' + str(multi_tau_carbon_dict['C'+ str(c)]['C_taus'][j]) + '_part'+str(i)+'_',
										carbon=c, el_RO = el_RO, 
										tau_list = current_tau_list,
										N_list = current_N_list,
										debug = False)

					# optimize()

			