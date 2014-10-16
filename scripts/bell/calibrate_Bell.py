import sweep_Bell
reload(sweep_Bell)
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
# reload all parameters and modules, import classes
from measurement.scripts.espin import espin_funcs
reload(espin_funcs)

def calibrate_pi_pulse(name, multiplicity=1, debug=False):
    m = pulsar_msmt.GeneralPiCalibration(name)
    sweep_Bell._setup_params(m, setup = qt.current_setup)

    m.params['multiplicity'] = multiplicity
    m.params['pulse_type'] = 'Hermite Bell'
    pts = 11
 
    m.params['Ex_SP_amplitude']=0
    m.params['SP_duration'] = 100

    m.params['pts'] = pts
    m.params['repetitions'] = 5000

    # sweep params
    m.params['MW_pulse_amplitudes'] =  m.params['MW_pi_amp'] + np.linspace(-0.1, 0.1, pts)  
    #m.params['MW_pulse_amplitudes'] = m.params['pulse_pi_amp']+  np.linspace(-0.05, 0.05, pts) #0.872982*np.ones(pts)#
    m.params['delay_reps'] = 1

    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1
    
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)

def calibrate_pi2_pulse(name, debug=False):
    m = pulsar_msmt.GeneralPi2Calibration(name)
    sweep_Bell._setup_params(m, setup = qt.current_setup)

    pts = 11
    m.params['pulse_type'] = 'Hermite Bell'    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 3000

    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = 2*pts 

    m.params['Ex_SP_amplitude']=0
    m.params['SP_duration'] = 50
    m.params['wait_for_AWG_done'] = 1

    sweep_axis =  m.params['MW_pi2_amp'] + np.linspace(-0.1, 0.1, pts)  
    m.params['pulse_pi2_sweep_amps'] = sweep_axis

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/2 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi, pulse_pi2=m.MW_pi2)

def calibrate_pi4_pulse(name,debug=False):
    m = pulsar_msmt.GeneralPi4Calibration(name)
    sweep_Bell._setup_params(m, setup = qt.current_setup)
    
    pts = 11 
    m.params['pulse_type'] = 'Hermite Bell'   
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 5000
    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = 2*pts 
    m.params['Ex_SP_amplitude']=0
    m.params['SP_duration'] = 50
    m.params['wait_for_AWG_done'] = 1

    sweep_axis = m.params['MW_pi4_amp'] + np.linspace(-0.1, 0.1, pts) 
    m.params['pulse_pi4_sweep_amps'] = sweep_axis

    m.params['pulse_pi4_sweep_durations']=np.ones(pts)*m.params['MW_pi4_duration']
    m.params['pulse_pi4_sweep_phases'] = np.zeros(pts)
    m.params['evolution_times'] = np.ones(pts)*500e-9
    m.params['extra_wait_final_pi4'] = np.ones(pts)*0.

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/4 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi, pulse_pi2=m.MW_pi2)

if __name__ == '__main__':
    stage = 3.2
    SAMPLE_CFG = qt.exp_params['protocols']['current']
    if   stage == 0 :
        print 'First measure the resonance frequency with a continuous ESR'
        execfile(r'D:/measuring/measurement/scripts/espin/esr.py')
        print 'set msmt_params: f_msm1_cntr'
    elif stage == 1 :
        print "First calibrate lasers, and go onto NV center!"
        print 'If not already done so: choose the cryo_half ~8 deg \n \
              from minimum CR counts on Ey (Ex axis)'
        print '\n Execute SSRO calibration:' 
        execfile(r'D:/measuring/measurement/scripts/ssro/ssro_calibration.py')
        print 'set msmt_params: integrated SSRO_duration'
        print '(choose thresholds according to CR histogram, repeat SSRO)'
    elif stage == 2 :
        print 'Execute FastSSRO calibration'
        execfile(r'D:/measuring/measurement/scripts/ssro/ssro_fast.py')
        print 'check RO fidelities (set A_SP_amplitude if bad SP ms0)'
        print 'set Bell params AWG_RO_power' 
    elif stage == 3.1:
        print 'Execute DarkESR calibration'
        execfile(r'D:/measuring/measurement/scripts/espin/darkesr.py')
        print 'set msmt_params: f_msm1_cntr'
    elif stage == 3.2:
        calibrate_pi_pulse(SAMPLE_CFG+'_Bell_Pi', multiplicity=1)
        print 'set msmt_params Hermite_pi_amp'
    elif stage == 3.3:
        calibrate_pi_pulse(SAMPLE_CFG, multiplicity=5)
        print 'set msmt_params Hermite_pi_amp'
    elif stage == 3.4:
        calibrate_pi2_pulse(SAMPLE_CFG)
        print 'set msmt_params Hermite_pi2_amp'
    elif stage == 3.5:
        calibrate_pi4_pulse(SAMPLE_CFG)
        print 'set msmt_params Hermite_pi4_amp'
    elif stage == 4.1: #echo sweep tests DD
        sweep_Bell.echo_sweep(SAMPLE_CFG)
        print 'set params_ltx echo_offset (should be 0 ns)'
    elif stage == 4.2: #rnd_echo_ro tests fast ssro, DD and RND generation
        sweep_Bell.rnd_echo_ro(SAMPLE_CFG)
        print 'check only, if bad, check Fast SSRO params, all MW, RND and RO delays'
    elif stage == 5: #rnd_echo_ro tests fast ssro, DD and RND generation
        print 'First optimize on ZPL, and do rejection!'
        sweep_Bell.tail_sweep(SAMPLE_CFG)
        print 'set params_lt3/3 aom_amplitude'
    elif stage == 6: 
        print 'Spin-Photon correlations (if necc.)'
        print 'in bell_lt4 script!'
        print 'and do not forget to progam the PLU'
    elif stage == 7:
        execfile('check_awg_triggering.py')
        print 'check only, repeat untill succesful'