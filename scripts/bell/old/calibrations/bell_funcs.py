import qt
import numpy as np


from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.scripts.ssro import ssro_calibration
reload(ssro_calibration)
from measurement.scripts.bell import joint_params, params_lt3, params_lt1
reload(joint_params)
reload(params_lt3)
reload(params_lt1)

# test to add the analysis
from analysis.lib.m2.ssro import ssro, mbi, sequence, pqsequence
reload(ssro)
from analysis.scripts.espin import analysis_espin_calibration as aec
reload(aec)




def prepare(m, params=None):
    m.params.from_dict(params)
    m.params['send_AWG_start'] = 1
    m.params['SSRO_stop_after_first_photon'] = 0
    m.params['cycle_duration'] = 300


def finish(m, upload=True, debug=False, **kw):
    m.autoconfig()
    m.generate_sequence(upload=upload, **kw)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()


def pulse_defs(msmt, pulse_type):
       
    if pulse_type == 'Square':
        msmt.params['MW_pi_duration'] = 2e-6
        msmt.params['mw_frq'] = msmt.params['mw_frq']-msmt.params['MW_pulse_mod_frequency'] 
        msmt.params['pulse_pi_amp'] = msmt.params['MW_amp_dark_ESR']
        IQ_Square_pi = pulselib.MW_IQmod_pulse('Square pi-pulse',
                I_channel='MW_Imod',
                Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                length = msmt.params['MW_pi_duration'],
                amplitude = msmt.params['pulse_pi_amp'],
                frequency = msmt.params['MW_pulse_mod_frequency'],
                PM_risetime = msmt.params['MW_pulse_mod_risetime'])
        Dummy_IQ_Square_pi2 = pulselib.MW_IQmod_pulse('Square pi/2-pulse',
                I_channel='MW_Imod',
                Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                length = msmt.params['MW_pi_duration'],
                amplitude = 0.0,
                frequency = msmt.params['MW_pulse_mod_frequency'],
                PM_risetime = msmt.params['MW_pulse_mod_risetime'])
        pulse_pi=IQ_Square_pi
        pulse_pi2=Dummy_IQ_Square_pi2


    elif pulse_type == 'Hermite':

        Hermite_pi = pulselib.HermitePulse_Envelope('Hermite pi-pulse',
                MW_channel='MW_Imod',
                PM_channel='MW_pulsemod',
                amplitude = msmt.params['MW_pi_amp'],
                length = msmt.params['MW_pi_duration'],
                PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                pi2_pulse = False)

        Hermite_pi2 = pulselib.HermitePulse_Envelope('Hermite pi/2-pulse',
                MW_channel='MW_Imod',
                PM_channel='MW_pulsemod',
                amplitude = msmt.params['MW_pi2_amp'],
                length = msmt.params['MW_pi2_duration'],
                PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                pi2_pulse = True)
            
        pulse_pi=Hermite_pi
        pulse_pi2=Hermite_pi2
    
    else :
        print 'The pulse type you asked for is not defined.'
        
    return pulse_pi, pulse_pi2




def slow_rabi(name, params, debug = False):
    '''
    Rabi oscillations with a pulse duration set to 2 us.
    '''

    m = pulsar_msmt.GeneralElectronRabi(name)
    prepare(m, params)
    pulse, pulse_pi2_not_used = pulse_defs(m, pulse_type = 'Square')


    m.params['pulse_type'] = 'Square'
    m.params['IQmod'] = True

  
    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 2000


    m.params['Ex_SP_amplitude']=0

    #pi pulse of 2 us
    m.params['pulse_sweep_durations'] =  np.ones(pts)*2000e-9 

    m.params['pulse_sweep_amps'] = np.linspace(0.,0.05,pts)

    # for autoanalysis
    m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'

    m.params['sweep_pts'] = m.params['pulse_sweep_amps']


    finish(m, upload=True, debug=debug, pulse_pi=pulse)


def dark_esr(name, params, debug = False):
    '''
    dark ESR on the 0 <-> -1 transition with IQ mod Square pulses.
    '''

    m = pulsar_msmt.GeneralDarkESR(name)
    prepare(m, params)
    pulse_pi, pulse_pi2_not_used = pulse_defs(m,pulse_type = 'Square')

    m.params['pulse_type'] = 'Square'
    m.params['IQmod'] = True

  
    m.params['repetitions']  = 1000
    m.params['Ex_SP_amplitude']=0

    m.params['range']        = 4e6
    m.params['pts'] = 131

    m.params['MW_pi_duration'] = 2.e-6
    m.params['pulse_pi_amp'] = m.params['MW_amp_dark_ESR']

    m.params['ssbmod_frq_start'] = m.params['MW_pulse_mod_frequency'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['MW_pulse_mod_frequency'] + m.params['range']


    finish(m, upload=True, debug=False,  pulse_pi=pulse_pi)



def calibrate_Hermite_pi_pulse(name, params, debug=False):

    m = pulsar_msmt.GeneralPiCalibration(name)
    prepare(m, params)
    pulse_pi, pulse_pi2_not_used = pulse_defs(m,pulse_type = 'Hermite' )

    m.params['pulse_type'] = 'Hermite'
    m.params['IQmod'] = False
    m.params['multiplicity'] = 5
 
    m.params['Ex_SP_amplitude']=0

    pts = 21
    m.params['pts'] = pts
    m.params['repetitions'] = 2000

    # sweep params
    m.params['MW_pulse_amplitudes'] = m.params['MW_pi_amp']+  np.linspace(-0.05, 0.05, pts) #0.872982*np.ones(pts)#
    m.params['delay_reps'] = 1

    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1
    
    finish(m, debug=debug, pulse_pi=pulse_pi)



def calibrate_Hermite_pi2_pulse(name, params, debug=False):
    

    m = pulsar_msmt.GeneralPi2Calibration(name)
    
    prepare(m, params)
    pulse_pi, pulse_pi2 = pulse_defs(m,pulse_type = 'Hermite' )

    m.params['pulse_type'] = 'Hermite'
    m.params['IQmod'] = False

    pts = 11    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 3000
    m.params['Ex_SP_amplitude']=0
    m.params['wait_for_AWG_done'] = 1

    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = 2*pts 


    sweep_axis =  m.params['MW_pi2_amp']+np.linspace(-0.15,0.15,pts)
    m.params['pulse_pi2_sweep_amps'] = sweep_axis

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/2 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    
    finish(m, debug=debug, pulse_pi=pulse_pi, pulse_pi2=pulse_pi2)



def calibrate_Hermite_pi4_pulse(name, params, pi4_calib = '1',  debug=False):
    
    if pi4_calib == '1' :
        m = pulsar_msmt.GeneralPi4Calibration(name)
    elif pi4_calib == '2':
        m = pulsar_msmt.GeneralPi4Calibration_2(name)
    
    prepare(m, params)
    pulse_pi, pulse_pi2 = pulse_defs(m, pulse_type = 'Hermite')

    m.params['pulse_type'] = 'Hermite'
    m.params['IQmod'] = False
    
    pts = 11    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 2000
    m.params['Ex_SP_amplitude']=0
    m.params['wait_for_AWG_done'] = 1

    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = 2*pts 

    sweep_axis = m.params['MW_RND_amp_I'] + np.linspace(-0.15,0.15,pts)
    m.params['pulse_pi4_sweep_amps'] = sweep_axis

    m.params['pulse_pi4_sweep_durations']=np.ones(pts)*m.params['MW_RND_duration_I']
    m.params['pulse_pi4_sweep_phases'] = np.zeros(pts)
    m.params['evolution_times'] = np.ones(pts)*500e-9
    m.params['extra_wait_final_pi4'] = np.ones(pts)*0.

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/4 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    
    finish(m, debug=debug, pulse_pi=pulse_pi, pulse_pi2=pulse_pi2)
