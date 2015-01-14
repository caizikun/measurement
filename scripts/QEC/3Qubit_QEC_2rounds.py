''' This script runs the experiments for two rounds of error correction, where the second round is a classical majority vote
at the end, which is implemented in software'''

import numpy as np
import qt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


# import the DESR measurement, DESR fit, magnet tools and master of magnet
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']; reload(mt)
ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

nm_per_step = qt.exp_params['magnet']['nm_per_step']
f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
f0m_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
N_hyperfine = qt.exp_params['samples'][SAMPLE]['N_HF_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']
# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro


range_fine  = 0.40
pts_fine    = 51
reps_fine   = 1500 #1000

import msvcrt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro


def ssrocalibration(name,RO_power=None,SSRO_duration=None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])

    if RO_power != None:
        m.params['Ex_RO_amplitude'] = RO_power
    if SSRO_duration != None:
        m.params['SSRO_duration'] = SSRO_duration

    # ms = 0 calibration
    m.params['Ex_SP_amplitude'] = 0
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration']     = 500
    m.params['A_SP_amplitude']  = 0.
    m.params['Ex_SP_amplitude'] = 15e-9
    m.run()
    m.save('ms1')

    m.finish()

def MBE(name, carbon_list   = [1,5,2],

        carbon_init_list              = [2,5,1],
        carbon_init_states            = 3*['up'],
        carbon_init_methods           = 3*['swap'],
        carbon_init_thresholds        = 3*[0],

        number_of_MBE_steps           = 1,
        logic_state                   = 'X',
        mbe_bases                     = ['Y','Y','Y'],
        MBE_threshold                 = 1,
        RO_C                          = 1,

        number_of_parity_msmnts       = 2,
        error_on_qubit                = 'all',
        el_RO                         = 'positive',
        debug                         = False,
        error_sign                    = 1,
        error_probability_list        = np.linspace(0,1,3),
        parity_orientations           = ['positive','negative'],
        error_prob_magnitude          = '< 0.5'):

    m = DD.Three_QB_det_QEC(name)
    funcs.prepare(m)

    ### Calculate the new error probability p_e' for splitting up the error in two rounds ###

    ### for errors < 0.5
    if error_prob_magnitude == '< 0.5':
        error_probability_list_per_round = (1 - (1 - 2*error_probability_list)**0.5)/2.
    

    ### for errors > 0.5
    elif error_prob_magnitude == '> 0.5':
        error_probability_list_per_round = 1 - (1 - (1 - 2*error_probability_list)**0.5)/2.
        error_probability_list_per_round = error_probability_list_per_round[::-1]


    phase_error                   = error_sign * 2*np.arcsin(np.sqrt(error_probability_list_per_round))*180./np.pi
    if error_on_qubit ==1:
        Qe                            = [1,0,0]
    elif error_on_qubit ==2:
        Qe                            = [0,1,0]
    elif error_on_qubit ==3:
        Qe                            = [0,0,1]
    elif error_on_qubit =='all':
        Qe                            = [1,1,1]

    m.params['phase_error_array'] = np.transpose([phase_error*Qe[0],phase_error*Qe[1],phase_error*Qe[2]])

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    m.params['Parity_a_RO_orientation'] = parity_orientations[0]
    m.params['Parity_b_RO_orientation'] = parity_orientations[1]

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 750


    m.params['add_wait_gate'] = False
    m.params['wait_in_msm1']  = False

    m.params['free_evolution_time_1'] = np.ones(len(phase_error))*0
    m.params['free_evolution_time_2'] = np.ones(len(phase_error))*0

    ### Carbons to be used
    m.params['MBE_list']      = carbon_list
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods
    m.params['init_state_list']     = carbon_init_states
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    '''Select right tomography basis '''

    if parity_orientations == ['positive','positive']:
        m.params['Tomo_Bases_00'] = TD.get_tomo_bases(Flip_qubit = '' ,  Flip_axis = '', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_01'] = TD.get_tomo_bases(Flip_qubit = '2',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_10'] = TD.get_tomo_bases(Flip_qubit = '3',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_11'] = TD.get_tomo_bases(Flip_qubit = '1',  Flip_axis = 'Z', RO_list = logic_state+'_list')[RO_C]

    elif parity_orientations == ['negative','negative']:
        m.params['Tomo_Bases_11'] = TD.get_tomo_bases(Flip_qubit = '' ,  Flip_axis = '', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_10'] = TD.get_tomo_bases(Flip_qubit = '2',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_01'] = TD.get_tomo_bases(Flip_qubit = '3',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_00'] = TD.get_tomo_bases(Flip_qubit = '1',  Flip_axis = 'Z', RO_list = logic_state+'_list')[RO_C]

    elif parity_orientations == ['positive','negative']:
        m.params['Tomo_Bases_01'] = TD.get_tomo_bases(Flip_qubit = '' ,  Flip_axis = '', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_00'] = TD.get_tomo_bases(Flip_qubit = '2',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_11'] = TD.get_tomo_bases(Flip_qubit = '3',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_10'] = TD.get_tomo_bases(Flip_qubit = '1',  Flip_axis = 'Z', RO_list = logic_state+'_list')[RO_C]

    elif parity_orientations == ['negative','positive']:
        m.params['Tomo_Bases_10'] = TD.get_tomo_bases(Flip_qubit = '' ,  Flip_axis = '', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_11'] = TD.get_tomo_bases(Flip_qubit = '2',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_00'] = TD.get_tomo_bases(Flip_qubit = '3',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_01'] = TD.get_tomo_bases(Flip_qubit = '1',  Flip_axis = 'Z', RO_list = logic_state+'_list')[RO_C]

    ###################
    ### MBE settings ###
    ####################

    m.params['Nr_MBE']              = number_of_MBE_steps
    m.params['MBE_bases']           = mbe_bases
    m.params['MBE_threshold']       = MBE_threshold
    m.params['3qb_logical_state']   = logic_state

    ###################################
    ### Parity measurement settings ###
    ###################################

    m.params['Nr_parity_msmts']     = number_of_parity_msmnts
    m.params['Parity_threshold']    = 1

    m.params['Parity_a_carbon_list'] = [2,1]
    m.params['Parity_b_carbon_list'] = [5,1]

    m.params['Parity_a_RO_list'] = ['X','X']
    m.params['Parity_b_RO_list'] = ['X','X']

    ### Derive other parameters
    m.params['pts']                 = len(error_probability_list)
    m.params['sweep_name']          = 'Error Probability'
    m.params['sweep_pts']           = error_probability_list

    ### RO params
    m.params['electron_readout_orientation'] = el_RO

    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':
    cnt = -1000

    error_list = {}
    error_list['0'] = np.linspace(0,0.2,3)
    error_list['1'] = np.linspace(0.3,0.5,3)
    error_list['2'] = np.linspace(0,0.2,3)
    error_list['3'] = np.linspace(0.3,0.5,3)

    for syn_round in [0,1,2,3]:

        for state in ['Z','mZ']:
            logic_state = state
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            if state == 'X' or state == 'mX':
                RO_list = [6]
            elif state == 'Y' or state == 'mY':
                RO_list = [4,5,6]
            elif state == 'Z' or state == 'mZ':
                RO_list = [0,1,2,6]


            GreenAOM.set_power(7e-6)
            ins_counters.set_is_running(0)
            optimiz0r.optimize(dims=['x','y','z'])

            for RO in RO_list:
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                ssrocalibration(SAMPLE_CFG)

                cnt += 1
                if cnt == 3:
                    for test_state in ['X','Y','Z']:
                            if test_state == 'X':
                                test_RO_list = [6]
                            elif test_state == 'Y':
                                test_RO_list = [4,5]
                            elif test_state == 'Z':
                                test_RO_list = [0]


                            print '-----------------------------------'
                            print 'press q to stop measurement cleanly'
                            print '-----------------------------------'
                            qt.msleep(2)
                            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                                break

                            for test_RO in test_RO_list:#range(7):

                                e_list = [0]
                                print '-----------------------------------'
                                print 'press q to stop measurement cleanly'
                                print '-----------------------------------'
                                qt.msleep(2)
                                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                                    break
                                MBE(SAMPLE + '00_positive_test_RO'+str(test_RO)+'_k0_sign1_'+test_state+'_test',RO_C = test_RO,
                                    logic_state = test_state,el_RO = 'positive',
                                    error_sign= 1,
                                    error_on_qubit = 'all',
                                    error_probability_list= e_list,
                                    parity_orientations           = ['positive','positive'])

                                MBE(SAMPLE + '00_negative_test_RO'+str(test_RO)+'_k0_sign1_'+test_state+'_test',RO_C = test_RO,
                                    logic_state = test_state,el_RO = 'negative',
                                    error_sign= 1,
                                    error_on_qubit = 'all',
                                    error_probability_list= e_list,
                                    parity_orientations           = ['positive','positive'])

                    DESR_msmt.darkesr('magnet_' +  'msm1', ms = 'msm',
                    range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0m_temp*1e9,# - N_hyperfine,
                    pulse_length = 8e-6, ssbmod_amplitude = 0.0025)


                    DESR_msmt.darkesr('magnet_' +  'msp1', ms = 'msp',
                    range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0p_temp*1e9,# + N_hyperfine,
                    pulse_length = 8e-6, ssbmod_amplitude = 0.006)

                    GreenAOM.set_power(7e-6)
                    ins_counters.set_is_running(0)
                    optimiz0r.optimize(dims=['x','y','z'])

                    ssrocalibration(SAMPLE_CFG)

                    cnt = 0

                for k in range(2):
                    print '-----------------------------------'
                    print 'press q to stop measurement cleanly'
                    print '-----------------------------------'
                    qt.msleep(2)
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                        break

                    for error_sign in [1,-1]:

                        logic_state = state

                        e_list = error_list[str(k)]
                        print '-----------------------------------'
                        print 'press q to stop measurement cleanly'
                        print '-----------------------------------'
                        qt.msleep(2)
                        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                            break

                        if syn_round == 0:

                            MBE(SAMPLE + '2Rounds_00_positive_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO,
                                logic_state = logic_state,el_RO = 'positive',
                                error_sign= error_sign,
                                error_on_qubit = 'all',
                                error_probability_list= e_list,
                                parity_orientations           = ['positive','positive'])

                            MBE(SAMPLE + '2Rounds_00_negative_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO,
                                logic_state = logic_state,el_RO = 'negative',
                                error_sign= error_sign,
                                error_on_qubit = 'all',
                                error_probability_list= e_list,
                                parity_orientations           = ['positive','positive'])

                        elif syn_round == 1:

                            MBE(SAMPLE + '2Rounds_11_positive_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO,
                                logic_state = logic_state,el_RO = 'positive',
                                error_sign= error_sign,
                                error_on_qubit = 'all',
                                error_probability_list= e_list,
                                parity_orientations           = ['negative','negative'])

                            MBE(SAMPLE + '2Rounds_11_negative_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO,
                                logic_state = logic_state,el_RO = 'negative',
                                error_sign= error_sign,
                                error_on_qubit = 'all',
                                error_probability_list= e_list,
                                parity_orientations           = ['negative','negative'])

                        elif syn_round == 2:

                            MBE(SAMPLE + '2Rounds_01_positive_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO,
                                logic_state = logic_state,el_RO = 'positive',
                                error_sign= error_sign,
                                error_on_qubit = 'all',
                                error_probability_list= e_list,
                                parity_orientations           = ['positive','negative'])

                            MBE(SAMPLE + '2Rounds_01_negative_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO,
                                logic_state = logic_state,el_RO = 'negative',
                                error_sign= error_sign,
                                error_on_qubit = 'all',
                                error_probability_list= e_list,
                                parity_orientations           = ['positive','negative'])

                        elif syn_round == 3:

                            MBE(SAMPLE + '2Rounds_10_positive_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO,
                                logic_state = logic_state,el_RO = 'positive',
                                error_sign= error_sign,
                                error_on_qubit = 'all',
                                error_probability_list= e_list,
                                parity_orientations           = ['negative','positive'])

                            MBE(SAMPLE + '2Rounds_10_negative_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO,
                                logic_state = logic_state,el_RO = 'negative',
                                error_sign= error_sign,
                                error_on_qubit = 'all',
                                error_probability_list= e_list,
                                parity_orientations           = ['negative','positive'])

