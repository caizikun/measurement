"""
Initializes a carbon via MBi into |x>
Repeptitively goes through an LDE element.
Performs tomogrpahy on the carbon.
We vary the estimated time it takes to repump the electron. I.e. the asymmetry of the sequence.

NK 2015
"""

import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.scripts.Qmemory.QMemory as QM; reload(QM) ## get the measurement class
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
import time
import msvcrt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

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
        Repetitions         = 5000,
        **kw):



    m = QM.QMemory_repumping(name)
    funcs.prepare(m)



    ############

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds*len(carbon_init_list)

    ''' set experimental parameters '''
    m.params['reps_per_ROsequence'] = Repetitions

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods*len(carbon_init_list)
    m.params['init_state_list']     = carbon_init_states*len(carbon_init_list)    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    m.params['el_after_init']       = '0'


    ##################################
    ###         RO bases           ###
    ##################################

    ## not necessary
    
    ####################
    ### MBE settings ###
    ####################
    """these parameters will be used later on"""

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

    ### determine sweep parameters
    pts = 12

    tau_larmor = kw.get('tau_larmor', round(1./m.params['C5_freq_0'],9))
    print 'Tau larmor is ', tau_larmor
    tau_larmor = 2.298e-6

    m.params['repump_wait'] =  pts*[tau_larmor] # time between pi pulse and beginning of the repumper
    m.params['average_repump_time'] = np.linspace(-0.5e-6,1.e-6,pts)#np.linspace(-0.2e-6,1.5e-6,pts) #this parameter has to be estimated from calibration curves, goes into phase calculation
    m.params['fast_repump_repetitions'] = pts*[kw.get('seq_reps',250.)]

    m.params['do_pi'] = True ### does a regular pi pulse
    m.params['do_BB1'] = False ### does a BB1 pi pulse NOTE: both bools should not be true at the same time.
    m.params['do_optical_pi']=kw.get('do_optical_pi', False)

    ps.X_pulse(m)
    print m.params['fast_pi_amp'],m.params['Hermite_pi_amp']
    m.params['pi_amps'] = pts*[m.params['fast_pi_amp']]
    # print 'this is the pi pulse amplitude',ps.X_pulse(m).env_amplitude,ps.X_pulse(m).Sw_risetime
    m.params['fast_repump_duration'] = pts*[2.5e-6] #how long the repump beam is applied.

    m.params['fast_repump_power'] = kw.get('repump_power', 50e-9)


    ### For the Autoanalysis
    m.params['pts']                 = pts
    m.params['sweep_name']          = 'average repump time (us)' 
    m.params['sweep_pts']           =  m.params['average_repump_time']*1e6
    
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




if __name__ == '__main__':

    # logic_state_list=['X','mX','Y','mY','Z','mZ'] doesn't do anything at the moment

    breakst=False    
    last_check=time.time()
    # QMem('C5_positive_tomo_X',debug=False,tomo_list = ['X'])
    # QMem('C5_positive_tomo_Y',debug=False,tomo_list = ['Y'])
    debug = False
    repump_power_sweep = [1000e-9]#,1000e-9,500e-9, 200e-9, 50e-9, 20e-9,10e-9, 5e-9, 1e-9,0.5e-9]

    if False: ### turn measurement on/off
        for sweep_elem in range(len(repump_power_sweep)):
            if breakst:
                break
            #stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
            # get repump speed
            #repump_speed('ElectronRepump_'+str(repump_power_sweep[sweep_elem])+'W', repump_power=repump_power_sweep[sweep_elem],max_duration = 5e-6)#-4.*repump_power_sweep[sweep_elem]/2.)
            
            for c in [5]:#,2,3,5,6]:#[1,3,5,6,2]:
                if breakst:
                    break
                for tomo in ['X','Y']:
                    optimize(breakst or debug)

                    if breakst:
                        break
                    for ro in ['positive','negative']:
                        breakst = show_stopper()
                        if breakst:
                            break
                        QMem('Sweep_repump_time_'+ro+'_Tomo_'+tomo+'_C'+str(c)+'_repump_power'+str(repump_power_sweep[sweep_elem]),
                                                                            debug=debug,
                                                                            tomo_list = [tomo], 
                                                                            el_RO = ro,
                                                                            carbon_list   = [c],               
                                                                            carbon_init_list        = [c],
                                                                            carbon_init_thresholds  = [1],
                                                                            carbon_init_methods     = ['MBI'],
                                                                            Repetitions  = 250,
                                                                            seq_reps = 100,
                                                                            repump_power = repump_power_sweep[sweep_elem],
                                                                            do_optical_pi = False )
    if True: ### turn measurement on/off
        for sweep_elem in range(len(repump_power_sweep)):
            if breakst:
                break
            #stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
            # get repump speed
            #repump_speed('ElectronRepump_'+str(repump_power_sweep[sweep_elem])+'W', repump_power=repump_power_sweep[sweep_elem],max_duration = 5e-6)#-4.*repump_power_sweep[sweep_elem]/2.)
            
            for c in [5]:
                if breakst:
                    break
                for tomo in ['Z']:
                    optimize(breakst or debug)

                    if breakst:
                        break
                    for ro in ['positive','negative']:
                        breakst = show_stopper()
                        if breakst:
                            break
                        QMem('Sweep_repump_time_'+ro+'_Tomo_'+tomo+'_C'+str(c)+'_repump_power'+str(repump_power_sweep[sweep_elem]),
                                                                            debug=debug,
                                                                            tomo_list = [tomo], 
                                                                            el_RO = ro,
                                                                            carbon_list   = [c],               
                                                                            carbon_init_list        = [c],
                                                                            carbon_init_thresholds  = [0],
                                                                            carbon_init_methods     = ['swap'],
                                                                            Repetitions  = 250,
                                                                            seq_reps = 1000,
                                                                            repump_power = repump_power_sweep[sweep_elem],
                                                                            do_optical_pi = False )
   
    ######################
    ### two qubit loop ###
    ######################

    if False:

        
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
                        msmt_name = 'Sweep_repump_time_'+ro+'_state'+logic_state+'_Tomo_'+tomo[0]+tomo[1]+'_C'+str(c_list[0])+str(c_list[1])+'_repump_power'+str(repump_power_sweep[sweep_elem])
                        print last_check-time.time()
                        QMem(msmt_name,
                                debug                   = debug,
                                tomo_list               = tomo, 
                                el_RO                   = ro,
                                carbon_list             = c_list,               
                                carbon_init_list        = c_list,
                                carbon_init_thresholds  = [0],
                                number_of_MBE_steps     = 1,
                                Repetitions             = 2000,
                                carbon_init_methods     = ['swap'],
                                logic_state             = logic_state)

                        if abs(last_check-time.time()) > 30*60: ## check every 30 minutes
                            optimize(breakst or debug)
                            last_check = time.time()           



    #############################
    #### Tau Larmor sweep ######3
    #############################

    tau_Larmor_sweep_elements = np.arange( 1.9e-6, 2.6e-6, 0.1e-6)

    if False: ### turn measurement on/off
        for sweep_elem in range(len(tau_Larmor_sweep_elements)):
            if breakst:
                break
            #stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
            # get repump speed
            #repump_speed('ElectronRepump_'+str(repump_power_sweep[sweep_elem])+'W', repump_power=repump_power_sweep[sweep_elem],max_duration = 5e-6)#-4.*repump_power_sweep[sweep_elem]/2.)
            
            for c in [1,2]:#,2,3,5,6]:#[1,3,5,6,2]:
                if breakst:
                    break
                for tomo in ['X','Y','Z']:
                    optimize(breakst or debug)

                    if breakst:
                        break
                    for ro in ['positive','negative']:
                        breakst = show_stopper()
                        if breakst:
                            break
                        QMem('Sweep_repump_time_'+ro+'_Tomo_'+tomo+'_C'+str(c)+'tLarmor'+str(1e6*tau_Larmor_sweep_elements[sweep_elem]),
                                                                            debug=debug,
                                                                            tomo_list = [tomo], 
                                                                            el_RO = ro,
                                                                            carbon_list   = [c],               
                                                                            carbon_init_list        = [c],
                                                                            carbon_init_thresholds  = [1],
                                                                            carbon_init_methods     = ['MBI'],
                                                                            Repetitions  = 1000,
                                                                            seq_reps = 250,
                                                                            repump_power = 1000e-9,
                                                                            tau_larmor =  tau_Larmor_sweep_elements[sweep_elem]
                                                                            )
    if False: ### turn measurement on/off
        for sweep_elem in range(len(tau_Larmor_sweep_elements)):
            if breakst:
                break
            #stools.recalibrate_lt2_lasers(names = ['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
            # get repump speed
            #repump_speed('ElectronRepump_'+str(repump_power_sweep[sweep_elem])+'W', repump_power=repump_power_sweep[sweep_elem],max_duration = 5e-6)#-4.*repump_power_sweep[sweep_elem]/2.)
            
            for c in [1,2]:
                if breakst:
                    break
                for tomo in ['X','Y','Z']:
                    optimize(breakst or debug)

                    if breakst:
                        break
                    for ro in ['positive','negative']:
                        breakst = show_stopper()
                        if breakst:
                            break
                        QMem('Sweep_repump_time_'+ro+'_Tomo_'+tomo+'_C'+str(c)+'tLarmor'+str(1e6*tau_Larmor_sweep_elements[sweep_elem]),
                                                                            debug=debug,
                                                                            tomo_list = [tomo], 
                                                                            el_RO = ro,
                                                                            carbon_list   = [c],               
                                                                            carbon_init_list        = [c],
                                                                            carbon_init_thresholds  = [0],
                                                                            carbon_init_methods     = ['swap'],
                                                                            Repetitions  = 1000,
                                                                            seq_reps = 1000,
                                                                            repump_power = 1000e-9,
                                                                            tau_larmor =  tau_Larmor_sweep_elements[sweep_elem]
                                                                            )