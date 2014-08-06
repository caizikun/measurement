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
    if params==None:
        SAMPLE = qt.exp_params['samples']['current']
        SAMPLE_CFG = qt.exp_params['protocols']['current']
        
        m.params.from_dict(qt.exp_params['samples'][SAMPLE])
        m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
        m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
        m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
        m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
        m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
        m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    else:
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
        msmt.params['MW_pi_duration'] = msmt.params['Square_pi_length']
        msmt.params['MW_pi2_duration'] = msmt.params['Square_pi2_length']
        msmt.params['mw_frq'] = msmt.params['ms-1_cntr_frq']-msmt.params['MW_pulse_mod_frequency'] 
        msmt.params['pulse_pi_amp'] = msmt.params['IQ_Square_pi_amp']
        msmt.params['pulse_pi2_amp'] = msmt.params['IQ_Square_pi2_amp']
        IQ_Square_pi = pulselib.MW_IQmod_pulse('Square pi-pulse',
                I_channel='MW_Imod',
                Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                length = msmt.params['MW_pi_duration'],
                amplitude = msmt.params['pulse_pi_amp'],
                frequency = msmt.params['MW_pulse_mod_frequency'],
                PM_risetime = msmt.params['MW_pulse_mod_risetime'])
        IQ_Square_pi2 = pulselib.MW_IQmod_pulse('Square pi/2-pulse',
                I_channel='MW_Imod',
                Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                length = msmt.params['MW_pi2_duration'],
                amplitude = msmt.params['pulse_pi2_amp'],
                frequency = msmt.params['MW_pulse_mod_frequency'],
                PM_risetime = msmt.params['MW_pulse_mod_risetime'])
        pulse_pi=IQ_Square_pi
        pulse_pi2=IQ_Square_pi2


    elif pulse_type == 'Hermite':
        msmt.params['mw_frq'] = msmt.params['ms-1_cntr_frq'] 
        msmt.params['pulse_pi_amp'] = msmt.params['Hermite_pi_amp']
        msmt.params['pulse_pi2_amp'] = msmt.params['Hermite_pi2_amp']

        Hermite_pi = pulselib.HermitePulse_Envelope('Hermite pi-pulse',
                MW_channel='MW_Imod',
                PM_channel='MW_pulsemod',
                amplitude = msmt.params['pulse_pi_amp'],
                length = msmt.params['MW_pi_duration'],
                PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                pi2_pulse = False)

        Hermite_pi2 = pulselib.HermitePulse_Envelope('Hermite pi/2-pulse',
                MW_channel='MW_Imod',
                PM_channel='MW_pulsemod',
                amplitude = msmt.params['pulse_pi2_amp'],
                length = msmt.params['MW_pi2_duration'],
                PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                pi2_pulse = True)
            
        pulse_pi=Hermite_pi
        pulse_pi2=Hermite_pi2
    
    else :
        print 'The pulse type you asked for is not defined.'
        
    return pulse_pi, pulse_pi2




def slow_rabi(name, debug = False):

    m = pulsar_msmt.GeneralElectronRabi(name)
    prepare(m)
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
    print 'sweep pts : ', m.params['sweep_pts']


    finish(m, upload=True, debug=debug, pulse_pi=pulse)