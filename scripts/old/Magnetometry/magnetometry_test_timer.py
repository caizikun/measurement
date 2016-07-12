"""
Script for adaptive magnetometry. Uses deterministic N-spin initialization by conditional MW and spin-pumping
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import msvcrt

# import the msmt class
#from measurement.lib.measurement2.adwin_ssro import ssro
#from measurement.scripts.Magnetometry import ssro_calibration
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from analysis.scripts.espin import dark_esr_analysis
from analysis.lib.tools import toolbox
#from analysis.lib.m2.ssro import ssro

from measurement.scripts.Magnetometry import pulsar_magnetometry as pulsar_mgnt
reload(pulsar_mgnt)
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)
from measurement.scripts.espin import darkesr

#reload(darkesr)


SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['Gretel_sil10']
#print SAMPLE_CFG
#print SAMPLE



def adaptive_realtime_variableM (name, N, F, G, curr_f=None,do_adaptive = False, add_phase=False,detuning=0, repetitions=250, adwin_test = None, save_pk_n = 0, save_pk_m = 0):
    '''
    Ramsey experiment with phases calculated in real-time by the adwin according to the Cappellaro protocol
    
    Uses adwin script: adaptive_magnetometry_realtime_variableM_lt1.bas

    Parameters:
    -----------
    - N: nr_adptv_steps
    - M: nr of msmnts per adaptive step. If M>0, then we use constant M.
      Otherwise, if M<1, then we use variable-M, as: M = G+F(N-n)  
    - majority vote: maj_reps, maj_thr. We do not use maj vote, so we set maj_reps=1, maj_thr=0
    - Bayesian update is performed by exploiting the full knowledge over our experimetn, i.e. using T2* and RO-fid (fid0, fid1)
    - save_p_k: allows to store one selected probability distribution for debugging
    - adwin_test: array with externally-feeded msmnt results to test the adwin
    '''

    if (F==0):
        protocol = 'constant M, M = '+str(G)
        M = G
        F = 0
    else:
        protocol = 'M_n = '+str(G)+'+'+str(F)+'('+str(N)+'-n)'
        M = 0

    name_m = 'M=('+str(G)+', '+str(F)+')'
    print ' ------- ADAPTIVE MAGNETOMETRY ----------------------'
    print 'protocol: '+protocol
    print

    if (save_pk_n>0):
        name = '_pk_(n='+str(save_pk_n)+'_m='+str(save_pk_m)+')'
    adwin_test_cond = ((type(adwin_test)==np.ndarray) & (len(adwin_test)>=N))

    if adwin_test_cond:
        print 'Test!!!'
        ss = ''
        for i in np.arange(N):
            ss = ss + str(adwin_test[i])
        n = 'N='+str(N)+'_'+name_m+'_rtAdwin_timerTest'
        adwin_test = adwin_test[:N]
    else:
        if add_phase:
            n = 'det='+str(detuning/1e6)+'MHz_N = '+str(N)+'_'+name_m+'_addphase_rtAdwin_'+name    
        else:    
            n = 'det='+str(detuning/1e6)+'MHz_N = '+str(N)+'_'+name_m+'_rtAdwin_'+name    
    if (do_adaptive==False):
        n = n+'_non_adptv'

    nr_adptv_steps = N
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols']['Gretel_sil10']['Magnetometry'])
    if curr_f:
        m.params['mw_frq']=curr_f-m.params['MW_modulation_frequency']
    # General measurement parameters   
    m.params['tau0'] = 20e-9
    m.params['Ex_SP_amplitude'] = 0
    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000   
    m.params['FM_amplitude']=(np.arange(3)-1)*m.params['N_HF_frq']/m.params['FM_sensitivity']
    m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
    m.params['MW_pulse_amps'] = m.params['MW_pi2_pulse_amp']*np.ones(nr_adptv_steps)
    m.params['MW_pulse_durations'] = m.params['AWG_pi2_duration']*np.ones(nr_adptv_steps)
    m.params['ramsey_time'] = m.params['tau0']*(2**(nr_adptv_steps - np.arange(nr_adptv_steps)-1))
    m.params['fpga_mw_duration'] = m.params['fpga_pi2_duration']*np.ones(nr_adptv_steps)       
    m.params['MW_only_by_awg'] =  False
    m.params['do_MBI'] = 0
    m.params['do_phase_calibr'] = 0
    det=m.params['MW_modulation_frequency'] + detuning
    m.params['set_detuning_value'] = detuning
    m.params['phases_detuning']=det*360*m.params['ramsey_time']+ m.params['fpga_phase_offset']
    m.params['sweep_pts'] = m.params['ramsey_time']*1e9
    m.params['sweep_name'] = 'free evolution time [ns]'
    m.params['swarm_opt'] = False
    if adwin_test_cond:
        m.params['do_ext_test'] = 1
    else:
        m.params['do_ext_test'] = 0

    #Protocol parameters
    if add_phase:
        m.params['do_add_phase'] = 1
    else:
        m.params['do_add_phase'] = 0

    if do_adaptive:
        m.params['do_adaptive'] = 1 
    else:
        m.params['do_adaptive'] = 0    
    
    m.params['repetitions'] = repetitions
    m.params['adptv_steps'] = N
    m.params['M'] = M
    m.params['reps_majority_vote'] = 1
    m.params['threshold_majority_vote'] = 0
    m.params['G'] = G
    m.params['F'] = F
    m.params['renorm_ssro_M'] = 0
    m.params['fid0'] = 0.8756
    m.params['fid1'] = 0.0146
    m.params['T2'] = 96e-6/20e-9 #T2* in units of tau0
    m.params['save_pk_n'] = save_pk_n
    m.params['save_pk_m'] = save_pk_m


    phases = np.mod(m.params['phases_detuning'], 360)

    m.autoconfig()
    m.generate_sequence(upload=True)
    adwin.set_adaptive_magnetometry_realtime_var(phases=np.array(phases).astype(int))
    if adwin_test_cond:
        print '--------------------------------------------------------------'
        print '     Running ADwin test with pre-calculated msmsnt results!   '
        print '     results: ', adwin_test, ' - M =', M
        print '--------------------------------------------------------------'

        adwin.set_adaptive_magnetometry_realtime_var(ext_msmnt_results=adwin_test.astype(int))
    
    m.run()
    m.save()
    m.finish()


for nn in np.arange (11)+2:
    adaptive_realtime_variableM (name='test_timer', N=nn, F=0, G=5, do_adaptive=True, adwin_test = np.zeros(800), repetitions=20)

for nn in np.arange (11)+2:
    adaptive_realtime_variableM (name='test_timer', N=nn, F=2, G=5, do_adaptive=True, adwin_test = np.zeros(800), repetitions=20)

for nn in np.arange (11)+2:
    adaptive_realtime_variableM (name='test_timer', N=nn, F=7, G=5, do_adaptive=True, adwin_test = np.zeros(800), repetitions=20)
