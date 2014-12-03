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
            Final_Pulse='x', Initial_Pulse ='x', reps_per_ROsequence=1000):

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
    m.params['Initial_Pulse'] =Initial_Pulse
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
    
    # ### Measurement set for Carbon 5 gate ###
        
    # Number_of_pulses = np.concatenate([np.arange(1), np.arange(32,61,2)])
    # Final_Pulse_list = ['x','-x','y','-y','no_pulse']
    # tau_list         = np.linspace(8.916e-6,8.936e-6,11)

    # GreenAOM.set_power(5e-6)
    # ins_counters.set_is_running(0)  
    # optimiz0r.optimize(dims=['x','y','z'])

    # ssrocalibration(SAMPLE_CFG)

    # for tau in tau_list:
    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

    #     for Final_Pulse in Final_Pulse_list:
    #         SimpleDecoupling_swp_N(SAMPLE+'sweep_N_' + Final_Pulse +'_tau' +str(tau) , tau =tau, Final_Pulse= Final_Pulse, Number_of_pulses =Number_of_pulses,  
    #                 reps_per_ROsequence = 2000)


    # ### Measurement set for Carbon 1 gate ###
    # Number_of_pulses = np.concatenate([np.arange(1),np.arange(28,57,2)])
    # Final_Pulse_list = ['x','-x','y','-y','no_pulse']
    # tau_list         = np.linspace(4.984e-6,5.004e-6,11)

    # GreenAOM.set_power(5e-6)
    # ins_counters.set_is_running(0)  
    # optimiz0r.optimize(dims=['x','y','z'])

    # ssrocalibration(SAMPLE_CFG)

    # for tau in tau_list:
    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

    #     for Final_Pulse in Final_Pulse_list:
    #         SimpleDecoupling_swp_N(SAMPLE+'sweep_N_' + Final_Pulse +'_tau' +str(tau) , tau =tau, Final_Pulse= Final_Pulse, Number_of_pulses =Number_of_pulses,  
    #                 reps_per_ROsequence = 2000)


    ### Measurement set for Carbon 2 gate ###        

    Number_of_pulses   = np.concatenate([np.arange(1),np.arange(16,26,2)])
    Initial_Pulse_list = ['x', 'x', 'x', 'x', 'x', '-x']
    Final_Pulse_list   = ['x','-x','y','-y','no_pulse', 'no_pulse']
    tau_list           = np.linspace(10.058e-6-10e-9,10.058e-6+10e-9,11)

    GreenAOM.set_power(5e-6)
    ins_counters.set_is_running(0)  
    optimiz0r.optimize(dims=['x','y','z'])

    ssrocalibration(SAMPLE_CFG)

    for tau in tau_list:
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(4)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        for ii, Final_Pulse in enumerate(Final_Pulse_list):
            Initial_Pulse = Initial_Pulse_list[ii]
            SimpleDecoupling_swp_N(SAMPLE+'sweep_N_' + Final_Pulse +'_tau' +str(tau) , tau =tau, 
                    Final_Pulse= Final_Pulse, Initial_Pulse =Initial_Pulse, Number_of_pulses =Number_of_pulses,  
                    reps_per_ROsequence = 2000)
    
