'This script tests a measurement without branching'

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

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

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


def NoBranching_and_invert_test(name, 
    carbon_list = [1],
    A_list = ['X'],
    tomo_list = ['X'],
    debug = False,
    parity_orientations = ['positive','positive'],
    use_composite_pi= True):

    m = DD.test_undo_RO_phase_and_invert(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] = 5000
    m.params['pts'] = 1

    m.params['RO_trigger_duration'] = 150e-6

    m.params['use_composite_pi'] = use_composite_pi

    ##### Carbon initializations params
    m.params['Nr_C13_init'] = 1
    m.params['carbon_init_list']        = [1]#[]
    m.params['init_state_list']         = ['down']#['up','up']#['up']
    m.params['init_method_list']        = ['MBI']#['swap','swap']# ['swap']
    m.params['C13_MBI_threshold_list']  = [1]#[0,0]#[0]


    m.params['Nr_MBE']              = 0
    #m.params['MBE_bases']           = []
    #m.params['MBE_threshold']       = 1
    m.params['Nr_parity_msmts']     = 1
    m.params['add_wait_gate'] = False
    m.params['wait_in_msm1']  = False

    ###### RO mmtA params
    m.params['Parity_A_do_init_pi2'] = True
    m.params['Parity_A_carbon_list'] = carbon_list
    m.params['Parity_A_RO_list'] = A_list
    m.params['Parity_A_RO_orientation'] = parity_orientations[0]
    
    # if we do invert, we don't have to do anything conditional
    m.params['undo_parityA_conditional_pi'] = False
    m.params['undo_parityA_conditional_pi2'] = False

    m.params['Invert_A_do_final_pi2'] = False
    m.params['Tomo_do_init_pi2'] = False

    for s in tomo_list:
        if 'Z' in s:
            print 'tomography contains Z; doing pi/2 between invertRO and RO'
            m.params['Invert_A_do_final_pi2'] = True
            m.params['Tomo_do_init_pi2'] = True

    m.params['Tomo_carbon_list'] = carbon_list
    m.params['Tomo_RO_orientation'] = parity_orientations[1]
    m.params['Tomo_RO_list'] = tomo_list

    funcs.finish(m, upload =True, debug=debug)

def NoBranching_no_invert_test(name, 
    carbon_list = [1,2],
    A_list = ['X','X'],
    tomo_list = ['X','X'],
    debug = False,
    parity_orientations = ['positive','positive']):


    m = DD.test_undo_RO_phase(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] = 1200
    m.params['pts'] = 1

    m.params['RO_trigger_duration'] = 150e-6

    ##### Carbon initializations params
    m.params['Nr_C13_init'] = 2
    m.params['carbon_init_list']        = [1,2]
    m.params['init_state_list']         = 2*['up']
    m.params['init_method_list']        = 2*['swap']
    m.params['C13_MBI_threshold_list']  = [0,0]


    m.params['Nr_MBE']              = 0
    #m.params['MBE_bases']           = []
    #m.params['MBE_threshold']       = 1
    m.params['Nr_parity_msmts']     = 1
    m.params['add_wait_gate'] = False
    m.params['wait_in_msm1']  = False

    ###### RO mmtA params
    m.params['Parity_A_carbon_list'] = carbon_list
    m.params['Parity_A_RO_list'] = A_list
    m.params['Parity_A_RO_orientation'] = parity_orientations[0]

    # if we do X or Y tomography after, we have to do a conditional pi2, and no init pi2 for RO
    m.params['undo_parityA_conditional_pi2'] = True
    m.params['undo_parityA_conditional_pi'] = False
    # We merges the init pi2 of the tomography
    m.params['Tomo_do_init_pi2'] = False

    # if we do Z tomography after, we have to do a conditional pi, and a init pi2 for RO
    for s in tomo_list:
        if 'Z' in s:
            print 'tomography contains Z; doing conditional pi and pi/2 between invertRO and RO'
            m.params['undo_parityA_conditional_pi2'] = False
            m.params['undo_parityA_conditional_pi'] = True
            m.params['Tomo_do_init_pi2'] = True

    m.params['Tomo_carbon_list'] = carbon_list
    m.params['Tomo_RO_orientation'] = parity_orientations[1]
    m.params['Tomo_RO_list'] = tomo_list

    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':


    orientations_list=[
        ['positive','positive'],
        ['positive','negative'],
        ['negative','positive'],
        ['negative','negative'],
        ]      

    tomo_lists = [['X','X'],['X','Y'],['Y','X'],['Y','Y']]

    test_nobranching_and_invert = True
    test_nobranching_noinvert = False

    if test_nobranching_and_invert:   
        mmt_lists=[[['I','I','X'],['I','X','I']],
                    [['I','I','X'],['I','Y','I']],
                    [['X','I','I'],['I','X','I']],
                    [['X','I','I'],['I','Y','I']]]

        for mmt_list in mmt_lists:
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            GreenAOM.set_power(25e-6)
            ins_counters.set_is_running(0)
            optimiz0r.optimize(dims=['x','y','z'])

            ssrocalibration(SAMPLE_CFG)

            A_list = mmt_list[0]
            tomo_list = mmt_list[1]
            A_list_name = ''.join([a for a in A_list])                           
            tomo_name = ''.join([a for a in tomo_list])

            for kk,orientations in enumerate(orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = ''.join([o[0] for o in orientations])

                print 'mmtA: '+A_list_name+ ' tomo: '+tomo_name
                print orientations_name

                NoBranching_and_invert_test(SAMPLE+'C512_test_init1-X_mmt_'+A_list_name+'_'+'tomo'+tomo_name+'_'+orientations_name, 
                    carbon_list = [5,1,2], A_list = A_list, tomo_list = tomo_list, 
                    use_composite_pi=True,
                    parity_orientations = orientations, debug=False)




    if test_nobranching_noinvert:   
        mmtA_list = ['X','X']
        tomo_lists = [['X','X']]      
        for jj,tomo_list in enumerate(tomo_lists):
            # print '-----------------------------------'
            # print 'press q to stop measurement cleanly'
            # print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            # GreenAOM.set_power(25e-6)
            # ins_counters.set_is_running(0)
            # optimiz0r.optimize(dims=['x','y','z'])

            # ssrocalibration(SAMPLE_CFG+'GHZ_'+tomo_name[jj])

            for kk,orientations in enumerate(orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                mmtA_name = mmtA_list[0]+mmtA_list[1]
                tomo_name = tomo_list[0]+tomo_list[1]
                orientations_name = orientations[0][0]+orientations[1][0]

                print 'mmtA: '+mmtA_name+ ' tomo: '+tomo_name
                print orientations

                NoBranching_no_invert_test(SAMPLE+'NoBranching_noinvert_C12_test_mmt_'+mmtA_name+'_'+'tomo'+tomo_name+'_'+orientations_name, carbon_list = [1,2], 
                    A_list = mmtA_list, tomo_list = tomo_list, parity_orientations = orientations, debug=False)
