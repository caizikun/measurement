"""
Script to run nuclear environemnt fingerprint measurements. NK & SK
"""
import numpy as np
import qt


"""
Script for overnight measurements: N = 8, 16, 32, 64
"""


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
EL_TRANS = qt.exp_params['samples'][SAMPLE]['electron_transition']

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def optimize_NV(cycles = 1):
    qt.msleep(2)
    # AWG.clear_visa()
    stools.turn_off_all_lasers()
    qt.msleep(1)
    GreenAOM.set_power(12e-6)
    optimiz0r.optimize(dims=['x','y','z','x','y'], cycles = cycles)
    stools.turn_off_all_lasers()

def SimpleDecoupling(name, N, step_size,tot, start_point = 2, mbi = False, final_pulse = '-x', optimize = True, reps_per_RO = 1500):

    m = DD.SimpleDecoupling(name)


    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])


    # if optimize:
    #     qt.msleep(2)
    #     optimize_NV()

    for kk in range(tot):

        ## Option to stop the measurement cleanly
        print 'press q now to cleanly exit measurement loop'
        breakst = show_stopper()
        if breakst: break

        ### Set experimental parameters ###
        # m.params['reps_per_ROsequence'] = 1000
        m.params['reps_per_ROsequence'] = reps_per_RO
        m.params['Initial_Pulse'] ='x'
        m.params['Final_Pulse'] = final_pulse
        m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt' 
        # m.params['Decoupling_sequence_scheme'] = 'single_block'

        Number_of_pulses = N 
        pts = 51
        if N == 128:
            pts = 21
        start    = 3.5e-6  + (kk+start_point)     * (pts-1)*step_size 
        end      = 3.5e-6  + (kk+1+start_point) * (pts-1)*step_size
        tau_list = np.linspace(start, end, pts)

        ### Start measurement ###

            ### Measurement name
        msmt_name = 'measurement' + str(kk)
        
            ### Optimize position
        if optimize:
            qt.msleep(2)
            if mod(kk,5)==0:
                optimize_NV()

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
        # print tau_list
        print m.params['MBI_threshold']

        #     ### Run experiment            
        m.autoconfig()
        print 'finished autoconfig'
        m.params['E_RO_durations']      = [m.params['SSRO_duration']]
        m.params['E_RO_amplitudes']     = [m.params['Ex_RO_amplitude']]
        m.params['send_AWG_start']      = [1]
        m.params['sequence_wait_time']  = [0]
        m.generate_sequence(upload=True)


        debug = False

        if not debug:
            print 'STARTING ITERATION %s / %s' % (kk + 1, tot )
            m.run(setup=True, autoconfig=False)
            m.save(msmt_name)


                
    m.finish()

breakst = False
if __name__ == '__main__':
    print 'Looping over N'

    # print 'press q now to cleanly exit measurement loop'
    # breakst = show_stopper()
    # if breakst: break

    # every single_tau_block is pts*step_size = 200 ns. 100 blocks is thus from 3.5 to 23.5
    single_tau_blocks = 50
    pulse_list = [16,32,64]#[8,16,32,64]
    # optimal combinations of step_size and N. tot*pts*step_size should be constant
    for N in pulse_list:


        print 'N = ' + str(N)

        print 'press q now to cleanly exit measurement loop'
        breakst = show_stopper()
        if breakst: break

        
        SimpleDecoupling('Hermite_Fingerprint_ms'+ EL_TRANS[-2:] + '_' + SAMPLE + '_' + str(N),
            N = N, step_size = 4e-9, start_point= 0, tot = single_tau_blocks, 
            final_pulse = '-x', optimize=True, reps_per_RO = 500)


    n = 0

    # for start_point in [0,45,90,135]:
        
    #     for N in [64,128]:
    #         if N in [128, 64]:
    #             step_size = 4e-9
    #         else:
    #             step_size = 10e-9

    #         if N == 64 and start_point ==0:
    #             pulses = ['x']
    #         if N == 64 and start_point ==45:
    #             pulses = []
    #         else:
    #             pulses = ['-x','x']

    #         for final_pulse in pulses:


    #             print 'press q now to cleanly exit measurement loop'
    #             qt.msleep(3)
    #             if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #                 n = 0

        

    #             if n == 1:
    #                 SimpleDecoupling('Hermite_Fingerprint_msm1_' + SAMPLE + '_' + str(N) + final_pulse+str(start_point),
    #                         N = N, step_size = step_size, start_point= start_point, tot = 50, final_pulse = final_pulse, optimize=True, reps_per_RO = 500)

