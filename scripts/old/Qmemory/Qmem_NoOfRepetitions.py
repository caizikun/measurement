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
from measurement.scripts.Qmemory.repump_speed import run as repump_speed;
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

###############



def QMem(name,
        carbon_list   = [5],               
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
        tomo_list			= ['X'],
        Repetitions         = 300,
        carbon_swap_list    = [],
        e_swap_state        = ['X'],
        swap_type           = None,
        RO_after_swap       = True,
        **kw):

    m = QM.QMemory_repumping(name)
    funcs.prepare(m)

    m.params['do_optical_pi']=kw.get('do_optical_pi', False)
    m.params['initial_MW_pulse'] = kw.get('initial_MW_pulse','pi2')

    
    m.params['reps_per_ROsequence'] = Repetitions
    m.params['carbon_list']         = carbon_list   ### Carbons to be used

    #######################################
    ### Carbon Initialization settings ####
    #######################################
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods*len(carbon_init_list)
    m.params['init_state_list']     = carbon_init_states*len(carbon_init_list)    
    m.params['Nr_C13_init']         = len(carbon_init_thresholds)
    m.params['el_after_init']       = '0'

    ################################
    ### elec to carbon  swap settings ####
    ################################
    if swap_type == None:
        m.params['C13_MBI_threshold_list'] = carbon_init_thresholds*len(carbon_init_list)
    else:
        m.params['C13_MBI_threshold_list'] = carbon_init_thresholds
    print 'c_init_th' + str(m.params['C13_MBI_threshold_list'])

    m.params['carbon_swap_list']    = carbon_swap_list
    m.params['elec_init_state']     = e_swap_state 
    m.params['SWAP_type']           = swap_type #used in carbon_swap_gate to determine swap w carbon init or w/o carbon init
    m.params['Nr_C13_SWAP']         = len(carbon_swap_list)
    m.params['RO_after_swap']       = RO_after_swap

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

    coupling_difference = 0 ## sum up coupling differences in order to get an estimate for maxRepetitions.
    for ii,c in enumerate(carbon_list):
        if ii == 0:
            coupling_difference = m.params['C'+str(c)+'_freq_1_m1']
        else:
            if logic_state == 'X':
                # print 'carbon freqs',m.params['C'+str(c)+'_freq_1_m1'],m.params['C'+str(c)+'_freq_0']
                coupling_difference += (m.params['C'+str(c)+'_freq_1_m1']-m.params['C'+str(c)+'_freq_0'])
            else: 
                # print 'carbon freqs',m.params['C'+str(c)+'_freq_1_m1'],m.params['C'+str(c)+'_freq_0']
                coupling_difference +=  - m.params['C'+str(c)+'_freq_1_m1']-m.params['C'+str(c)+'_freq_0']
            # print c
            # print coupling_difference
    pts = kw.get('pts',None)
    if pts == None:
        if len(carbon_list) != 2:
            if 6 in carbon_list and not 5 in carbon_list:
                pts = 10
            elif 6 in carbon_list and 5 in carbon_list:
                pts = 6
            else:
                pts = 11
        else:
                pts = 11


    minReps = kw.get('minReps',0) # minimum number of LDE reps
    maxReps = kw.get('maxReps', 1e3 / abs(abs(coupling_difference)-m.params['C1_freq_0']))


    step = int((maxReps-minReps)/pts)

    
    m.params['fast_repump_repetitions'] = np.arange(minReps,minReps+pts*step,step)


    #############################
    ##### Sweep Params ##########
    #############################
    print 'min Reps: ', minReps, ' Max reps: ', maxReps
    print 'carbons ', carbon_list, ' couplings: ', abs(abs(coupling_difference)-m.params['C1_freq_0'])

    f_larmor = m.params['C1_freq_0']
    tau_larmor = round(1/f_larmor,9)
    # tau_larmor = 2.1e-6
    print 'Calculated tau_larmor', tau_larmor

    # tau_larmor = 2.298e-6

    m.params['repump_wait'] = pts*[tau_larmor]#tau_larmor] #pts*[2e-6] # time between pi pulse and beginning of the repumper
    m.params['fast_repump_power'] = kw.get('repump_power', 20e-9)
    m.params['fast_repump_duration'] = pts*[kw.get('fast_repump_duration',1.5e-6)] #how long the beam is irradiated
    m.params['average_repump_time'] = pts*[kw.get('average_repump_time',110e-9)] #this parameter has to be estimated from calibration curves, goes into phase calculation


    m.params['do_pi'] = True ### does a regular pi pulse
    m.params['do_BB1'] = False # ### does a BB1 pi pulse NOTE: both bools should not be true at the same time.

    ps.X_pulse(m) #this updated fast_pi_amp
    m.params['pi_amps'] =  pts*[m.params['fast_pi_amp']]

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
        GreenAOM.set_power(0e-6)

def optimisation_routine(last_check,repump_power,debug,breakst):
    if abs(last_check-time.time()) > 30*60 and not (breakst or debug): ## check every 30 minutes
        optimize(breakst or debug)
        last_check = time.time()
        # calibrate lasers
        stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
        # measure repump speed
        repump_speed('ElectronRepump_'+str(repump_power)+'nW', repump_power=repump_power,max_duration =4e-6-2.*repump_power/2.)
    
    return last_check


if __name__ == '__main__':

    last_check = time.time() ### time reference for long measurement loops
    breakst = False    
    debug = False
    repump_power = 10e-9


    ############################################################
    #### SK SWAP and subsequent Carbon Decay w ent attempts ####
    ############################################################
    if False:
 
        swap_type = ['swap_w_init']
        # print qt.exp_params['samples']['Pippin']['Carbon_LDE_phase_correction_list']
        for c in [1]:#,2,3,5,6]:
            if breakst:
                break
            for e in ['X','mX','Y','mY','Z','mZ']:
                optimize(breakst)
                if breakst:
                    break
                for tomo in ['X','Y','Z']:
                    if breakst:
                        break
                    for ro in ['positive','negative']:
                        breakst = show_stopper()
                        if breakst:
                            break
                        QMem('NoOfReps_'+ro+'_Tomo_'+tomo+'_elState_' + str(e) +'_C'+str(c),
                                    debug=debug,
                                    average_repump_time = 101e-9,
                                    tomo_list       = [tomo], 
                                    el_RO           = ro,
                                    carbon_list     = [c],               
                                    carbon_init_list        = [c],
                                    carbon_init_thresholds  = [0,1],  #1 XXX
                                    carbon_init_methods     = ['swap'], # MBI/swap XXX
                                    repump_power    = repump_power,
                                    repetitions     = 500,
                                    pts             = 20,
                                    do_optical_pi   = False,
                                    minReps         = 1,
                                    maxReps         = 801,
                                    carbon_swap_list = [c],
                                    e_swap_state    = e,
                                    swap_type       = swap_type,
                                    RO_after_swap   = True
                                    ) 


    #########################
    ### single qubit X loop ###
    #########################

    if True: ### turn measurement on/off
        # stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
        # get repump speed
        for c in [4]:#,2,3,5,6]:
            if breakst:
                break
            for tomo in ['Z']:#,'Y']:
                # optimize(breakst or debug)
                if breakst:
                    break
                for ro in ['positive']:#,'negative']:
                    breakst = show_stopper()
                    if breakst:
                        break
                    QMem('NoOfReps_'+ro+'_Tomo_'+tomo+'_C'+str(c),
                                debug=debug,
                                average_repump_time = 400e-9,
                                tomo_list = [tomo], 
                                el_RO = ro,
                                carbon_list   = [c],               
                                carbon_init_list        = [c],
                                carbon_init_thresholds  = [0],  #1 XXX
                                carbon_init_methods     = ['swap'], # MBI/swap XXX
                                repump_power = repump_power,
                                Repetitions = 5000,
                                maxReps = 500,
                                minReps = 200,
                                pts = 2,
                                do_optical_pi = False,
                                ) 
                ### optimize position and calibrate powers
                # last_check = optimisation_routine(last_check,repump_power,debug,breakst)

    ######################
    ### two qubit XX loop ###
    ######################
   

    if False: ### turn measurement on/off
        # stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])

        logic_state_list=['X','mX'] ### for DFS creation.
        tomo_list =[['X','X'],['Y','Y'],['X','Y'],['Y','X']]
        ### DFS configs ordered by coupling strength.
        llist_of_c_lists = [[1,5],[1,2],[1,3],[2,6],[3,6],[5,6]]
        # llist_of_c_lists = [[2,5]]

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
                        msmt_name = 'NoOfRepetitions_'+ro+'_state'+logic_state+'_Tomo_'+tomo[0]+tomo[1]+'_C'+str(c_list[0])+str(c_list[1])
                        # print last_check-time.time()
                        QMem(msmt_name,
                                debug                   = debug,
                                tomo_list               = tomo, 
                                el_RO                   = ro,
                                carbon_list             = c_list,               
                                carbon_init_list        = c_list,
                                carbon_init_thresholds  = [0],
                                number_of_MBE_steps     = 1,
                                carbon_init_methods     = ['swap'],
                                logic_state             = logic_state,
                                repump_power            = repump_power)
                    
                    ### optimize position and calibrate powers
                    last_check = optimisation_routine(last_check,repump_power,debug,breakst)
                    
    #########################
    ### single qubit Z loop ###
    #########################

    if False: ### turn measurement on/off
        # stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
        for c in [1]:
            if breakst:
                break

            for tomo in ['Z']:
                optimize(breakst or debug)
                if breakst:
                    break
                for ro in ['positive','negative']:
                    maxReps=5000
                    breakst = show_stopper()
                    if breakst:
                        break
                    QMem('NoOfRepetitions_'+ro+'_Tomo_'+tomo+'_C'+str(c),
                                                                        debug=debug,
                                                                        tomo_list = [tomo],
                                                                        average_repump_time = 111e-9,
                                                                        el_RO = ro,
                                                                        carbon_list   = [c],               
                                                                        carbon_init_list        = [c],
                                                                        maxReps                 = maxReps,
                                                                        carbon_init_thresholds  = [0],  #1 XXX
                                                                        carbon_init_methods     = ['swap'],
                                                                        pts                     = 15,
                                                                        repump_power            = repump_power) # MBI/swap XXX
                ### optimize position and calibrate powers
                last_check = optimisation_routine(last_check,repump_power,debug,breakst)

    #########################
    ### two qubit Z loop ###
    #########################

    if False: ### turn measurement on/off
        # stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
        logic_state_list=['X','mX'] ### for DFS creation.
        tomo_list =[['Z','Z']]
        # tomo_list = [['Z','Z']]
        # tomo_list = [['Z','Z']]
        llist_of_c_lists = [[2,3],[2,5],[3,5],[1,6],[1,5],[1,2],[1,3],[2,6],[3,6],[5,6]]
        # llist_of_c_lists = [[2,5]]

        for c_list in llist_of_c_lists:
            # if c_list in [[1,2],[1,3],[2,3],[2,5],[3,5],[3,6]]: # shorter decay when carbon 2 or 3 is involved
            #     number_of_repetitions_list = [[0,500],[600,1000]]
            # else:
            number_of_repetitions_list = [[0,1000],[1000,2000]]
            for logic_state in logic_state_list:
                if breakst:
                    break
                for tomo in tomo_list: 
                    if breakst:
                        break
                    for rep_list in number_of_repetitions_list:
                        if breakst:
                            break
                        for ro in ['positive','negative']:
                            breakst = show_stopper()
                            if breakst:
                                break
                            msmt_name = 'NoOfRepetitions_'+ro+'_state'+logic_state+'_Tomo_'+tomo[0]+tomo[1]+'_C'+str(c_list[0])+str(c_list[1])
                            print last_check-time.time()
                            QMem(msmt_name,
                                    debug                   = debug,
                                    tomo_list               = tomo, 
                                    el_RO                   = ro,
                                    carbon_list             = c_list,               
                                    carbon_init_list        = c_list,
                                    carbon_init_thresholds  = [0],
                                    number_of_MBE_steps     = 1,
                                    minReps                 = rep_list[0],
                                    maxReps                 = rep_list[1],
                                    carbon_init_methods     = ['swap'],
                                    logic_state             = logic_state,
                                    pts                     = 5,
                                    repump_power            = repump_power)

                            ### optimize position and calibrate powers
                            last_check = optimisation_routine(last_check,repump_power,debug,breakst)

    ######################
    ### Repump power sweep ###
    ######################
    if False: 

        repump_power_sweep = [2000e-9,1000e-9, 500e-9, 200e-9, 100e-9, 50e-9, 30e-9, 20e-9, 3e-9,1e-9,0.5e-9]
        average_repump_time_sweep = len(repump_power_sweep)*[750e-9]

    
        for sweep_elem in range(len(repump_power_sweep)):
            breakst = show_stopper()
            if breakst:
                break

            stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
            # get repump speed
            repump_speed('ElectronRepump_'+str(repump_power_sweep[sweep_elem])+'nW_Eprime', repump_power=repump_power_sweep[sweep_elem],max_duration = 10e-6-9.*repump_power_sweep[sweep_elem]/3.5)
            
            for c in [6,1,2,3,5]:
                if breakst:
                    break
                               

                for tomo in ['X','Y']:#'X','Y']:  XXX
                    optimize(breakst or debug)
                    if breakst:
                        break
                    for ro in ['positive','negative']:
                        breakst = show_stopper()
                        if breakst:
                            break
                        stools.recalibrate_lt2_lasers(names = ['MatisseAOM'],awg_names=[])
                        QMem('NoOfRepetitions_'+ro+'_Tomo_'+tomo+'_C'+str(c)+'_repumpP'+str(repump_power_sweep[sweep_elem]),
                                                                            debug=debug,
                                                                            tomo_list = [tomo], 
                                                                            el_RO = ro,
                                                                            carbon_list   = [c],               
                                                                            carbon_init_list        = [c],
                                                                            carbon_init_thresholds  = [1],  #1 XXX
                                                                            carbon_init_methods     = ['MBI'], # MBI/swap XXX
                                                                            repump_power = repump_power_sweep[sweep_elem],
                                                                            average_repump_time = average_repump_time_sweep[sweep_elem],
                                                                            fast_repump_duration = 3e-6
                                                                            ) 
                
                
                for tomo in ['Z']:#'X','Y']:  XXX
                    optimize(breakst or debug)
                    if breakst:
                        break
                    for ro in ['positive','negative']:
                        breakst = show_stopper()
                        if breakst:
                            break
                        stools.recalibrate_lt2_lasers(names = ['MatisseAOM'],awg_names=[])
                        QMem('NoOfRepetitions_'+ro+'_Tomo_'+tomo+'_C'+str(c)+'_repumpP'+str(repump_power_sweep[sweep_elem]),
                                                                            debug=debug,
                                                                            tomo_list = [tomo], 
                                                                            el_RO = ro,
                                                                            carbon_list   = [c],               
                                                                            carbon_init_list        = [c],
                                                                            carbon_init_thresholds  = [0],  #1 XXX
                                                                            carbon_init_methods     = ['swap'], # MBI/swap XXX
                                                                            repump_power = repump_power_sweep[sweep_elem],
                                                                            average_repump_time = average_repump_time_sweep[sweep_elem],
                                                                            fast_repump_duration = 3e-6) 
    
    ######################
    ### Duration sweep : Effect of Carbon T2* ###
    ######################

    # if False: ### turn measurement on/off
       
    #     logic_state_list=['X','mX'] ### for DFS creation.
    #     tomo_list =[['X','X'],['Y','Y'],['X','Y'],['Y','X']]
    #     # tomo_list = [['Z','Z']]
    #     # tomo_list = [['Z','Z']]
    #     list_of_repdurs =[1.5e-6,2.5e-6,4.5e-5,5.5e-6,10e-6,20e-6]
    #     for rep_dur in list_of_repdurs:
    #         for logic_state in logic_state_list:
    #             if breakst:
    #                 break
    #             for tomo in tomo_list: 
    #                 if breakst:
    #                     break
    #                 for ro in ['positive','negative']:
    #                     breakst = show_stopper()
    #                     if breakst:
    #                         break
    #                     msmt_name = 'NoOfRepetitions_'+ro+'_state'+logic_state+'_Tomo_'+tomo[0]+tomo[1]+'_C'+str(25)+'_repdur_'+str(rep_dur)
    #                     print last_check-time.time()
    #                     QMem(msmt_name,
    #                             debug                   = debug,
    #                             tomo_list               = tomo, 
    #                             el_RO                   = ro,
    #                             carbon_list             = [2,5],               
    #                             carbon_init_list        = [2,5],
    #                             carbon_init_thresholds  = [0],
    #                             number_of_MBE_steps     = 1,
    #                             carbon_init_methods     = ['swap'],
    #                             logic_state             = logic_state,
    #                             fast_repump_duration    = rep_dur)

    #                     if abs(last_check-time.time()) > 30*60: ## check every 30 minutes
    #                         optimize(breakst or debug)
    #                         last_check = time.time()


