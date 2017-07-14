'''
Allows for sweeps of general parameters within the purification sequence.
Only supports single setup experiments with one specific adwin script
NK 2016
'''

import numpy as np
import qt 
import purify_slave; reload(purify_slave)
import msvcrt
import time
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

def prepare_LT2_dummy_stuff(m):
    MW_parallel_shift = 0e-9
    qt.pulsar.define_channel(id='ch1', name='MW_Imod', type='analog', high=1.0, #name = 'MW_1'
        low=-1.0, offset=0., delay=200e-9+MW_parallel_shift, active=True) #DD
    qt.pulsar.define_channel(id='ch2', name='MW_Qmod', type='analog', high=1.0,  #name = 'MW_2'
        low=-1.0, offset=0., delay=200e-9+MW_parallel_shift, active=True) #DD # note measured delay on fast scope 2014-10-13: 59 ns
    qt.pulsar.define_channel(id='ch3', name='EOM_AOM_Matisse', type='analog', 
        high=1.0, low=-1.0, offset=0.0, delay=(490e-9 + 76e-9), active=True) #PH Changed from (490e-9+ 5e-9)
    qt.pulsar.define_channel(id='ch4', name='EOM_Matisse', type='analog', high=2.0,
        low=-2.0, offset=0., delay=(199e-9+100e-9-20e-9), active=True) #DD #measured delay on apd's (tail) 2014-10-13: 40 ns


    # marker channels
    qt.pulsar.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker', 
        high=2.0, low=0, offset=0., delay=256e-9+MW_parallel_shift, active=True) ##267e-9#DD #previous 267e-9# previous:289; measured 242e-9 on the scope made an error??2014-10-13
    qt.pulsar.define_channel(id='ch1_marker2', name='sync', type='marker', # HydraHarp Sync
        high=2.0, low=0, offset=0., delay=102e-9, active=True) #XX plug in/ calibrate delay

    # qt.pulsar.define_channel(id='ch2_marker1', name='plu_sync', type='marker', 
    #    high=2.0, low=0, offset=0, delay=182e-9, active=True)
    qt.pulsar.define_channel(id='ch2_marker2', name='self_trigger', type='marker', 
       high=2.0, low=0.0, offset=0.0, delay=0., active=True)
    qt.pulsar.define_channel(id='ch3_marker1', name='adwin_sync', type='marker', 
        high=2.0, low=0.0, offset=0., delay=0., active=True) 
    qt.pulsar.define_channel(id='ch3_marker2', name='adwin_count', type='marker', 
        high=2.0, low=0, offset=0., delay=0e-9, active=True)

    qt.pulsar.define_channel(id='ch4_marker1', name='AOM_Newfocus', type='marker',
        high=0.4, low=0.0, offset=0.0, delay=200e-9, active=True) #Do not change delay w.r.t. MWs! NK

    qt.pulsar.define_channel(id='ch4_marker2', name='AOM_Matisse', type='marker',
        high=0.4, low=0.0, offset=0.0, delay=200e-9, active=True) #Do not change delay w.r.t. MWs! NK


def prepare(m, setup=qt.current_setup,name=qt.exp_params['protocols']['current']):
    '''
    loads all necessary msmt parameters
    '''
    m.params['setup']=setup
    sample_name = qt.exp_params['samples']['current']
    name = qt.exp_params['protocols']['current']
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+delay'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO+C13'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][name]['pulses'])
    m.params.from_dict(qt.exp_params['samples'][sample_name])

    m.params['multiple_source'] = False
    # m.params['MW_switch_channel'] = 'None'

    ### soon not necessary anymore.
    m.params['Nr_C13_init']     = 0 # Not necessary (only for adwin: C13 MBI)
    m.params['Nr_MBE']          = 0 # Not necessary (only for adwin: C13 MBI)
    m.params['Nr_parity_msmts'] = 0 # Not necessary (only for adwin: C13 MBI)

    if setup == 'lt1':
        import params_lt1
        reload(params_lt1)
        for k in params_lt1.params_lt1:
            m.params[k] = params_lt1.params_lt1[k]


    elif setup == 'lt4' :
        import params_lt4
        reload(params_lt4)
        m.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt4.params_lt4:
            m.params[k] = params_lt4.params_lt4[k]

    elif setup == 'lt3' :
        import params_lt3
        reload(params_lt3)
        m.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt3.params_lt3:
            m.params[k] = params_lt3.params_lt3[k]

    elif setup == 'lt2' :
        prepare_LT2_dummy_stuff(m)
        print "WARNING: LT2 has only been used as a debugging setup, all parameters currently only haves dummy values"
        import params_lt4
        reload(params_lt4)
        m.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt4.params_lt4:
            m.params[k] = params_lt4.params_lt4[k]

        # import params_lt2
        # reload(params_lt2)
        # m.AWG_RO_AOM = qt.instruments['PulseAOM']
        # for k in params_lt2.params_lt2:
        #     m.params[k] = params_lt2.params_lt2[k]

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
        print("I'm the master")
    else:
        m.params['is_master'] = 0

    m.params['send_AWG_start'] = 1
    m.params['sync_during_LDE'] = 0
    m.params['wait_for_AWG_done'] = 0
    m.params['do_general_sweep']= 1
    m.params['trigger_wait'] = 1

    prepare_carbon_params(m)

def extract_carbon_param_list(m, param, carbons, etrans = None):
    if etrans is None:
        etrans = m.params['electron_transition']
    return [m.params['C%d_%s%s' % (c_id, param, etrans)] for c_id in carbons] 

def prepare_carbon_params(m):
    m.params['number_of_carbons'] = len(m.params['carbons'])
    m.params['nuclear_frequencies'] = np.array(extract_carbon_param_list(m, 'freq', m.params['carbons']))
    m.params['nuclear_phases_per_seqrep'] = np.array(extract_carbon_param_list(m, 'phase_per_LDE_sequence', m.params['carbons']))
    m.params['nuclear_phases_offset'] = np.array(extract_carbon_param_list(m, 'init_phase_correction_' + m.params['sequence_type'], m.params['carbons']))

    # add an empty entry for C0, as numpy arrays are 0-indexed but our carbon parameter array is 1-indexed
    m.params['Carbon_LDE_phase_correction_list'] = np.array([0.0] + extract_carbon_param_list(m, 'phase_per_LDE_sequence', list(range(1,m.params['number_of_carbon_params'] + 1))))
    if m.params['delay_feedback_use_calculated_phase_offsets'] > 0:
        m.params['Carbon_LDE_init_phase_correction_list'] = np.zeros(m.params['number_of_carbon_params'] + 1)
    else:
        m.params['Carbon_LDE_init_phase_correction_list'] = np.array([0.0] + extract_carbon_param_list(m, 'init_phase_correction', list(range(1,m.params['number_of_carbon_params'] + 1))))

def run_sweep(m,debug=True, upload_only=True,save_name='adwindata',multiple_msmts=False,autoconfig = True,mw=True,simplify_wfnames=False):

    if autoconfig:
        m.autoconfig()    

    m.generate_sequence(simplify_wfnames=simplify_wfnames)
    m.dump_AWG_seq()

    if (m.params['do_phase_fb_delayline'] > 0
        and m.params['delay_feedback_use_calculated_phase_offsets'] > 0):
        stddev = np.std(m.calculated_phase_offsets, axis=0)
        if np.max(stddev) > 0.1:
            print "Warning: phase offset differs per sweep point!"
        print m.calculated_phase_offsets
        m.params['nuclear_phases_offset'] = m.calculated_phase_offsets[0,:]
        m.adwin_set_var('nuclear_phases_offset', m.params['nuclear_phases_offset'])
    
    if upload_only:
        return



    m.setup(debug=debug,mw=mw)

    if not debug:
        m.run(autoconfig=False, setup=False, pq_save_name="pq_data/" + save_name)

        if save_name != '':
            m.save(save_name)
        else:
            m.save()

        if multiple_msmts:
            return

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
    m.params['do_LDE_1']                = 0
    m.params['do_C_init_SWAP_wo_SSRO']  = 0
    m.params['MW_before_LDE1']          = 0
    m.params['LDE_1_is_init']           = 0
    m.params['do_swap_onto_carbon']     = 0
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 0
    m.params['do_LDE_2']                = 0
    m.params['do_phase_correction']     = 0 
    m.params['do_purifying_gate']       = 0 
    m.params['do_carbon_readout']       = 0 
    m.params['do_repump_after_LDE2']    = 0
    m.params['PLU_during_LDE']          = 0
    m.params['is_TPQI']                 = 0
    m.params['force_LDE_attempts_before_init'] = 0
    m.params['no_repump_after_LDE1']    = 0
    m.params['do_phase_fb_delayline']   = 0
    m.params['do_delay_fb_pulses']      = 0
    ### Should be made: PQ_during_LDE = 0??? Most of the time we don't need it.
    ### interesting to look at the spinpumping though...

def turn_all_sequence_elements_on(m):
    """
    turns all parts of the AWG sequence on. except for do_LDE_1
    Running this function before generating the sequence
    creates the full purification sequence (no special sequences such as TPQI etc.)
    """

    m.params['is_two_setup_experiment'] = 1
    m.params['do_N_MBI']                = 0 # we never do this (or might actually do this... depends)
    m.params['do_carbon_init']          = 1
    m.params['do_LDE_1']                = 1
    m.params['do_C_init_SWAP_wo_SSRO']  = 1
    m.params['LDE_1_is_el_init']        = 0
    m.params['do_swap_onto_carbon']     = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2']                = 1
    m.params['do_phase_correction']     = 1 
    m.params['do_purifying_gate']       = 1 
    m.params['do_carbon_readout']       = 1 
    m.params['do_repump_after_LDE2']    = 0
    m.params['PLU_during_LDE']          = 1
    m.params['is_TPQI']                 = 0
    m.params['force_LDE_attempts_before_init'] = 0
    m.params['no_repump_after_LDE1']    = 0
    
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

    m.params['do_LDE_1'] = 1
    m.params['MW_before_LDE1'] = 1 # allows for init in -1 before LDE
    m.params['LDE_1_is_init']  = 1
    m.params['input_el_state'] = 'mZ'
    m.params['MW_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE1_attempts'] = 1

    # m.params['is_two_setup_experiment'] = 1

    # m.params['Hermite_pi_amp'] = 0
    ### prepare sweep
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_SP_duration'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(0.0,2.e-6,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e9
    m.params['is_two_setup_experiment']=0  

    ### upload and run

    run_sweep(m,debug = debug,upload_only = upload_only)


def sweep_number_of_reps_ionization(name,do_Z = False, upload_only = False, debug=False, ms0 = False):
    """
    Initializes the electron in ms = -1 or ms = 0
    and sweeps the number of LDE repetitions: used to measure ionization
    """

    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 15
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters

    m.params['do_LDE_1'] = 1
    m.params['LDE_1_is_init']  = 1
    m.params['input_el_state'] = 'mZ' ### mZ or Z!
    m.params['MW_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE1_attempts'] = 1
    m.params['do_LDE_2'] = 1


    if ms0:
        m.params['mw_first_pulse_amp'] = 0

    # else: ## do not manipulate the pi/2 pulse yet.
        # m.params['mw_first_pulse_amp'] = 0
        # m.params['mw_first_pulse_length'] = 100e-9
    ### calculate the sweep array
    minReps = 1
    maxReps = 2000
    step = int((maxReps-minReps)/pts)+1
    ### define sweep
    m.params['general_sweep_name'] = 'LDE2_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,maxReps,step)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    print 'sweep pts', np.arange(minReps,maxReps,step)
    ### loop over tomography bases and RO directions upload & run

    breakst = False
    run_sweep(m,debug = debug, upload_only = upload_only)
    m.finish()

def ionzation_sweep_pi_amp(name,upload_only = False, debug = False):
    """
    Initializes the electron in ms = -1 or ms = 0
    and sweeps the number of LDE repetitions: used to measure ionization
    """

    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    sweep_array  = np.array([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.925])
    pts = len(sweep_array)
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters

    m.params['do_LDE_1'] = 1
    m.params['LDE_1_is_init']  = 1
    m.params['input_el_state'] = 'mZ' ### mZ or Z!
    m.params['MW_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE1_attempts'] = 1
    m.joint_params['LDE2_attempts'] = 1700
    m.params['do_LDE_2'] = 1
    m.params['mw_first_pulse_amp'] = 0

    ### calculate the sweep array

    ### define sweep
    m.params['general_sweep_name'] = 'Hermite_pi_amp'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = sweep_array
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    ### loop over tomography bases and RO directions upload & run

    breakst = False
    run_sweep(m,debug = debug, upload_only = upload_only)
    m.finish()

def sweep_average_repump_time(name,do_Z = False,upload_only = False,debug=False):
    """
    sweeps the average repump time.
    runs the measurement for X and Y tomography. Also does positive vs. negative RO
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 26
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['is_two_setup_experiment'] = 0
    m.params['PLU_during_LDE'] = 0

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep']    = 1
    m.params['do_carbon_init']  = 1 
    m.params['do_carbon_readout']  = 1
    m.params['do_LDE_1'] = 1

    m.params['LDE1_attempts'] = 100
    m.joint_params['LDE1_attempts'] = 100
    m.params['MW_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 0

    ### define sweep
    m.params['general_sweep_name'] = 'average_repump_time'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(-0.5e-6,1.8e-6,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e6

    
    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    if do_Z:
        for t in ['Z']:
            m.joint_params['LDE1_attempts'] = 800
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
                # m.params['do_C_init_SWAP_wo_SSRO'] = 1
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
    pts = 20
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep']    = 1
    m.params['do_carbon_init']  = 1
    m.params['do_LDE_1'] = 1
    m.params['do_carbon_readout']  = 1
    # m.params['mw_first_pulse_amp'] = 0
    m.params['MW_during_LDE'] = 1
    # m.params['mw_first_pulse_amp'] = 0#m.params['Hermite_pi_amp']
    #m.params['mw_first_pulse_phase'] = m.params['Y_phase']# +180 
    #m.params['mw_first_pulse_length'] = m.params['Hermite_pi_length']
    m.joint_params['opt_pi_pulses'] = 0

    ### calculate the sweep array
    minReps = 1
    maxReps = 600
    step = int((maxReps-minReps)/pts)+1
    ### define sweep
    m.params['general_sweep_name'] = 'LDE1_attempts'
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
    m.params['reps_per_ROsequence'] = 1000

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['is_two_setup_experiment'] = 0
    m.params['PLU_during_LDE'] = 0

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep']    = 1
    m.params['do_carbon_init']  = 1 # 
    m.params['do_C_init_SWAP_wo_SSRO'] = 1 # 
    m.params['do_carbon_readout']  = 1 
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    # m.params['do_C_init_SWAP_wo_SSRO'] = 0
    m.params['do_LDE_1'] = 1
    m.params['LDE_1_is_init'] = 1 # only use a preparational value
    # m.params['MW_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 0 # no pi pulses in this sequence.


    # m.params['is_two_setup_experiment'] = 1
    # m.params['PLU_during_LDE'] = 0

    ### define sweep
    m.params['general_sweep_name'] = 'Tomography_bases'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = [['X'],['Y'],['Z']]
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    ### prepare phases and pulse amplitudes for LDE1 (i.e. the initialization of the electron spin)
    el_state_list = ['X','mX','Y','mY','Z']
    el_state_list = ['X','Y','Z']

    x_phase = m.params['X_phase']
    y_phase = m.params['Y_phase']

    first_mw_phase_dict = { 'X' :   y_phase, 
                            'mX':   y_phase + 180,
                            'Y' :   x_phase + 180, 
                            'mY':   x_phase, 
                            'Z' :   x_phase + 180, 
                            'mZ':   x_phase + 180}

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

def characterize_el_to_c_swap_success(name, upload_only = False,debug=False):
    """
    runs the measurement for X and Y tomography. Also does positive vs. negative RO
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    m.params['reps_per_ROsequence'] = 1000

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['is_two_setup_experiment'] = 0
    m.params['PLU_during_LDE'] = 0

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep'] = 0
    m.params['do_carbon_init']  = 1 # 
    m.params['do_C_init_SWAP_wo_SSRO'] = 1 # 
    m.params['do_carbon_readout']  = 0 
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 0
    # m.params['do_C_init_SWAP_wo_SSRO'] = 0
    m.params['do_LDE_1'] = 1
    m.params['LDE_1_is_init'] = 1 # only use a preparational value
    # m.params['MW_during_LDE'] = 0

    m.joint_params['opt_pi_pulses'] = 0 # no pi pulses in this sequence.


    # m.params['is_two_setup_experiment'] = 1
    # m.params['PLU_during_LDE'] = 0

    m.params['pts'] = 1

    ### prepare phases and pulse amplitudes for LDE1 (i.e. the initialization of the electron spin)
    el_state_list =  ['X','mX','Y','mY','Z','mZ']
    

    x_phase = m.params['X_phase']
    y_phase = m.params['Y_phase']

    first_mw_phase_dict = { 'X' :   y_phase, 
                            'mX':   y_phase + 180,
                            'Y' :   x_phase + 180, 
                            'mY':   x_phase, 
                            'Z' :   x_phase + 180, 
                            'mZ':   x_phase + 180}

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
       
        breakst = show_stopper()
        if breakst:
            break

        save_name = 'el_state_'+ el_state
        m.params['input_el_state'] = el_state
        m.params['mw_first_pulse_amp'] = first_mw_amp_dict[el_state]
        m.params['mw_first_pulse_length'] = first_mw_length_dict[el_state]
        m.params['mw_first_pulse_phase'] = first_mw_phase_dict[el_state]
        
        run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig = autoconfig)
        autoconfig = False

    m.finish()

def sweep_LDE_attempts_before_swap(name, upload_only = False,debug=False):
    """
    Sweeps the number of actual LDE attempts before doing the carbon swap via the final LDE attempt
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    m.params['reps_per_ROsequence'] = 350

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['is_two_setup_experiment'] = 1
    m.params['PLU_during_LDE'] = 0

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['is_two_setup_experiment'] = 0
    m.params['do_general_sweep']    = 1
    m.params['do_carbon_init']  = 1 # 
    m.params['do_C_init_SWAP_wo_SSRO'] = 1 # 
    m.params['do_carbon_readout']  = 1 
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_1'] = 1
    m.params['LDE_1_is_init'] = 1 # only use a preparational value
    m.joint_params['opt_pi_pulses'] = 1 # no pi pulses in this sequence.
    m.params['force_LDE_attempts_before_init'] = 1

    ### calculate the sweep array
    pts = 13
    m.params['pts'] = pts
    minReps = 1
    maxReps = 700
    step = int((maxReps-minReps)/pts)+1

    ### define sweep
    m.params['general_sweep_name'] = 'LDE1_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,maxReps,step)
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    ### we loop over different electron input states and therefore different tomography bases.
    ### this is done to get an idea whether or not the swap has some inherent asymmetry
    el_state_list = ['X','Y','Z']
    tomo_dict = {
    'X' : 'Z',
    'Y' : 'Y',
    'Z' : 'X'
    }



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

            tomo = tomo_dict[el_state]
            m.params['input_el_state'] = el_state
            m.params['Tomography_bases'] = [tomo]
            m.params['carbon_readout_orientation'] = ro
            save_name = tomo+'_'+ro
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
    # pts = 15
    ### calculate sweep array
    minReps = 1
    maxReps = 48
    step = 3

    #### increase the detuning for more precise measurements
    m.params['phase_detuning'] = 16.
    
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
    m.params['do_LDE_1'] = 1
    m.params['LDE_1_is_init'] = 1 
    m.joint_params['opt_pi_pulses'] = 0 
    m.params['input_el_state'] = 'Z'
    m.params['mw_first_pulse_phase'] = m.params['X_phase']
    # m.params['mw_first_pulse_amp'] = 0

    if len(m.params['carbons']) > 1:
        print("Warning: LDE phase calibration is only supported on one carbon at a time")

    carbon = m.params['carbons'][0]


    

    ### define sweep
    m.params['do_general_sweep']    = 1
    m.params['general_sweep_name'] = 'LDE2_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,maxReps,step)
    print m.params['general_sweep_pts']
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    m.params['Carbon_LDE_phase_correction_list'][carbon] += m.params['phase_detuning']
    m.params['nuclear_phases_per_seqrep'][0] += m.params['phase_detuning']

    print "Applied phase correction ", m.params['Carbon_LDE_phase_correction_list'][carbon]

                     
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

    m.params['use_old_feedback'] = 1

    ### general params
    #  pts = 15
    ### calculate sweep array
    minReps = 2
    maxReps = 15
    step = 1
    
    m.params['reps_per_ROsequence'] = 1500

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_carbon_init'] = 1
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_C_init_SWAP_wo_SSRO']  = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2'] = 1
    m.params['do_phase_correction'] = 0
    m.params['Tomography_bases'] = ['X']
    m.params['do_carbon_readout']  = 1
    m.params['do_dd_phase_correction_calibration'] = 1


    ### awg sequencing logic / lde parameters
    m.params['do_LDE_1'] = 1
    m.params['LDE_1_is_init'] = 1 
    m.joint_params['opt_pi_pulses'] = 0 
    m.params['input_el_state'] = 'Z'
    m.params['MW_during_LDE'] = 1
    m.params['mw_first_pulse_phase'] = m.params['X_phase']
    m.params['mw_first_pulse_amp'] = 0
    m.joint_params['LDE2_attempts'] = 1

    ### define sweep
    m.params['do_general_sweep']    = 1
    m.params['general_sweep_name'] = 'phase_correct_max_reps'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,int(maxReps),step)
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    ### for the analyis - phase detuning is always zero
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

def apply_dynamic_phase_correction(name,debug=False,upload_only = False,input_state = 'Z'):
    """
    combines all carbon parts of the sequence in order to 
    verify that all parts of the sequence work correctly.
    Can be used to calibrate the phase per LDE attempt!
    Here the adwin performs dynamic phase correction such that an
    initial carbon state |x> (after swapping) is rotated back onto itself and correctly read out.
    Has the option to either sweep the repetitions of LDE2 (easy mode)
    """
    m = purify_slave.purify_single_setup(name+'_'+input_state)
    prepare(m)

    m.params['use_old_feedback'] = 1

    ### general params
    pts = 10

    ### calculate sweep array
    minReps = 202
    maxReps = 300
    step = int((maxReps-minReps)/pts)+1

    #### increase the detuning for more precise measurements
    m.params['phase_detuning'] = 0.0
    
    m.params['reps_per_ROsequence'] = 1000

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_carbon_init'] = 1
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2'] = 1
    m.params['do_phase_correction'] = 1
    
    m.params['do_purifying_gate'] = 0
    m.params['do_carbon_readout']  = 1
    m.params['do_repump_after_LDE2'] = 1
    ####



    ### awg sequencing logic / lde parameters
    m.params['do_LDE_1'] = 1
    m.params['LDE_1_is_init'] = 1 
    m.joint_params['opt_pi_pulses'] = 0 
    m.params['input_el_state'] =  input_state

    tomo_dict = { 'X' : ['Z'],
                  'mX': ['Z'],
                  'Y' : ['Y'],
                  'mY': ['Y'],
                  'Z' : ['X'],
                  'mZ': ['X']}

    m.params['Tomography_bases'] = tomo_dict[input_state]
    # m.params['mw_first_pulse_phase'] = m.params['X_phase']


    phase_per_rep = m.params['phase_per_sequence_repetition']
    m.params['phase_per_sequence_repetition'] = phase_per_rep + m.params['phase_detuning']


    ### define sweep
    m.params['do_general_sweep']    = 1
    m.params['general_sweep_name'] = 'LDE2_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,maxReps,step)
    print m.params['general_sweep_pts']
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

     ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    for ro in ['positive','negative']:
        breakst = show_stopper()
        if breakst:
            break
        save_name = 'X_'+ro
        m.params['carbon_readout_orientation'] = ro

        print (m.params['phase_per_compensation_repetition'])
        run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig = autoconfig)
        autoconfig = False
    m.finish()

def check_phase_offset_after_LDE2(name,debug=False,upload_only = False,tomo = 'X'):
    """
    Goal of this measurement: calibrate the phase offset after LDE attempts and phase correction.
    This is the last verification measurement.
    Carbon is initialized in X.
    After LDE2 the electron is in a superposition. It is decoupled by via the phase feedback and properly stopped by the adwin.
    Then the electron is rotated back onto an eigenstate. 
    We perform a carbon gate around X/Y, RO the electron state and measure the carbon in Z afterwards.
    The idea is to preserve the carbon in X for the purifying gate.
    Such that a Y rotation gives maximum Z RO and an X rotation for the purfiying gate returns 0 contrast. 
    This measurement sweeps this offset phase
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 10
    
    m.params['reps_per_ROsequence'] = 1000

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_carbon_init'] = 1
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_C_init_SWAP_wo_SSRO'] = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2'] = 1
    m.params['do_phase_correction'] = 1
    m.params['do_purifying_gate'] = 1
    m.params['do_carbon_readout']  = 1
    m.joint_params['LDE2_attempts'] = 1

    ### awg sequencing logic / lde parameters
    m.params['do_LDE_1'] = 1
    m.params['LDE_1_is_init'] = 1 
    m.joint_params['opt_pi_pulses'] = 0 
    m.params['input_el_state'] = 'Z' ### 'Z' puts the carbon in 'X' and 'X' puts the carbon in 'Z'; Y puts in Y
    m.params['mw_first_pulse_phase'] = m.params['Y_phase'] #+ 180 #align with the phase of the purification gate.
    m.params['mw_first_pulse_amp'] = m.params['Hermite_pi2_amp']
    m.params['Tomography_bases'] = tomo

    
    ### define sweep
    m.params['do_general_sweep']    = 1

    m.params['general_sweep_name'] = 'total_phase_offset_after_sequence'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = m.params['total_phase_offset_after_sequence']+np.linspace(0.,540.,pts)
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = 'Phase offset after LDE2 (degrees)'
    m.params['sweep_pts'] = m.params['general_sweep_pts']-m.params['total_phase_offset_after_sequence']


    ### loop over RO directions upload & run
    breakst = False
    autoconfig = True
    for ro in ['positive','negative']:
        breakst = show_stopper()
        if breakst:
            break
        save_name = m.params['Tomography_bases']+'_'+ro
        m.params['carbon_readout_orientation'] = ro

        run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig= autoconfig)
        autoconfig = False

    m.finish()

def full_sequence_local(name,debug=False,upload_only = False,do_Z = False):
    """
    Initialize carbon in X via swap.
    do LDE 2 (sweep number of reps)
    perform purification gate
    perform final carbon RO (with branching depending on the electron RO result!)
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 10
    
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_carbon_init'] = 1
    m.params['do_LDE_1'] = 1
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_C_init_SWAP_wo_SSRO'] = 1 # we still have to decide on this
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2'] = 1
    m.params['do_phase_correction'] = 1
    m.params['do_purifying_gate'] = 1
    m.params['do_carbon_readout']  = 1
    m.params['is_two_setup_experiment'] = 0
    # m.joint_params['LDE_attempts'] = 20

    ### awg sequencing logic / lde parameters
    m.params['LDE_1_is_init'] = 1 
    m.joint_params['opt_pi_pulses'] = 0 

    m.params['mw_first_pulse_phase'] = m.params['Y_phase'] #align with the phase the first pi/2 of the purification gate.

    if do_Z:
        m.params['input_el_state'] = 'Y' #'Z' ### puts the carbon in 'X'
        m.params['Tomography_bases'] = ['Z']
    else:
        m.params['input_el_state'] = 'Z' #'Z' ### puts the carbon in 'X'
        m.params['Tomography_bases'] = ['X']



    ### define sweep
    m.params['do_general_sweep']    = 1

    ### calculate sweep array
    minReps = 1
    maxReps = 200
    step = int((maxReps-minReps)/pts)+1
    # step = 1

    ### define sweep
    m.params['do_general_sweep']    = 1
    m.params['general_sweep_name'] = 'LDE2_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,maxReps,step)
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    #### increase the detuning for more precise measurements
    m.params['phase_detuning'] = 0
    phase_per_rep = m.params['Carbon_LDE_phase_correction_list'][m.params['carbon']]
    m.params['Carbon_LDE_phase_correction_list'][m.params['carbon']] = phase_per_rep + m.params['phase_detuning']

                     
    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    for ro in ['positive','negative']:
        breakst = show_stopper()
        if breakst:
            break
        save_name = m.params['Tomography_bases'][0]+'_'+ro
        m.params['carbon_readout_orientation'] = ro

        run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig = autoconfig)
        autoconfig = False
    m.finish()


def analyse_simple_el_init_swap(name, debug=False, upload_only=False, input_state='Z',
                                simplify_wfnames=False, dry_run=False):
    """
    combines all carbon parts of the sequence in order to
    verify that all parts of the sequence work correctly.
    Can be used to calibrate the phase per LDE attempt!
    Here the adwin performs dynamic phase correction such that an
    initial carbon state |x> (after swapping) is rotated back onto itself and correctly read out.
    Has the option to either sweep the repetitions of LDE2 (easy mode)
    """
    """
        runs the measurement for X and Y tomography. Also does positive vs. negative RO
        """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    m.params['reps_per_ROsequence'] = 1000

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['is_two_setup_experiment'] = 0
    m.params['PLU_during_LDE'] = 0

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep'] = 1
    m.params['do_carbon_init'] = 1  #
    m.params['do_C_init_SWAP_wo_SSRO'] = 1  #
    m.params['do_carbon_readout'] = 1
    m.params['do_swap_onto_carbon'] = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    # m.params['do_C_init_SWAP_wo_SSRO'] = 0
    m.params['do_LDE_1'] = 0
    m.params['LDE_1_is_init'] = 0 # only use a preparational value
    m.params['simple_el_init'] = 1
    # m.params['MW_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 0  # no pi pulses in this sequence.

    # m.params['is_two_setup_experiment'] = 1
    # m.params['PLU_during_LDE'] = 0

    ### define sweep
    m.params['general_sweep_name'] = 'Tomography_bases'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = [['X'], ['Y'], ['Z']]
    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    ### prepare phases and pulse amplitudes for LDE1 (i.e. the initialization of the electron spin)
    el_state_list = ['X', 'mX', 'Y', 'mY', 'Z']
    el_state_list = ['X', 'Y', 'Z']

    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    for el_state in el_state_list:
        if breakst:
            break
        for ro in ['positive', 'negative']:
            breakst = show_stopper()
            if breakst:
                break

            save_name = 'el_state_' + el_state + '_' + ro
            m.params['input_el_state'] = el_state
            m.params['carbon_swap_el_states'] = [el_state]
            m.params['carbon_readout_orientation'] = ro
            run_sweep(m, debug=debug, upload_only=upload_only, multiple_msmts=True, save_name=save_name,
                      autoconfig=autoconfig)
            autoconfig = False

    m.finish()

def apply_dynamic_phase_correction_delayline(name,debug=False,upload_only = False,simplify_wfnames=False, dry_run=False, do_phase_offset_sweep=False):
    """
    combines all carbon parts of the sequence in order to 
    verify that all parts of the sequence work correctly.
    Can be used to calibrate the phase per LDE attempt!
    Here the adwin performs dynamic phase correction such that an
    initial carbon state |x> (after swapping) is rotated back onto itself and correctly read out.
    Has the option to either sweep the repetitions of LDE2 (easy mode)
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)
    # prepare_carbon_params(m)

    ### general params


    if not do_phase_offset_sweep:
        pts = 11
        m.params['phase_detuning'] = 0.
        ### calculate sweep array
        minReps = 10
        maxReps = 311
        # minReps = 340
        # maxReps = 641
        # minReps = 670
        # maxReps = 971
        step = 30 # int((maxReps-minReps)/pts)+1

        m.params['general_sweep_pts'] = np.arange(minReps, maxReps, step)
        print(m.params['general_sweep_pts'])
        print("len: %d" % (len(m.params['general_sweep_pts'])))
        want_this = raw_input("Do you want this? (y)")
        if not want_this == "y":
            return

        ### define sweep
        m.params['do_general_sweep'] = 1
        m.params['general_sweep_name'] = 'LDE2_attempts'
        print 'sweeping the', m.params['general_sweep_name']

        m.params['pts'] = len(m.params['general_sweep_pts'])
        m.params['sweep_name'] = m.params['general_sweep_name']
        m.params['sweep_pts'] = m.params['general_sweep_pts']
    else:
        pts = 11
        offset_range = 360.0
        m.params['phase_detuning'] = 0.0

        m.params['do_general_sweep'] = 0
        m.params['LDE2_attempts'] = 10
        m.joint_params['LDE2_attempts'] = 10

        m.params['pts'] = pts
        m.params['sweep_name'] = 'sequence_phase_offset'
        m.params['nuclear_phases_offset_sweep'] = np.linspace(-offset_range/2, offset_range/2, pts)
        m.params['sweep_pts'] = m.params['nuclear_phases_offset_sweep']
    
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)
    m.params['do_phase_offset_sweep'] = 1 if do_phase_offset_sweep else 0

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    if not dry_run:
        m.params['do_carbon_init'] = 1
        m.params['do_swap_onto_carbon'] = 1
        m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
        m.params['do_LDE_1'] = 0
        m.params['simple_el_init'] = 1
        m.params['do_LDE_2'] = 1
        m.params['do_phase_correction'] = 1
        
        m.params['do_purifying_gate'] = 0
        m.params['do_carbon_readout']  = 1
        m.params['do_repump_after_LDE2'] = 1
        mw = True
        ####
    else:
        m.params['do_carbon_init'] = 1
        m.params['do_C_init_SWAP_wo_SSRO'] = 1
        m.params['do_swap_onto_carbon'] = 1
        m.params['do_SSRO_after_electron_carbon_SWAP'] = 0
        m.params['do_LDE_1'] = 0
        m.params['simple_el_init'] = 1
        m.params['do_LDE_2'] = 1
        m.params['do_phase_correction'] = 1
        
        m.params['do_purifying_gate'] = 0
        m.params['do_carbon_readout'] = 1
        m.params['do_repump_after_LDE2'] = 1
        mw = False


    m.params['do_phase_fb_delayline'] = 1

    m.params['carbon_encoding'] = 'MBE'
    m.params['carbon_swap_el_states'] = ['X']
    # print(m.params['Hermite_pi_amp'], m.params['Hermite_pi_length'], m.params['X_phase'])
    # m.params['mw_first_pulse_amp'] = m.params['Hermite_pi_amp']  #### needs to be changed back to regular pi/2 for most calibrations
    # m.params['mw_first_pulse_length'] = m.params['Hermite_pi_length']
    # m.params['mw_first_pulse_phase'] = m.params['X_phase']



    ### awg sequencing logic / lde parameters
    m.params['LDE_1_is_init'] = 0
    m.joint_params['opt_pi_pulses'] = 0
    # input el state is not used anymore
    m.params['input_el_state'] = None

    # Note that these Tomography bases don't really make sense for multiple carbons

    # tomo_dict = { 'X' : ['Z'] * m.params['number_of_carbons'],
    #               'mX': ['Z'] * m.params['number_of_carbons'],
    #               'Y' : ['Y'] * m.params['number_of_carbons'],
    #               'mY': ['Y'] * m.params['number_of_carbons'],
    #               'Z' : ['X'] * m.params['number_of_carbons'] ,
    #               'mZ': ['X'] * m.params['number_of_carbons']}
    #
    # m.params['Tomography_bases'] = tomo_dict[input_state]

    m.params['Tomography_list'] = [
        ['X','X']
    ]

    # m.params['Tomography_bases'] = ['X','X']

    # m.params['mw_first_pulse_phase'] = m.params['X_phase']

    #### increase the detuning for more precise measurements
    # m.params['phase_detuning'] = 6.0
    # # phase_per_rep = m.params['phase_per_sequence_repetition']
    # m.params['phase_per_sequence_repetition'] = phase_per_rep + m.params['phase_detuning']
    m.params['Carbon_LDE_phase_correction_list'] += m.params['phase_detuning']
    m.params['nuclear_phases_per_seqrep'] += np.array([1.0, 0.0]) * m.params['phase_detuning']

    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    for tomo_bases in m.params['Tomography_list']:
        m.params['Tomography_bases'] = tomo_bases
        for ro in ['positive','negative']:
            breakst = show_stopper()
            if breakst:
                break
            save_name = "".join(m.params['Tomography_bases']) + "_" + ro
            m.params['carbon_readout_orientation'] = ro

            run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig = autoconfig, simplify_wfnames=simplify_wfnames, mw=mw)
            autoconfig = False
    m.finish()


def apply_dynamic_phase_correction_delayline_tomo(name, debug=False, upload_only=False, simplify_wfnames=False,
                                             dry_run=False):
    """
    combines all carbon parts of the sequence in order to
    verify that all parts of the sequence work correctly.
    Can be used to calibrate the phase per LDE attempt!
    Here the adwin performs dynamic phase correction such that an
    initial carbon state |x> (after swapping) is rotated back onto itself and correctly read out.
    Has the option to either sweep the repetitions of LDE2 (easy mode)
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)
    # prepare_carbon_params(m)

    ### general params

    m.params['LDE2_attempts'] = 10
    m.joint_params['LDE2_attempts'] = 10

    m.params['do_general_sweep'] = 1
    m.params['general_sweep_name'] = 'Tomography_bases'
    m.params['general_sweep_pts'] = [
        ['X', 'I'], ['Y', 'I'], ['Z', 'I'],
        ['I', 'X'], ['I', 'Y'], ['I', 'Z'],
        ['X', 'X'], ['Y', 'Y'], ['Z', 'Z']
    ]

    print 'sweeping the', m.params['general_sweep_name']

    m.params['pts'] = len(m.params['general_sweep_pts'])
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)
    m.params['do_phase_offset_sweep'] = 0

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    if not dry_run:
        m.params['do_carbon_init'] = 1
        m.params['do_swap_onto_carbon'] = 1
        m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
        m.params['do_LDE_1'] = 0
        m.params['simple_el_init'] = 1
        m.params['do_LDE_2'] = 1
        m.params['do_phase_correction'] = 1

        m.params['do_purifying_gate'] = 0
        m.params['do_carbon_readout'] = 1
        m.params['do_repump_after_LDE2'] = 1
        mw = True
        ####
    else:
        m.params['do_carbon_init'] = 1
        m.params['do_C_init_SWAP_wo_SSRO'] = 1
        m.params['do_swap_onto_carbon'] = 1
        m.params['do_SSRO_after_electron_carbon_SWAP'] = 0
        m.params['do_LDE_1'] = 0
        m.params['simple_el_init'] = 1
        m.params['do_LDE_2'] = 1
        m.params['do_phase_correction'] = 1

        m.params['do_purifying_gate'] = 0
        m.params['do_carbon_readout'] = 1
        m.params['do_repump_after_LDE2'] = 1
        mw = False

    m.params['do_phase_fb_delayline'] = 1

    m.params['carbon_encoding'] = 'MBE'
    m.params['carbon_swap_el_states'] = ['X']
    # print(m.params['Hermite_pi_amp'], m.params['Hermite_pi_length'], m.params['X_phase'])
    # m.params['mw_first_pulse_amp'] = m.params['Hermite_pi_amp']  #### needs to be changed back to regular pi/2 for most calibrations
    # m.params['mw_first_pulse_length'] = m.params['Hermite_pi_length']
    # m.params['mw_first_pulse_phase'] = m.params['X_phase']



    ### awg sequencing logic / lde parameters
    m.params['LDE_1_is_init'] = 0
    m.joint_params['opt_pi_pulses'] = 0
    # input el state is not used anymore
    m.params['input_el_state'] = None

    #### increase the detuning for more precise measurements
    # m.params['phase_detuning'] = 6.0
    # # phase_per_rep = m.params['phase_per_sequence_repetition']
    # m.params['phase_per_sequence_repetition'] = phase_per_rep + m.params['phase_detuning']
    # m.params['Carbon_LDE_phase_correction_list'] += m.params['phase_detuning']
    # m.params['nuclear_phases_per_seqrep'] += np.array([1.0, 0.0]) * m.params['phase_detuning']

    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    for ro in ['positive', 'negative']:
        breakst = show_stopper()
        if breakst:
            break
        save_name = ro
        m.params['carbon_readout_orientation'] = ro

        run_sweep(m, debug=debug, upload_only=upload_only, multiple_msmts=True, save_name=save_name,
                  autoconfig=autoconfig, simplify_wfnames=simplify_wfnames, mw=mw)
        autoconfig = False
    m.finish()

def sweep_number_of_delay_feedback_pulses(name, do_Z=False, debug=False, upload_only=False, dry_run=False):
    """
        runs the measurement for X and Y tomography. Also does positive vs. negative RO
        """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    m.params['reps_per_ROsequence'] = 10000

    ### calculate the sweep array
    minReps = 1
    maxReps = 5
    step = 1
    sweep_pts = np.arange(minReps, maxReps, step)
    pts = len(sweep_pts)

    C_id = m.params['carbons'][0]
    C_freq_0 = m.params['C%s_freq_0' % C_id]

    delay_cycles_fixed = int(round((1.0/C_freq_0 - m.params['delay_time_offset']) / m.params['delay_clock_cycle_time'] ))
    print("delay_cycles_fixed: %d" % delay_cycles_fixed)

    m.params['pts'] = pts
    m.params['delay_cycles_sweep'] = np.ones(pts, dtype=np.int32) * delay_cycles_fixed

    print(sweep_pts)
    want_this = raw_input("Do you want this? (y)")
    if not want_this == "y":
        return

    ### define sweep
    m.params['general_sweep_name'] = 'delay_feedback_N'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = sweep_pts
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    turn_all_sequence_elements_off(m)
    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep'] = 1
    m.params['do_carbon_init'] = 1
    m.params['do_LDE_1'] = 0
    m.params['do_delay_fb_pulses'] = 1
    m.params['do_sweep_delay_cycles'] = 1
    m.params['do_carbon_readout'] = 1
    # m.params['mw_first_pulse_amp'] = 0
    m.params['MW_during_LDE'] = 1
    # m.params['mw_first_pulse_amp'] = 0#m.params['Hermite_pi_amp']
    # m.params['mw_first_pulse_phase'] = m.params['Y_phase']# +180
    # m.params['mw_first_pulse_length'] = m.params['Hermite_pi_length']
    m.joint_params['opt_pi_pulses'] = 0
    m.params['feedback_HHsync_include'] = 1

    mw = dry_run


    ### loop over tomography bases and RO directions upload & run

    breakst = False
    autoconfig = True
    if do_Z:
        for t in ['Z']:
            if breakst:
                break
            for ro in ['positive', 'negative']:
                breakst = show_stopper()
                if breakst:
                    break
                print t, ro
                m.params['do_C_init_SWAP_wo_SSRO'] = 1
                save_name = t + '_' + ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                run_sweep(m, debug=debug, upload_only=upload_only, multiple_msmts=True, save_name=save_name,
                          autoconfig=autoconfig, mw=mw)
                autoconfig = False

    else:
        for t in ['X', 'Y']:
            if breakst:
                break
            for ro in ['positive', 'negative']:
                breakst = show_stopper()
                if breakst:
                    break
                if not dry_run:
                    m.params['do_C_init_SWAP_wo_SSRO'] = 0
                    m.params['carbon_init_method'] = 'MBI'
                else:
                    m.params['do_C_init_SWAP_wo_SSRO'] = 1
                print t, ro
                save_name = t + '_' + ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                run_sweep(m, debug=debug, upload_only=upload_only, multiple_msmts=True, save_name=save_name,
                          autoconfig=autoconfig, mw=mw)
                autoconfig = False

    m.finish()


# some auxiliary functions for ADwin debugging
def get_overlong_cycles():
    return adwin.get_purification_delayfb_var('overlong_cycles_per_mode', start=1, length=100)

def get_flowchart():
    flowchart_length = 200
    cur_idx = adwin.get_purification_delayfb_var('flowchart_index')
    return cur_idx, adwin.get_purification_delayfb_var('mode_flowchart', start=1, length=flowchart_length), adwin.get_purification_delayfb_var('mode_flowchart_cycles', start=1, length=flowchart_length)

def print_flowchart(length = 60):
    a,b,c = get_flowchart()
    for i in range(a-length,a):
        print "%d\t%d"%( b[i],c[i])

def check_LDE_attempts(reps=100000, exp_att=9):
    att = adwin.get_purification_delayfb_var('attempts_second', start=1, length=reps)
    return att, np.where(att != exp_att)

if __name__ == '__main__':

    # repump_speed(name+'_repump_speed',upload_only = False)

    # sweep_average_repump_time(name+'_Sweep_Repump_time_Z',do_Z = True,debug = False)
    # sweep_average_repump_time(name+'_Sweep_Repump_time_X',do_Z = False,debug=False)

    # sweep_number_of_reps(name+'_sweep_number_of_reps_X',do_Z = False, debug=False)
    # sweep_number_of_reps(name+'_sweep_number_of_reps_Z',do_Z = True)

    # characterize_el_to_c_swap(name+'_Swap_el_to_C',  upload_only = False)
    # characterize_el_to_c_swap_success(name+'_SwapSuccess_el_to_C', upload_only = False)

    # analyse_simple_el_init_swap(name + '_Swap_simple_el_init_to_C', upload_only=False)

    # sweep_LDE_attempts_before_swap(name+'LDE_attempts_vs_swap',upload_only = False)

    # calibrate_LDE_phase(name+'_LDE_phase_calibration',upload_only = False)
    # calibrate_dynamic_phase_correct(name+'_phase_compensation_calibration',upload_only = False)


    # start_time = time.time()
    # optimize_time = time.time()
    # while time.time()-start_time < 16*60*60:
    #     if show_stopper():
    #         break
    #     if time.time()-optimize_time > 30*60:
    #         GreenAOM.set_power(1e-5)
    #         optimiz0r.optimize(dims=['x','y','z','y','x'])
    #         GreenAOM.turn_off()
    #         optimize_time = time.time()

    # apply_dynamic_phase_correction(name+'_ADwin_phase_compensation',upload_only = False,input_state = 'Z')
    # AWG.clear_visa()
    # #check_phase_offset_after_LDE2(name+'_phase_offset_after_LDE_X',upload_only = False,tomo = 'X')
    # check_phase_offset_after_LDE2(name+'_phase_offset_after_LDE_Y',upload_only = False,tomo = 'Y')
    # check_phase_offset_after_LDE2(name+'_phase_offset_after_LDE_Z',upload_only = False,tomo = 'Z')
    # full_sequence_local(name+'_full_sequence_local', upload_only = False,do_Z = False)
    #full_sequence_local(name+'_full_sequence_local_Z', upload_only = False,do_Z = True)
    
    # apply_dynamic_phase_correction(name+'_ADwin_phase_compensation',upload_only = False,input_state = 'Z')
    # apply_dynamic_phase_correction_delayline(
    #     name + '_phase_offset_fb_delayline',
    #     upload_only=False,
    #     dry_run=False,
    #     input_state='Z',
    #     do_phase_offset_sweep=True
    # )
    #
    apply_dynamic_phase_correction_delayline(
        name + '_phase_fb_delayline',
        upload_only=True,
        dry_run=False,
    )

    # sweep_number_of_delay_feedback_pulses("_delay_pulses_sweep",
    #                                       debug=False,
    #                                       upload_only=False,
    #                                       do_Z=True
    #                                       )


    #### ionization studies:
    # sweep_number_of_reps_ionization(name+'_ionization_check_ms0',upload_only=False,ms0=True)
    # sweep_number_of_reps_ionization(name+'_ionization_check',upload_only=False,ms0=False)
    # ionzation_sweep_pi_amp(name+'_ionization_sweep_pi_amp', upload_only = False)