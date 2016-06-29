"""
Carbon gate optimization.
Initializes carbons via COMP and measures the Bloch vector length
Gate parameters are being swept.
Should result in less overhead from reprogramming and a faster calibration routine.

NK 2015
"""

import numpy as np
import qt
import msvcrt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

reload(DD)

ins_counters = qt.instruments['counters']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def put_sweep_together(N1s,tau1s,N2s,tau2s,phases):
    ### put together into one sweep parameter
    x_list = ['X_'+str(N1s[i])+'_'+str(tau1s[i])+'_'+str(N2s[i])+'_'+str(tau2s[i])+'_'+str(phases[i]) for i in range(len(N1s))]
    y_list = ['Y_'+str(N1s[i])+'_'+str(tau1s[i])+'_'+str(N2s[i])+'_'+str(tau2s[i])+'_'+str(phases[i]) for i in range(len(N1s))]
    ## having fun with slices
    com_list = x_list + y_list

    tomos = len(x_list)*[['X'],['Y']]

    return com_list,2*N1s,2*tau1s,2*N2s,2*tau2s,2*phases,tomos


def SweepGates(name,**kw):

    debug = kw.pop('debug',False)
    carbon = kw.pop('carbon',False)
    el_RO = kw.pop('el_RO','positive')


    m = DD.Sweep_Carbon_Gate_COMP(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = [1]
    m.params['el_after_init'] = '0'



    ''' set experimental parameters '''

    m.params['reps_per_ROsequence']=1500

    ### Carbons to be used
    m.params['carbon_list']         =[carbon]

    ### Carbon Initialization settings
    m.params['carbon_init_list']    = [carbon]
    m.params['init_method_list']    = ['COMP']    
    m.params['init_state_list']     = ['up']
    m.params['Nr_C13_init']         = 1

    ##################################
    ### RO bases,timing and number of pulses (sweep parameters) ###
    ##################################

    # m.params['Tomography Bases'] = [['X'],['Y']]
    print m.params['electron_transition']

    #Parameters for the initialization sweep
    m.params['C1_gate_optimize_tau1_list_m1'] = [7.204e-6]*9#,7.204e-6,7.204e-6,7.204e-6,7.204e-6,7.204e-6,7.204e-6,7.204e-6,7.204e-6]

    m.params['C1_gate_optimize_tau2_list_m1']= [7.230e-6]*9#,7.230e-6,7.230e-6,7.230e-6,7.230e-6,7.230e-6,7.230e-6,7.230e-6,7.230e-6]
    
    m.params['C1_gate_optimize_N1_list_m1']= [28]*9
    m.params['C1_gate_optimize_N2_list_m1']= [20]*9
    m.params['C1_gate_optimize_phase_list_m1']= [0,10,20,30,40,50,60,70,80]


    m.params['C2_gate_optimize_tau1_list_m1'] = [13.592e-6]*9#,13.592e-6,13.592e-6,13.592e-6,13.592e-6,13.592e-6,13.592e-6,13.592e-6,13.592e-6]

    m.params['C2_gate_optimize_tau2_list_m1']= [13.612e-6]*9#,13.612e-6,13.612e-6,13.612e-6,13.612e-6,13.612e-6,13.612e-6,13.612e-6,13.612e-6]

    m.params['C2_gate_optimize_N1_list_m1']= [22]*9
    m.params['C2_gate_optimize_N2_list_m1']= [18]*9
    m.params['C2_gate_optimize_phase_list_m1']= [0,30,60,90,120,150,180,210,240]


   # m.params['C5_gate_optimize_tau1_list_m1'] = [11.228e-6,11.228e-6,11.228e-6,11.228e-6,11.228e-6,11.228e-6,11.228e-6,11.228e-6,11.228e-6]

    #m.params['C5_gate_optimize_tau2_list_m1']= [11.244e-6,11.244e-6,11.244e-6,11.244e-6,11.244e-6,11.244e-6,11.244e-6,11.244e-6,11.244e-6]

    #m.params['C5_gate_optimize_N1_list_m1']= [18,20,22,18,20,22,22,20,18]
    #m.params['C5_gate_optimize_N2_list_m1']= [18,20,22,22,18,20,18,22,20]
    #m.params['C5_gate_optimize_phase_list_m1']= [0,0,0,0,0,0,0,0,0]

    m.params['C5_gate_optimize_tau1_list_m1'] =[11.292e-6]*9

    m.params['C5_gate_optimize_tau2_list_m1']= [11.324e-6]*9

    m.params['C5_gate_optimize_N1_list_m1']= [16]*9
    m.params['C5_gate_optimize_N2_list_m1']= [36]*9
    m.params['C5_gate_optimize_phase_list_m1']= [0,10,20,30,40,50,60,70,80]

    com_list,m.params['N1_list'],m.params['tau1_list'],m.params['N2_list'],m.params['tau2_list'],m.params['extra_phase_list'],m.params['Tomography Bases'] = put_sweep_together(m.params['C'+str(carbon)+'_gate_optimize_N1_list'+m.params['electron_transition']],m.params['C'+str(carbon)+'_gate_optimize_tau1_list'+m.params['electron_transition']], m.params['C'+str(carbon)+'_gate_optimize_N2_list'+m.params['electron_transition']],m.params['C'+str(carbon)+'_gate_optimize_tau2_list'+m.params['electron_transition']],m.params['C'+str(carbon)+'_gate_optimize_phase_list'+m.params['electron_transition']])
    ###################
    ### Measurement settings###
    ###################
    m.params['C1_Ren_tau_m1']=[7.204e-6]
    m.params['C1_Ren_N_m1']=[28]
    m.params['C1_Ren_tau2_m1']=[7.230e-6]
    m.params['C1_Ren_N2_m1']=[20]


    m.params['C2_Ren_tau_m1']=[13.592e-6]
    m.params['C2_Ren_N_m1']=[22]
    m.params['C2_Ren_tau2_m1']=[13.612e-6]
    m.params['C2_Ren_N2_m1']=[18]



    m.params['C5_Ren_tau_m1']=[11.292e-6]
    m.params['C5_Ren_N_m1']=[16]
    m.params['C5_Ren_tau2_m1']=[11.324e-6]
    m.params['C5_Ren_N2_m1']=[36]



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
    GreenAOM.set_power(10e-6)
    counters.set_is_running(1)
    optimiz0r.optimize(dims = ['x','y','z','y','x'])


if __name__ == '__main__':
    carbons = [2]


    brekast = False
    for c in carbons:

        breakst = show_stopper()
        if breakst: break

        # optimize()

        for el_RO in ['positive','negative']:

            breakst = show_stopper()
            if breakst: break

            SweepGates(el_RO+'_C'+str(c),carbon=c, el_RO = el_RO, debug = False)



