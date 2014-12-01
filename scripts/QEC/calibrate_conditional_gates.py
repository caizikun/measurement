"""
Script for a simple Decoupling sequence
Based on Electron T1 script
"""
import numpy as np
import qt
import msvcrt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling_swp_N(name,tau=None, Number_of_pulses=np.arange(80,100,2), 
            Final_Pulse='x', reps_per_ROsequence=1000):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    #input parameters
    m.params['reps_per_ROsequence'] = reps_per_ROsequence
    pts = len(Number_of_pulses)

    if tau == None: 
        tau = m.params['C3_Ren_tau'][0] 
    tau_list = tau*np.ones(pts)
    print 'tau_list =' + str(tau_list)

    #inital and final pulse
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] = Final_Pulse
    #Method to construct the sequence
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    m.params['pts'] = pts
    m.params['tau_list'] = tau_list
    m.params['Number_of_pulses'] = Number_of_pulses
    m.params['sweep_pts'] = Number_of_pulses
    print m.params['sweep_pts']
    m.params['sweep_name'] = 'Number of pulses'

    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    
    Number_of_pulses = np.arange(28,57,2)
    Final_Pulse_list = ['x','-x','y','-y','no_pulse']
    tau_list         = np.linspace(4.984e-6,5.004e-6,11)

    GreenAOM.set_power(5e-6)
    ins_counters.set_is_running(0)  
    optimiz0r.optimize(dims=['x','y','z'])

    for tau in tau_list:
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(4)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        for Final_Pulse in Final_Pulse_list:
            SimpleDecoupling_swp_N(SAMPLE+'sweep_N_' + Final_Pulse +'_tau' +str(tau) , tau =tau, Final_Pulse= Final_Pulse, Number_of_pulses =Number_of_pulses,  
                    reps_per_ROsequence = 2000)



    Number_of_pulses = np.arange(32,61,2)
    Final_Pulse_list = ['x','-x','y','-y','no_pulse']
    tau_list         = np.linspace(8.916e-6,8.936e-6,11)

    GreenAOM.set_power(5e-6)
    ins_counters.set_is_running(0)  
    optimiz0r.optimize(dims=['x','y','z'])

    for tau in tau_list:
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(4)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        for Final_Pulse in Final_Pulse_list:
            SimpleDecoupling_swp_N(SAMPLE+'sweep_N_' + Final_Pulse +'_tau' +str(tau) , tau =tau, Final_Pulse= Final_Pulse, Number_of_pulses =Number_of_pulses,  
                    reps_per_ROsequence = 2000)

    Number_of_pulses = np.arange(12,37,2)
    Final_Pulse_list = ['x','-x','y','-y','no_pulse']
    tau_list         = np.linspace(10.038e-6,10.078e-6,21)

    GreenAOM.set_power(5e-6)
    ins_counters.set_is_running(0)  
    optimiz0r.optimize(dims=['x','y','z'])

    for tau in tau_list:
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(4)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        for Final_Pulse in Final_Pulse_list:
            SimpleDecoupling_swp_N(SAMPLE+'sweep_N_' + Final_Pulse +'_tau' +str(tau) , tau =tau, Final_Pulse= Final_Pulse, Number_of_pulses =Number_of_pulses,  
                    reps_per_ROsequence = 2000)