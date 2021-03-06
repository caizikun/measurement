"""
Script for a simple Decoupling sequence
Based on Electron T1 script
"""
import numpy as np
import qt
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling(name, N, step_size, start_point, tot,start_tau = 0.52e-6):

    m = DD.SimpleDecoupling(name)

    for kk in range(tot):
        
        ### Set experimental parameters ###
        m.params['reps_per_ROsequence'] = 500 
        m.params['Initial_Pulse'] ='x'
        m.params['Final_Pulse'] ='-x'
        m.params['Decoupling_sequence_scheme'] = 'single_block'

        Number_of_pulses = N 
        pts = 41
        start    = start_tau + (kk+start_point)     * (pts-1)*step_size 
        end      = start_tau + (kk+1+start_point)   * (pts-1)*step_size
        tau_list = np.linspace(start, end, pts)

        ### Start measurement ###

            ### Measurement name
        msmt_name = 'measurement' + str(kk)
        
            ### Optimize position
        '''qt.msleep(2)
        if mod(kk,2)==0:
            AWG.clear_visa()
            stools.turn_off_all_lt2_lasers()
            qt.msleep(1)
            GreenAOM.set_power(5e-6)
            optimiz0r.optimize(dims=['x','y','z','x','y'])'''

            ### Define and print parameters
        funcs.prepare(m)
        m.params['pts']              = len(tau_list)
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        = tau_list*1e6
        m.params['sweep_name']       = 'tau (us)'

        print 'run = ' + str(kk) + ' of ' + str(tot)
        print m.params['sweep_pts']
        print tau_list

            ### Run experiment            
        m.autoconfig()
        m.params['E_RO_durations'] = [m.params['SSRO_duration']]
        m.params['E_RO_amplitudes'] = [m.params['Ex_RO_amplitude']]
        m.generate_sequence(upload=True, debug=False)
        m.run(setup=True, autoconfig=False)
        m.save(msmt_name)

            ### Option to stop the measurement cleanly
        print 'press q now to cleanly exit measurement loop'
        qt.msleep(5)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
    
        ### Close the fileexperiment in ot out the loop, that is the question, what happens if this is just in?
    m.finish()

if __name__ == '__main__':
    ## Extend the N=64 measurement to longer tau
    #SimpleDecoupling('Fingerprint_' + SAMPLE + str(64), N=64, step_size = 4e-9,  start_point = 150, tot = 100)
    #SimpleDecoupling('Fingerprint_' + SAMPLE + str(32), N=32, step_size = 10e-9, start_point = 90, tot = 90)
    #SimpleDecoupling('Fingerprint_' + SAMPLE + str(16), N=16, step_size = 10e-9, tot = 140)
    #SimpleDecoupling('Fingerprint_' + SAMPLE + str(8), N=8, step_size = 10e-9, start_point=0,tot = 250)

    #SimpleDecoupling('Fingerprint_Short_Tau_' + SAMPLE +'_N_' + str(32), N=32, step_size = 10e-9, start_point = 0, tot = 1)
    # SimpleDecoupling('Fingerprint_short_tau_' + SAMPLE + str(16), N=16, step_size = 4e-9,  start_point = 0, tot = 5,start_tau = 2.1e-6)
    # SimpleDecoupling('Fingerprint_short_tau_' + SAMPLE + str(32), N=32, step_size = 4e-9,  start_point = 0, tot = 5,start_tau = 2.1e-6)
    SimpleDecoupling('Fingerprint_short_tau_' + SAMPLE + str(64), N=64, step_size = 4e-9,  start_point = 0, tot = 5,start_tau = 2.1e-6)
    

