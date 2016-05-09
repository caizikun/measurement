"""
Initializes a carbon via SWAP into |Z>
Repeptitively goes through an LDE element.
Perofrms tomogrpahy on the carbon.
We vary the timing of the sequence in order to detect spurious resonances.

NK 2015
"""

import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.scripts.Qmemory.QMemory as QM; reload(QM) ## get the measurement class
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import time
import msvcrt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


#### Parameters and imports for DESR ####
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)

#nm_per_step = qt.exp_params['magnet']['nm_per_step']
f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
f0m_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
N_hyperfine = qt.exp_params['samples'][SAMPLE]['N_HF_frq']
#ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

range_fine  = 0.40
pts_fine    = 51
reps_fine   = 1500 #1000
###############



def QMem(name, carbon_list   = [5],               
        
        carbon_init_list        = [5],
        carbon_init_states      = ['up'], 
        carbon_init_methods     = ['MBI'], 
        carbon_init_thresholds  = [1],  

        number_of_MBE_steps = 0,
        mbe_bases           = ['Y','Y'],
        MBE_threshold       = 1,
        logic_state         = 'X',

        el_RO               = 'positive',
        debug               = True,
        tomo_list           = ['X'],
        Repetitions         = 300):



    m = QM.QMemory_repumping(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds*len(carbon_init_list)
    m.params['reps_per_ROsequence'] = Repetitions
    m.params['carbon_list']         = carbon_list
    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods*len(carbon_init_list)
    m.params['init_state_list']     = carbon_init_states*len(carbon_init_list)    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    m.params['el_after_init']       = '0'

    ####################
    ### MBE settings ###
    ####################

    m.params['Nr_MBE']              = number_of_MBE_steps 
    m.params['MBE_bases']           = mbe_bases
    m.params['MBE_threshold']       = MBE_threshold
    m.params['2qb_logical_state']   = logic_state
    m.params['2C_RO_trigger_duration'] = 150e-6
    
    ###################################
    ### Parity measurement settings ###
    ###################################

    m.params['Nr_parity_msmts']     = 0
    m.params['Parity_threshold']    = 1

    ###################################
    ###	   LDE element settings		###
    ###################################

    pts = 11
    #f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/m.params['C5_freq_0'],9)
    ### calculate the carbon revival:
    f0 = m.params['C5_freq_0']
    f1 = m.params['C5_freq_1_m1']
    df = abs(f1-f0)
    # tau_c2 = 1/df-mod(1/df,tau_larmor)
    # print tau_c2,tau_larmor,mod(1/df,tau_larmor)
    # print 1/df
    print tau_larmor,m.params['C5_freq_0']
    rng = tau_larmor*pts/2
    m.params['repump_wait'] =  np.linspace(tau_larmor-1400e-9,tau_larmor,pts)#np.round(np.arange(tau_c2-rng,tau_c2+rng,tau_larmor),9) # time between pi pulse and beginning of the repumper
    m.params['average_repump_time'] = pts*[110e-9] #this parameter has to be estimated from calivbration curves, goes into phase calculation
    m.params['fast_repump_repetitions'] = [1000]*pts

    m.params['do_pi'] = True ### does a regular pi pulse
    m.params['do_BB1'] = False ### does a BB1 pi pulse NOTE: both bools should not be true at the same time.


    ps.X_pulse(m) #this updated fast_pi_amp
    m.params['pi_amps'] = pts*[m.params['Hermite_pi_amp']]
    print m.params['repump_wait']
    print np.mod(m.params['repump_wait'],tau_larmor)

    m.params['fast_repump_duration'] = pts*[2.5e-6] #how long the repumper beam is shined in.

    m.params['fast_repump_power'] = 1000e-9


    ### For the Autoanalysis
    m.params['pts']                 = pts
    m.params['sweep_name']          = 'Wait time (us)' 
    m.params['sweep_pts']           =  m.params['repump_wait']*1e6
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    m.params['Tomo_bases'] = tomo_list

    funcs.finish(m, upload =True, debug=debug)


def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def optimize(breakst):
    if not breakst:
        GreenAOM.set_power(10e-6)
        counters.set_is_running(1)
        optimiz0r.optimize(dims = ['x','y','z','y','x'])

if __name__ == '__main__':

    breakst=False    
    last_check=time.time()
    debug = False

    if True:   #turn measurement on or off
        for c in [5]:
            if breakst:
                break
            for tomo in ['Z']:
                #optimize(breakst or debug)
                if breakst:
                    break
                for ro in ['positive','negative']:
                    breakst = show_stopper()
                    if breakst:
                        break
                    QMem('sweep_timing_'+ro+'_Tomo_'+tomo+'_C'+str(c),
                                                                        debug=False,
                                                                        tomo_list = [tomo], 
                                                                        el_RO = ro,
                                                                        carbon_list   = [c],               
                                                                        carbon_init_list        = [c],
                                                                        carbon_init_methods     = ['swap'], 
                                                                        carbon_init_thresholds  = [0])

    if False:   #turn measurement on or off
        for c in [1,2]:
            if breakst:
                break
            for tomo in ['X', 'Y']:
                optimize(breakst or debug)
                if breakst:
                    break
                for ro in ['positive','negative']:
                    breakst = show_stopper()
                    if breakst:
                        break
                    QMem('sweep_timing_'+ro+'_Tomo_'+tomo+'_C'+str(c),
                                                                        debug=False,
                                                                        tomo_list = [tomo], 
                                                                        el_RO = ro,
                                                                        carbon_list   = [c],               
                                                                        carbon_init_list        = [c],
                                                                        carbon_init_methods     = ['MBI'], 
                                                                        carbon_init_thresholds  = [0])

    if False: #turn measurement on or off
        logic_state_list=['mX'] ### for DFS creation.
        tomo_list =[['X','X'],['Y','Y'],['X','Y'],['Y','X']]
        # tomo_list = [['Z','Z']]
        # tomo_list = [['Z','Z']]
        # llist_of_c_lists = [[2,5],[5,6],[1,5],[1,3],[1,6],[2,3],[2,6],[3,5],[3,6],[1,2]]
        llist_of_c_lists = [[2,5]]
        for c_list in llist_of_c_lists:
            for logic_state in logic_state_list:
                if breakst:
                    break
                for tomo in tomo_list: 
                    if breakst:
                        break
                    for ro in ['positive','negative']:
                        breakst = show_stopper()
                        if breakst:
                            break
                        msmt_name = 'sweep_timing_'+ro+'_state'+logic_state+'_Tomo_'+tomo[0]+tomo[1]+'_C'+str(c_list[0])+str(c_list[1])
                        print last_check-time.time()
                        QMem(msmt_name,
                                debug                   = debug,
                                tomo_list               = tomo, 
                                el_RO                   = ro,
                                carbon_list             = c_list,               
                                carbon_init_list        = c_list,
                                carbon_init_thresholds  = [0],
                                number_of_MBE_steps     = 1,
                                carbon_init_methods     = ['swap'],
                                logic_state             = logic_state)

                        if abs(last_check-time.time()) > 30*60: ## check every 30 minutes
                            optimize(breakst or debug)
                            last_check = time.time()