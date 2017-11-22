import io,sys
import numpy as np
import qt
import msvcrt
import copy
from analysis.scripts.QEC import carbon_ramsey_analysis as cr
reload(cr)

execfile(qt.reload_current_setup)

ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

SETUP = qt.current_setup

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

electron_transition_string = qt.exp_params['samples'][SAMPLE]['electron_transition']

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)
n = 1

def stop_msmt():
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(5)
    if msvcrt.kbhit() and msvcrt.getch() == 'q':
        print "breaking"
        return False

    else:
        print "continuing"
        return True

def measure_T2star(name,
                                        carbon_nr=5,
                                        carbon_init_state='up',
                                        detuning=0.5e3,
                                        el_state=0,
                                        debug=False):
    m = DD.NuclearRamseyWithInitialization(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 2000
    m.params['C13_MBI_RO_state'] = 0
    ### overwritten from msmnt params

    ####################################
    ### Option 1; Sweep waiting time ###
    ####################################

    # 1A - Rotating frame with detuning
    m.params['add_wait_gate'] = True
    m.params['pts'] = 25
    m.params['free_evolution_time'] = 400e-6 + np.linspace(0e-6, 3 * 1. / detuning, m.params['pts'])
    # m.params['free_evolution_time'] = 180e-6 + np.linspace(0e-6, 4*1./74e3,m.params['pts'])


    m.params['C' + str(carbon_nr) + '_freq_0'] += detuning
    m.params['C' + str(carbon_nr) + '_freq_1' + m.params['electron_transition']] += detuning
    m.params['C_RO_phase'] = 'X'

    m.params['sweep_name'] = 'free_evolution_time'
    m.params['sweep_pts'] = m.params['free_evolution_time']

    '''Derived and fixed parameters'''
    #
    m.params['carbon_nr'] = carbon_nr
    m.params['init_state'] = carbon_init_state
    m.params['electron_after_init'] = str(el_state)
    m.params['Nr_C13_init'] = 1
    m.params['Nr_MBE'] = 0
    m.params['Nr_parity_msmts'] = 0

    Tomography_list = [
        'X',
        'Y'
    ]

    readout_orientations = {
        'positive',
        'negative'
    }

    for ero in readout_orientations:
        if not stop_msmt():
            break
        m.params['electron_readout_orientation'] = ero
        for tomo in Tomography_list:
            if not stop_msmt():
                break
            m.params['C_RO_phase'] = [tomo] * m.params['pts']
            save_name = "%s_%s" % (tomo, ero)
            print("Measuring " + save_name)
            funcs.finish(m, upload=True, debug=debug, save_name=save_name, last_msmt=False)

    m.finish()

execfile(r"overnight_tools.py")

if __name__ == '__main__':
    optimize()
    recalibrate_all()
    execfile(r"espin_calibrations.py")

    carbons = np.arange(1,8)

    max_evolution_time = 10e-3
    detuning = np.round(3. / max_evolution_time, -1)

    for c in carbons:
        if not stop_msmt():
            print 'bye'
            break

        optimize()
        recalibrate_all()
        execfile(r"espin_calibrations.py")

        m_name = "T2star_el1_C%d" % c
        measure_T2star(
            m_name,
            carbon_nr=c,
            carbon_init_state='up',
            detuning=detuning,
            debug=False,
            el_state=1
        )

