import numpy as np
import qt
import msvcrt


execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs;reload(funcs)


def SweepTransferPhase(name, 
                     
        transfer_begin      = '_m1', 
        transfer_end        = '_p1',
        sweep               = linspace(0,360,21),
        invert_pop_RO           =   False,
        el_state            = 0,
        debug               = False,
        readout_pop       = '_m1',
        delay               = 200e-9):
    
    m = DD.Electrontransfercalibration_V2(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 1000
    m.params['C13_MBI_RO_state'] = 0
    m.params['do_elec_transfer'] = True

    ### overwritten from msmnt params

    ####################################
    ### Option 1; sweep RO phase ###
    ####################################

    m.params['pts'] = len(sweep)
    m.params['phase_sweep'] = sweep
    m.params['sweep_name'] = 'RO_phase sweep'
    m.params['sweep_pts']  = m.params['phase_sweep']
    
    

    ####################################
    # ### Option 2; Sweep delay ###
    # ####################################

    # ##determine experiment parameters##
    # m.params['pts'] = len(sweep)
    # m.params['delay_sweep'] = sweep
    # m.params['sweep_name'] = 'delay_sweep'
    # m.params['sweep_pts']  = m.params['delay_sweep']
    m.params['delay']=230e-9

  
    m.params['invert_pop_ro']=invert_pop_RO
    m.params['transfer_begin'] = transfer_begin
    m.params['transfer_end'] = transfer_end
    m.params['readout_pop'] = readout_pop


    
    m.params['electron_after_init'] = str(el_state)
    m.params['electron_readout_orientation']=str(el_state)
    
    m.autoconfig()

    funcs.finish(m, upload =True, debug=debug)


def qstop(sleep=3):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

if __name__ == '__main__':
    debug = False
    delay = 230e-9
    delay_str = str(delay*1000000000)
       
    for readout_pop in ['_m1','_0','_p1']:

            SweepTransferPhase(SAMPLE + '_transfer_gate_cal_measured'+readout_pop+'delay_'+delay_str +'calib_phase', 
                     
        transfer_begin      = '_m1', 
        transfer_end        = '_p1',
        sweep               = linspace(0,360,11),
        invert_pop_RO           =   True,
        readout_pop       = readout_pop,
        el_state            =   0,
        delay               = delay,
        debug               = True)
    