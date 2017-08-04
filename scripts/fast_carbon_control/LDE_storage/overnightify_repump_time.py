import json
import itertools
import copy
import msvcrt
import qt

name = qt.exp_params['protocols']['current']

def show_stopper():
    print '-----------------------------------'
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def recalibrate_newfocus():
    stools.recalibrate_lt4_lasers(names=['NewfocusAOM'], awg_names=['NewfocusAOM'])

def recalibrate_all():
    stools.recalibrate_lt4_lasers(names=['GreenAOM', 'MatisseAOM', 'NewfocusAOM'],
                                  awg_names=['NewfocusAOM'])

def optimize():
    GreenAOM.set_power(10e-6)
    optimiz0r.optimize(dims=['x','y','z','y','x'])
    GreenAOM.turn_off()

if __name__ == '__main__':
    debug = False
    # overnight section
    carbons = [1,2,3,4,5,6,7]
    LDE_attempts = [50, 100, 150, 200, 250, 500]
    powers = [4e-6, 1e-6]

    LDE_msmt_sweep_range = [
        (1,12,1),
        (12,24,1)
    ]

    LDE_first_pulses = [
        'pi2',
        'pi',
        'none'
    ]

    breakst = False
    bitchy_newfocus = False

    for p in powers:
        for c in carbons:
            for pulse_type in LDE_first_pulses:
                if not debug:
                    optimize()
                    recalibrate_all()
                for range_i, sw_rng in enumerate(LDE_msmt_sweep_range):
                    m_name = "%s_LDE_phase_%s_C%d_pow%duW_sec%d" % (
                        name, pulse_type, c, int(p*1e6), range_i
                    )
                    m = {
                        'requested_measurement': 'LDE_phase',
                        'carbons': [c],
                        'debug': debug,
                        'minReps': sw_rng[0],
                        'maxReps': sw_rng[1],
                        'step': sw_rng[2],
                        'phase_detuning': 0.0,
                        'm_name': m_name,
                        'first_mw_pulse_type': pulse_type,
                    }

                    with open('overnight_m.json', 'w') as json_file:
                        json.dump(m, json_file)
                    execfile("./LDE_storage_sweep.py")

                for l in LDE_attempts:

                    if c == 1 and l >101:
                        continue

                    if c != 7 and l > 450:
                        continue

                    if c == 7 and l < 201:
                        continue

                    if breakst:
                        break
                    breakst = show_stopper()
                    if breakst:
                        break
                    if not debug:
                        optimize()
                        recalibrate_all()

                    m_name = "%s_Sweep_Repump_time_%s_C%d_LDE%d_pow%duW_X" % (
                        name, pulse_type, c, l, int(p*1e6)
                    )

                    m = {
                        'requested_measurement': 'sweep_average_repump_time',
                        'carbons': [c],
                        'debug': debug,
                        'LDE1_attempts': l,
                        'AWG_SP_power': p,
                        'm_name': m_name,
                        'first_mw_pulse_type': pulse_type,
                    }

                    with open('overnight_m.json', 'w') as json_file:
                        json.dump(m, json_file)
                    execfile("./LDE_storage_sweep.py")

