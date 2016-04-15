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
    px_list = ['X_'+str(Ns[i])+'_'+str(taus[i]) for i in range(len(Ns))]
    py_list = ['Y_'+str(Ns[i])+'_'+str(taus[i]) for i in range(len(Ns))]


    ## having fun with slices
    com_list = px_list + py_list

    tomos = len(px_list)*['X']+len(px_list)*['Y']

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

    m.params['reps_per_ROsequence'] = 1500

    ### Carbons to be used
    m.params['carbon_list']         =[carbon]

    ### Carbon Initialization settings
    m.params['carbon_init_list']    = [carbon]
    m.params['init_method_list']    = ['MBI']    
    m.params['init_state_list']     = ['up']
    m.params['Nr_C13_init']         = 1

   
    m.params["C1_gate_sym_tau_list"]=[3.882e-6,9.436e-6,4.996e-6,3.888e-6,8.322e-6,6.102e-6,8.328e-6,7.220e-6,6.112e-6]
    m.params["C1_gate_sym_N_list"]=[34,62,36,34,58,40,50,44,46]
       
    #m.params['C2_gate_sym_N_list']= [18]*4
    #m.params['C2_gate_sym_tau_list']=[8.880e-6]*4
    m.params["C2_gate_sym_tau_list"]=[10.816e-6,9.680e-6,11.956e-6,8.540e-6,13.092e-6,7.402e-6,14.232e-6,6.262e-6,5.126e-6,14.238e-6]
    m.params["C2_gate_sym_N_list"]=[14,14,14,14,16,14,16,14,12,16]
       
    #m.params['C3_gate_sym_N_list']= [16]*4
    #m.params['C3_gate_sym_tau_list']=[14.232e-6]*4
    m.params["C3_gate_sym_tau_list"]=[10.816e-6,9.680e-6,11.956e-6,8.540e-6,13.092e-6,7.402e-6,14.232e-6,6.262e-6,5.126e-6,14.238e-6]
    m.params["C3_gate_sym_N_list"]=[14,14,14,14,16,14,16,14,12,16]

    #m.params['C4_gate_sym_N_list']= [34,36,38,40,34,40,40,36]
   # m.params['C4_gate_sym_tau_list']=[6.428e-6,1.760e-6,14.604e-6,6.430e-6,8.764e-6,5.264e-6,2.930e-6,14.590e-6]
    m.params["C5_gate_sym_tau_list"]=[5.356e-6,6.544e-6,10.122e-6,11.310e-6,10.126e-6,4.162e-6,11.314e-6,12.504e-6,7.736e-6,13.680e-6]
    m.params["C5_gate_sym_N_list"]=[26,28,34,38,42,26,46,46,30,58]
    ##################################
    ### RO bases,timing and number of pulses (sweep parameters) ###
    ##################################

    print m.params['electron_transition']
    com_list,m.params['N_list'],m.params['tau_list'],m.params['Tomography Bases'] = put_sweep_together(m.params['C'+str(carbon)+'_gate_sym_N_list'],m.params['C'+str(carbon)+'_gate_sym_tau_list'])
 
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

    print com_list
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


if __name__ == '__main__':
    carbons = [3,5]


    brekast = False
    for c in carbons:

        breakst = show_stopper()
        if breakst: break

        optimize()

        for el_RO in ['positive','negative']:

            breakst = show_stopper()
            if breakst: break

            SweepGates(el_RO+'_C'+str(c),carbon=c, el_RO = el_RO, debug = False)