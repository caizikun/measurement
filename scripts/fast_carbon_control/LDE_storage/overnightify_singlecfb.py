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

def bell_check_powers():

    prot_name = qt.exp_params['protocols']['current']

    names=['MatisseAOM', 'NewfocusAOM','GreenAOM']
    setpoints = [qt.exp_params['protocols'][prot_name]['AdwinSSRO']['Ex_RO_amplitude'],
                4000e-9, # The amount for repumping in purification
                10e-6]
    relative_thresholds = [0.15,0.15,0.15]
    qt.instruments['PMServo'].move_in()
    qt.msleep(2)
    qt.stools.init_AWG()
    qt.stools.turn_off_all_lasers()

    all_fine=True
    for n,s,t in zip(names, setpoints,relative_thresholds):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
        setpoint, value = qt.stools.check_power(n, s, 'adwin', 'powermeter', 'PMServo', False)
        deviation =np.abs(1-setpoint/value)
        print 'deviation', deviation
        if deviation>t:
            all_fine=False
            qt.stools.recalibrate_laser(n, 'PMServo', 'adwin')
            if n == 'NewfocusAOM':
                qt.stools.recalibrate_laser(n, 'PMServo', 'adwin',awg=True)
            break
    qt.instruments['PMServo'].move_out()
    return all_fine



def optimize():
    GreenAOM.set_power(10e-6)
    optimiz0r.optimize(dims=['x','y','z','y','x'])
    GreenAOM.turn_off()

if __name__ == '__main__':
    debug = False
    # overnight section
    carbons = [1,2,3,4,5,6,7]

    LDE_calibration_range = [
        (2,35,3),
        (35,68,3),
        (68,101,3)
    ]

    feedback_ranges = [
        (2, 302, 30),
        (302, 602, 30)
    ]

    breakst = False
    bitchy_newfocus = False

    for c in carbons:
        if not debug:
            optimize()
            recalibrate_all()

        for rpt in range(2):
            # do the calibration twice for good measure #yolo
            bell_check_powers()
            m = {
                "requested_measurement": "stitched_LDE_calibration",
                "calibration_carbon": c,
                "m_ranges": LDE_calibration_range,
                "debug": debug
            }
            with open('overnight_m.json', 'w') as json_file:
                json.dump(m, json_file)
            execfile("./LDE_storage_sweep.py")

        # for i_fr, fr in enumerate(feedback_ranges):
        #     bell_check_powers()
        #     m_name = name + "_phase_fb_delayline_C%d_sec%d" % (c, i_fr)
        #
        #     m = {
        #         "requested_measurement": "LDE_sweep",
        #         "m_name": m_name,
        #         "carbons": [c],
        #         "minReps": fr[0],
        #         "maxReps": fr[1],
        #         "step": fr[2],
        #         "Tomography_list": [
        #             ['X'],
        #             ['Y']
        #         ],
        #         "carbon_encoding": "serial_swap",
        #         "debug": debug
        #     }
        #
        #     with open('overnight_m.json', 'w') as json_file:
        #         json.dump(m, json_file)
        #     execfile("./LDE_storage_sweep.py")
        #
        #
        # bell_check_powers()
        # m = {
        #     "requested_measurement": "decay_curve",
        #     "carbons": [c],
        #     "debug": debug
        # }
        # with open('overnight_m.json', 'w') as json_file:
        #     json.dump(m, json_file)
        # execfile("./LDE_storage_sweep.py")




        # for l in LDE_attempts:


        #     if c != 7 and l > 450:
        #         continue

        #     if c == 7 and l < 49:
        #         continue

        #     if breakst:
        #         break
        #     breakst = show_stopper()
        #     if breakst:
        #         break
        #     if not debug:
        #         optimize()
        #         bell_check_powers()

        #     m_name = "%s_Sweep_Repump_time_p1_%s_C%d_LDE%d_pow%duW_X" % (
        #         name, pulse_type, c, l, int(p*1e6)
        #     )

        #     m = {
        #         'requested_measurement': 'sweep_average_repump_time',
        #         'carbons': [c],
        #         'debug': debug,
        #         'LDE1_attempts': l,
        #         'AWG_SP_power': p,
        #         'm_name': m_name,
        #         'first_mw_pulse_type': pulse_type,
        #     }

        #     with open('overnight_m.json', 'w') as json_file:
        #         json.dump(m, json_file)
        #     execfile("./LDE_storage_sweep.py")

