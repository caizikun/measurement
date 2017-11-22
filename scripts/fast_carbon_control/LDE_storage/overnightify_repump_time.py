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

execfile(r"overnight_tools.py")

if __name__ == '__main__':
    debug = False
    # overnight section
    carbons = [2]
    LDE_attempts = [100]
    powers = [4e-6]

    LDE_msmt_sweep_range = [
        (1,12,1),
        (12,24,1)
    ]

    LDE_first_pulses = [
        'pi2'#,
        #'pi',
        #'none'
    ]

    breakst = False
    bitchy_newfocus = False

    for p in powers:
        for c in carbons:
            for pulse_type in LDE_first_pulses:
                if not debug:
                    optimize()
                    bell_check_powers()
                # for range_i, sw_rng in enumerate(LDE_msmt_sweep_range):
                #     m_name = "%s_LDE_phase_%s_C%d_pow%duW_sec%d" % (
                #         name, pulse_type, c, int(p*1e6), range_i
                #     )
                #     m = {
                #         'requested_measurement': 'LDE_phase',
                #         'carbons': [c],
                #         'debug': debug,
                #         'minReps': sw_rng[0],
                #         'maxReps': sw_rng[1],
                #         'step': sw_rng[2],
                #         'phase_detuning': 0.0,
                #         'm_name': m_name,
                #         'first_mw_pulse_type': pulse_type,
                #     }

                #     with open('overnight_m.json', 'w') as json_file:
                #         json.dump(m, json_file)
                #     execfile("./LDE_storage_sweep.py")

                for l in LDE_attempts:


                    # if c != 7 and l > 450:
                    #     continue
                    #
                    # if c == 7 and l < 49:
                    #     continue

                    if breakst:
                        break
                    breakst = show_stopper()
                    if breakst:
                        break
                    if not debug:
                        optimize()
                        bell_check_powers()

                    m_name = "%s_Sweep_Repump_time_%s_C%d_LDE%d_pow%duW_X" % (
                        name, pulse_type, c, l, int(p*1e6)
                    )

                    m = {
                        'requested_measurement': 'sweep_average_repump_time',
                        'carbons': [c],
                        'debug': debug,
                        'LDE1_attempts': l,
                        'LDE2_attempts': l,
                        'AWG_SP_power': p,
                        'm_name': m_name,
                        'first_mw_pulse_type': pulse_type,
                    }

                    with open('overnight_m.json', 'w') as json_file:
                        json.dump(m, json_file)
                    execfile("./LDE_storage_sweep.py")

