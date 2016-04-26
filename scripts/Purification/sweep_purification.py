'''
Tries to generate the purification sequence in the AWG

NK 2016
'''
import numpy as np
import qt 
import purify_slave; reload(purify_slave)


def prepare(m, setup=qt.current_setup,name=qt.exp_params['protocols']['current']):
    '''
    loads all necessary msmt parameters
    '''
    m.params['setup']=setup
    sample_name = qt.exp_params['samples']['current']
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO+C13'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][name]['pulses'])
    m.params.from_dict(qt.exp_params['samples'][sample_name])


    if not(hasattr(m,'joint_params')):
        m.joint_params = {}
    import joint_params
    reload(joint_params)
    for k in joint_params.joint_params:
        m.joint_params[k] = joint_params.joint_params[k]


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
    # elif setup == 'lt3' :
    #     import params_lt3
    #     reload(params_lt3)
    #     msmt.AWG_RO_AOM = qt.instruments['PulseAOM']
    #     for k in params_lt3.params_lt3:
    #         msmt.params[k] = params_lt3.params_lt3[k]
    #     msmt.params['MW_BellStateOffset'] = 0.0
    #     bseq.pulse_defs_lt3(msmt)
    else:
        print 'Sweep_purification: invalid setup:', setup

    m.params['send_AWG_start'] = 1
    m.params['sync_during_LDE'] = 1
    m.params['wait_for_AWG_done'] = 0
    m.params['do_general_sweep']= 1
    m.params['trigger_wait'] = 1


def run_sweep(m,debug=True, upload_only=True):
    m.autoconfig()
    m.generate_sequence()
    if upload_only:
        return
    m.setup(debug=debug)

    # m.run(autoconfig=False, setup=False,debug=th_debug)    
    # m.save()    
    # m.finish()
def generate_AWG_seq(name):

    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    m.params['pts'] = 1
    m.params['reps_per_ROsequence'] = 1

    ### adwin process variables: should be automatically set.
    m.params['Nr_C13_init']     = 0 # Not necessary (only for C13 MBI)
    m.params['Nr_MBE']          = 0 # Not necessary (only for C13 MBI)
    m.params['Nr_parity_msmts'] = 0 # Not necessary (only for C13 MBI)
    m.params['Tomography_bases'] = ['X']


    ###parts of the sequence do you want to incorporate.
    m.params['do_general_sweep']    = False
    m.params['non_local']           = 1
    m.params['do_N_MBI']            = 0 # Not necessary (only for C13 MBI)
    m.params['init_and_ro_carbon']  = 1 # XXXX C_init_SWAP_wo_SSRO threshold?
    m.params['do_LDE_1']            = 1 # TODO finish jumping and event triggering for LDE / INIT ELEMENT
    m.params['swap_onto_carbon']    = 1 # do_SSRO_after_electron_carbon_SWAP
    m.params['do_LDE_2']            = 1 # TODO finish jumping and event triggering for LDE
    m.params['phase_correct']       = 1 # do_phase_correction
    m.params['purify']              = 0 # do_purifying_gate

    ### upload
    run_sweep(m,debug = True,upload_only = True)

if __name__ == '__main__':
    generate_AWG_seq('testing')