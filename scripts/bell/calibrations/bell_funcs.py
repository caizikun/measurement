import qt
import numpy as np


from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.scripts.ssro import ssro_calibration
reload(ssro_calibration)
import params
reload(params)



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


def pulse_defs(msmt, IQmod, pulse_type):

    if pulse_type == 'CORPSE' :
        msmt.params['pulse_pi_amp'] = msmt.params['MW_pi_amp']
        msmt.params['pulse_pi2_amp'] = msmt.params['MW_pi2_amp']
        if IQmod : 
            CORPSE_frq = 4.5e6
            msmt.params['CORPSE_rabi_frequency'] = CORPSE_frq
            msmt.params['mw_frq'] -= msmt.params['MW_pulse_mod_frequency'] 
            IQ_CORPSE_pi = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
                    I_channel = 'MW_Imod', 
                    Q_channel = 'MW_Qmod',    
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
                    amplitude = msmt.params['pulse_pi_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 180)
    
            IQ_CORPSE_pi2 = pulselib.IQ_CORPSE_pulse('CORPSE pi/2-pulse',
                    I_channel = 'MW_Imod', 
                    Q_channel = 'MW_Qmod',    
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
                    amplitude = msmt.params['pulse_pi2_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 90)
            pulse_pi = IQ_CORPSE_pi
            pulse_pi2 = IQ_CORPSE_pi2
        else :
            CORPSE_frq = 9e6
            msmt.params['CORPSE_rabi_frequency'] = CORPSE_frq

            CORPSE_pi = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
                    MW_channel = 'MW_Imod',     
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
                    amplitude = msmt.params['pulse_pi_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 180)
    
            CORPSE_pi2 = pulselib.MW_CORPSE_pulse('CORPSE pi/2-pulse',
                    MW_channel = 'MW_Imod',    
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
                    amplitude = msmt.params['pulse_pi2_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 90)
            pulse_pi=CORPSE_pi
            pulse_pi2=CORPSE_pi2
        
    elif pulse_type == 'Square':
        msmt.params['MW_pi_duration'] = msmt.params['MW_pi_duration']
        msmt.params['MW_pi2_duration'] = msmt.params['MW_pi2_duration']
        msmt.params['pulse_pi_amp'] = msmt.params['MW_pi_amp']
        msmt.params['pulse_pi2_amp'] = msmt.params['MW_pi2_amp']
        if IQmod :
            msmt.params['mw_frq'] -= msmt.params['MW_pulse_mod_frequency'] 
            IQ_Square_pi = pulselib.MW_IQmod_pulse('Square pi-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    length = msmt.params['MW_pi_duration'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])
            IQ_Square_pi2 = pulselib.MW_IQmod_pulse('Square pi/2-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    length = msmt.params['MW_pi_duration'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])
            pulse_pi=IQ_Square_pi
            pulse_pi2=IQ_Square_pi2
        else :            
            Square_pi = pulselib.MW_pulse('Square pi-pulse',
                    MW_channel='MW_Imod',
                    PM_channel='MW_pulsemod',
                    amplitude = msmt.params['pulse_pi_amp'],
                    length = msmt.params['MW_pi_duration'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])

            Square_pi2 = pulselib.MW_pulse('Square pi/2-pulse',
                    MW_channel='MW_Imod',
                    PM_channel='MW_pulsemod',
                    amplitude = msmt.params['pulse_pi2_amp'],
                    length = msmt.params['MW_pi2_duration'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])               
            pulse_pi=Square_pi
            pulse_pi2=Square_pi2


    elif pulse_type == 'Hermite':
        msmt.params['MW_pi_duration'] = msmt.params['MW_pi_duration']
        msmt.params['MW_pi2_duration'] = msmt.params['MW_pi2_duration']
        msmt.params['pulse_pi_amp'] = msmt.params['MW_pi_amp']
        msmt.params['pulse_pi2_amp'] = msmt.params['MW_pi2_amp']
        if IQmod :
            msmt.params['mw_frq'] -= msmt.params['MW_pulse_mod_frequency'] 
            IQ_Hermite_pi = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    length = msmt.params['MW_pi_duration'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])
            IQ_Hermite_pi2 = pulselib.HermitePulse_Envelope_IQ('Hermite pi/2-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    length = msmt.params['MW_pi_duration'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])
            pulse_pi=IQ_Hermite_pi
            pulse_pi2=IQ_Hermite_pi2
        else :
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
            #print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', msmt.params['MW_pi2_duration'], msmt.params['pulse_pi_amp']
            pulse_pi=Hermite_pi
            pulse_pi2=Hermite_pi2
    
    else :
        print 'The pulse type you asked for is not defined.'
        
    return pulse_pi, pulse_pi2