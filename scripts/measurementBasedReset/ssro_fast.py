"""
Script for AWG ssro calibration.
"""

import numpy as np
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
import msvcrt
from measurement.lib.measurement2.adwin_ssro.pulsar_msmt import PulsarMeasurement
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

class FastSSRO(PulsarMeasurement):

    def autoconfig(self, **kw):
        self.params['AWG_controlled_readout'] = 1
        self.params['send_AWG_start'] = 0
        self.params['wait_for_AWG_done'] = 0
        self.params['sequence_wait_time'] = 0

        PulsarMeasurement.autoconfig(self, **kw)
        
        self.params['E_RO_voltages_AWG']=np.zeros(np.size(self.params['E_RO_amplitudes_AWG']))
        
        if np.size(self.params['E_RO_amplitudes_AWG']) > 1:
            for i in range(self.params['pts']):
                
                self.params['E_RO_voltages_AWG'][i] = \
                        MatisseAOM.power_to_voltage(
                                self.params['E_RO_amplitudes_AWG'][i], controller='sec')
            if qt.pulsar.channels['AOM_Matisse']['type'] == 'marker' and self.params['pts']>1:
                print 'FastSSRO: WARNING, AOM Matisse is on marker channel, cannot sweep its power!'
                print 'Setting max RO power'
                qt.pulsar.set_channel_opt('AOM_Matisse', 'high', self.params['E_RO_voltages_AWG'][-1])
        else:
            self.params['E_RO_voltages_AWG'] = \
                        MatisseAOM.power_to_voltage(
                                self.params['E_RO_amplitudes_AWG'], controller='sec')
            qt.pulsar.set_channel_opt('AOM_Matisse', 'high', self.params['E_RO_voltages_AWG'])


    def generate_sequence(self, upload=True):

        RO_pulse            =        pulse.SquarePulse(channel = 'AOM_Matisse',  amplitude = 1.0)
        # T                   =        pulse.SquarePulse(channel = 'AOM_Newfocus', length = self.params['wait_length'], amplitude = 0)
        adwin_trigger_pulse =        pulse.SquarePulse(channel = 'adwin_sync',   length = 3e-6,   amplitude = 2)
        # MW_pi_pulse  =       pulselib.HermitePulse_Envelope('Hermite pi-pulse',
        #                                 MW_channel='MW_Imod',
        #                                 PM_channel='MW_pulsemod',
        #                                 second_MW_channel='MW_Qmod', 
        #                                 amplitude = self.params['Hermite_pi_amp'],
        #                                 length = self.params['Hermite_pi_length'],
        #                                 PM_risetime = self.params['MW_pulse_mod_risetime'],
        #                                 pi2_pulse = False)


        elements = []
        seq = pulsar.Sequence('FastSSRO')

        for i in range(self.params['pts']):

            e0 =  element.Element('FastSSRO-{}'.format(i), pulsar = qt.pulsar)
            e0.append(pulse.cp(RO_pulse, length=1e-9, amplitude =0)) # Need to start with a little delay to ensure channel starts low.
            if np.size(self.params['E_RO_voltages_AWG']) > 1:
                e0.append(pulse.cp(RO_pulse, length=self.params['E_RO_durations_AWG'][i],\
                    amplitude = self.params['E_RO_voltages_AWG'][i]))
            else:
                e0.append(pulse.cp(RO_pulse, length=self.params['E_RO_durations_AWG'][i]))
            
            e0.append(adwin_trigger_pulse)
            elements.append(e0)

            seq.append(name='SSRO-ms0-{}'.format(i), wfname=e0.name, trigger_wait=True)
            

        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)


SAMPLE_CFG = qt.exp_params['protocols']['current']
SAMPLE_NAME =  qt.exp_params['samples']['current']


def fast_ssro_calibration(name):

    m = FastSSRO('FastSSROCalib_'+name)

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['samples'][SAMPLE_NAME])

    pts = 20
    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    m.params['E_RO_amplitudes_AWG'] =   70e-9
    m.params['E_RO_durations_AWG']  =    np.linspace(0,1.,pts)*5e-6

    m.params['sweep_name'] = 'Readout duration [mus]'
    m.params['sweep_pts'] = m.params['E_RO_durations_AWG']*1e6
    
    debug=False
    upload=True#'old_method'

    m.params['SP_duration'] = m.params['SP_duration_ms0']
    m.params['Ex_SP_amplitude'] = 0.
    
    m.autoconfig()
    m.generate_sequence(upload=upload)
    m.setup(debug=debug)

    if not(debug):
        if m.run(autoconfig=False, setup=False):
            m.save(name='ms0')

            # ms = 1 calibration
            m.params['SP_duration'] = m.params['SP_duration_ms1']
            m.params['A_SP_amplitude'] = 0.
            m.params['Ex_SP_amplitude'] = m.params['Ex_SP_calib_amplitude']


            ssro.IntegratedSSRO.autoconfig(m)
            ssro.IntegratedSSRO.setup(m)
            m.run(autoconfig=False, setup=False)
            ssro.IntegratedSSRO.save(m,name='ms1')
  
    m.finish()


if __name__ == '__main__':
    fast_ssro_calibration(SAMPLE_CFG)