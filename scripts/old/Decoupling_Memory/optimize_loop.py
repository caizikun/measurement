"""
MAB 24-4-2015
ElectronT1 using dynamicaldecoupling class
"""
import numpy as np
import qt 
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


def qstop(sleep=2):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True



if __name__ == '__main__':
  while True:
    print '--------------------------------'
    print 'press q to stop optimize loop'
    print '--------------------------------'
    qt.msleep(10)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        break
    else:
        GreenAOM.set_power(20e-6)
        counters.set_is_running(1)
        optimiz0r.optimize(dims = ['x','y','z','x','y'], int_time = 120)