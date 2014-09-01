# Calibration steps for the Bell test experiment
from measurement.scripts.bell.calibrations import bell_funcs as bf
reload(bf)




def run_calibrations(name, setup, do_ssro, do_dark_ESR, do_MW_pulse_calib, do_MW_pi4_calib, debug = False):

    if setup == 'lt3':
        params = params_lt3.params_lt3
    elif setup == 'lt1':
        params = params_lt1.params_lt1

    str_slow_rabi_result = ''
    str_dark_esr_result  = ''
    str_pi_result        = ''
    str_pi2_result       = ''

    if do_ssro :
        e_sp = params['Ex_SP_amplitude']
        params['Ex_SP_amplitude'] = qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO']['Ex_SP_amplitude'] 
        print '\nFor the SSRO calibration, the Ex SP amplitude is set to {} nW.\n'.format(params['Ex_SP_amplitude']*1e9)
        
        ### SSRO Calibration ###
        bf.ssro_calibration.ssrocalibration('SAMPLE_CFG', **params)
        
        params['Ex_SP_amplitude'] = e_sp
        print '\nThe Ex SP amplitude is reset to {} nW.\n'.format(params['Ex_SP_amplitude']*1e9)

        ### SSRO Calibration analysis ###
        bf.ssro.ssrocalib(plot_photon_ms0=False)


    if do_dark_ESR :

        ### Rabi analysis ###
        bf.slow_rabi(name, params, debug=debug)

        ### Rabi analysis ###
        rabi_fit_result = bf.aec.analyse_Rabi(guess_frq=1/params['MW_amp_dark_ESR'])

        str_slow_rabi_result = '\n Before the MW amplitude for a 2us pi pulse was {:.3f} V.\n\
        Now it is {:.3f} V. \n \
        If different, change it in msmt_params.py, kw : \'IQ_Square_pi_amp\' after the calibration.\
        \n'.format(params['MW_amp_dark_ESR'], 1/2./rabi_fit_result['params'][0])

        print  '\n\n', str_slow_rabi_result,  '\n\n'

        params['MW_amp_dark_ESR'] = 1/2./rabi_fit_result['params'][0]

        bf.dark_esr(name, params)

        ### dark ESR analysis ###
        dark_esr_fit_result = bf.aec.analyse_dark_esr(guess_x0=params['mw_frq'])


        str_dark_esr_result = '\n Before the center resonant frequency was {:.3f} MHz.\n\
        Now it is {:.3f} MHz. \n \
        If different, change it in msmt_params.py, kw : \'mw_freq\' after the calibration.\
        \n'.format(params['mw_frq']*1e-6, dark_esr_fit_result['params'][3]*1e3)

        print  '\n\n', str_dark_esr_result,  '\n\n'

        params['mw_frq'] =  dark_esr_fit_result['params'][3]*1e9


    if do_MW_pulse_calib : 

        ### Pi pulse calibration ###
        bf.calibrate_Hermite_pi_pulse(name,params, debug = debug)

        ### Pi pulse calibration analysis ###
        pi_fit_result = bf.aec.analyse_pi_pulse(x0_guess = params['MW_pi_amp'])

        print 'The contrast is {:.2f} % for multiplicity = 5.'.format((pi_fit_result['params'][0])*100)

        str_pi_result = '\nPrevioulsy, the MW pi pulse amplitude was {:.3f} V.\n\
        Now it is {:.3f} V. \n \
        If different, change it in msmt_params.py, kw : \'Hermite_pi_amp\' after the calibration.\
        \n'.format(params['MW_pi_amp'], pi_fit_result['params'][2])

        print '\n\n',  str_pi_result ,  '\n\n'

        ### Pi/2 pulse calibration ###
        bf.calibrate_Hermite_pi2_pulse(name,params, debug = debug)

        ### Pi/2 pulse calibration analysis ###
        pi2_fit_result = bf.aec.analyse_pi2_pulse()

        str_pi2_result = '\n Previoulsy, the MW pi/2 pulse amplitude was {:.3f} V.\n\
        Now it is {:.3f} V. \n \
        If different, change it in msmt_params.py, kw : \'Hermite_pi2_amp\' after the calibration.\
        \n'.format(params['MW_pi2_amp'], pi2_fit_result['params'][1])

        print  '\n\n', str_pi2_result ,  '\n\n'


    if do_MW_pi4_calib : 

        ### Pi/4 pulse calibration 1 ###
        bf.calibrate_Hermite_pi4_pulse(name,params, pi4_calib = '1', debug = debug)

        ### Pi/4 pulse calibration analysis for the 1st calibration ###
        pi4_fit_result_1 = bf.aec.analyse_pi4_pulse(pi4_calib = '1')

        str_pi4_result_1 = '\n Previoulsy, the MW pi/4 pulse amplitude was {:.3f} V.\n\
        Now the 1st calibration gives {:.3f} V. \n \
        If different, change it in msmt_params.py, kw : \'Hermite_pi4_amp\' after the calibration.\
        \n'.format(params['MW_RND_amp_I'], pi4_fit_result_1['params'][1])

        print  '\n\n', str_pi4_result_1 ,  '\n\n'


        ### Pi/4 pulse calibration 2 ###
        bf.calibrate_Hermite_pi4_pulse(name,params, pi4_calib = '2', debug = debug)

        ### Pi/4 pulse calibration analysis for the 2nd calibration ###
        pi4_fit_result_2 = bf.aec.analyse_pi4_pulse(pi4_calib = '2')

        str_pi4_result_2 = '\n Previoulsy, the MW pi/4 pulse amplitude was {:.3f} V.\n\
        Now the 2nd calibration gives {:.3f} V. \n \
        If different, change it in msmt_params.py, kw : \'Hermite_pi4_amp\' after the calibration.\
        \n'.format(params['MW_RND_amp_I'], pi4_fit_result_2['params'][1])

        print  '\n\n', str_pi4_result_2 ,  '\n\n'


    print '\nCalibration summary :'
    print str_slow_rabi_result, str_dark_esr_result, str_pi_result, str_pi2_result, str_pi4_result_1, str_pi4_result_2





if __name__ == '__main__':

    name = 'Sam'
    setup = 'lt3'

    do_ssro = True
    do_dark_ESR = True
    do_MW_pulse_calib = True
    do_MW_pi4_calib = True

    debug = False

    run_calibrations(name, setup, do_ssro, do_dark_ESR, do_MW_pulse_calib, do_MW_pi4_calib, debug = debug)


