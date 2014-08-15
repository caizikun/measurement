# Calibration steps for the Bell test experiment
from measurement.scripts.bell.calibrations import bell_funcs as bf
reload(bf)




def run_calibrations(debug = False):

    do_ssro = False
    do_dark_ESR = True

    if do_ssro :
        e_sp = params_lt3.params_lt3['Ex_SP_amplitude']
        params_lt3.params_lt3['Ex_SP_amplitude'] = qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO']['Ex_SP_amplitude'] 
        print '\nFor the SSRO calibration, the Ex SP amplitude is set to {} nW.\n'.format(params_lt3.params_lt3['Ex_SP_amplitude']*1e9)
        
    #SSRO Calibration
        bf.ssro_calibration.ssrocalibration('SAMPLE_CFG', **params_lt3.params_lt3)
        
        params_lt3.params_lt3['Ex_SP_amplitude'] = e_sp
        print '\nThe Ex SP amplitude is reset to {} nW.\n'.format(params_lt3.params_lt3['Ex_SP_amplitude']*1e9)

    #SSRO Calibration analysis
        bf.ssro.ssrocalib(plot_photon_ms0=False)


    if do_dark_ESR :
        #bf.slow_rabi('SAMPLE'+'_'+'rabi', debug=debug)

    #Rabi analysis
        bf.aec.analyse_Rabi(guess_frq=1/0.03)

if __name__ == '__main__':
    print '\n bouh'

    run_calibrations(debug = False)


