import sweep_Bell
reload(sweep_Bell)
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
# reload all parameters and modules, import classes
from measurement.scripts.espin import espin_funcs
from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
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
    m.params['repetitions'] = 1000 if multiplicity == 1 else 5000

    # sweep params
    rng = 0.2 if multiplicity == 1 else 0.05
    # rng = 0.05
    m.params['MW_pulse_amplitudes'] =  m.params['MW_pi_amp'] + np.linspace(-rng, rng, pts)  #XXXXX -0.05, 0.05 
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

if __name__ == '__main__':
    stage = 3.3
    SAMPLE_CFG = qt.exp_params['protocols']['current']

    debug = False

    if  stage == 0 :
        execfile(r'D:/measuring/measurement/scripts/espin/esr.py')
    elif stage == 1:
        execfile(r'D:/measuring/measurement/scripts/espin/darkesr.py')
    elif stage == 2:
        calibrate_pi_pulse(SAMPLE_CFG+'_Bell_Pi_15_rep', multiplicity=15,debug = False)
    elif stage == 4:
        calibrate_pi2_pulse_2(SAMPLE_CFG+'_Bell_Pi2_2_15_rep_MWon', multiplicity = 15,debug = debug)
    elif stage == 5: #echo sweep tests DD
        sweep_Bell.echo_sweep(SAMPLE_CFG)
    elif stage == 6: # sweep tail
        sweep_Bell.tail_sweep(SAMPLE_CFG)
    elif stage == 7:
        print 'to be implemented'