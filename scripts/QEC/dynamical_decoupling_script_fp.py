"""
Script to run nuclear environemnt fingerprint measurements. THT
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling(name, N, step_size, start_point, tot, mbi = True, final_pulse = '-x', optimize = True):

    m = DD.SimpleDecoupling(name)

    for kk in range(tot):
        
        ### Set experimental parameters ###
        m.params['reps_per_ROsequence'] = 500 
        m.params['Initial_Pulse'] ='x'
        m.params['Final_Pulse'] = final_pulse
        m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

        Number_of_pulses = N 
        pts = 51
        start    = 2.0e-6  + (kk+start_point)     * (pts-1)*step_size 
        end      = 2.0e-6  + (kk+1+start_point) * (pts-1)*step_size
        tau_list = np.linspace(start, end, pts)

        ### Start measurement ###

            ### Measurement name
        msmt_name = 'measurement' + str(kk)
        
            ### Optimize position
        
        if optimize:
            qt.msleep(2)
            if mod(kk,2)==0:
                AWG.clear_visa()
                stools.turn_off_all_lt2_lasers()
                qt.msleep(1)
                GreenAOM.set_power(20e-6)
                optimiz0r.optimize(dims=['x','y','z','x','y'])

            ### Define and print parameters
        funcs.prepare(m)
        m.params['pts']              = len(tau_list)
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        = tau_list*1e6
        m.params['sweep_name']       = 'tau (us)'
        
        if mbi == False:
            m.params['MBI_threshold'] = 0
            m.params['Ex_SP_amplitude'] = 0
            m.params['Ex_MBI_amplitude'] = 0
            m.params['SP_E_duration'] = 2000
            
            m.params['repump_after_MBI_A_amplitude'] = [15e-9]
            m.params['repump_after_MBI_duration'] = [50]    

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
    m.finish()

if __name__ == '__main__':
    

    #SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(8), N=8, step_size = 10e-9, start_point=0, tot = 40, final_pulse = '-x', mbi = True)

    SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16), N=16, step_size = 10e-9, start_point=0, tot = 40, final_pulse = '-x', mbi = True)
   
    SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32), N=32, step_size = 10e-9, start_point= 0, tot = 40, final_pulse = '-x')

    SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(64), N=64, step_size = 4e-9, start_point= 0, tot = 50, final_pulse = '-x')
      



