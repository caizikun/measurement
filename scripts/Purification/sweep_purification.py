'''
Allows for sweeps of general parameters within the purification sequence.
Only supports single setup experiments with one specific adwin script
NK 2016
'''

import numpy as np
import qt 
import purify_slave; reload(purify_slave)
import msvcrt
name = qt.exp_params['protocols']['current']

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False
def print_adwin_stuff(m):
    print m.params['cycle_duration']
    print m.params['SP_duration']
    print m.params['wait_after_pulse_duration']
    print m.params['MBI_attempts_before_CR']
    print m.params['Dynamical_stop_ssro_threshold']
    print m.params['Dynamical_stop_ssro_duration']
    print m.params['is_master']
    print m.params['is_two_setup_experiment'] 
    print m.params['do_carbon_init'] # goes to mbi sequence, ends with tomography
    print m.params['do_C_init_SWAP_wo_SSRO']
    print m.params['do_swap_onto_carbon']
    print m.params['do_SSRO_after_electron_carbon_SWAP']
    print m.params['do_LDE_2']
    print m.params['do_phase_correction'             ]
    print m.params['do_purifying_gate'               ]
    print m.params['do_carbon_readout'               ]
    print m.params['wait_for_awg_done_timeout_cycles'] 
    print m.params['adwin_comm_safety_cycles'        ] 
    print m.params['adwin_comm_timeout_cycles'       ] 
    print m.params['remote_awg_trigger_channel'      ]
    print m.params['invalid_data_marker_do_channel'  ]  


def prepare(m, setup=qt.current_setup,name=qt.exp_params['protocols']['current']):
    '''
    loads all necessary msmt parameters
    '''
    m.params['setup']=setup
    sample_name = qt.exp_params['samples']['current']
    name = qt.exp_params['protocols']['current']
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO+C13'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][name]['pulses'])
    m.params.from_dict(qt.exp_params['samples'][sample_name])

    ### soon not necessary anymore.
    m.params['Nr_C13_init']     = 0 # Not necessary (only for adwin: C13 MBI)
    m.params['Nr_MBE']          = 0 # Not necessary (only for adwin: C13 MBI)
    m.params['Nr_parity_msmts'] = 0 # Not necessary (only for adwin: C13 MBI)

    if setup == 'lt1':
        import params_lt1
        reload(params_lt1)
        for k in params_lt1.params_lt1:
            m.params[k] = params_lt1.params_lt1[k]

        ### below: copied from bell and commented out for later
    elif setup == 'lt4' :
        import params_lt4
        reload(params_lt4)
        m.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt4.params_lt4:
            m.params[k] = params_lt4.params_lt4[k]
        # msmt.params['MW_BellStateOffset'] = 0.0
        # bseq.pulse_defs_lt4(msmt)
    elif setup == 'lt3' :
         import params_lt3
         reload(params_lt3)
         m.AWG_RO_AOM = qt.instruments['PulseAOM']
         for k in params_lt3.params_lt3:
             m.params[k] = params_lt3.params_lt3[k]
         #msmt.params['MW_BellStateOffset'] = 0.0
         #bseq.pulse_defs_lt3(msmt)
    else:
        print 'Sweep_purification.py: invalid setup:', setup

    if not(hasattr(m,'joint_params')):
        m.joint_params = {}
    import joint_params
    reload(joint_params)
    for k in joint_params.joint_params:
        m.joint_params[k] = joint_params.joint_params[k]

    if setup == m.joint_params['master_setup']:
        m.params['is_master'] = 1
    else:
        m.params['is_master'] = 0

    m.params['send_AWG_start'] = 1
    m.params['sync_during_LDE'] = 1
    m.params['wait_for_AWG_done'] = 0
    m.params['do_general_sweep']= 1
    m.params['trigger_wait'] = 1


def run_sweep(m,debug=True, upload_only=True,save_name='',multiple_msmts=False,autoconfig = True):

    if autoconfig:
        m.autoconfig()    

    m.generate_sequence()

    if upload_only:
        return



    m.setup(debug=debug)

    if not debug:
        m.run(autoconfig=False, setup=False)

        if save_name != '':
            m.save(save_name)
        else:
            m.save()

        if multiple_msmts:
            return

        print 'i was here'
        m.finish()


def turn_all_sequence_elements_off(m):
    """
    turns all parts of the AWG sequence off. except for do_LDE_1
    running this function before sequence generation will generate 
    Barrett & Kok like sequences
    """

    m.params['is_two_setup_experiment'] = 0
    m.params['do_N_MBI']                = 0 
    m.params['do_carbon_init']          = 0
    m.params['do_C_init_SWAP_wo_SSRO']  = 0
    m.params['MW_before_LDE1']          = 0
    m.params['LDE_1_is_init']           = 0
    m.params['do_swap_onto_carbon']     = 0
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 0
    m.params['do_LDE_2']                = 0
    m.params['do_phase_correction']     = 0 
    m.params['do_purifying_gate']       = 0 
    m.params['do_carbon_readout']       = 0 
    m.params['do_repump_after_LDE2'] = 0
    m.params['PLU_during_LDE'] = 0

    ### Should be made: PQ_during_LDE = 0??? Most of the time we don't need it.
    ### interesting to look at the spinpumping though...

def turn_all_sequence_elements_on(m):
    """
    turns all parts of the AWG sequence on. except for do_LDE_1
    Running this function before generating the sequence
    creates the full purification sequence
    """

    m.params['is_two_setup_experiment'] = 1
    m.params['do_N_MBI']                = 0 # we never do this (or might actually do this... depends)
    m.params['do_carbon_init']          = 1
    m.params['do_C_init_SWAP_wo_SSRO']  = 1
    m.params['LDE_1_is_el_init']        = 0
    m.params['do_swap_onto_carbon']     = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2']                = 1
    m.params['do_phase_correction']     = 1 
    m.params['do_purifying_gate']       = 1 
    m.params['do_carbon_readout']       = 1 
    m.params['do_repump_after_LDE2'] = 0
    m.params['PLU_during_LDE'] = 1


def repump_speed(name,debug = False,upload_only=False):
    """
    Initializes the electron in ms = -1 
    and sweeps the repump duration at the beginning of LDE_1
    """

    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 101
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['MW_before_LDE1'] = 1 # allows for init in -1 before LDE
    m.params['LDE_1_is_init']  = 1
    m.params['input_el_state'] = 'mZ'
    m.params['MW_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE_attempts'] = 1

    # m.params['Hermite_pi_amp'] = 0
    ### prepare sweep
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_SP_duration'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(0.0,2.e-6,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e9

    ### upload and run

    run_sweep(m,debug = debug,upload_only = upload_only)


def sweep_average_repump_time(name,do_Z = False,upload_only = False,debug=False):
    """
    sweeps the average repump time.
    runs the measurement for X and Y tomography. Also does positive vs. negative RO
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep']    = 1
    m.params['do_carbon_init']  = 1 
    m.params['do_carbon_readout']  = 1 

    m.joint_params['LDE_attempts'] = 150
    m.params['MW_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 1

    ### define sweep
    m.params['general_sweep_name'] = 'average_repump_time'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(-0.3e-6,0.8e-6,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e6

    
    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    if do_Z:
        for t in ['Z']:
            m.joint_params['LDE_attempts'] = 300
            if breakst:
                break
            for ro in ['positive','negative']:
                breakst = show_stopper()
                if breakst:
                    break
                save_name = t+'_'+ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                m.params['do_C_init_SWAP_wo_SSRO'] = 1

                run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig=autoconfig)
                autoconfig = False

    else:
        for t in ['X','Y']:
            if breakst:
                break
            for ro in ['positive','negative']:
                breakst = show_stopper()
                if breakst:
                    break
                m.params['carbon_init_method'] = 'MBI'
                m.params['do_C_init_SWAP_wo_SSRO'] = 0
                save_name = t+'_'+ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig=autoconfig)
                autoconfig = False

    m.finish()


def sweep_number_of_reps(name,do_Z = False, upload_only = False, debug=False):

    """
    runs the measurement for X and Y tomography. Also does positive vs. negative RO
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 15
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep']    = 1
    m.params['do_carbon_init']  = 1
    m.params['do_carbon_readout']  = 1 

    m.params['MW_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 0

    ### calculate the sweep array
    minReps = 1
    maxReps = 500
    step = int((maxReps-minReps)/pts)+1
    ### define sweep
    m.params['general_sweep_name'] = 'LDE_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,maxReps,step)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    print 'sweep pts', np.arange(minReps,maxReps,step)
    ### loop over tomography bases and RO directions upload & run

    breakst = False
    autoconfig = True
    if do_Z:
        for t in ['Z']:
            if breakst:
                break
            for ro in ['positive','negative']:
                breakst = show_stopper()
                if breakst:
                    break
                print t,ro
                m.params['do_C_init_SWAP_wo_SSRO'] = 1
                save_name = t+'_'+ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                run_sweep(m,debug = debug, upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig = autoconfig)
                autoconfig = False

    else:
        for t in ['X','Y']:
            if breakst:
                break
            for ro in ['positive','negative']:
                breakst = show_stopper()
                if breakst:
                    break
                m.params['do_C_init_SWAP_wo_SSRO'] = 0
                m.params['carbon_init_method'] = 'MBI'
                print t,ro
                save_name = t+'_'+ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                run_sweep(m,debug = debug, upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig=autoconfig)
                autoconfig = False

    m.finish()


def characterize_el_to_c_swap(name, upload_only = False,debug=False):
    """
    runs the measurement for X and Y tomography. Also does positive vs. negative RO
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    m.params['reps_per_ROsequence'] = 350

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep']    = 1
    m.params['do_carbon_init']  = 1 # 
    m.params['do_C_init_SWAP_wo_SSRO'] = 1 # 
    m.params['do_carbon_readout']  = 1 
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    # m.params['do_C_init_SWAP_wo_SSRO'] = 0
    m.params['LDE_1_is_init'] = 1 # only use a preparational value
    m.params['MW_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 0 # no pi pulses in this sequence.

    ### define sweep
    m.params['general_sweep_name'] = 'Tomography_bases'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = [['X'],['Y'],['Z']]
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    ### prepare phases and pulse amplitudes for LDE1 (i.e. the initialization of the electron spin)
    el_state_list = ['mZ']
    
    print m.params['carbon_init_method']

    x_phase = m.params['X_phase']
    y_phase = m.params['Y_phase']

    first_mw_phase_dict = { 'X' :   y_phase, 
                            'mX':   y_phase + 180,
                            'Y' :   x_phase + 180, 
                            'mY':   x_phase, 
                            'Z' :   x_phase + 180, 
                            'mZ':   x_phase}

    first_mw_amp_dict = {   'X' :   m.params['Hermite_pi2_amp'], 
                            'mX':   m.params['Hermite_pi2_amp'],
                            'Y' :   m.params['Hermite_pi2_amp'], 
                            'mY':   m.params['Hermite_pi2_amp'], 
                            'Z' :   0, 
                            'mZ':   m.params['Hermite_pi_amp']}

    first_mw_length_dict = {'X' :   m.params['Hermite_pi2_length'], 
                            'mX':   m.params['Hermite_pi2_length'],
                            'Y' :   m.params['Hermite_pi2_length'], 
                            'mY':   m.params['Hermite_pi2_length'], 
                            'Z' :   m.params['Hermite_pi_length'], 
                            'mZ':   m.params['Hermite_pi_length']}                        



    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    for el_state in el_state_list:
        if breakst:
            break
        for ro in ['positive','negative']:
            breakst = show_stopper()
            if breakst:
                break

            save_name = 'el_state_'+ el_state +'_'+ro
            m.params['input_el_state'] = el_state
            m.params['mw_first_pulse_amp'] = first_mw_amp_dict[el_state]
            m.params['mw_first_pulse_length'] = first_mw_length_dict[el_state]
            m.params['mw_first_pulse_phase'] = first_mw_phase_dict[el_state]
            m.params['carbon_readout_orientation'] = ro

            run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig = autoconfig)
            autoconfig = False

    m.finish()

def calibrate_LDE_phase(name, upload_only = False,debug=False):
    """
    uses LDE 1 and swap to initialize the carbon in state |x>.
    Sweeps the number of repetitions (LDE2) and performs tomography of X.
    Is used to calibrate the acquired phase per LDE repetition.
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 20
    
    m.params['reps_per_ROsequence'] = 350

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_carbon_init'] = 1
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_C_init_SWAP_wo_SSRO']  = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2'] = 1
    m.params['Tomography_bases'] = ['X']
    m.params['do_carbon_readout']  = 1

    ### awg sequencing logic / lde parameters
    m.params['LDE_1_is_init'] = 1 
    m.joint_params['opt_pi_pulses'] = 0 
    m.params['input_el_state'] = 'Z'
    m.params['mw_first_pulse_phase'] = m.params['X_phase'] + 180
    m.params['mw_first_pulse_amp'] = 0
    m.params['mw_first_pulse_length'] = m.params['Hermite_pi_length']

    ### calculate sweep array
    minReps = 1
    maxReps = 20
    step = int((maxReps-minReps)/pts)+1

    ### define sweep
    m.params['do_general_sweep']    = 1
    m.params['general_sweep_name'] = 'LDE_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,maxReps,step)
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    #### increase the detuning for more precise measurements
    m.params['phase_detuning'] = 80.6
    phase_per_rep = m.params['Carbon_LDE_phase_correction_list'][m.params['carbon']]
    m.params['Carbon_LDE_phase_correction_list'][m.params['carbon']] = phase_per_rep + m.params['phase_detuning']

                     
    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    for ro in ['positive','negative']:
        breakst = show_stopper()
        if breakst:
            break
        save_name = 'X_'+ro
        m.params['carbon_readout_orientation'] = ro

        run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig = autoconfig)
        autoconfig = False
    m.finish()

def calibrate_dynamic_phase_correct(name, upload_only = False,debug=False):
    """
    same as calibrate LDE_phase but here we add a dynamic phase correct element and
    sweep the number of repetitions of that element.
    Serves as a calibration for the adwin
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 15
    
    m.params['reps_per_ROsequence'] = 350

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_carbon_init'] = 1
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_C_init_SWAP_wo_SSRO']  = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2'] = 1
    m.params['do_phase_correction'] = 1
    m.params['Tomography_bases'] = ['X']
    m.params['do_carbon_readout']  = 1
    m.params['MW_during_LDE'] = 1

    ### awg sequencing logic / lde parameters
    m.params['LDE_1_is_init'] = 1 
    m.joint_params['opt_pi_pulses'] = 0 
    m.params['input_el_state'] = 'Z'
    m.params['mw_first_pulse_phase'] = m.params['X_phase']
    m.params['mw_first_pulse_amp'] = 0
    m.joint_params['LDE_attempts'] = 1


    ### calculate sweep array
    minReps = 2
    maxReps = 90.
    step = int((maxReps-minReps)/pts)+1

    ### define sweep
    m.params['do_general_sweep']    = 1
    m.params['general_sweep_name'] = 'phase_correct_max_reps'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,maxReps,step)
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    ### for the analyis
    m.params['phase_detuning'] = 0 
                     
    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    for ro in ['positive','negative']:
        breakst = show_stopper()
        if breakst:
            break
        save_name = 'X_'+ro
        m.params['carbon_readout_orientation'] = ro

        run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig = autoconfig)
        autoconfig = False

    m.finish()

def apply_dynamic_phase_correction(name,debug=False,upload_only = False,PLU = False):
    """
    combines all carbon parts of the sequence in order to 
    verify that all parts of the sequence work correctly.
    Can be used to calibrate the phase per LDE attempt!
    Here the adwin performs dynamic phase correction such that an
    initial carbon state |x> (after swapping) is rotated back onto itself and correctly read out.
    Has the option to either sweep the repetitions of LDE2 (easy mode)
    Or use the plu to trigger events. <-- still needs to be programmed.
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 15
    
    m.params['reps_per_ROsequence'] = 350

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_carbon_init'] = 1
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2'] = 1
    m.params['do_phase_correction'] = 1
    m.params['Tomography_bases'] = ['X']
    m.params['do_purifying_gate'] = 1
    m.params['do_carbon_readout']  = 0
    m.params['do_repump_after_LDE2'] = 1

    if PLU:
        m.params['PLU_during_LDE'] = 1

    ### awg sequencing logic / lde parameters
    m.params['LDE_1_is_init'] = 1 
    m.joint_params['opt_pi_pulses'] = 0 
    m.params['input_el_state'] = 'Z'
    m.params['mw_first_pulse_phase'] = m.params['X_phase']
    # m.params['mw_first_pulse_amp'] = 0

    #### increase the detuning for more precise measurements
    m.params['phase_detuning'] = 10
    phase_per_rep = m.params['phase_per_sequence_repetition']
    m.params['phase_per_sequence_repetition'] = phase_per_rep + m.params['phase_detuning']



    ### define sweep
    m.params['do_general_sweep']    = 1
    m.params['general_sweep_name'] = 'LDE_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(1,61,6)#np.arange(minReps,maxReps,step)
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

                     
    ### loop over tomography bases and RO directions upload & run
    breakst = False


    run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = False)

def check_phase_offset_after_LDE2(name,debug=False,upload_only = False):
    """
    Goal of this measurement: calibrate the phase offset after LDE attempts and phase correction.
    This is the last verification measurement.
    Carbon is initialized in X.
    After LDE2 the electron is in a superposition. It is decoupled by via the phase feedback and properly stopped by the adwin.
    Then the electron is rotated back onto an eigenstate. 
    We perform a carbon gate around X/Y, RO the electron state and measure the carbon in Z afterwards.
    The idea is to preserve the carbon in X for the purifying gate.
    Such that a Y rotation gives maximum Z RO and an X rotation for the purfiying gate returns 0 contrast. 
    This measurement sweeps the tomography bases of the carbon.
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 1
    
    m.params['reps_per_ROsequence'] = 350

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_carbon_init'] = 1
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_C_init_SWAP_wo_SSRO'] = 1 # we still have to decide on this
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2'] = 1
    m.params['do_phase_correction'] = 1
    m.params['do_purifying_gate'] = 1
    m.params['do_carbon_readout']  = 1
    m.joint_params['LDE_attempts'] = 5

    ### awg sequencing logic / lde parameters
    m.params['LDE_1_is_init'] = 1 
    m.joint_params['opt_pi_pulses'] = 0 
    m.params['input_el_state'] = 'Z'
    m.params['mw_first_pulse_phase'] = m.params['Y_phase'] + 180

    m.params['total_phase_offset_after_sequence'] = m.params['total_phase_offset_after_sequence']+90
    

    ### define sweep
    m.params['do_general_sweep']    = 1

    m.params['general_sweep_name'] = 'Tomography_bases'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = ['X','Y','Z']
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']


    ### loop over RO directions upload & run
    breakst = False
    autoconfig = True
    for ro in ['positive','negative']:
        breakst = show_stopper()
        if breakst:
            break
        save_name = ro
        m.params['carbon_readout_orientation'] = ro

        run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig= autoconfig)
        autoconfig = False

    m.finish()

if __name__ == '__main__':

    # repump_speed(name+'_repump_speed',upload_only = False)

    # sweep_average_repump_time(name+'_Sweep_Repump_time_Z',do_Z = True,debug = False)
    # sweep_average_repump_time(name+'_Sweep_Repump_time_X',do_Z = False,debug=False)

    # sweep_number_of_reps(name+'_sweep_number_of_reps_X',do_Z = False)
    # sweep_number_of_reps(name+'_sweep_number_of_reps_Z',do_Z = True)

    # characterize_el_to_c_swap(name+'_Swap_el_to_C')

    calibrate_LDE_phase(name+'_LDE_phase_calibration',upload_only = False)
    # calibrate_dynamic_phase_correct(name+'_Phase_compensation_calibration',upload_only = False)

    # apply_dynamic_phase_correction(name+'_ADwin_phase_compensation',upload_only = False)
    # apply_dynamic_phase_correction(name+'_Compensate_LDE_phase', PLU = True)

    #check_phase_offset_after_LDE2(name+'_phase_offset_after_LDE',upload_only = False)