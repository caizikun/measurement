"""
Script for fine optimization of the magnet XY-position (using the average ms=-1, ms=+1 freq).
Fine optimization measures only the center resonance
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""
import numpy as np
import qt
import msvcrt
from analysis.lib.fitting import fit, common; reload(common)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

# import the DESR measurement, DESR fit, magnet tools and master of magnet
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']; reload(mt)

execfile(qt.reload_current_setup)

ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

nm_per_step = qt.exp_params['magnet']['nm_per_step']
current_f_msp1 = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

def SimpleDecoupling_swp_tau(name,tau_min=9e-6,tau_max=10e-6,tau_step =50e-9, N =16):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    if N%4 == 0: 
        m.params['Final_Pulse'] ='-x'
    else:
        m.params['Final_Pulse'] ='x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    Number_of_pulses = N 
    tau_list = np.arange(tau_min,tau_max,tau_step) 
    print tau_list

    m.params['pts']              = len(tau_list)
    m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
    m.params['tau_list']         = tau_list
    m.params['sweep_pts']        = tau_list*1e6
    m.params['sweep_name']       = 'tau (us)'

    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    
    ######################
    ## Input parameters ##
    ######################

    range_coarse = 5.00
    pts_coarse  = 81   
    reps_coarse   = 500

    range_fine = 0.25
    pts_fine  = 51   
    reps_fine   = 4000

    for ii in range(10000):

        ###########
        ## start ##
        ###########

        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        #use a higher threshold at the very end
        GreenAOM.set_power(5e-6)
        ins_counters.set_is_running(0)
        int_time = 1000 
        cnts = ins_adwin.measure_counts(int_time)[0]
        print 'counts = '+str(cnts)
        if cnts < 30e4:
            optimiz0r.optimize(dims=['x','y','z'])

        #measure both frequencies
            #ms=-1 coarse
        DESR_msmt.darkesr('magnet_msm1_coarse', ms = 'msm', range_MHz=range_coarse, pts=pts_coarse, reps=reps_coarse)
        f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msm1*1e-9, qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9)
            #ms=-1 fine
        DESR_msmt.darkesr('magnet_msm1', ms = 'msm', range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0m_temp*1e9)
        f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr_single(current_f_msp1*1e-9)
                   
        qt.msleep(1)
        
            #ms=+1 coarse
        DESR_msmt.darkesr('magnet_msp1_coarse', ms = 'msp', range_MHz=range_coarse, pts=pts_coarse, reps=reps_coarse)
        f0p_temp, u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9, qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9)
            #ms=+1 fine
        DESR_msmt.darkesr('magnet_msp1', ms = 'msp', range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0p_temp*1e9)
        f0p_temp, u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr_single(current_f_msp1*1e-9)

        Bz_measured, Bx_measured = mt.get_B_field(msm1_freq=f0m_temp*1e9, msp1_freq=f0p_temp*1e9)
        
        f_centre    = (f0m_temp+f0p_temp)/2
        f_diff = (f_centre-ZFS*1e-9)*1e6


        print '-----------------------------'
        print 'Fitted ms-1 transition frequency is '+str(f0m_temp)+' GHz' + ' +/- ' + str(u_f0m_temp*1e6) + ' khz'
        print 'Fitted ms+1 transition frequency is '+str(f0p_temp)+' GHz' + ' +/- ' + str(u_f0p_temp*1e6) + ' khz'
        print 'Calculated centre between ms=-1 and ms=+1 is '+ str(f_centre)+' GHz +/- '+str((u_f0m_temp**2+u_f0p_temp**2)**(1./2)/2*1e6)+' kHz'
        print 'Difference to ZFS = '+ str((f_centre-ZFS*1e-9)*1e6)+ 'kHz'
        print 'Measured B_field is: Bz = '+str(Bz_measured)+ ' G ,Bx = '+str(Bx_measured)+ ' G'
        print '-----------------------------'
       


        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        #use a higher threshold at the very end
        GreenAOM.set_power(5e-6)
        ins_counters.set_is_running(0)
        int_time = 1000 
        cnts = ins_adwin.measure_counts(int_time)[0]
        print 'counts = '+str(cnts)
        if cnts < 30e4:
            optimiz0r.optimize(dims=['x','y','z'])

        SimpleDecoupling_swp_tau(SAMPLE+'_msmt_around15_'+str(ii), tau_min=15.0e-6,tau_max=15.5e-6,tau_step =10e-9, N =32)
        
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        #use a higher threshold at the very end
        GreenAOM.set_power(5e-6)
        ins_counters.set_is_running(0)
        int_time = 1000 
        cnts = ins_adwin.measure_counts(int_time)[0]
        print 'counts = '+str(cnts)
        if cnts < 30e4:
            optimiz0r.optimize(dims=['x','y','z'])

        SimpleDecoupling_swp_tau(SAMPLE+'_msmt_around18_'+str(ii), tau_min=18.3e-6,tau_max=18.8e-6,tau_step =10e-9, N =32)


