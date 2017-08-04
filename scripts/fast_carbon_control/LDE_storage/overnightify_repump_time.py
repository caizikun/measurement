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

    breakst = False
    bitchy_newfocus = False

    for p in powers:
        for l in LDE_attempts:
            for c in carbons:

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

                m_name = "%s_Sweep_Repump_time_C%d_LDE%d_pow%duW_X" % (name, c, l, int(p*1e6))

                m = {
                    'requested_measurement': 'sweep_average_repump_time',
                    'carbons': [c],
                    'debug': debug,
                    'LDE1_attempts': l,
                    'AWG_SP_power': p,
                    'm_name': m_name,
                }

                with open('overnight_m.json', 'w') as json_file:
                    json.dump(m, json_file)
                execfile("./LDE_storage_sweep.py")