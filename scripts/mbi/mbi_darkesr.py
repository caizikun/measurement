import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
import time
import msvcrt

execfile(qt.reload_current_setup)
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)


def run(name, mw_switch = False):

    if mw_switch:
        m = pulsar_mbi_espin.ElectronRabi_Switch(name)
    else:
        m = pulsar_mbi_espin.ElectronRabi(name)

    funcs.prepare(m)

    # m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])
    pts = 81
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 1582e-9

    # MW pulses
    m.params['MW_pulse_durations']  = np.ones(pts) * m.params['AWG_MBI_MW_pulse_duration'] #3e-6 #3000e-9
    m.params['MW_pulse_amps']       = np.ones(pts) * m.params['AWG_MBI_MW_pulse_amp']  #0.01525 #for msm1,  ??? for msp1, 

    m.params['MW_pulse_mod_frqs']   = np.linspace(m.params['MW_modulation_frequency']
            -3.5e6, m.params['MW_modulation_frequency']+3.5e6, pts)

    print m.params['MW_pulse_mod_frqs']



    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse frequency (MHz)'
    m.params['sweep_pts']  = (m.params['MW_pulse_mod_frqs'] + m.params['mw_frq'])/1.e6
    

    # print 'MBI_Threshold', m.params['MBI_threshold']
    funcs.finish(m, debug=False)



# def show_stopper():
#     print '-----------------------------------'            
#     print 'press q to stop measurement cleanly'
#     print '-----------------------------------'
#     qt.msleep(2)
#     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
#         return True
#     else: return False

# def optimize():
#     GreenAOM.set_power(15e-6)
#     counters.set_is_running(1)
#     optimiz0r.optimize(dims = ['x','y','z','y','x'])

if __name__ == '__main__':
    run('MBI_DESR',mw_switch = True)






