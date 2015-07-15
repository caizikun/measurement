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

    print 'threshold =' + str(m.params['MBI_threshold'])

    # m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])
    pts_coarse = 31
   
    fine_pts = 51
    fine_range = 0.4e6
    n_split = m.params['N_HF_frq']
    mw_mod = m.params['MW_modulation_frequency']
    outer_minus = np.linspace(mw_mod-1e6,mw_mod-fine_range,pts_coarse)
    outer_plus = np.linspace(mw_mod+fine_range,mw_mod+1e6,pts_coarse) + 2*n_split
    aplus_list = np.linspace(mw_mod-fine_range,mw_mod+fine_range,fine_pts) +2*n_split
    a0_list = np.linspace(mw_mod-fine_range,mw_mod+fine_range,fine_pts) + n_split
    amin_list = np.linspace(mw_mod-fine_range,mw_mod+fine_range,fine_pts)

    amin_to_a0 = np.linspace(mw_mod+fine_range,mw_mod-fine_range+n_split,pts_coarse)

    a0_to_aplus = np.linspace(mw_mod+fine_range+n_split,mw_mod-fine_range+2*n_split,pts_coarse)
    # m.params['MW_pulse_mod_frqs']   = np.linspace(m.params['MW_modulation_frequency']
    #         -1.5e6, m.params['MW_modulation_frequency']+5.5e6, pts)

    m.params['MW_pulse_mod_frqs'] = np.r_[outer_minus,amin_list,amin_to_a0,a0_list,a0_to_aplus,aplus_list,outer_plus]
    print m.params['MW_pulse_mod_frqs']

    pts = len(m.params['MW_pulse_mod_frqs'])
    m.params['reps_per_ROsequence'] = 250
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 2500e-9

    # MW pulses
    m.params['MW_pulse_durations']  = np.ones(pts) * 8e-6 #m.params['AWG_MBI_MW_pulse_duration']*4 #3e-6 #3000e-9
    m.params['MW_pulse_amps']       = np.ones(pts) * 0.006 #m.params['AWG_MBI_MW_pulse_amp']/4  #0.01525 #for msm1,  ??? for msp1, 

    m.params['pts'] = pts

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse frequency (MHz)'
    m.params['sweep_pts']  = (m.params['MW_pulse_mod_frqs'] + m.params['mw_frq'])/1.e6
    

    print m.params['MBI_threshold']
    funcs.finish(m, debug=False)

    # print m.params['AWG_MBI_MW_pulse_mod_frq']

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(2)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def optimize():
    GreenAOM.set_power(15e-6)
    counters.set_is_running(1)
    optimiz0r.optimize(dims = ['x','y','z','y','x'])

if __name__ == '__main__':
    # run('MBI_DESR',mw_switch = True)



    #### below: long term measurement loop!!

    breakstatement = False

    last_optimize = time.time()
    start_time = time.time()

    optimize()

    while abs(time.time()- start_time) < 12*60*60: ### 12 hours of measurement. HOOORAY!
        #some info
        print 'Time until I stop', 12*60*60 - (time.time()- start_time)

        ### stop experiment? Press q.
        breakstatement = show_stopper()
        if breakstatement: break

    #     ## run experiment
        run('MBI_DESR',mw_switch = True)

        ### optimize on NV position if necessary.

        print 'last optimize', 0.5*60*60 - (time.time()-last_optimize)
        if abs(time.time()-last_optimize) > 0.5*60*60:
            optimize()
            last_optimize = time.time()