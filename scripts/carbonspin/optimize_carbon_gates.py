"""
Carbon gate optimization.
Initializes carbons via MBI and measures the Bloch vector length
Gate parameters are being swept.
Should result in less overhead from reprogramming and a faster calibration routine.

NK 2015

TODO:
Positive and negative RO into the AWG in one go.
This method would fit for carbons with less than 52 electron pulses per gate.
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
	x_list = ['X_'+str(Ns[i])+'_'+str(taus[i]) for i in range(len(Ns))]
	y_list = ['Y_'+str(Ns[i])+'_'+str(taus[i]) for i in range(len(Ns))]
	## having fun with slices
	com_list = x_list + y_list

	tomos = len(x_list)*[['X'],['Y']]

	return com_list,2*Ns,2*taus,tomos


def SweepGates(name,**kw):

	debug = kw.pop('debug',False)
	carbon = kw.pop('carbon',False)
	el_RO = kw.pop('el_RO','positive')


	m = DD.Sweep_Carbon_Gate(name)
	funcs.prepare(m)

	m.params['C13_MBI_threshold_list'] = [1]
	m.params['el_after_init'] = '0'



	''' set experimental parameters '''

	m.params['reps_per_ROsequence'] = 2000

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

	# m.params['Tomography Bases'] = [['X'],['Y']]

	com_list,m.params['N_list'],m.params['tau_list'],m.params['Tomography Bases'] = put_sweep_together(m.params['C'+str(carbon)+'_gate_optimize_N_list'],m.params['C'+str(carbon)+'_gate_optimize_tau_list'])
 
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
    GreenAOM.set_power(15e-6)
    counters.set_is_running(1)
    optimiz0r.optimize(dims = ['x','y','z','y','x'])


if __name__ == '__main__':
	carbons = [1,2,5]


	brekast = False
	for c in carbons:

		breakst = show_stopper()
		if breakst: break

		optimize()

		for el_RO in ['positive','negative']:

			breakst = show_stopper()
			if breakst: break

			SweepGates(el_RO+'_C'+str(c),carbon=c, el_RO = el_RO, debug = False)