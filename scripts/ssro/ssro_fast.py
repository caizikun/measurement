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
        pulsar_pq.PQPulsarMeasurement.autoconfig(self, **kw)

		self.params['send_AWG_start'] = 1
    	self.params['wait_for_AWG_done'] = 1

		self.params['A_SP_voltage_AWG'] = \
	                self.A_aom.power_to_voltage(
	                        self.params['A_SP_amplitude_AWG'], controller='sec')
			qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['A_SP_voltage_AWG'])

		self.params['E_SP_voltages_AWG']=np.zeros(self.params['pts']/2)
		self.params['E_RO_voltages_AWG']=np.zeros(self.params['pts']/2)
		
		for i in range(self.params['pts']/2):
			
			self.params['E_SP_voltages_AWG'][i] = \
	                self.E_aom.power_to_voltage(
	                        self.params['E_SP_amplitudes_AWG'][i], controller='sec')

	        self.params['E_RO_voltages_AWG'][i] = \
	                self.E_aom.power_to_voltage(
	                        self.params['E_RO_amplitudes_AWG'][i], controller='sec')
		

	def generate_sequence(self):

		SP_A_pulse 		= 		pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
		SP_E_pulse		=       pulse.SquarePulse(channel = 'AOM_Matisse',  amplitude = 1.0)
		RO_pulse 		= 		pulse.SquarePulse(channel = 'AOM_Matisse',  amplitude = 1.0)
		T 				=		pulse.SquarePulse(channel = 'AOM_Newfocus', length = self.params['wait_length'], amplitude = 0)
		adwin_trigger_pulse = 	pulse.SquarePulse(channel = 'adwin_sync',   length = 5e-6,   amplitude = 2)
        PQ_sync 		=		pulse.SquarePulse(channel = 'PQ_sync', length = self.params['pq_sync_length'], amplitude = 1.0)

        elements = [] 

        finished_element = element.Element('finished', pulsar = qt.pulsar)
    	finished_element.append(adwin_trigger_pulsee)
        elements.append(finished_element)

		seq = pulsar.Sequence('FastSSRO')

        for i in range(self.params['pts']/2):
            e0 =  element.Element('SSRO-ms0-{}'.format(i), pulsar = qt.pulsar)
            e0.append(T)
            e0.append(PQ_sync)  
            e0.append(pulse.cp(SP_A_pulse, length=self.params['A_SP_durations_AWG'][i]))
            e0.append(T)
            e0.append(RO_pulse, length=self.params['E_RO_durations_AWG'][i],
            		amplitude=self.params['E_RO_voltages_AWG'][i]))
            elements.append(e0)

            seq.append(name='SSRO-ms0-{}'.format(i), wfname=e0.name, trigger_wait=True)
            seq.append(name='finished-ms0-{}'.format(i), wfname=finished_element.name, trigger_wait=False)

            e1 =  element.Element('SSRO-ms1-{}'.format(i), pulsar = qt.pulsar)
            e1.append(T)
            e1.append(PQ_sync)  
            e1.append(pulse.cp(SP_E_pulse, length=self.params['E_SP_durations_AWG'][i], 
            		amplitude=self.params['E_SP_voltages_AWG'][i]))
            e1.append(T)
            e1.append(RO_pulse, length=self.params['E_RO_durations_AWG'][i],
            		amplitude=self.params['E_RO_voltages_AWG'][i]))
            elements.append(e1)

            seq.append(name='SSRO-ms1-{}'.format(i), wfname=e1.name, trigger_wait=True)
            seq.append(name='finished-ms1-{}'.format(i), wfname=finished_element.name, trigger_wait=False)
            
        qt.pulsar.program_awg(seq,*elements)


SAMPLE_CFG = qt.exp_params['protocols']['current']

def fast_ssro_calibration(name):

	m = FastSSRO('FastSSROCalibration_'+name)

	m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
	m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])

    pts = 10
    m.params['pts'] = 2*pts
    m.params['repetitions'] = 1000

    m.params['wait_length']	= 100e-9
    m.params['pq_sync_length']	= 50e-9
	m.params['E_RO_amplitudes_AWG']	=	np.linspace(0,2,pts)*m.params['Ex_RO_amplitude']
	m.params['E_RO_durations_AWG']	=	np.ones(pts)*100e-6

	m.params['E_SP_amplitudes_AWG']	=	np.ones(pts)*m.params['Ex_SP_amplitude']
	m.params['A_SP_amplitude_AWG']	=	m.params['A_SP_amplitude']
	m.params['A_SP_durations_AWG']	=	np.ones(pts)*m.params['SP_duration']*1e-6
	m.params['E_SP_durations_AWG']	=	np.ones(pts)*m.params['SP_duration']*1e-6

	m.params['sweep_name'] = 'Readout power [nW]'
    m.params['sweep_pts'] = m.params['E_RO_amplitudes_AWG']*1e9
	
	m.params['SP_duration'] = 1
	m.params['A_SP_amplitude'] = 0
	m.params['E_SP_amplitude'] = 0
	m.params['SSRO_duration'] = 1

	debug=False

    m.autoconfig()
    m.generate_sequence()
    
    if not debug:
        m.setup(mw=False, pq_calibrate=True)
        m.run(autoconfig=False, setup=False)    
        m.save()
        m.finish()

if __name__ == '__main__':
    fast_ssro_calibration('test')