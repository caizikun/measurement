### test ###

import qt
import os
import traceback
from instrument import Instrument
import numpy as np
from collections import deque
import gobject
import instrument_helper
from lib import config
from analysis.lib.fitting import common,fit
import multiple_optimizer as mo
reload(mo)


class phase_stab_calib(class):
    def __init__(self, name):
        ins_pars  ={'min_cr_counts'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10},
                    }           
        instrument_helper.create_get_set(self,ins_pars)

        qt.instruments['counters'].set_is_running(True) 
        V_max = qt.instruments['PhaseAOM'].get_V_max()

    def measure_counts(self):
        print 'Calibrating PhaseAOM countrate'
        for i in xrange(100):
            qt.instruments['PhaseAOM'].apply_voltage(V_max*i/1000)
            qt.msleep(0.1)
            counts = qt.instruments['counters'].get_countrate()
            if (counts > 1e6):
                self.V_setpoint = V_max*i/1000
                return False

            
    def measure_interferometer(self):
        qt.instruments['adwin'].load_fibre_stretcher_setpoint()
        qt.instruments['adwin'].start_fibre_stretcher_setpoint(delay = 4)
        print 'Calibrating Interferometer'
        qt.msleep(20)
        qt.instruments['adwin'].stop_fibre_stretcher_setpoint()


if __name__ == '__main__':

    print 'Start Phase stability Calibration'
    self.measure_counts()
    self.measure_interferometer()
    g_0 = qt.instrument['physical_adwin'].Get_FPar(75)
    visibility = qt.instrument['physical_adwin'].Get_FPar(76)

    self.save_adwin_data(name,[ ('AOM_setpoint',1, self.V_setpoint),
                                ('g_0',1, g_0),
                                ('Visibility',1, visibility),
                                ])
    print 'Finished'



