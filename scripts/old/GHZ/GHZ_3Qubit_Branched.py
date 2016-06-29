'This script runs the GHZ measurement, branching out after each measurement and the corresponding result'


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


def feedforward_flips(tomo_list):
    ###this defines which outcomes to flip, for a ppp (positive-positive-positive) readout
    ###the reference (never flipped) is the 111 readout, corresponding to a 'basic' GHZ state.
    if tomo_list == ['X','X','X']:
        flips = ['000','011','101','110']
    elif tomo_list == ['X','Y','Y']:
        flips = ['000','001','010','011']
    elif tomo_list == ['Y','X','Y']:
        flips = ['000','001','100','101']
    elif tomo_list == ['Y','Y','X']:
        flips = ['000','010','100','110']
    elif tomo_list == ['Z','Z','I']:
        flips = ['010','011','100','101']
    elif tomo_list == ['Z','I','Z']:
        flips = ['001','011','100','110']
    elif tomo_list == ['I','Z','Z']:
        flips = ['001','010','101','110']
    else:
        flips = []

    return(flips)

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

def GHZ(name, 
    carbon_list = [1,2,5],
    xyy_list = ['X','Y','Y'],
    yxy_list = ['Y','X','Y'],
    yyx_list = ['Y','Y','X'],
    tomo_list = ['X','X','X'],
    feedforward = False,
    debug = False,
    parity_orientations = ['positive','positive','positive','positive'],
    final_phases = [0,0,0],
    initialize_carbons = False,
    init_carbon_list = [1,2,5],
    init_carbon_states = 3*['up'],
    init_carbon_methods = 3*['swap'],
    init_carbon_thresholds = [0,0,0],
    tomo_carbons = [1,2,5],
    electron_RO = False,
    mmtA_electron_RO = False,
    ):

    m = DD.GHZ_ThreeQB(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] = 4000
    m.params['pts'] = 1

    ##### Carbon initializations params
    m.params['initialize_carbons'] = initialize_carbons
    if initialize_carbons:
        m.params['Nr_C13_init'] = len(init_carbon_list)
        m.params['carbon_init_list']        = init_carbon_list
        m.params['init_state_list']         = init_carbon_states
        m.params['init_method_list']        = init_carbon_methods
        m.params['C13_MBI_threshold_list']  = init_carbon_thresholds
    else:
        m.params['Nr_C13_init'] = 0
        m.params['carbon_init_list']        = []
        m.params['init_state_list']         = []
        m.params['init_method_list']        = []
        m.params['C13_MBI_threshold_list']  = []
    

    m.params['Nr_MBE']              = 0 
    #m.params['MBE_bases']           = []
    #m.params['MBE_threshold']       = 1
    m.params['Nr_parity_msmts']     = 3
    m.params['add_wait_gate'] = False
    m.params['wait_in_msm1']  = False

    ###### RO xyy params
    m.params['Parity_xyy_do_RO_electron'] = mmtA_electron_RO
    if mmtA_electron_RO:
        m.params['Parity_xyy_do_init_pi2'] = False
        m.params['Invert_Parity_xyy_carbon_list'] = carbon_list
        m.params['Invert_Parity_xyy_RO_list'] = ['I','I','X']
        m.params['Parity_xyy_carbon_list'] = []
        m.params['Parity_xyy_RO_list'] = []
    else:
        m.params['Parity_xyy_do_init_pi2'] = True
        m.params['Invert_Parity_xyy_carbon_list'] = carbon_list
        m.params['Invert_Parity_xyy_RO_list'] = xyy_list
        m.params['Parity_xyy_carbon_list'] = carbon_list
        m.params['Parity_xyy_RO_list'] = xyy_list
    m.params['Parity_xyy_RO_orientation'] = parity_orientations[0]

    m.params['Invert_xyy_do_final_pi2'] = False
    m.params['Parity_yxy_do_init_pi2'] = False
    m.params['Parity_yxy_carbon_list'] = carbon_list
    m.params['Parity_yxy_RO_list'] = yxy_list
    m.params['Parity_yxy_RO_orientation'] = parity_orientations[1]

    ###### invert yxy and RO yyx params
    m.params['Invert_yxy_do_final_pi2'] = False
    m.params['Parity_yyx_do_init_pi2'] = False
    m.params['Parity_yyx_carbon_list'] = carbon_list
    m.params['Parity_yyx_RO_list'] = yyx_list
    m.params['Parity_yyx_RO_orientation'] = parity_orientations[2]
    
    ###### invert yyx and RO TOMO params
    m.params['RO_electron'] = electron_RO

    m.params['Invert_yyx_do_final_pi2'] = False
    m.params['Tomo_do_init_pi2'] = False

    if electron_RO:
        m.params['Invert_yyx_do_final_pi2'] = True
        m.params['Tomo_do_init_pi2'] = False

    for s in tomo_list:
        if 'Z' in s:
            print 'tomography contains Z; doing pi/2 between invertRO and RO'
            m.params['Invert_yyx_do_final_pi2'] = True
            m.params['Tomo_do_init_pi2'] = True
    m.params['Tomo_carbon_list'] = tomo_carbons
    m.params['Tomo_RO_orientation'] = parity_orientations[3]
    m.params['final_phases'] = final_phases

    m.params['Tomo_RO_list'] = tomo_list

    m.params['flip_000'] = False
    m.params['flip_001'] = False
    m.params['flip_010'] = False
    m.params['flip_011'] = False
    m.params['flip_100'] = False
    m.params['flip_101'] = False
    m.params['flip_110'] = False
    m.params['flip_111'] = False

    if feedforward:
        flip_states = feedforward_flips(tomo_list)
        print('flipping before orientation correction:')
        print(flip_states)

        ###correct for the orientations when determining which outcomes have to be flipped.
        for j in np.arange(3):
            if parity_orientations[j] == 'negative':
                for k,state in enumerate(flip_states):
                    outcome = state[j]
                    outcome_n = np.mod(int(state[j])+1,2)
                    state = state[:j] + str(outcome_n) + state[(j+1):]
                    flip_states[k] = state
        print('flipping after orientation correction:')
        print(flip_states)

        if '000' in flip_states:
            m.params['flip_000'] = True
        if '001' in flip_states:
            m.params['flip_001'] = True 
        if '010' in flip_states:
            m.params['flip_010'] = True
        if '011' in flip_states:
            m.params['flip_011'] = True
        if '100' in flip_states:
            m.params['flip_100'] = True
        if '101' in flip_states:
            m.params['flip_101'] = True
        if '110' in flip_states:
            m.params['flip_110'] = True
        if '111' in flip_states:
            m.params['flip_111'] = True

    funcs.finish(m, upload =True, debug=debug)

def GHZ_debug(name, 
    carbon_list = [1,2,5],
    A_list = ['I','I','X'],
    tomo_list = ['Z','Z','I'],
    feedforward = False,
    debug = False,
    parity_orientations = ['positive','positive'],
    final_phases = [0,0,0], 
    do_invert_RO=True,
    initialize_carbons=False):


    m = DD.GHZ_Debug_ZZTomo(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] = 1200
    m.params['pts'] = 1

    ##### Carbon initializations params
    m.params['initialize_carbons'] = initialize_carbons
    if initialize_carbons:
        m.params['Nr_C13_init'] = len(init_carbon_list)
        m.params['carbon_init_list']        = init_carbon_list
        m.params['init_state_list']         = init_carbon_states
        m.params['init_method_list']        = init_carbon_methods
        m.params['C13_MBI_threshold_list']  = init_carbon_thresholds
    else:
        m.params['Nr_C13_init'] = 0
        m.params['carbon_init_list']        = []
        m.params['init_state_list']         = []
        m.params['init_method_list']        = []
        m.params['C13_MBI_threshold_list']  = []
    

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


    m.params['do_invert_RO']=do_invert_RO

    if do_invert_RO:
        m.params['Invert_A_do_final_pi2'] = False
        m.params['Tomo_do_init_pi2'] = False
    else:
        m.params['Invert_A_do_final_pi2'] = False
        m.params['Tomo_do_init_pi2'] = True        

    for s in tomo_list:
        if 'Z' in s:
            print 'tomography contains Z; doing pi/2 between invertRO and RO'
            m.params['Invert_A_do_final_pi2'] = True
            m.params['Tomo_do_init_pi2'] = True

    m.params['Tomo_carbon_list'] = carbon_list
    m.params['Tomo_RO_orientation'] = parity_orientations[1]
    m.params['final_phases'] = final_phases

    m.params['Tomo_RO_list'] = tomo_list

    funcs.finish(m, upload =True, debug=debug)


if __name__ == '__main__':

    #####Start with a test measurement 

    #GHZ(SAMPLE+'GHZ_C152_RO_XYY_YXY_YYX_XXX_Test', carbon_list = [1,5,2], tomography=False,
    #    xyy_list =['X','Y','Y'], yxy_list = ['Y','X','Y'], yyx_list=['Y','Y','X'], xxx_list=['X','X','X'], debug=False)

    sweep_orientations=False
    sweep_final_phases=False
    deterministic_GHZ=False
    test_ZII = False
    single_qubit_tomo=False
    two_qubit_tomo=False
    debug_X_Tomo=False
    tomography=True
    debug_ZZ_Tomo_3mmts=False
    debug_electron_readout= False
    debug_X_X_X_tomo = False

    orientations_list=[
        ['positive','positive','positive','positive'],
        ['positive','positive','positive','negative'],
        ['positive','positive','negative','positive'],
        ['positive','positive','negative','negative'],
        ['positive','negative','positive','positive'],
        ['positive','negative','positive','negative'],
        ['positive','negative','negative','positive'],
        ['positive','negative','negative','negative'],
        ['negative','positive','positive','positive'],
        ['negative','positive','positive','negative'],
        ['negative','positive','negative','positive'],
        ['negative','positive','negative','negative'],
        ['negative','negative','positive','positive'],
        ['negative','negative','positive','negative'],
        ['negative','negative','negative','positive'],
        ['negative','negative','negative','negative']
        ]

    debug_orientations_list=[
        ['positive','positive'],
        ['positive','negative'],
        ['negative','positive'],
        ['negative','negative'],
        ]        

    debug_3mmts_orientations_list=[
        ['positive','positive','positive','positive'],
        ['positive','positive','positive','negative'],
        # ['negative','positive','positive','positive'],
        # ['negative','positive','positive','negative'],
        ]  

    tomo_lists = [
        ['X','X','X'],
        # ['Z','Z','I'],
        # ['Z','I','Z'],
        # ['I','Z','Z'],
        # ['X','Y','Y'],
        # ['Y','X','Y'],
        # ['Y','Y','X']
        ]

    full_tomo_lists = [
        # ['X','I','I'],
        # ['Y','I','I'],
        # ['Z','I','I'],
        # ['I','X','I'],
        # ['I','Y','I'],
        # ['I','Z','I'],
        # ['I','I','X'],['I','I','Y'],
        # ['I','I','Z'],

        # ['X','X','I'],
        # ['X','Y','I'],
        ['X','Z','I'],
        #['Y','X','I'],
        #['Y','Y','I'],
        ['Y','Z','I']
        # ['Z','X','I'],['Z','Y','I'],
        # ['Z','Z','I'],

        # ['X','I','X'],
        # ['Y','I','X'],
        # ['Z','I','X'],
        # ['X','I','Y'],
        # ['Y','I','Y'],
        # ['Z','I','Y'],
        # ['X','I','Z'],['Y','I','Z'],['Z','I','Z'],

        # ['I','X','X'],
        # ['I','Y','X'],
        # ['I','Z','X'],
        # ['I','X','Y'],
        # ['I','Y','Y'],
        # ['I','Z','Y'],
        # ['I','X','Z'],['I','Y','Z'],['I','Z','Z'],

        # ['X','X','X'],
        # ['X','Y','X'],
        # ['X','Z','X'],
        # ['Y','X','X'],
        # ['Y','Y','X'],
        # ['Y','Z','X'],
        # ['Z','X','X'],['Z','Y','X'],
        # ['Z','Z','X'],

        # ['X','X','Y'],
        # ['X','Y','Y'],
        # ['X','Z','Y'],
        # ['Y','X','Y'],
        # ['Y','Y','Y'],['Y','Z','Y'],
        # ['Z','X','Y'],['Z','Y','Y'],
        # ['Z','Z','Y'],

        # ['X','X','Z'],['X','Y','Z'],
        # ['X','Z','Z'],
        # ['Y','X','Z'],['Y','Y','Z'],
        # ['Y','Z','Z'],
        # ['Z','X','Z'],['Z','Y','Z'],['Z','Z','Z']]
        ]

    single_qubit_tomo_lists = [
        # ['X','I','I'],
        ['I','X','I'],
        ['I','I','X'],
        ['Y','I','I'],
        ['I','Y','I'],
        ['I','I','Y'],
        ['Z','I','I'],
        ['I','Z','I'],
        ['I','I','Z']          
        ]

    two_qubit_tomo_lists = [
        # ['X','X','I'],
        # ['I','X','X'],
        # ['X','I','X'],
        # ['Y','Y','I'],
        # ['I','Y','Y'],
        # ['Y','I','Y'],
        # ['Z','Z','I'],
        # ['I','Z','Z'],
        # ['Z','I','Z'], 
        ['X','Y','I'],
        ['I','X','Y'],
        ['X','I','Y'],
        ['Y','X','I'],
        ['I','Y','X'],
        ['Y','I','X'],   
        ['X','Z','I'],
        ['I','X','Z'],
        ['X','I','Z'],
        ['Z','X','I'],
        ['I','Z','X'],
        ['Z','I','X'],     
        ['Y','Z','I'],
        ['I','Y','Z'],
        ['Y','I','Z'],
        ['Z','Y','I'],
        ['I','Z','Y'],
        ['Z','I','Y'],
        ]



    if sweep_orientations:

        for kk,orientations in enumerate(orientations_list):
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            print orientations
            print orientations_name[kk]

            GHZ(SAMPLE+'GHZ_C125_'+orientations_name[kk], carbon_list = [1,2,5], parity_orientations = orientations, debug=False)

    if deterministic_GHZ:

        for jj,tomo_list in enumerate(tomo_lists):
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            GreenAOM.set_power(25e-6)
            ins_counters.set_is_running(0)
            optimiz0r.optimize(dims=['x','y','z'])
            
            tomo_name = tomo_list[0]+tomo_list[1]+tomo_list[2]

            ssrocalibration(SAMPLE_CFG)

            for kk,orientations in enumerate(orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = orientations[0][0]+ orientations[1][0]+ orientations[2][0] +orientations[3][0]

                print tomo_name
                print orientations_name

                GHZ(SAMPLE+'GHZ_C125_feedforward_RO_'+tomo_name+'_'+orientations_name,feedforward=True, carbon_list = [1,2,5], 
                    tomo_list = tomo_list, parity_orientations = orientations, debug=False)

    if tomography:

        for jj,tomo_list in enumerate(full_tomo_lists):
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

            for kk,orientations in enumerate(orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = orientations[0][0]+ orientations[1][0]+ orientations[2][0] +orientations[3][0]
                tomo_name = tomo_list[0]+tomo_list[1]+tomo_list[2]
                print tomo_name
                print orientations_name

                GHZ(SAMPLE+'GHZ_C125_tomo_'+tomo_name+'_'+orientations_name,feedforward=False, carbon_list = [1,2,5], 
                    tomo_list = tomo_list, parity_orientations = orientations, 
                    initialize_carbons = False, init_carbon_list = [3], init_carbon_states =['up'], init_carbon_methods = ['swap'],
                    init_carbon_thresholds = [0], debug=False)

    if debug_X_X_X_tomo:
        tomo_lists = [['X'],['Y'],['Z']]

        for jj,tomo_list in enumerate(tomo_lists):
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

            for kk,orientations in enumerate(orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = ''.join([o[0] for o in orientations])
                tomo_name = ''.join([b for b in tomo_list])
                print 'tomo'+tomo_name
                print orientations_name


                GHZ(SAMPLE+'GHZ_C1_branched_X_X_X_tomo_'+tomo_name+'_'+orientations_name, feedforward=False,carbon_list = [1], 
                    xyy_list = ['X'],yxy_list=['X'],yyx_list=['X'],tomo_list = tomo_list, tomo_carbons=[1], parity_orientations = orientations, 
                    initialize_carbons=False,debug=False)


    if debug_X_Tomo:

        mmtA_list = ['X','X']
        tomo_lists = [['X','X']]#,['Y'],['Z']]

        for jj,tomo_list in enumerate(tomo_lists):
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            # GreenAOM.set_power(25e-6)
            # ins_counters.set_is_running(0)
            # optimiz0r.optimize(dims=['x','y','z'])

            # ssrocalibration(SAMPLE_CFG+'GHZ_'+tomo_name[jj])

            for kk,orientations in enumerate(debug_orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = ''.join([o[0] for o in orientations])
                mmtA_name = ''.join([a for a in mmtA_list])
                tomo_name = ''.join([b for b in tomo_list])

                print mmtA_name
                print tomo_name
                print orientations_name

                GHZ_debug(SAMPLE+'GHZ_C1_'+mmtA_name+'_'+'tomo'+tomo_name+'_'+orientations_name, carbon_list = [1,2], 
                    A_list = mmtA_list, tomo_list = tomo_list, parity_orientations = orientations, do_invert_RO=True, debug=False)
   
    if debug_ZZ_Tomo_3mmts:

        mmtA_list = ['I','I','X']
        #tomo_list = ['Y','Y','I']
        mmtC_list = ['Y','Y','I']

        for ii,mmtB_list in enumerate(debug_mmtB_lists):
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            #for jj,mmtC_list in enumerate(debug_mmtC_lists):
            for jj,tomo_list in enumerate(debug_mmtC_lists):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                # GreenAOM.set_power(25e-6)
                # ins_counters.set_is_running(0)
                # optimiz0r.optimize(dims=['x','y','z'])

                # ssrocalibration(SAMPLE_CFG+'GHZ_'+tomo_name[jj])

                for kk,orientations in enumerate(debug_3mmts_orientations_list):
                    print '-----------------------------------'
                    print 'press q to stop measurement cleanly'
                    print '-----------------------------------'
                    qt.msleep(2)
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                        break

                    mmtA_name = mmtA_list[0]+mmtA_list[1]+mmtA_list[2]
                    mmtB_name = mmtB_list[0]+mmtB_list[1]+mmtB_list[2]
                    mmtC_name = mmtC_list[0]+mmtC_list[1]+mmtC_list[2]
                    tomo_name = tomo_list[0]+tomo_list[1]+tomo_list[2]
                    orientations_name = orientations[0][0]+ orientations[1][0]+ orientations[2][0] +orientations[3][0]
                    print 'mmtA: '+mmtA_name+' mmtB: '+ mmtB_name+' mmtC: '+mmtC_name + ' tomo: '+tomo_name
                    print orientations_name
     
                    GHZ(SAMPLE+'GHZ_C125_debug_noinit_mmts_'+mmtA_name+'_'+mmtB_name+'_'+mmtC_name+'_'+'eRO_'+orientations_name, 
                        carbon_list = [1,2,5], xyy_list = mmtA_list, yxy_list = mmtB_list, yyx_list = mmtC_list, tomo_list = tomo_list,
                        parity_orientations = orientations, 
                        initialize_carbons = True, init_carbon_list = [5], init_carbon_states =['up'], init_carbon_methods = ['swap'],
                        init_carbon_thresholds = [0],
                        feedforward = False, debug=False)

    if debug_electron_readout:

        mmtA_list = ['I','I','X']
        mmtB_list = ['X','X','I']
        mmtC_list = ['Y','Y','I']
        tomo_list = []

        for kk,orientations in enumerate(debug_3mmts_orientations_list):
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            mmtA_name = 'electron_RO'#mmtA_list[0]+mmtA_list[1]+mmtA_list[2]
            mmtB_name = mmtB_list[0]+mmtB_list[1]+mmtB_list[2]
            mmtC_name = mmtC_list[0]+mmtC_list[1]+mmtC_list[2]
            tomo_name = 'electron_RO'
            orientations_name = orientations[0][0]+ orientations[1][0]+ orientations[2][0] +orientations[3][0]
            print 'mmtA: '+mmtA_name+' mmtB: '+ mmtB_name+' mmtC: '+mmtC_name + ' tomo: '+tomo_name
            print orientations_name

            GHZ(SAMPLE+'GHZ_C125_debug_initZZ_mmts_'+mmtA_name+'_'+mmtB_name+'_'+mmtC_name+'_'+'eRO_'+orientations_name, 
                carbon_list = [1,2,5], xyy_list = mmtA_list, yxy_list = mmtB_list, yyx_list = mmtC_list, tomo_list = tomo_list, tomo_carbons=[],
                parity_orientations = orientations, 
                initialize_carbons = False, init_carbon_list = [3], init_carbon_states =['up'], init_carbon_methods = ['swap'],  
                init_carbon_thresholds = [0],
                electron_RO = True, mmtA_electron_RO = False, 
                feedforward = False, debug=False)   


    if sweep_final_phases:
        points = 10
        phases = np.linspace(-360,0,points)

        for kk,phase in enumerate(phases):
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break
            print phase
            GHZ(SAMPLE+'GHZ_C125_sweep_phases_'+str(phase)+'deg', carbon_list = [1,2,5], final_phases = [0,0,phase], debug=False)
           