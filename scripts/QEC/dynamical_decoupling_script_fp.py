"""
Script to run nuclear environemnt fingerprint measurements. THT
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs
import msvcrt
#import measurement.scripts.QEC.carbon_ramseys_no_init.carbon_ramsey_script_noDD as crs
#import measurement.scripts.QEC
#reload(DD) - Should do this in reload_all.py !!!

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
    GreenAOM.set_power(50e-6)
    optimiz0r.optimize(dims=['x','y','z','x','y'], cycles = cycles)

def SimpleDecoupling(name, N, step_size, start_point, tot, mbi = True, final_pulse = '-x', optimize = True, reps_per_RO = 1500):

    m = DD.SimpleDecoupling(name)

    # NOTE: ADDED from ElectronT1_Hermite on 23-04-2015
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
        pts = 21
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
            if mod(kk,2)==0:
                AWG.clear_visa()
                stools.turn_off_all_lasers()
                qt.msleep(1)
                GreenAOM.set_power(50e-6)
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

            ### Run experiment            
        m.autoconfig()
        m.params['E_RO_durations'] = [m.params['SSRO_duration']]
        m.params['E_RO_amplitudes'] = [m.params['Ex_RO_amplitude']]
        m.generate_sequence(upload=True, debug=False)
        ### m.generate_sequence(upload=False, debug=False)
        print 'STARTING ITERATION %s / %s' % (kk + 1, tot )
        m.run(setup=True, autoconfig=False)
        m.save(msmt_name)

            ## Option to stop the measurement cleanly
        print 'press x now to cleanly exit measurement loop'
        qt.msleep(3)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'x')):
            break
    m.finish()

if __name__ == '__main__':
    start=40
    N=64
    SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = 8e-9, start_point= start, tot = 50, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)
    
    N=128
    SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = 8e-9, start_point= start, tot = 50, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)

    N=32
    SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = 8e-9, start_point= start, tot = 50, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)

    #####################
    #### Last measurements Koen did
    ##############
    '''
    SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(128) + 'pulses_145', N = 128, step_size = 8e-9, start_point= 145, tot = 10, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    
    number_pulses = [32]
        SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'pulses_' + str(109), N = 32, step_size = 8e-9, start_point= 109, tot = 1, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
        for N in number_pulses:
            start_pts = np.arange(120,161,10)
            for start in start_pts:
                SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(start), N = N, step_size = 8e-9, start_point= start, tot = 10, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
                interrupt_script()
                optimize_NV(cycles = 3)
                interrupt_script(wait = 4)
    

    '''

    #SimpleDecoupling('DD' + SAMPLE + '_XY' + str(32), N=32, step_size = 50e-6, start_point=0, tot = 1, final_pulse = '-x', mbi = True)

    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16)+'no_pulses', N = 16, step_size = 24e-9, start_point=380, tot =1, final_pulse = '-x', mbi = False,optimize=False)
    # previously step_size = 400e-9
    
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16) + 'no_pulses', N = 16, step_size = 4e-9, start_point= 290, tot = 10, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    # interrupt_script()
    # optimize_NV()
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 4e-9, start_point= 290, tot = 10, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)

    # SIL2
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16) + 'no_pulses', N = 16, step_size = 16e-9, start_point= 1, tot = 11, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 1000)
    # interrupt_script()

    # optimize_NV()
    # 40-50 requires start = 467, end = 592 (125 steps)
    # interrupt_script()
    # interrupt_script()
    # optimize_NV(cycles = 3)
    # start_pts = np.arange(90,261,10)
    # for start in start_pts:
    #     SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'pulses_' + str(start), N = 32, step_size = 8e-9, start_point= start, tot = 10, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    #     interrupt_script()
    #     optimize_NV(cycles = 3)
    #     interrupt_script()

    # interrupt_script()
    # number_pulses = np.array([128])
    # for N in number_pulses:
    #     SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(N) + 'pulses_' + str(292), N = N, step_size = 4e-9, start_point= 292, tot = 8, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    #     interrupt_script()
    #     optimize_NV(cycles = 3)
    #interrupt_script()
    #optimize_NV(cycles = 10)

    ## Still to do!
    #interrupt_script(wait = 4)
    #SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(64) + 'pulses_' + str(start), N = 64, step_size = 8e-9, start_point= 43, tot = 7, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    #optimize_NV(cycles = 3)
    #interrupt_script()
    
    # start_pts = np.array([198, 209, 220])
    
    #tau_start = np.arange(2854, 5855, 100)
    #for tau_start in tau_start:
     #   crs.Carbon_Ramsey(SAMPLE, t_start = tau_start , t_end = tau_start + 96, pts = 21)
      #  interrupt_script()
       # optimize_NV(cycles = 3)

    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16) + 'pulses_' + str(start), N = 16, step_size = 16e-9, start_point= start, tot = 1, final_pulse = '-x', mbi = False,optimize=False, reps_per_RO = 2000)
    # start_pts = np.array([198])
    # for start in start_pts:
    #     interrupt_script(wait = 3)
    #     SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16) + 'pulses_' + str(start), N = 16, step_size = 16e-9, start_point= start, tot = 1, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    #     interrupt_script()
    #     optimize_NV(cycles = 8)
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16) + 'pulses_' + str(11), N = 16, step_size = 16e-9, start_point= 0, tot = 17, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16) + 'no_pulses', N = 16, step_size = 16e-9, start_point= 22, tot = 11, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    # interrupt_script()
    # optimize_NV()
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 512e-9, start_point= 5, tot = 5, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    # interrupt_script()
    # optimize_NV()
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(64) + 'no_pulses', N = 64, step_size = 512e-9, start_point= 0, tot = 5, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    # interrupt_script()
    # optimize_NV()    
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(64) + 'no_pulses', N = 64, step_size = 512e-9, start_point= 5, tot = 5, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    # interrupt_script()
    # optimize_NV()
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(128) + 'no_pulses', N = 128, step_size = 512e-9, start_point= 0, tot = 5, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    # interrupt_script()
    # optimize_NV()    
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(128) + 'no_pulses', N = 128, step_size = 512e-9, start_point= 5, tot = 5, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    # # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 60e-9, start_point= 23, tot = 5, final_pulse = '-x', mbi = False,optimize=True)
    
    """
    Complete fingerprint with increased resolution near the resonance lines
    N = 32
    """
    # 1st & 2nd order until 29
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 120e-9, start_point= 0, tot = 9, final_pulse = '-x', mbi = False,optimize=True)
    # interrupt_script()
    # # Between 2nd and 3rd order - from 27 to until 56
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 360e-9, start_point= 3, tot = 3, final_pulse = '-x', mbi = False,optimize=True)
    # interrupt_script()
    # # 3rd & 4th order from 56 until 83
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 120e-9, start_point= 18, tot = 9, final_pulse = '-x', mbi = False,optimize=True)
    # interrupt_script()
    # # between 4th & fifth order - 83 until 92
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 120e-9, start_point= 27, tot = 3, final_pulse = '-x', mbi = False,optimize=True)
    # interrupt_script()
    # # between 4th & fifth order - 92 until 98
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 60e-9, start_point= 60, tot = 4, final_pulse = '-x', mbi = False,optimize=True, reps_per_RO = 2000)
    # interrupt_script()

    # # Until 1st order
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 240e-9, start_point= 0, tot = 1, final_pulse = '-x', mbi = False,optimize=True)
    # interrupt_script()
    # # # 1st order, dt = 0.06
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 60e-9, start_point= 4, tot = 1, final_pulse = '-x', mbi = False,optimize=True)
    # interrupt_script()
    # # # Between 2nd & 3rd order
    # SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32) + 'no_pulses', N = 32, step_size = 240e-9, start_point= 0, tot = 1, final_pulse = '-x', mbi = False,optimize=True)
    # interrupt_script()

    #SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16)+'5', N=16, step_size = 250e-9, start_point=4, tot = 1, final_pulse = '-x', mbi = False,optimize=True)
    #SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16)+'6', N=16, step_size = 250e-9, start_point=5, tot = 1, final_pulse = '-x', mbi = False,optimize=True)
    #SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16)+'7', N=16, step_size = 250e-9, start_point=6, tot = 1, final_pulse = '-x', mbi = False,optimize=True)
    #SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(16)+'8', N=16, step_size = 250e-9, start_point=7, tot = 1, final_pulse = '-x', mbi = False,optimize=True)
    #SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(32), N=32, step_size = 10e-9, start_point= 0, tot = 40, final_pulse = '-x')

    #SimpleDecoupling('Fingerprint_msm1_x' + SAMPLE + '_' + str(64), N=64, step_size = 4e-9, start_point= 0, tot = 50, final_pulse = '-x')
      



