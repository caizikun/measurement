"""
Script to run nuclear environemnt fingerprint measurements. THT
"""
import numpy as np
import qt



"""
Script for a simple Decoupling sequence
"""
import numpy as np
import qt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

import msvcrt


SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def interrupt_script(wait = 5):
    print 'press q now to exit measurement script'
    qt.msleep(wait)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        sys.exit()

def optimize_NV(cycles = 3):
    qt.msleep(2)
    AWG.clear_visa()
    stools.turn_off_all_lasers()
    qt.msleep(1)
    GreenAOM.set_power(12e-6)
    optimiz0r.optimize(dims=['x','y','z','x','y'], cycles = cycles)

def SimpleDecoupling(name, N, step_size, start_point, tot, pts=21,mbi = True, final_pulse = '-x', optimize = True, reps_per_RO = 1500):

    m = DD.SimpleDecoupling(name)


    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])


    for kk in range(tot):

        ### Set experimental parameters ###
        # m.params['reps_per_ROsequence'] = 1000
        m.params['reps_per_ROsequence'] = reps_per_RO
        m.params['Initial_Pulse'] ='x'
        m.params['Final_Pulse'] = final_pulse
        m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt' 
        # m.params['Decoupling_sequence_scheme'] = 'single_block'

        Number_of_pulses = N 
        pts = pts
        # start    = 200e-9   + (kk+start_point)     * (pts-1)*step_size 
        # end      = 200e-9  + (kk+1+start_point) * (pts-1)*step_size
        start    = 2.50e-6 + m.params['fast_pi_duration']  + (kk+start_point)     * (pts-1)*step_size 
        end      = 2.50e-6 + m.params['fast_pi_duration']  + (kk+1+start_point) * (pts-1)*step_size
        tau_list = np.linspace(start, end, pts)

        ### Start measurement ###

            ### Measurement name
        msmt_name = 'measurement' + str(kk)
        
            ### Optimize position
        
        if optimize:
            qt.msleep(2)
            if mod(kk,5)==0:
                AWG.clear_visa()
                stools.turn_off_all_lasers()
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
            m.params['SP_E_duration'] = 20 #2000
            
            m.params['repump_after_MBI_A_amplitude'] = [15e-9]
            m.params['repump_after_MBI_duration'] = [300] # 50    

        print 'run = ' + str(kk) + ' of ' + str(tot)
        print m.params['sweep_pts']
        print tau_list

        #     ### Run experiment            
        m.autoconfig()
        print 'finished autoconfig'
        m.params['E_RO_durations']      = [m.params['SSRO_duration']]
        m.params['E_RO_amplitudes']     = [m.params['Ex_RO_amplitude']]
        m.params['send_AWG_start']      = [1]
        m.params['sequence_wait_time']  = [0]
        m.generate_sequence(upload=True, debug=False)

        print 'STARTING ITERATION %s / %s' % (kk + 1, tot )
        m.run(setup=True, autoconfig=False)
        m.save(msmt_name)

            ## Option to stop the measurement cleanly
        print 'press q now to cleanly exit measurement loop'
        qt.msleep(3)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            n = 0
            break
            
    m.finish()

if __name__ == '__main__':
    tau_start=39.5e-6
    pts=16
    step_size=12e-9
    start=(tau_start-2.64e-6)/step_size/float(pts-1)

    start=int(start)-5
    N=128
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = step_size, start_point= start, tot = 10, pts=16,final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)
    # N=64
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = step_size, start_point= start, tot = 10, pts=16,final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)
    # N=200
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = step_size, start_point= start, tot = 10, pts=16,final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)

    tau_start=66.15e-6
    pts=16
    step_size=12e-9
    start=(tau_start-2.64e-6)/step_size/float(pts-1)

    start=int(start)-5
    # N=128
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = step_size, start_point= start, tot = 10, pts=16,final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)
    # N=64
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = step_size, start_point= start, tot = 10, pts=16,final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)
    # N=200
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = step_size, start_point= start, tot = 10, pts=16,final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)

    
    
