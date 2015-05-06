import qt

def do_optimize_rejection():
    if qt.current_setup=='lt4':
        print 'Starting  Optimize rejection LT4'
        stools.start_bs_counter()
		PulseAOM.turn_on()
		qt.msleep(0.5)
		qt.instruments['rejecter'].nd_optimize(max_range=15,stepsize=1.,method=2,quick_scan=False)
		qt.msleep(0.5)
		PulseAOM.turn_off()
        lt3_helper = qt.instruments['lt3_helper']
        lt3_helper.set_is_running(False)
        lt3_helper.set_script_path(r'Y:/measurement/scripts/bell/optimize_rejection.py')
        lt3_helper.execute_script()
        while lt3_helper.get_is_running():
            if(msvcrt.kbhit() and msvcrt.getch()=='q'): 
                print 'measurement aborted'
                break
            qt.msleep(0.2)
        output = lt3_helper.get_measurement_name()
        print output
    else:
        print 'Starting Optmize rejection LT3'
        PulseAOM.turn_on()
		qt.msleep(0.5)
        qt.instruments['rejecter'].nd_optimize(max_range=15,stepsize=2.,method=2,quick_scan=True)
        qt.msleep(0.5)
        PulseAOM.turn_off()

if __name__ == '__main__':
    do_optimize_rejection()


