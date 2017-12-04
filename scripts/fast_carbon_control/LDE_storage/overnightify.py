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
def measure():
    with open('overnight_m.json', 'w') as json_file:
        json.dump(m, json_file)
    do_overnight_msmt = True
    execfile("./LDE_storage_sweep.py")

def recalibrate_newfocus():

    stools.recalibrate_lt4_lasers(names=['NewfocusAOM'], awg_names=['NewfocusAOM'])

def recalibrate_all():
    stools.recalibrate_lt4_lasers(names=['GreenAOM', 'MatisseAOM', 'NewfocusAOM'],
                                  awg_names=['NewfocusAOM'])

def optimize():
    GreenAOM.set_power(2e-6)
    optimiz0r.optimize(dims=['x','y','z','y','x'])
    GreenAOM.turn_off()

def check_powers():
    prot_name = qt.exp_params['protocols']['current']

    names=['NewfocusAOM']#,'MatisseAOM','GreenAOM'] #
    setpoints = [#qt.exp_params['protocols'][prot_name]['AdwinSSRO']['Ex_RO_amplitude'],
                20e-9]
                #2e-6]
    relative_thresholds = [0.15,0.15,0.5]
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
def check_all_powers():
    for i in range(5):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if check_powers():
            powers_ok=True
            print 'All powers are ok.'
            break
    return

if __name__ == '__main__':
    debug = False


    # overnight section
    carbons = [3,6]#,6]#[1,2,3,4,5,6,7]
    # C13_X_phase = 0.0

    # msmt_sweep_limits = [
    #     (10, 190, 30),
    #     (190, 340, 30),
    #     (340, 850, 120),
    # ]

    # LDE_calibration_range = [
    #     (2, 35, 3),
    #     (35, 68, 3),
    #     (68, 101, 3)
    # ]

    # msmt_templates = [
    #     {
    #         'carbon_encoding':              'serial_swap',
    #         'carbon_swap_el_states':        ['Z', 'Z'],
    #         'Tomography_list': [
    #             # ['X', 'I'],
    #             # ['I', 'X'],
    #             ['X', 'X'],
    #             [C13_X_phase + 45.0, C13_X_phase + 45.0],
    #             [C13_X_phase + 45.0, C13_X_phase - 45.0],
    #         ]
    #     },
    #     {
    #         'carbon_encoding':              'MBE',
    #         'carbon_swap_el_states':        ['X'],
    #         'Tomography_list': [
    #             ['X', 'X'],
    #             ['Y', 'Y'],
    #             ['Z', 'Z'],
    #             ['X', 'Y'],
    #             ['Y', 'X'],
    #         ]
    #     },
    #     {
    #         'carbon_encoding':              'MBE',
    #         'carbon_swap_el_states':        ['-X'],
    #         'Tomography_list': [
    #             ['X', 'X'],
    #             ['Y', 'Y'],
    #             ['Z', 'Z'],
    #             ['X', 'Y'],
    #             ['Y', 'X'],
    #         ]
    #     }
    # ]


    carbon_combis =[]# list(itertools.combinations(carbons, 2))

    breakst = False
    recalibrate_LDE = True

    start_from_combi = 0

    print("I'm going to do carbon combinations: " + str(carbon_combis[start_from_combi:]))

    want_this = raw_input("Do you want this?")
    if want_this != 'y':
        raise Exception("Getting out of here")

    if False:

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
    if True:
        for c in carbons:
            for p in [False,1e-6,2e-6,3e-6,5e-6]:#[0.1e-6,0.5e-6,1.5e-6,3e-6,False]:
                for LDE_multiplier in [1,2]:#[1,2]:
                    for carbon_pis in [2]:
                        if c == 3:
                            LDE_decoup_time = np.array([15.82e-6])[0]
                        elif c == 6:
                            LDE_decoup_time = np.array([12.81e-6])[0]

                        do_wait = not p
                        print 'do_wait', do_wait
                        check_all_powers()
                        m = {
                            'requested_measurement': 'decay_curve',
                            'carbons': [c],
                            'LDE_decouple_time': LDE_multiplier*LDE_decoup_time,
                            'AWG_SP_power': p,
                            'do_z_in_loop': False,
                            'first_mw_pulse_type':'pi',
                            'do_carbon_hahn_echo': 1,
                            'number_of_carbon_pis': carbon_pis,
                            'skip_LDE_mw_pi' : 1,
                            'MW_during_LDE': 0,
                            'do_wait_instead_LDE': do_wait,
                            'debug': debug
                        }
                        measure()

    if True:
        for ii,p in enumerate([6e-6]):#[4e-6,3e-6,2e-6,1.5e-6,1e-6,0.5e-6,0.1e-6]):
            for carbon_pis in [1,2]:
                for first_pulse in ['pi','pi2']: 
                    for c in carbons:
                        # if (c == 6 and p < 3.5e-6):
                        #     continue
                        if breakst:
                                break

                        taus_dict = {'3':np.array([15.82]*3+[15.8,15.8]+[15.79,15.76])*1e-6,
                                    '6':np.array([12.81]+[12.81]*2+[12.79,12.79]+[12.75,12.73])*1e-6}

                        if str(c) not in taus_dict.keys():
                            raise Exception("The required nuclear spin has no calibrated LDE duration")
                        central_tau = taus_dict[str(c)][ii]
                        # tau_larmor = 2.256e-6
                        # tau_range = 400e-9
                        # taus = np.linspace(central_tau-tau_range,central_tau+tau_range,8) #np.concatenate((benchmark_tau,np.linspace(central_tau,central_tau,13)))
                        taus = [central_tau]

                        if p == 3e-6:
                            do_z_in_loop = True
                        else:
                            do_z_in_loop = False
                        for LDE_decoup_time in taus:
                            if breakst:
                                break
                            breakst = show_stopper()
                            if breakst:
                                break
                            if not debug:
                                optimize()
                                check_all_powers()
                            m = {
                                'requested_measurement': 'decay_curve',
                                'carbons': [c],
                                'first_mw_pulse_type': first_pulse,
                                'LDE_decouple_time': LDE_decoup_time,
                                'AWG_SP_power': p,
                                'do_z_in_loop': do_z_in_loop,
                                'do_carbon_hahn_echo': 1,
                                'MW_during_LDE': 1,
                                'number_of_carbon_pis': carbon_pis,
                                'skip_LDE_mw_pi' : 1,
                                'do_wait_instead_LDE': False,
                                'debug': debug
                            }
                            
                            measure()