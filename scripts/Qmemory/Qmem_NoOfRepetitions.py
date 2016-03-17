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
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import time
import msvcrt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


#### Parameters and imports for DESR ####
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)


range_fine  = 0.40
pts_fine    = 51
###############



def QMem(name, carbon_list   = [1],               
        
        carbon_init_list        = [1],
        carbon_init_states      = ['up'], 
        carbon_init_methods     = ['swap'], 
        carbon_init_thresholds  = [1],  

        number_of_MBE_steps = 0,
        mbe_bases           = ['Y','Y'],
        MBE_threshold       = 1,
        logic_state         = 'X',

        el_RO               = 'positive',
        debug               = True,
        tomo_list			= ['X'],
        Repetitions         = 500,

        repump_power        = 500, 
        tau                 = 200, 

        minReps             = 1,
        maxReps             = 120,
        ):



    m = DD.QMemory_repumping(name)
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
    m.params['dephasing_AOM'] = 'NewfocusAOM' 
    pts = 7
    minReps = minReps # minimum number of LDE reps
    maxReps = maxReps # max number of LDe reps. this number is going to be rounded
    reps_linear_incr=np.linspace(minReps**(1/3.),maxReps**(1/3.),pts) # do the increment linear on a log scale for better precission (info of decay curve is easier to measure in beginning)



    f_larmor = m.params['C1_freq_0']#(m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)

    tau_larmor = tau*1e-9
    m.params['repump_wait'] =  pts*[tau_larmor] # time between pi pulse and beginning of the repumper
    m.params['average_repump_time'] = pts*[1e-9] #this parameter has to be estimated from calibration curves, goes into phase calculation
    
    m.params['fast_repump_repetitions'] =np.rint(reps_linear_incr**3)#[1,56,112,167,223]#np.rint(np.linspace(1,500,pts))##np.rint(np.linspace(1,500,pts))##np.array([1913,3174,4895,7146,1e4])#np.array([1,35,172,483,1040])# np.rint(reps_linear_incr**3)#pts*[50]
    print m.params['fast_repump_repetitions']
    m.params['fast_repump_power'] = repump_power*1e-9
    m.params['fast_repump_duration'] = pts*[20e-6] #how long the 'Zeno' beam is shined in.
    m.params['wait_after_repump']=2e-6 # wait for singlet and avoid laser overlap with subsequent MW pulses
    m.params['do_pi'] = True
    m.params['do_pi2'] = True
    m.params['pi_amps'] = pts*[m.params['Hermite_fast_Xpi_amp']]


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
        GreenAOM.set_power(7e-6)
        counters.set_is_running(1)
        optimiz0r.optimize(dims = ['x','y','z','y','x']*2)

if __name__ == '__main__':

    

    breakst=False    
    # last_check=time.time()
    # QMem('RO_electron',debug=False,tomo_list = ['Z'])
    # QMem('C5_positive_tomo_X',debug=False,tomo_list = ['X'])

    #########################
    ### single qubit loop ###
    #########################
    reps=[[1,500],[500,3000]]
    #[120,240],[240,360],[360,480],[480,500],[500,620],[620,740],[740,860],[860,920],[920,1040]
    repump_powers=[10,50,90]   #in nW
    tau = 200#1e9/24.342e3 # in ns
    n = 1 ### turn measurement on/off
    if n == 1:
        for c in [1]:
            if breakst:
                break
            for rp in repump_powers:
                stools.recalibrate_lasers(names=['MatisseAOM','NewfocusAOM'],awg_names=['NewfocusAOM'])
                for rep in reps:
                    print rp
                    for tomo in ['X','Y']:
                        if breakst:
                            break
                        for ro in ['positive','negative']:
                            optimize(breakst)
                            breakst = show_stopper()
                            if breakst:
                                break
                            msmnt_name='NoOf_Repetitions_'+ro+'_Tomo_'+tomo+'_C'+str(c)+'pi_'+str(tau)+'_'+str(rp)+'nW'   
                            QMem(msmnt_name,debug=False,
                                            tomo_list = [tomo], 
                                            el_RO = ro,
                                            carbon_list   = [c],               
                                            carbon_init_list        = [c],
                                            repump_power = rp,
                                            tau=tau,
                                            minReps=rep[0],
                                            maxReps = rep[1])


    ######################
    ### two qubit loop ###
    ######################

    n = 0 ### turn measurement on/off
    if n == 1:
        logic_state_list=['X','mX'] ### for DFS creation.
        for c_list in [[1,2],[2,5]]:
            for logic_state in logic_state_list:
                if breakst:
                    break
                for tomo in [['X','X'],['X','Y'],['Y','Y'],['Y','X']]:
                    optimize(breakst)
                    if breakst:
                        break
                    for ro in ['positive','negative']:
                        breakst = show_stopper()
                        if breakst:
                            break
                        msmt_name = 'NoOf_Repetitions_'+ro+'_state'+logic_state+'_Tomo_'+tomo+'_C'+str(c_list[0])+str(c_list[1])
                        
                        QMem(msmt_name,
                                debug                   = False,
                                tomo_list               = tomo, 
                                el_RO                   = ro,
                                carbon_list             = c_list,               
                                carbon_init_list        = c_list,
                                carbon_init_thresholds  = [0],
                                number_of_MBE_steps     = 1,
                                carbon_init_methods     = ['swap'],
                                logic_state             = logic_state,
                                Repetitions = 500 )