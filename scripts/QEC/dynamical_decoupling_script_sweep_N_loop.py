"""
Script for a loop of N sweeps for different tau
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

def SimpleDecoupling(name,tau,N_step,N_init,N_finish,pts_per_run=11):
    m = DD.SimpleDecoupling(name)

    total_pts = (N_finish-N_init)/N_step+1
    print 'Running measurement for tau is: '+str(tau*1e6)

    for kk in range(total_pts/pts_per_run):
        
        ### Set experimental parameters ###
        m.params['reps_per_ROsequence'] = 1250 
        m.params['Initial_Pulse'] ='x'
        m.params['Final_Pulse'] ='-x'
        m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

        pts = pts_per_run
        N_start    = (kk+N_init)     * (pts-1)*N_step 
        N_end      = (kk+1+N_init) * (pts-1)*N_step
        N_list     = np.linspace(N_start, N_end, pts)

        ### Start measurement ###

            ### Measurement name
        msmt_name = 'measurement'+ str(kk)
        
            ### Optimize position
        qt.msleep(2)
        if mod(kk,2)==0:
            AWG.clear_visa()
            stools.turn_off_all_lt2_lasers()
            qt.msleep(1)
            GreenAOM.set_power(5e-6)
            optimiz0r.optimize(dims=['x','y','z','x','y'])

            ### Define and print parameters
        funcs.prepare(m)
        m.params['pts']              = len(N_list)
        m.params['Number_of_pulses'] = N_list
        m.params['tau_list']         = tau*np.ones(m.params['pts']).astype(int)
        m.params['sweep_pts']        = N_list
        m.params['sweep_name']       = 'N'

        print 'run = ' + str(kk) + ' of ' + str(total_pts/pts_per_run) + ' for this tau'
        print m.params['sweep_pts']
        

            ### Run experiment            
        m.autoconfig()
        m.params['E_RO_durations'] = [m.params['SSRO_duration']]
        m.params['E_RO_amplitudes'] = [m.params['Ex_RO_amplitude']]
        m.generate_sequence(upload=True, debug=False)
        m.run(setup=True, autoconfig=False)
        m.save(msmt_name)

            ### Option to stop the measurement cleanly
        print 'press q now to cleanly exit this measurement loop'
        print 'Note that there is a loop over tau, you have to press q another time'
        qt.msleep(5)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
    
    m.finish()


if __name__ == '__main__':

    tau_list = [6.522,18.102,31.138,54.294,6.620,9.560,8.088,12.500,11.010,8.640,8.828,9.558,12.038,12.086,18.576,6.456,
                15.066,6.726,9.712,12.706,7.068,10.214,13.352,14.918,21.192,21.211,24.328,24.366,13.528,9.824,12.848,
                17.378,9.854,11.370,12.888,15.920,22.570,24.132,30.354,11.701,14.820,24.172,27.294,30.412,16.500]
    N_steps_list = [4,4,4,4,8,8,8,8,8,4,4,4,4,4,4,8,8,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,8,8,8,8,16,16,16,16,16,16,16,16,16]
    
    for jj in range(len(tau_list)):

        SimpleDecoupling(SAMPLE +' _Sweep_N_' +str(int(tau_list[jj]*1e3)) , tau_list[jj]*1e-6, N_steps_list[jj], 0, 320, pts_per_run=11)
        
        print 'press q now to cleanly exit the tau sweep measurement loop'

        qt.msleep(5)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

