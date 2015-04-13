import numpy as np
import qt
import msvcrt
from analysis.scripts.QEC import carbon_ramsey_analysis as cr 
reload(cr)

execfile(qt.reload_current_setup)

ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs
import measurement.scripts.QEC.carbon_calibration_routine as CCR

if __name__ == '__main__':
	CCR.NuclearRamseyWithInitialization_cal(name, 
	        carbon_nr           = 5,               
	        carbon_init_state   = 'up', 
	        el_RO               = 'positive',
	        detuning            = 0.1e3,
	        el_state            = 1,
	        debug               = False)