import sweep_Bell
reload(sweep_Bell)
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
# reload all parameters and modules, import classes
from measurement.scripts.espin import espin_funcs
reload(espin_funcs)
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

def calibrate_pi_pulse(name, multiplicity=1, debug=False):
    m = pulsar_msmt.GeneralPiCalibration(name)
    sweep_Bell._setup_params(m, setup = qt.current_setup)

    m.params['multiplicity'] = multiplicity
    m.params['pulse_type'] = 'Hermite Bell'
    pts = 11
 
    m.params['Ex_SP_amplitude']=0
    m.params['SP_duration'] = 100

    m.params['pts'] = pts
    m.params['repetitions'] = 1000 if multiplicity == 1 else 500

    # sweep params
    rng = 0.2 if multiplicity == 1 else 0.05
    # rng = 0.05
    m.params['MW_pulse_amplitudes'] = m.params['MW_pi_amp'] + np.linspace(-rng, rng, pts)  #XXXXX -0.05, 0.05 
    #m.params['MW_pulse_amplitudes'] =  np.linspace(0.52, 0.59, pts) #0.872982*np.ones(pts)#
    m.params['delay_reps'] = 15  # spacing between pi pulses in us

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
    m.params['repetitions'] = 5000

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

    
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi, pulse_pi2=m.MW_pi2)#, upload='old_method')


def calibrate_pi2_pulse_2(name, multiplicity = 1, debug=False):
    m = pulsar_msmt.GeneralPi2Calibration_2(name)
    sweep_Bell._setup_params(m, setup = qt.current_setup)

    pts = 11
    m.params['multiplicity'] = multiplicity
    m.params['pulse_type'] = 'Hermite Bell'    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 2000 if multiplicity == 1 else 5000

    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = pts 

    m.params['Ex_SP_amplitude']=0
    m.params['SP_duration'] = 50
    m.params['wait_for_AWG_done'] = 1

    rng = 0.1 if multiplicity == 1 else 0.07
    sweep_axis =  m.params['MW_pi2_amp'] + np.linspace(-rng, rng, pts)
    m.params['pulse_pi2_sweep_amps'] = sweep_axis
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/2 amp (V)'
    m.params['sweep_pts'] = sweep_axis
    m.params['wait_for_AWG_done'] = 1

    
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi, pulse_pi2=m.MW_pi2)



def calibrate_pi2_pulse_3(name, multiplicity = 1, debug=False):
    m = pulsar_msmt.GeneralPi2Calibration_3(name)
    sweep_Bell._setup_params(m, setup = qt.current_setup)

    pts = 11
    m.params['multiplicity'] = multiplicity
    m.params['pulse_type'] = 'Hermite Bell'    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 2000 if multiplicity == 1 else 5000

    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = pts 

    m.params['Ex_SP_amplitude']=0
    m.params['SP_duration'] = 50
    m.params['wait_for_AWG_done'] = 1

    rng = 0.1 if multiplicity == 1 else 0.09
    sweep_axis =  m.params['MW_pi2_amp'] + np.linspace(-rng, rng, pts)
    m.params['pulse_pi2_sweep_amps'] = sweep_axis
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/2 amp (V)'
    m.params['sweep_pts'] = sweep_axis
    m.params['wait_for_AWG_done'] = 1

    
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi, pulse_pi2=m.MW_pi2)



def calibrate_Npi4_pulse(name,debug=False):
    m = pulsar_msmt.GeneralNPi4Calibration(name)
    sweep_Bell._setup_params(m, setup = qt.current_setup)
    
    pts = 11 
    m.params['pulse_type'] = 'Hermite Bell'   
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 5000
    # we do actually two msmts for every sweep point, that's why the awg gets only half of the pts;
    m.params['pts'] = 2*pts 
    m.params['Ex_SP_amplitude']=0
    m.params['SP_duration'] = 50
    m.params['wait_for_AWG_done'] = 1

    sweep_axis = m.params['MW_Npi4_amp'] + np.linspace(-0.1, 0.1, pts) 
    m.params['pulse_Npi4_sweep_amps'] = sweep_axis
    
    m.params['pulse_Npi4_sweep_durations']=np.ones(pts)*m.params['MW_Npi4_duration']
    m.params['pulse_Npi4_sweep_phases'] = np.zeros(pts)
    m.params['evolution_times'] = np.ones(pts)*500e-9
    m.params['extra_wait_final_Npi4'] = np.ones(pts)*0.

    # for the autoanalysis
    m.params['sweep_name'] = 'MW Npi/4 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi, pulse_pi2=m.MW_pi2)

def check_pi4_pulse_poles(name, debug=False):
    m = pulsar_msmt.GeneralNPi4Calibration_3(name)
    sweep_Bell._setup_params(m, setup = qt.current_setup)

    m.params['pulse_type'] = 'Hermite Bell'
    pts = 11
 
    m.params['Ex_SP_amplitude']=0
    m.params['SP_duration'] = 100

    m.params['pts'] = pts
    m.params['repetitions'] = 5000

    # sweep params
    sweep_axis = m.params['MW_Npi4_amp'] + np.linspace(-0.05, 0.05, pts) 
    m.params['pulse_Npi4_sweep_amps'] = sweep_axis

    m.params['pulse_Npi4_sweep_durations']=np.ones(pts)*m.params['MW_Npi4_duration']
    m.params['pulse_Npi4_sweep_phases'] = np.zeros(pts)
    m.params['evolution_times'] = np.ones(pts)*500e-9
    m.params['extra_wait_final_Npi4'] = np.ones(pts)*0.

    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
    m.params['sweep_pts'] = sweep_axis
    m.params['wait_for_AWG_done'] = 1
    
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi, pulse_pi4=m.MW_pi2)


if __name__ == '__main__':
    stage = 3.42
    print 'Stage:', stage
    SAMPLE_CFG = qt.exp_params['protocols']['current']

    debug = False

    if  stage == 0 :
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
        calibrate_pi_pulse(SAMPLE_CFG+'_Bell_Pi_15_rep', multiplicity=7,debug = False)
        print 'set msmt_params Hermite_pi_amp'
    elif stage == 3.4:
        calibrate_pi2_pulse(SAMPLE_CFG+'_Bell_Pi2',debug = False)
        print 'set msmt_params Hermite_pi2_amp'
    elif stage == 3.42: #new pi/2 pulse calibration
        calibrate_pi2_pulse_2(SAMPLE_CFG+'_Bell_Pi2_2_15_rep_MWon', multiplicity =15,debug = debug)
        # calibrate_pi2_pulse_3(SAMPLE_CFG+'_Bell_Pi2_3_5_rep', multiplicity = 1)
        print 'set msmt_params Hermite_pi2_amp'
    elif stage == 3.5:
        calibrate_Npi4_pulse(SAMPLE_CFG)
        print 'set msmt_params Hermite_Npi4_amp'
    elif stage == 3.52:
        check_pi4_pulse_poles(SAMPLE_CFG+'_Bell_Pi4_check', debug=debug)
        print 'set msmt_params Hermite_Npi4_amp'
    elif stage == 4.1: #echo sweep tests DD
        sweep_Bell.echo_sweep(SAMPLE_CFG)
        print 'set params_ltx echo_offset'
    elif stage == 4.2: #rnd_echo_ro tests fast ssro, DD and RND generation
        sweep_Bell.rnd_echo_ro(SAMPLE_CFG,debug = debug)
        print 'check only, if bad, check Fast SSRO params, all MW, RND and RO delays'
    elif stage == 5: # sweep tail
        print 'First optimize on ZPL, and do rejection!'
        sweep_Bell.tail_sweep(SAMPLE_CFG)
        print 'set params_lt3/4 aom_amplitude'
    elif stage == 6: 
        print 'Spin-Photon correlations (if necc.)'
        print 'in bell_lt4 script!'
        print 'and do not forget to progam the PLU'
    elif stage == 7:
        execfile('check_awg_triggering.py')
        print 'check only, repeat untill succesful'