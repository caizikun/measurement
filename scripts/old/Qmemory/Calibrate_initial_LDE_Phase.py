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

    pts = kw.get('pts',20)
    
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


    ##########################################
    ##### Detuning for sweep of LDE phase ####
    ##########################################

    

    m.params['Carbon_LDE_init_phase_correction_list'] = np.array([0.0]+[0.0]*10)

    m.params['fast_repump_repetitions'] = np.array([1]*pts)

    #############################
    ##### Sweep Params ##########
    #############################
    print 'min Reps: ', minReps, ' Max reps: ', maxReps
    print 'carbons ', carbon_list, ' couplings: ', abs(abs(coupling_difference)-m.params['C1_freq_0'])

    f_larmor = m.params['C1_freq_0']
    tau_larmor = round(1/f_larmor,9)
    # tau_larmor = 2.1e-6
    print 'Calculated tau_larmor', tau_larmor

    m.params['repump_wait'] = pts*[tau_larmor]#tau_larmor] #pts*[2e-6] # time between pi pulse and beginning of the repumper
    m.params['fast_repump_power'] = kw.get('repump_power', 20e-9)
    m.params['fast_repump_duration'] = pts*[kw.get('fast_repump_duration',1.5e-6)] #how long the beam is irradiated
    m.params['average_repump_time'] = pts*[kw.get('average_repump_time',110e-9)] #this parameter has to be estimated from calibration curves, goes into phase calculation

    m.params['do_pi'] = True ### does a regular pi pulse
    m.params['do_BB1'] = False # ### does a BB1 pi pulse NOTE: both bools should not be true at the same time.

    ps.X_pulse(m) #this updates fast_pi_amp
    m.params['pi_amps'] =  pts*[m.params['fast_pi_amp']]

   
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    m.params['Tomo_bases'] = np.linspace(-60.,400.,pts)

     ### For the Autoanalysis
    m.params['pts']                 = pts
    m.params['sweep_name']          = 'Carbon RO phase' 
    m.params['sweep_pts']           =  m.params['Tomo_bases']

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
    repump_power = 1000e-9


    if False:
        for c in [1]:
            if breakst:
                break
            for tomo in ['X']:
                # optimize(breakst or debug)
                if breakst:
                    break
                for ro in ['positive','negative']:
                    breakst = show_stopper()
                    if breakst:
                        break
                    QMem('NoOfReps_'+ro+'_Tomo_'+tomo+'_C'+str(c),
                                debug=debug,
                                average_repump_time = 101e-9,
                                tomo_list = [tomo], 
                                el_RO = ro,
                                carbon_list   = [c],               
                                carbon_init_list        = [c],
                                carbon_init_thresholds  = [1],  #1 XXX
                                carbon_init_methods     = ['MBI'], # MBI/swap XXX
                                repump_po10wer = repump_power,
                                Repetitions = 250,
                                pts = 20,
                                do_optical_pi = False
                                ) 

