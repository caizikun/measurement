"""
Takes hardcoded gate parameters for one carbon and sweeps these parameters. 
Scans a large range!

Similar to the script carbonspin/optimize_carbon_gates.py

NK 2015
"""

import numpy as np
import qt
import msvcrt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

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

	tomos = len(px_list)*[['X'],['Y']]

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

	m.params['reps_per_ROsequence'] = 500

	### Carbons to be used
	m.params['carbon_list']         =[carbon]

	### Carbon Initialization settings
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


def add_carbon_dictionary(C_taus = None, C_tau_rng = 10e-9, C_N = 24, C_N_steps = 10, carbon = 5):


	if C_taus == None:
		print 'No C_taus supplied, please find the resonant carbon tau values first'
		return

	# or exception?
	# if C_tau_rng%(2e-9) !=0 or C_N_steps%2 !=0:
	# 	print 'Either C_tau_rng or C_N_steps is not of step size 2e-9 or 2 respectively'
	# 	return


	# Build N_list
	# dirty hack since arrange with difference zero doesn't do anything
	raw_N_list = np.linspace(C_N-C_N_steps,C_N+C_N_steps,C_N_steps+1)
	N_list = []
	for i in range(int(C_tau_rng/2e-9*2)+1):
		N_list = np.concatenate((N_list,raw_N_list))

	multi_tau_carbon_dict['C' + str(c)]['N_list'] = N_list	

	# Build tau_lists
	for j, t in enumerate(C_taus):	
		## make this a function that returns a custom msmt dict for each carbon
		raw_tau_list = np.linspace(C_taus[j]-C_tau_rng,C_taus[j]+C_tau_rng,C_tau_rng*1e9+1)
		
		#put complete list together.
		tau_list = []
		for i in range(len(raw_tau_list)):
			tau_list = tau_list + [raw_tau_list[i]]*(C_N_steps+1)

		## every msmt consists of 9 gate configurations. 
		## One can refine this with an additional parameter and add it to the dictionary.
		## This would guarantee most efficient AWG loading.
			
		multi_tau_carbon_dict['C' + str(c)]['tau_list' + str(j)] = tau_list

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

	### Enter sweep parameters for each Carbon
	multi_tau_carbon_dict = {}
	if qt.current_setup == 'lt3':


		''' Give tau_rng in multiples of 2e-9 and C_N_steps in multiples of 2'''

		#sweep parameters C4
		multi_tau_carbon_dict['C4'] = {'C_taus' 	: [9.3e-6, 14.77e-6,16.96e-6,18.053e-6],
										'C_tau_rng'  :20e-9, # steps of 2e-9
										'C_N' 		: 28,
										'C_N_steps' : 12} # steps of 2 	

		# sweep parameters C5
		multi_tau_carbon_dict['C5'] = {'C_taus' 	: [7.108e-6],#[9.3e-6, 14.77e-6,16.96e-6,18.053e-6],
										'C_tau_rng'  :12e-9, # steps of 2e-9
										'C_N' 		: 28,
										'C_N_steps' : 12} # steps of 2 	


		#sweep parameters C6
		multi_tau_carbon_dict['C6'] = {'C_taus' 	: [17.175e-6, 19.395e-6, 23.838e-6 ,24.940e-6],
		 								'C_tau_rng' : 12e-9,
										'C_N' 		: 24, 
										'C_N_steps' : 12} 

	elif qt.current_setu == 'lt4':
		pass

	### choose your carbons.
	carbons = [5]

	### msmt loop begins here.
	breakst = False
	for c in carbons:

		#get on NV before we start
		optimize()

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
		
		# Load parameter from dictionary for quicker access
		N_list = 	multi_tau_carbon_dict['C'+str(c)]['N_list']

		for j, t in enumerate(multi_tau_carbon_dict['C'+ str(c)]['C_taus']):	

			breakst = show_stopper()
			if breakst: break

			#	start the measurement
			print 'Starting measurement for tau = ' + str(multi_tau_carbon_dict['C'+ str(c)]['C_taus'][j])
			
			# Rename msmt params locally for shorter access
			No_of_msmts = multi_tau_carbon_dict['C' + str(c)]['nr_of_blocks_single_tau']
			tau_list =	 multi_tau_carbon_dict['C'+str(c)]['tau_list' + str(j)]

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

					SweepGates('_C'+str(c)+ '_' + el_RO + '_tau' + str(j) + '_' + str(multi_tau_carbon_dict['C'+ str(c)]['C_taus'][j]) + '_part'+str(i+1),
										carbon=c, el_RO = el_RO, 
										tau_list = current_tau_list,
										N_list = current_N_list,
										debug = False)

					optimize()

			