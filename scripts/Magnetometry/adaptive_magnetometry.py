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
SAMPLE_CFG = qt.exp_params['protocols']['current']
#print SAMPLE_CFG
#print SAMPLE


def rabi (name='', fpga=False):
    '''
    initializes N-spin, then sweeps the duration of the FPGA pulse
    '''


    if fpga:
        n = 'rabi_fpga_pulse_'+name
    else:
        n = 'rabi_awg_pulse_'+name

    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])

    m.params['do_MBI'] = 0
    print 'MW mod frequency:', m.params['MW_modulation_frequency']/1e6, ' MHz'
    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000
    m.params['Ex_SP_amplitude'] = 0
    #m.params['init_repetitions'] = 100
    m.params['M'] = 1
    m.params['reps_majority_vote'] = 1
    m.params['threshold_majority_vote'] = 0
    #m.params['FM_amplitude']=(np.arange(3)-3)*m.params['N_HF_frq']/m.params['FM_sensitivity']
    m.params['FM_amplitude']=np.array([1,0.5,0.5])*m.params['N_HF_frq']/m.params['FM_sensitivity']
    print 'FM_amp'
    print m.params['FM_amplitude']
    nr_adptv_steps = 21
    m.params['do_adaptive'] = 0
    m.params['do_phase_calibr'] = 1
    #m.params['min_phase'] = 0
    #m.params['delta_phase'] = 0 #just to have a label in the ssro data file
    m.params['adptv_steps'] = nr_adptv_steps
    m.params['repetitions'] = 1000
    m.params['MW_only_by_awg'] =  False#variable to do ramsey with only AWG, should be FALSE for rabi msmnts
    m.params['phase_second_pi2'] =  np.zeros(nr_adptv_steps) #variable to do ramsey with only AWG, does nothing for rabi msmnts
    m.params['G']=1
    m.params['F']=0
    m.params['K']=1
    m.params['do_add_phase']=0



    if fpga:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = np.zeros(nr_adptv_steps)
        m.params['MW_pulse_durations'] = np.zeros(nr_adptv_steps)#0*np.linspace(0, 300e-9, nr_adptv_steps)#
        m.params['ramsey_time'] = np.zeros(nr_adptv_steps)
        m.params['fpga_mw_duration'] = (np.arange(nr_adptv_steps)*900)*1e-9#np.linspace (0e-9, 40e-9, nr_adptv_steps)
        m.params['sweep_pts'] = m.params['fpga_mw_duration']*1e9
        m.params['sweep_name'] = 'fpga pulse duration [ns]'

    else:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = m.params['MW_pi2_pulse_amp']*np.ones(nr_adptv_steps)
        m.params['MW_pulse_durations'] = (np.arange(nr_adptv_steps)*900)*1e-9##
        #m.params['MW_pulse_durations'] = (1+np.arange(nr_adptv_steps)*150)*1e-9##
        m.params['ramsey_time'] = 0*np.ones(nr_adptv_steps)
        m.params['fpga_mw_duration'] = np.zeros(nr_adptv_steps)
        m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
        m.params['sweep_name'] = 'awg pulse duration [ns]'
    m.params['phases']=np.linspace(0,0,nr_adptv_steps)
    m.params['phases']=m.params['phases']*255/360  
    
    GreenAOM.turn_off()
    m.autoconfig()
    m.generate_sequence(upload=True)
    adwin.set_adaptive_magnetometry_var(phases=0*np.array(m.params['phases']).astype(int))
    m.run()
    m.save()
    m.finish()


def ramsey (name, fix_tau = None, phase = None,test_only_awg=False):
    '''
    initializes N-spin, ramsey experiment, sweeping time or phase of the fpga pulse
    '''
 
    if (fix_tau==None):
        sweep_time = 1
    else:
        sweep_time = 0

    if sweep_time:
        n = 'ramsey_sweep_time'+name
    else:
        n = 'ramsey_sweep_phase'+str(fix_tau*1e9)+'ns_'+name

    if test_only_awg:
        n = n+'_onlyAWG'
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])

    detuning = 0*500e3
    
    print 'MW mod frequency:', m.params['MW_modulation_frequency']/1e6, ' MHz'
    m.params['Ex_SP_amplitude'] = 0
    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000
    m.params['M'] = 1
    m.params['reps_majority_vote'] = 1
    m.params['threshold_majority_vote'] = 0
    m.params['FM_amplitude']=(np.arange(3)-1)*m.params['N_HF_frq']/m.params['FM_sensitivity']
    m.params['do_MBI'] = 0



    nr_adptv_steps = 21
    m.params['do_adaptive'] = 0
    m.params['do_phase_calibr'] = 1
    m.params['do_add_phase']=0
    m.params['min_phase'] = 0
    m.params['adptv_steps'] = nr_adptv_steps
    m.params['G']=1
    m.params['F']=0
    m.params['K']=1
    m.params['repetitions'] = 1500
    
 
    pi2_mw_dur = m.params['AWG_pi2_duration']
    pi2_fpga_dur =m.params['fpga_pi2_duration']

    if sweep_time:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = m.params['MW_pi2_pulse_amp']*np.ones(nr_adptv_steps)
        m.params['MW_pulse_durations'] = pi2_mw_dur*np.ones(nr_adptv_steps)
        m.params['ramsey_time'] = 1e-9*np.linspace(10, 2510, nr_adptv_steps)
        mod_detuning = m.params['MW_modulation_frequency']
        set_detuning = 500e3
        det=mod_detuning + set_detuning
        m.params['phases']=np.mod(det*360*m.params['ramsey_time']+ m.params['fpga_phase_offset'], 360)
        m.params['fpga_mw_duration'] = pi2_fpga_dur*np.ones(nr_adptv_steps) 
        
        m.params['MW_only_by_awg'] =  test_only_awg #variable to do ramsey with only AWG
        m.params['phase_second_pi2'] =   m.params['phases']
        m.params['sweep_pts'] = m.params['ramsey_time']*1e9
        m.params['sweep_name'] = 'free evolution time [ns]'
        #m.params['sweep_pts'] = np.arange(nr_adptv_steps)*m.params['delta_phase']
        #m.params['sweep_name'] = 'phase fpga pulse [deg]'

    else:
        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = m.params['MW_pi2_pulse_amp']*np.ones(nr_adptv_steps)
        m.params['MW_pulse_durations'] = pi2_mw_dur*np.ones(nr_adptv_steps)
        m.params['ramsey_time'] = fix_tau*np.ones(nr_adptv_steps)
        m.params['fpga_mw_duration'] = pi2_fpga_dur*np.ones(nr_adptv_steps) 
        mod_detuning = m.params['MW_modulation_frequency']
        set_detuning = -0e3
        det=mod_detuning + set_detuning        
        m.params['phases']=np.mod(np.linspace(0,360,nr_adptv_steps)+det*360*m.params['ramsey_time']+ m.params['fpga_phase_offset'], 360)
        
        m.params['MW_only_by_awg'] =  test_only_awg #variable to do ramsey with only AWG
        m.params['phase_second_pi2'] = m.params['phases']
        m.params['sweep_pts'] =  np.linspace(0,360,nr_adptv_steps)
        m.params['sweep_name'] = 'phase fpga pulse [deg]'

    if (m.params['do_MBI']<1):
        m.params['init_repetitions'] = 100


    GreenAOM.turn_off()
    m.params['phases']=m.params['phases']*255/360    
    m.autoconfig()
    m.generate_sequence(upload=True)
    adwin.set_adaptive_magnetometry_var(phases=np.array(m.params['phases']).astype(int))
    m.run()
    m.save()
    m.finish()




def adaptive (name, do_adaptive = False, detuning=0, N=1,M=1, maj_reps =1, maj_thr = 0, tau0=20e-9,repetitions=200,curr_f=None):
    '''
    Ramsey experiment with phases stored in the decision-tree array (DATA_27 in adwin)
    Parameters:
    - nr_adptv_steps
    - M: nr of msmnts per adaptive step
    - majority vote: maj_reps, maj_thr
    '''
 
    opt_nv_pos = False

    if opt_nv_pos:
        counters.set_is_running(True)
        qt.msleep(0.5)
        GreenAOM.set_power(5e-6)
        qt.msleep(0.5)
        cnts=counters.get_cntr1_countrate()
        if cnts<185000:
            optimiz0r.optimize(dims=['x','y','z','y','x'],cnt=1,int_time=100,cycles=1)
    GreenAOM.turn_off()


    n = 'det='+str(detuning/1e6)+'MHz_N='+str(N)+'_M='+str(M)+'_majReps='+str(maj_reps)+'_majThr='+str(maj_thr)+name    
    if (do_adaptive==False):
        n = n+'_non_adptv'
    
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
   
    print 'MW mod frequency:', m.params['MW_modulation_frequency']/1e6, ' MHz'

    m.params['Ex_SP_amplitude'] = 0
    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000
    m.params['M'] = M
    m.params['reps_majority_vote'] = maj_reps
    m.params['threshold_majority_vote'] = maj_thr
    m.params['FM_amplitude']=(np.arange(3)-1)*m.params['N_HF_frq']/m.params['FM_sensitivity']
    m.params['do_MBI'] = 0
    if curr_f:
        m.params['mw_frq']=curr_f-m.params['MW_modulation_frequency']
    nr_adptv_steps = N
    #For both adaptive and no-adaptive we use the same settings in the adwin script
    #the only difference is that we set the adaptive table to zero for the non-adaptive case
    if do_adaptive:
        m.params['do_adaptive'] = 1 
    else:
        m.params['do_adaptive'] = 0
    m.params['do_phase_calibr'] = 0
    m.params['min_phase'] = 0
    m.params['adptv_steps'] = nr_adptv_steps
    m.params['repetitions'] = repetitions
    m.params['tau0'] = tau0
    ttt = int(m.params['tau0']*1e9)
    
    
    m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
    m.params['MW_pulse_amps'] = m.params['MW_pi2_pulse_amp']*np.ones(nr_adptv_steps)
    m.params['MW_pulse_durations'] = m.params['AWG_pi2_duration']*np.ones(nr_adptv_steps)
    m.params['ramsey_time'] = m.params['tau0']*(2**(nr_adptv_steps - np.arange(nr_adptv_steps)-1))
    #m.params['ramsey_time'] = np.linspace(0,60,nr_adptv_steps)*1e-9
    m.params['fpga_mw_duration'] = m.params['fpga_pi2_duration']*np.ones(nr_adptv_steps)       
    m.params['MW_only_by_awg'] =  False

    det=m.params['MW_modulation_frequency'] + detuning
    m.params['set_detuning_value'] = detuning

    m.params['phases_detuning']=det*360*m.params['ramsey_time']+ m.params['fpga_phase_offset']
    
    phase_det = []
    for i in np.arange(nr_adptv_steps):
        #Bayesian update table
        phase_det = phase_det + (((m.params['M']+1)**(i))*[m.params['phases_detuning'][i]])
    phase_det = np.array(phase_det)
    print 'phase array len: ', len(phase_det)
    if do_adaptive:    
        a = np.load ('D:/measuring/measurement/scripts/Magnetometry/adaptive_tables_lt1/tau0='+str(ttt)+'ns/adptv_table_cappellaro_N='+str(nr_adptv_steps)+'_M='+str(M)+'.npz')
        adaptv_phases = a['table'][:]
        print adaptv_phases
    else:
        adaptv_phases = np.zeros(len(phase_det))
    phases = np.mod(phase_det + adaptv_phases, 360)
    
    m.params['sweep_pts'] = m.params['ramsey_time']*1e9
    m.params['sweep_name'] = 'free evolution time [ns]'

    phases=phases*255/360    
    m.autoconfig()
    m.generate_sequence(upload=True)
    adwin.set_adaptive_magnetometry_var(phases=np.array(phases).astype(int))
    m.run()
    m.save()
    m.finish()


def sample_B_space(N, M, maj_reps, maj_thr,repetitions=200,curr_f=None,stop=False):

    tau0 = 20e-9
    delta_f = 1./(tau0*(2**N))
    print 'Period: ', delta_f/1e6, ' MHz'
    nr_available_periods = 2**N
    nr_periods_to_sweep = 3
    nr_points_per_period = 7 

    if (nr_periods_to_sweep>nr_available_periods):
        nr_periods_to_sweep = nr_available_periods
    
    periods = np.unique(np.random.randint(0, nr_available_periods, size=nr_periods_to_sweep)-nr_available_periods/2)
    print periods
    ind_per = 0
    for per in periods:
        if stop: break
        B = np.linspace(per*delta_f, (per+1)*delta_f, nr_points_per_period)
        ind_b = 0
        for bbb in B:
            if (msvcrt.kbhit() and (msvcrt.getch() == 'x')): stop=True
            s,cnts =optimize(185000,1)
            if s:
                print 'Optimize: ', s
                print 'Counts: ', cnts
            else:
                print 'Optimizing Failed, stopping loop'
                stop=True  
            if stop: break      
            label = '_p'+str(ind_per)+'b'+str(ind_b)  
            adaptive (name = label, do_adaptive=True, detuning = bbb, N=N, M=M, maj_reps=maj_reps, maj_thr=maj_thr, tau0=tau0,repetitions=repetitions,curr_f=curr_f)
            qt.msleep(1)
            ind_b+=1
            if stop: break
        ind_per+=1
        if stop: break
    return stop
def sample_B_space_realtime_varM(N, G,F,repetitions=200,curr_f=None,stop=False,add_phase=False,do_adaptive=True):
    tau0 = 20e-9
    delta_f = 1./(tau0*(2**N))
    print 'Period: ', delta_f/1e6, ' MHz'
    nr_available_periods = 2**N
    nr_periods_to_sweep = 1
    nr_points_per_period = 7 

    if (nr_periods_to_sweep>nr_available_periods):
        nr_periods_to_sweep = nr_available_periods
    
    periods = np.unique(np.random.randint(0, nr_available_periods, size=nr_periods_to_sweep)-nr_available_periods/2)
    print periods
    ind_per = 0
    for per in periods:
        if stop: break
        B = np.linspace(per*delta_f, (per+1)*delta_f, nr_points_per_period)
        ind_b = 0
        for bbb in B:
            if (msvcrt.kbhit() and (msvcrt.getch() == 'x')): stop=True
            '''
            s,cnts =optimize(178000,5)
            if s:
                print 'Optimize: ', s
                print 'Counts: ', cnts
            else:
                print 'Optimizing Failed, stopping loop'
                stop=True  
            '''
            if stop: break      
            label = '_p'+str(ind_per)+'b'+str(ind_b)  
            #adaptive_realtime_variableM (name=label, N=N, F=F, G=G, curr_f=curr_f,do_adaptive = do_adaptive, add_phase=add_phase,detuning=bbb, repetitions=repetitions, adwin_test = [], save_pk_n = 0, save_pk_m = 0)
            adaptive_realtime_swarm_opt (name=label, N=N, F=F, G=G, curr_f=curr_f, detuning=bbb, repetitions=repetitions)
            qt.msleep(1)
            ind_b+=1
            if stop: break
        ind_per+=1
        if stop: break
    return stop    
def optimize(threshold,max_nr_of_tries=1):
    for i in np.arange(max_nr_of_tries):
        counters.set_is_running(True)
        qt.msleep(0.5)
        GreenAOM.set_power(5e-6)
        qt.msleep(0.5)
        optimiz0r.optimize(dims=['x','y','z','y','x'],cnt=1,int_time=100,cycles=1)
        cnts=counters.get_cntr1_countrate()
        GreenAOM.turn_off()
        if cnts>threshold:
            Succes=True
        else:
            Succes=False
        if Succes:break
            
    return Succes, cnts

def ESR(curr_f):
    darkesr.darkesr_FM(SAMPLE_CFG,width=4,upload=True,f_msm1_cntr=curr_f)
    qt.msleep(2)

    try:     
        f=toolbox.latest_data('DarkESR')
        res=dark_esr_analysis.analyze_dark_esr(f,curr_f*1e-9)
        measured_f=(res[0]*1e-3+2.8)*1e9
        if (np.abs(measured_f-curr_f)>100e3):
            new_f=curr_f
        else:
            new_f=measured_f    
    except:
        new_f=curr_f    
    return new_f



def adaptive_realtime (name, N, M, do_adaptive = False, detuning=0, maj_reps =1, maj_thr = 0,repetitions=250, adwin_test = None, save_p_k = 0):
    '''
    Ramsey experiment with phases calculated in real-time by the adwin according to the Cappellaro protocol
    
    Uses adwin script: adaptive_magnetometry_realtime_lt1.bas

    Parameters:
    - nr_adptv_steps (=N)
    - M: nr of msmnts per adaptive step
    - majority vote: maj_reps, maj_thr
    '''

    print '$$$$$$$$$$$$$$$$$$$$ M = ', M, ' $$$$$$$$$$$$$$$$$$$$$$$$$'

    if ((save_p_k>0)&(save_p_k<=N)):
        name = '_pk_n='+str(save_p_k)
    adwin_test_cond = ((type(adwin_test)==np.ndarray) & (len(adwin_test)>=N))
    if adwin_test_cond:
        ss = ''
        for i in np.arange(N):
            ss = ss + str(adwin_test[i])
        n = 'N='+str(N)+'_M='+str(M)+'_rtAdwin_'+ss+'_test'+name
    else:
        n = 'det='+str(detuning/1e6)+'MHz_N = '+str(N)+'_M='+str(M)+'_rtAdwin_'+name    
    if (do_adaptive==False):
        n = n+'_non_adptv'
    nr_adptv_steps = N
    
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])

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

    det=m.params['MW_modulation_frequency'] + detuning
    m.params['set_detuning_value'] = detuning
    m.params['phases_detuning']=det*360*m.params['ramsey_time']+ m.params['fpga_phase_offset']
    m.params['sweep_pts'] = m.params['ramsey_time']*1e9
    m.params['sweep_name'] = 'free evolution time [ns]'
    if adwin_test_cond:
        m.params['do_ext_test'] = 1
    else:
        m.params['do_ext_test'] = 0

    #Protocol parameters
    m.params['do_adaptive'] = 1 
    m.params['repetitions'] = repetitions
    m.params['adptv_steps'] = N
    m.params['M'] = M 
    m.params['reps_majority_vote'] = 1
    m.params['threshold_majority_vote'] = 0
    m.params['G'] = 5
    m.params['F'] = 3
    m.params['renorm_ssro_M'] = 0
    m.params['fid0'] = 0.87
    m.params['fid1'] = 0.02
    m.params['save_p_k'] = save_p_k



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
    adwin_test_cond = False#((type(adwin_test)==np.ndarray) & (len(adwin_test)>=N))

    if adwin_test_cond:
        ss = ''
        for i in np.arange(N):
            ss = ss + str(adwin_test[i])
        n = 'N='+str(N)+'_'+name_m+'_rtAdwin_'+ss+'_test'+name
        adwin_test = adwin_test[:N]
    else:
        if add_phase:
            n = 'det='+str(detuning/1e6)+'MHz_N = '+str(N)+'_'+name_m+'_addphase_rtAdwin_'+name    
        else:    
            n = 'det='+str(detuning/1e6)+'MHz_N = '+str(N)+'_'+name_m+'_rtAdwin_'+name    
    if (do_adaptive==False):
        n = n+'_non_adptv'

    nr_adptv_steps = N
    GreenAOM.turn_off()
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
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


def adaptive_realtime_swarm_opt (name, N, F, G, curr_f=None, detuning=0, repetitions=250):
    '''
    Ramsey experiment with phases calculated in real-time by the adwin according to the Berry's protocol,
    involving:  i) Cappellaro phase, calculated before each read-out
                ii) swarm-optimized phase increment, dependent on last measurement outcome
    
    Uses adwin script: adaptive_magnetometry_superoptimized_lt1.bas

    Parameters:
    -----------
    - N: nr_adptv_steps
    - M: nr of msmnts per adaptive step. If M>0, then we use constant M.
      Otherwise, if M<1, then we use variable-M, as: M = G+F(N-n)  
    - majority vote: maj_reps, maj_thr. We do not use maj vote, so we set maj_reps=1, maj_thr=0
    - Bayesian update is performed by exploiting the full knowledge over our experimetn, i.e. using T2* and RO-fid (fid0, fid1)

    Swarm optimization arrays are loaded from d:/measuring/analysis/scripts/magnetometry/swarm_optimization/ 
    and passed to adwin
    
    Data is saved such that we save every read-out outcome with the corresponding set phase
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

    n = 'det='+str(detuning/1e6)+'MHz_N = '+str(N)+'_'+name_m+'_swarm'+name    

    nr_adptv_steps = N
    K=N-1
    GreenAOM.turn_off()
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
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
    m.params['do_ext_test'] = 0
    m.params['do_add_phase'] = 0
    m.params['do_adaptive'] = 1 
    
    m.params['repetitions'] = repetitions
    m.params['adptv_steps'] = N
    m.params['M'] = 0
    m.params['reps_majority_vote'] = 1
    m.params['threshold_majority_vote'] = 0
    m.params['G'] = G
    m.params['F'] = F
    m.params['renorm_ssro_M'] = 0
    m.params['fid0'] = 0.8756
    m.params['fid1'] = 0.0146
    m.params['T2'] = 96e-6/20e-9 #T2* in units of tau0
    m.params['save_pk_n'] = 0
    m.params['save_pk_m'] = 0
    m.params['swarm_opt'] = True
    
    swarm_opt_pars = np.load ('D:/measuring/analysis/scripts/magnetometry/swarm_optimization/phases_G'+str(G)+'_F'+str(F)+'/swarm_opt_G='+str(G)+'_F='+str(F)+'_K='+str(K)+'.npz')
    u0 = swarm_opt_pars['u0']
    u1 = swarm_opt_pars['u1']          

    phases = np.mod(m.params['phases_detuning'], 360)

    m.autoconfig()
    m.generate_sequence(upload=True)
    adwin.set_adaptive_magnetometry_realtime_swarm_var(phases=np.array(phases).astype(int))
    adwin.set_adaptive_magnetometry_realtime_swarm_var(swarm_u0=np.array(u0).astype(float))
    adwin.set_adaptive_magnetometry_realtime_swarm_var(swarm_u1=np.array(u1).astype(float))    
    
    m.run()
    m.save()
    m.finish()


if __name__ == '__main__':
    #adaptive_realtime_swarm_opt (name='', N=12, F=2, G=5, curr_f=None, detuning=-10e6, repetitions=101)

    #for t in [50e-9, 60e-9, 70e-9, 100e-9, 200e-9, 300e-9, 500e-9, 1000e-9]:
    #for i in np.arange(3)-9:
    
    #rabi (name='msp1_lines_AWG', fpga=False)

    #ramsey (name='det_20kHz', fix_tau = None,test_only_awg=False)
    curr_f=0.286e6+2.845e9

    stop_scan=False
    f_list = []
    #sample_B_space_realtime_varM(N=2, G=5,F=2,add_phase=False,do_adaptive=True,repetitions=2,curr_f=curr_f,stop=False)
    
    for i in [12]:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'x')): stop_scan=True
        if stop_scan: break
        #ssro_calibration.ssrocalibration(qt.exp_params['protocols']['current'])
        #ssro.ssrocalib()
        stop_scan=sample_B_space_realtime_varM(N=i, G=5,F=2,add_phase=False,do_adaptive=True,repetitions=101,curr_f=curr_f,stop=False)
        #stop_scan=sample_B_space (N=i+1, M =3, maj_reps=7, maj_thr = 2,repetitions=250,curr_f=curr_f)
        
        if stop_scan: break
        curr_f=ESR(curr_f)
        print 'Measured frequency : ', curr_f
        f_list.append(curr_f)
    

