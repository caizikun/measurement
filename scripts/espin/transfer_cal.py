import numpy as np
import qt
import msvcrt


execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs;reload(funcs)


def Transfer_gate_calibration(name, 
        carbon_nr           = 1,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        detuning            = 0.5e3,
        el_state            = 1,
        debug               = False,
        fid_transition      = 'm1',
        sweep  = 400e-6 + np.linspace(0., 6.0e-3,44),
        dyn_dec_wait=False):
    
    m = DD.Transfer_gate_calibration(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500
    m.params['C13_MBI_RO_state'] = 0
    ### overwritten from msmnt params


    ###########################################
    ## Option 1; Sweep RO phase at set time ###
    ###########################################
    
    if fid_transition == '_m1':
        m.params['first_transition'] = fid_transition
        m.params['second_transition'] = '_p1'
    else:
        m.params['first_transition'] = fid_transition
        m.params['second_transition'] = '_m1'



    

    m.params['pts'] = len(sweep)
    m.params['add_wait_gate'] = False
    m.params['add_transfer_gate'] = True
    m.params['C_RO_phase'] = sweep

    m.params['sweep_name'] = 'phase'
    m.params['sweep_pts']  = sweep

    '''Derived and fixed parameters'''

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['electron_after_init'] = str(el_state)
    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    funcs.finish(m, upload =True, debug=debug)

def qstop(sleep=3):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

if __name__ == '__main__':
    
    for c in [2]:
        for el_RO in ['negative','positive']:
            qstop()

            Transfer_gate_calibration(SAMPLE_CFG+'transfer_gate_cal_carbon_'+str(c)+'_el_'+str(el_RO), 
        carbon_nr           = c,               
        carbon_init_state   = 'up', 
        el_RO               = el_RO,
        el_state            = 0,
        debug               = True,
        fid_transition      = '_m1',
        sweep  =  np.linspace(0,360,1))
   