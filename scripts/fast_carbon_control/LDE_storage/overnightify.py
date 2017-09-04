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

if __name__ == '__main__':
    debug = False
    # overnight section
    carbons = [5,4]#[1,2,3,4,5,6,7]
    C13_X_phase = 0.0

    msmt_sweep_limits = [
        (10, 190, 30),
        (190, 340, 30),
        (340, 850, 120),
    ]

    LDE_calibration_range = [
        (2, 35, 3),
        (35, 68, 3),
        (68, 101, 3)
    ]

    msmt_templates = [
        {
            'carbon_encoding':              'serial_swap',
            'carbon_swap_el_states':        ['Z', 'Z'],
            'Tomography_list': [
                # ['X', 'I'],
                # ['I', 'X'],
                ['X', 'X'],
                [C13_X_phase + 45.0, C13_X_phase + 45.0],
                [C13_X_phase + 45.0, C13_X_phase - 45.0],
            ]
        },
        {
            'carbon_encoding':              'MBE',
            'carbon_swap_el_states':        ['X'],
            'Tomography_list': [
                ['X', 'X'],
                ['Y', 'Y'],
                ['Z', 'Z'],
                ['X', 'Y'],
                ['Y', 'X'],
            ]
        },
        {
            'carbon_encoding':              'MBE',
            'carbon_swap_el_states':        ['-X'],
            'Tomography_list': [
                ['X', 'X'],
                ['Y', 'Y'],
                ['Z', 'Z'],
                ['X', 'Y'],
                ['Y', 'X'],
            ]
        }
    ]


    carbon_combis = list(itertools.combinations(carbons, 2))

    breakst = False
    recalibrate_LDE = True

    start_from_combi = 0

    print("I'm going to do carbon combinations: " + str(carbon_combis[start_from_combi:]))

    want_this = raw_input("Do you want this?")
    if want_this != 'y':
        raise Exception("Getting out of here")

    # for c in carbons:
    #     if breakst:
    #         break
    #     breakst = show_stopper()
    #     if breakst:
    #         break
    #     if not debug:
    #         optimize()
    #         recalibrate_all()
    #
    #     for i in range(2):
    #         m = {
    #             'requested_measurement': 'LDE_calibration',
    #             'calibration_carbon': c,
    #             'debug': debug
    #         }
    #
    #         with open('overnight_m.json', 'w') as json_file:
    #             json.dump(m, json_file)
    #         do_overnight_msmt = True
    #         execfile("./LDE_storage_sweep.py")

# if False:

    for combi in carbon_combis[start_from_combi:]:
        if breakst:
            break
        breakst = show_stopper()
        if breakst:
            break
        if not debug:
            optimize()
            recalibrate_all()
            execfile(r"espin_calibrations.py")

        # calibrate both carbons participating in this measurement
        if recalibrate_LDE:
            for c in combi:
                if not debug:
                    bell_check_powers()

                for i in range(2):
                    m = {
                        "requested_measurement": "stitched_LDE_calibration",
                        "calibration_carbon": c,
                        "m_ranges": LDE_calibration_range,
                        "debug": debug
                    }
                    with open('overnight_m.json', 'w') as json_file:
                        json.dump(m, json_file)
                    do_overnight_msmt = True
                    execfile("./LDE_storage_sweep.py")

        for d_i, d in enumerate(msmt_sweep_limits):
            if breakst:
                break
            breakst = show_stopper()
            if breakst:
                break
            if not debug:
                optimize()
                execfile(r"espin_calibrations.py")

            for m_template in msmt_templates:
                if breakst:
                    break
                breakst = show_stopper()
                if breakst:
                    break

                if not debug:
                    bell_check_powers()
                    optimize()
                m = copy.deepcopy(m_template)
                m['minReps'] = d[0]
                m['maxReps'] = d[1]
                m['step'] = d[2]
                m['carbons'] = combi

                m_name = "%s_phase_fb_delayline_C%s_%s_%s_sec%d" % (
                    name,
                    "".join([str(c) for c in combi]),
                    m['carbon_encoding'],
                    "".join(m['carbon_swap_el_states']),
                    d_i
                )

                m['m_name'] = m_name
                m['requested_measurement'] = 'LDE_sweep'
                m['debug'] = debug

                with open('overnight_m.json', 'w') as json_file:
                    json.dump(m, json_file)
                do_overnight_msmt = True
                execfile("./LDE_storage_sweep.py")

    # for c in carbons:
    #     if breakst:
    #         break
    #     breakst = show_stopper()
    #     if breakst:
    #         break
    #     if not debug:
    #         optimize()
    #         recalibrate_all()
    #         execfile(r"espin_calibrations.py")

    #     # m = {
    #     #     'requested_measurement': 'sweep_average_repump_time',
    #     #     'carbons': [c],
    #     #     'debug': debug
    #     # }
    #     #
    #     # with open('overnight_m.json', 'w') as json_file:
    #     #     json.dump(m, json_file)
    #     # do_overnight_msmt = True
    #     # execfile("./LDE_storage_sweep.py")

    #     m = {
    #         "requested_measurement": "stitched_LDE_calibration",
    #         "calibration_carbon": c,
    #         "m_ranges": LDE_calibration_range,
    #         "debug": debug
    #     }
    #     with open('overnight_m.json', 'w') as json_file:
    #         json.dump(m, json_file)
    #     # do_overnight_msmt = True
    #     execfile("./LDE_storage_sweep.py")

    #     for i_fr, fr in enumerate(msmt_sweep_limits):
    #         if not debug:
    #             bell_check_powers()
    #         m_name = name + "_phase_fb_delayline_C%d_sec%d" % (c, i_fr)

    #         m = {
    #             "requested_measurement": "LDE_sweep",
    #             "m_name": m_name,
    #             "carbons": [c],
    #             "minReps": fr[0],
    #             "maxReps": fr[1],
    #             "step": fr[2],
    #             "Tomography_list": [
    #                 ['X'],
    #                 ['Y']
    #             ],
    #             "carbon_encoding": "serial_swap",
    #             "debug": debug
    #         }

    #         with open('overnight_m.json', 'w') as json_file:
    #             json.dump(m, json_file)
    #         do_overnight_msmt = True
    #         execfile("./LDE_storage_sweep.py")

    #     if not debug:
    #         bell_check_powers()
    #     m = {
    #         'requested_measurement': 'decay_curve',
    #         'carbons': [c],
    #         'debug': debug
    #     }

    #     with open('overnight_m.json', 'w') as json_file:
    #         json.dump(m, json_file)
    #     do_overnight_msmt = True
    #     execfile("./LDE_storage_sweep.py")