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
from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

class FastSSRO(pulsar_pq.PQPulsarMeasurement):

    def autoconfig(self, **kw):
        self.params['send_AWG_start'] = 1
        self.params['wait_for_AWG_done'] = 1
        pulsar_pq.PQPulsarMeasurement.autoconfig(self, **kw)
        self.params['A_SP_voltage_AWG'] = \
                    self.A_aom.power_to_voltage(
                            self.params['A_SP_amplitude_AWG'], controller='sec')
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['A_SP_voltage_AWG'])

        self.params['E_SP_voltages_AWG']=np.zeros(self.params['pts']/2)
        self.params['E_RO_voltages_AWG']=np.zeros(self.params['pts']/2)
        
        for i in range(self.params['pts']/2):
            
            self.params['E_SP_voltages_AWG'][i] = \
                    self.AWG_RO_AOM.power_to_voltage(
                            self.params['E_SP_amplitudes_AWG'][i], controller='sec')

            self.params['E_RO_voltages_AWG'][i] = \
                    self.AWG_RO_AOM.power_to_voltage(
                            self.params['E_RO_amplitudes_AWG'][i], controller='sec')
        if qt.pulsar.channels['EOM_AOM_Matisse']['type'] == 'marker' and self.params['pts']>1:
            print 'FastSSRO: WARNING, AOM Matisse is on marker channel, cannot sweep its power!'
            print 'Setting max RO power'
            qt.pulsar.set_channel_opt('EOM_AOM_Matisse', 'high', self.params['E_RO_voltages_AWG'][-1])

    def generate_sequence(self, upload=True):

        SP_A_pulse         =         pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
        SP_E_pulse        =       pulse.SquarePulse(channel = 'EOM_AOM_Matisse',  amplitude = 1.0)
        RO_pulse         =         pulse.SquarePulse(channel = 'EOM_AOM_Matisse',  amplitude = 1.0)
        T                 =        pulse.SquarePulse(channel = 'AOM_Newfocus', length = self.params['wait_length'], amplitude = 0)
        adwin_trigger_pulse =     pulse.SquarePulse(channel = 'adwin_sync',   length = 5e-6,   amplitude = 2)
        PQ_sync         =        pulse.SquarePulse(channel = 'sync', length = self.params['pq_sync_length'], amplitude = 1.0)

        elements = [] 

        finished_element = element.Element('finished', pulsar = qt.pulsar)
        finished_element.append(adwin_trigger_pulse)
        elements.append(finished_element)

        seq = pulsar.Sequence('FastSSRO')

        for i in range(self.params['pts']/2):
            e0 =  element.Element('SSRO-ms0-{}'.format(i), pulsar = qt.pulsar)
            e0.append(pulse.cp(T,length=3e-6))
            e0.append(PQ_sync)
            e0.append(T)  
            e0.append(pulse.cp(SP_A_pulse, length=self.params['A_SP_durations_AWG'][i]))
            e0.append(T)
            e0.append(pulse.cp(RO_pulse, length=self.params['E_RO_durations_AWG'][i],
                    amplitude=self.params['E_RO_voltages_AWG'][i]))
            e0.append(T)
            elements.append(e0)

            seq.append(name='SSRO-ms0-{}'.format(i), wfname=e0.name, trigger_wait=True)
            seq.append(name='finished-ms0-{}'.format(i), wfname=finished_element.name, trigger_wait=False)

            e1 =  element.Element('SSRO-ms1-{}'.format(i), pulsar = qt.pulsar)
            e0.append(pulse.cp(T,length=3e-6))
            e1.append(PQ_sync)
            e1.append(T)  
            e1.append(pulse.cp(SP_E_pulse, length=self.params['E_SP_durations_AWG'][i], 
                    amplitude=self.params['E_SP_voltages_AWG'][i]))
            e1.append(T)
            e1.append(pulse.cp(RO_pulse, length=self.params['E_RO_durations_AWG'][i],
                    amplitude=self.params['E_RO_voltages_AWG'][i]))
            e1.append(T)
            elements.append(e1)

            seq.append(name='SSRO-ms1-{}'.format(i), wfname=e1.name, trigger_wait=True)
            seq.append(name='finished-ms1-{}'.format(i), wfname=finished_element.name, trigger_wait=False)
            
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)


SAMPLE_CFG = qt.exp_params['protocols']['current']

def fast_ssro_calibration(name):

    m = FastSSRO('FastSSROCalib_'+name)
    m.AWG_RO_AOM = qt.instruments['PulseAOM']

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])

    pts = 11
    m.params['pts'] = 2*pts
    m.params['repetitions'] = 2000

    m.params['wait_length']    = 1000e-9
    m.params['pq_sync_length']    = 150e-9
    m.params['E_RO_amplitudes_AWG']    =    np.linspace(0,3,pts)*m.params['Ex_RO_amplitude']
    m.params['E_RO_durations_AWG']    =    np.ones(pts)*20e-6

    m.params['E_SP_amplitudes_AWG']    =    np.ones(pts)*m.params['Ex_SP_amplitude']
    m.params['A_SP_amplitude_AWG']    =    m.params['A_SP_amplitude']
    m.params['A_SP_durations_AWG']    =    np.ones(pts)*15*1e-6
    m.params['E_SP_durations_AWG']    =    np.ones(pts)*200*1e-6

    m.params['sweep_name'] = 'Readout power [nW]'
    m.params['sweep_pts'] = m.params['E_RO_amplitudes_AWG']*1e9
    
    m.params['SP_duration'] = 1
    m.params['A_SP_amplitude'] = 0
    m.params['E_SP_amplitude'] = 0
    m.params['SSRO_duration'] = 1

    debug=False
    measure_bs=False
    upload=True#'old_method'

    m.autoconfig()

    m.generate_sequence(upload=upload)
    

    m.setup(mw=False, debug=debug)
    m.params['MAX_SYNC_BIN'] = (np.max(m.params['E_SP_durations_AWG']) + np.max(m.params['E_RO_durations_AWG']))/(2**m.params['BINSIZE']*m.PQ_ins.get_BaseResolutionPS()*1e-12)
    print m.params['MAX_SYNC_BIN']

    if measure_bs:
        bs_helper = qt.instruments['bs_helper']
        bs_helper.set_script_path(r'D:/measuring/measurement/scripts/bs_scripts/remote_ssro_fast.py')
        bs_helper.set_is_running(True)
        bs_helper.execute_script()
    
    m.run(autoconfig=False, setup=False, debug=debug)    
    m.save()
    
    if measure_bs:
        bs_helper.set_is_running(False)
        m.params['bs_data_path'] = bs_helper.get_data_path()
    
    m.finish()


if __name__ == '__main__':
    fast_ssro_calibration('Pippin_SIL3_Ex_10deg')