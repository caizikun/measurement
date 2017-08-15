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
    carbons = [2,4,5,3,6,7]
    C13_X_phase = 0.0

    msmt_sweep_limits = [
        (10, 190, 30),
        (190, 340, 30),
        (340, 850, 120),
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


    carbon_combis = itertools.combinations(carbons, 2)

    breakst = False
    bitchy_newfocus = False
    recalibrate_LDE = True

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
    #         execfile("./LDE_storage_sweep.py")

# if False:

    for c in carbons:
        if breakst:
            break
        breakst = show_stopper()
        if breakst:
            break
        if not debug:
            optimize()
            recalibrate_all()

        m = {
            'requested_measurement': 'sweep_average_repump_time',
            'carbons': [c],
            'debug': debug
        }

        with open('overnight_m.json', 'w') as json_file:
            json.dump(m, json_file)
        execfile("./LDE_storage_sweep.py")

        m = {
            'requested_measurement': 'decay_curve',
            'carbons': [c],
            'debug': debug
        }

        with open('overnight_m.json', 'w') as json_file:
            json.dump(m, json_file)
        execfile("./LDE_storage_sweep.py")

    for combi in carbon_combis:
        if breakst:
            break
        breakst = show_stopper()
        if breakst:
            break
        if not debug:
            optimize()
            recalibrate_all()

        for calibration_carbon in carbons:
            if breakst:
                break
            breakst = show_stopper()
            if breakst:
                break

            if recalibrate_LDE:
                m = {
                    'requested_measurement': 'LDE_calibration',
                    'calibration_carbon': calibration_carbon,
                    'debug': debug
                }

                with open('overnight_m.json', 'w') as json_file:
                    json.dump(m, json_file)
                execfile("./LDE_storage_sweep.py")
            # calibrate_LDE_phase(
            #     name+'_LDE_phase_calibration_C%d' % calibration_carbon,
            #     upload_only = debug,
            #     update_msmt_params=True,
            #     carbon_override=calibration_carbon,
            #     max_correction=2.0
            # )

        for d_i, d in enumerate(msmt_sweep_limits):
            if breakst:
                break
            breakst = show_stopper()
            if breakst:
                break
            if not debug:
                optimize()
            for m_template in msmt_templates:
                if breakst:
                    break
                breakst = show_stopper()
                if breakst:
                    break
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

                if not debug and bitchy_newfocus:
                    recalibrate_all()

                with open('overnight_m.json', 'w') as json_file:
                    json.dump(m, json_file)
                execfile("./LDE_storage_sweep.py")

                # apply_dynamic_phase_correction_delayline(
                #     m_name,
                #     upload_only=debug,
                #     dry_run=False,
                #     extra_params=m
                # )
                import gc
                gc.collect()