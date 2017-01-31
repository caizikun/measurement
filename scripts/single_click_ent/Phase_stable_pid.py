"""
LT2 script for adwin ssro.
"""
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

# import the msmt class
from measurement.scripts.single_click_ent import Timing_PID; reload(Timing_PID)

SAMPLE_CFG = qt.exp_params['protocols']['current']


def Phase_stable_pid(name, **additional_params):
    m = Timing_PID.PIDtiming('PIDmsmt_'+name)

    m.params['PhaseAOMvoltage'] = 1
    m.params['PID_cycles'] = 500
    m.params['sample_cycles'] = 5000
    m.params['delay'] = 2
    m.params['max_repetitions'] = 100

    m.run()
    
    m.save()

    m.finish()

if __name__ == '__main__':
    for i in range(10):
        # stools.turn_off_all_lasers()
        Phase_stable_pid(SAMPLE_CFG)

    
