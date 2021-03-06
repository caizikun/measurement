import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
import time
import msvcrt

from measurement.lib.measurement2.adwin_ssro import DD_2 as DD

execfile(qt.reload_current_setup)
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)


def run(name, mw_switch = False):

    if mw_switch:
        m = pulsar_mbi_espin.ElectronRabi_Switch(name)
    else:
        m = pulsar_mbi_espin.NitrogenRabiDirectRF(name)

    funcs.prepare(m)
    m.params['centerfreq'] = 5.068e6
    # m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])
    pts = 31
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 300
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 100e-9

    # # MW pulses
    # m.params['MW_pulse_durations']  = np.linspace(10e-9,5e-6,pts) #3e-6 #3000e-9
    # print 'MW_pulse_durateions', m.params['MW_pulse_durations']
    # m.params['MW_pulse_amps']       = 0*np.ones(pts) * m.params['AWG_MBI_MW_pulse_amp']  #0.01525 #for msm1,  ??? for msp1, 

    # m.params['MW_pulse_mod_frqs']   = np.ones(pts) * m.params['MW_modulation_frequency']

    # print m.params['MW_pulse_mod_frqs']

    ## RF parameters

    m.params['RF_pulse_amps'] = np.ones(m.params['pts']) * 1
    m.params['RF_pulse_length'] = np.linspace(1e-6, 1000e-6, pts)
    # m.params['RF_pulse_durations'] = 10e-6 + np.linspace(0e-6,10e-6,pts)
    m.params['RF_pulse_frqs'] = m.params['centerfreq']# np.linspace(m.params['centerfreq']-50e3,m.params['centerfreq']+50e3,pts) #np.linspace(m.params['centerfreq']-50e3,m.params['centerfreq']+50e3,pts)
    m.params['sweep_name'] = 'RF_pulse_length (us)'
    m.params['RF_pulse_amp'] = 0.35 




    # for the autoanalysis
    m.params['sweep_name'] = 'RF_pulse_length (us)'
    m.params['sweep_pts']  = (m.params['RF_pulse_length'])/1.e-6
    

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
    run('MBI_RABI',mw_switch = False)






