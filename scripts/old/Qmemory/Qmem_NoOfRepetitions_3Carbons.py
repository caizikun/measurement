"""
Initializes a carbon via MBi into |x>
Repeptitively goes through an LDE element.
Perofrms tomogrpahy on the carbon.
We vary the power of the repumper at the end of the LDE.

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

nm_per_step = qt.exp_params['magnet']['nm_per_step']
f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
f0m_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
N_hyperfine = qt.exp_params['samples'][SAMPLE]['N_HF_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

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
        mbe_bases           = ['Y','Y','Y'],
        MBE_threshold       = 1,
        logic_state         = 'X',

        el_RO               = 'positive',
        debug               = True,
        tomo_list           = ['X'],
        Repetitions         = 200):



    m = QM.QMemory_repumping(name)
    funcs.prepare(m)



    #############

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds*len(carbon_init_list)

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = Repetitions

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods*len(carbon_init_list)  
    m.params['init_state_list']     = carbon_init_states
    m.params['Nr_C13_init']         = len(carbon_init_list)

    m.params['el_after_init']       = '0'

    ##################################
    ###         RO bases           ###
    ##################################

    ## not necessary
    
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
    ###    LDE element settings     ###
    ###################################
    maxReps = repetition_calculator(carbon_init_states,carbon_list)
    ### determine sweep parameters
    if 6 in carbon_list and not 5 in carbon_list:
        pts = 5
    elif 6 in carbon_list and 5 in carbon_list:
        pts = 5

    elif 3 and not 6 in carbon_list:
        pts = 9

    elif 3 in carbon_list:
        pts = 8
    else:
        pts = 6

    minReps = 1 # minimum number of LDE reps

    # maxReps =1701 # max number of LDe reps. this number is going to be rounded
    step = int((maxReps-minReps)/pts)
    maxReps = minReps + step*pts


    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)

    # tau_larmor = 500e-9
    m.params['repump_wait'] = pts*[2e-6]#tau_larmor] #pts*[2e-6] # time between pi pulse and beginning of the repumper
    m.params['average_repump_time'] = pts*[250e-9] #this parameter has to be estimated from calibration curves, goes into phase calculation
    m.params['fast_repump_repetitions'] = np.arange(minReps,maxReps,step)


    m.params['fast_repump_duration'] = pts*[3.5e-6] #how long the beam is shined in.

    m.params['fast_repump_power'] = 850e-9
    m.params['do_pi'] = False ### does a regular pi pulse
    m.params['do_BB1'] = True ### does a BB1 pi pulse NOTE: both bools should not be true at the same time.
    m.params['pi_amps'] = pts*[m.params['fast_pi_amp']]


    ### For the Autoanalysis
    m.params['pts']                 = pts
    m.params['sweep_name']          = 'repump repetitions' 
    m.params['sweep_pts']           =  m.params['fast_repump_repetitions']
    
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

def repetition_calculator(init_config,carbons):
    init_config = [1 if state is 'up' else -1 for state in init_config]
    coupling_difference = 0
    # sum up coupling differences in order to get an estimate for maxRepetitions.
    for ii,c,state_sign in zip(range(len(carbons)),carbons,init_config):
        coupling_difference += state_sign*(qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_freq_1_m1']-qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_freq_0'])

    
    maxReps = 41e3/abs(coupling_difference)*160. # at 41 kHz coupling strength we got a decay with decay constant 120
    print maxReps
    if maxReps > 1000:
        maxReps = 1000

    return maxReps


if __name__ == '__main__':

    last_check = time.time() ### time reference for long mesaurement loops

    breakst=False    
    debug = False

    config_list = [['up']*3]#,['up']*2+['down'],['down']+['up']*2, ['up','down','up']]
    config_dict = {
        '125': ['up']*3,
        '126': ['down']+['up']*2,
        '123': ['up']*2+['down'],
        '235': ['down']+['up']*2,
        '236': ['up']+['down']+['up'],
        '256': ['up']*3,
        '356': ['down']+['up']*2}
    n = 1 ### turn measurement on/off
    if n == 1:

        
        logic_state_list=['X'] ### for DFS creation.
        tomo_list =[['X','X','X'],['Y','Y','Y'],['Y','X','Y'],['X','Y','Y'],['Y','Y','X'],['X','X','Y'],['X','Y','X'],['Y','X','X']]

        llist_of_c_lists =[[1,2,5],[1,2,3],[1,2,6],[2,3,5],[2,3,6],[2,5,6],[3,5,6]]# [[2,5],[5,6],[1,5],[1,3],[1,6],[2,3],[2,6],[3,5],[3,6],[1,2]]
        # llist_of_c_lists = [[5,6][2,5]]
        for c_list in llist_of_c_lists:

            ## select initial state

            c_key = str(c_list[0])+str(c_list[1])+str(c_list[2])
            init_config = config_dict[c_key]


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
                        msmt_name = 'NoOf_Repetitions_'+ro+'_state'+logic_state+'_Tomo_'+tomo[0]+tomo[1]+tomo[2]+'_C'+str(c_list[0])+str(c_list[1])+str(c_list[2])
                        print last_check-time.time()


                        #### get max number of repetitions we want to do:
                        maxReps = repetition_calculator(init_config,c_list)
                        QMem(msmt_name,
                                debug                   = debug,
                                tomo_list               = tomo, 
                                el_RO                   = ro,
                                carbon_list             = c_list,               
                                carbon_init_list        = c_list,
                                carbon_init_thresholds  = [0],
                                number_of_MBE_steps     = 1,
                                carbon_init_methods     = ['swap'],
                                carbon_init_states      = init_config,
                                logic_state             = logic_state)

                        if abs(last_check-time.time()) > 30*60: ## check every 30 minutes
                            optimize(breakst or debug)
                            last_check = time.time()              



