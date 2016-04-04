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

	print 'len taus in put swep together',len(taus), taus
	print 'len Ns in put sweep together',len(Ns),Ns
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

	print m.params['electron_transition']
	if N_list == None or tau_list == None:

		com_list,m.params['N_list'],m.params['tau_list'],m.params['Tomography Bases'] = put_sweep_together(m.params['C'+str(carbon)+'_gate_optimize_N_list'+m.params['electron_transition']],m.params['C'+str(carbon)+'_gate_optimize_tau_list'+m.params['electron_transition']])
		
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


if __name__ == '__main__':

	### choose your carbon.
	carbons = [3]




	if qt.current_setup == 'lt3':

		#put sweep together for carbon 5

		C5tau = 13.734e-6
		C5tau_rng = 10e-9 #stepsize is 2 ns.
		C5N = 38
		C5N_steps = 10 #on step corresponds to two pulses


		## make this a function that returns a custom msmt dict for each carbon
		raw_tau_list = np.arange(C5tau-C5tau_rng,C5tau+C5tau_rng,2e-9)
		raw_N_list = np.arange(C5N-2*C5N_steps,C5N+2*C5N_steps,2)
		sweep_len = len(raw_tau_list)*len(raw_N_list)
		tau_list = []
		N_list = []

		#put comeplete list together.

		for i in range(len(raw_tau_list)):
			tau_list = tau_list + [raw_tau_list[i]]*C5N_steps*2

		N_list = raw_N_list

		for i in range(int(C5tau_rng/2e-9*2)-1):
			N_list = np.concatenate((N_list,raw_N_list))


		Msmts_for_C5 = int(len(tau_list)/9.)\

		if len(tau_list)%9 !=0:
			Msmts_for_C5 +=1 
		## every msmt consists of 9 gate configurations. 
		## One can refine this with an additional parameter and add it to the dictionary.
		## This would guarantee most efficient AWG loading.
	
		msmt_dict = {'C5' : [tau_list,N_list,Msmts_for_C5]}


	elif qt.current_setu == 'lt4':
		pass

	print 'so many msmts',Msmts_for_C5
	print len(msmt_dict['C5'][1])/9.
	
	### msmt loop begins here.
	breakst = False
	for c in carbons:

		breakst = show_stopper()
		if breakst: break

		#optimize()
		No_of_msmts = msmt_dict['C5'][2]
		tau_list = msmt_dict['C5'][0]
		N_list = msmt_dict['C5'][1]
		#gate_configs_per_msmt = msmt_dict['C'+str(c)][3] ## to be added for efficient AWG loading.

		# print 'len tau', len(tau_list)
		# print 'len N', len(N_list)
		for i in range(No_of_msmts):
			print i
			breakst = show_stopper()
			if breakst: break

			if i!= No_of_msmts-1:

				#cut out 9 values from the long tau and N lists.
				current_N_list = N_list[i*9:i*9+9]
				current_tau_list = tau_list[i*9:i*9+9]


			else:
				current_N_list = N_list[i*9:-1]
				current_tau_list = tau_list[i*9:-1]
				print current_N_list, len(current_N_list)
				# print current_tau_list, len(current_tau_list)

			for el_RO in ['positive','negative']:
				print el_RO
				breakst = show_stopper()
				if breakst: break

				SweepGates(el_RO+'_C'+str(c)+'_part'+str(i+1),
									carbon=c, el_RO = el_RO, 
									tau_list = current_tau_list,
									N_list = current_N_list,
									debug = False)

				optimize()

			