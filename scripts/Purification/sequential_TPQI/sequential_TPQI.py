"""
Script for two-photon interference (TPQI) between single photons produced using sequential pulses on the same NV
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

#reload(funcs)
SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def sequential_TPQI(name):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = seq_TPQI(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['setup'] = 'lt3'
    m.params['repetitions']  = 500
    m.params['opt_pulse_delays']  = 1
   	m.params['opt_pi_pulses']  = 10
     
   
    # Stuff for the time tagger
	m.params['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
	m.params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
	m.params['MIN_SYNC_BIN'] =       0
	m.params['MAX_SYNC_BIN'] =       20000
	m.params['MIN_HIST_SYNC_BIN'] =  1
	m.params['MAX_HIST_SYNC_BIN'] =  15000
	m.params['TTTR_RepetitiveReadouts'] =  10 #
	m.params['TTTR_read_count'] = 	1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)


    list_swp_pts =np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    m.params['sweep_pts'] = (np.array(list_swp_pts) +  m.params['mw_frq'])*1e-9
    m.autoconfig()
    #m.params['sweep_pts']=m.params['pts']
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()



from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.pulsar import pulselib, element, pulsar, eom_pulses
import measurement.scripts.bell.sequence as bseq

class seq_TPQI(pulsar_pq.PQPulsarMeasurement):

   mprefix = 'seq_TPQI'

    def autoconfig(self):

        pulsar_pq.PQPulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        getattr(bseq,'pulse_defs_'+self.params['setup']+'(self)')

        # Here is our pi pulse for excitation
		eom_pulse = msmt.eom_pulse

        # A handy sync pulse for the time tagger 
    	T_sync = pulse.SquarePulse(channel='sync',
        length = 50e-9, amplitude = 0)

        # Everyone likes delays
        T = pulse.SquarePulse(channel='MW_Imod', name='delay')
        T.amplitude = 0.

        # make the elements - one for each delay
        elements = []

        for i, delay in enumerate(self.params['opt_pulse_delays']):

            e = element.Element('seq_TPQI_delay-%d' % i, pulsar=qt.pulsar)
            e.append(T_sync)
            # Add in a bunch of optical pi pulses, separated by our precious delay
		    for i in range(self.params['opt_pi_pulses']):
		        name = 'opt pi {}'.format(i+1)
		        T.length = delay
		        e.append(eom_pulse)
		       	e.append(T)

		    elements.append(e)
		    
        # create a sequence from the pulses
        seq = pulsar.Sequence('seq_TPQI sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

     # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)
