"""
Script for two-photon interference (TPQI) between single photons produced using sequential pulses on the same NV
"""
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.pulsar import pulselib, element, pulsar, eom_pulses
import measurement.scripts.bell.sequence as bseq
reload(bseq)

#reload all parameters and modules
execfile(qt.reload_current_setup)

#reload(funcs)
SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def sequential_TPQI(name):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = seq_TPQI(name)
    _setup_params(m, qt.current_setup)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['repetitions']  = 1000
    m.params['opt_pulse_delays']  = [200e-9]
    m.params['opt_pi_pulses']  = 50
    m.params['pts'] = len(m.params['opt_pulse_delays'])
   
    # Stuff for the time tagger
    m.params['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
    m.params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       0
    m.params['MAX_SYNC_BIN'] =       20000
    m.params['MIN_HIST_SYNC_BIN'] =  1
    m.params['MAX_HIST_SYNC_BIN'] =  15000
    m.params['TTTR_RepetitiveReadouts'] =  10 #
    m.params['TTTR_read_count'] =   1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)

    m.autoconfig()
    #m.params['sweep_pts']=m.params['pts']
    m.generate_sequence(upload=True)
    #m.run()
    #m.save()
    #m.finish()


def _setup_params(msmt, setup):
    msmt.params['setup']=setup

    if setup == 'lt4':

        import measurement.scripts.bell.params_lt4 as params_lt4
        reload(params_lt4)

        for k in params_lt4.params_lt4:
            msmt.params[k] = params_lt4.params_lt4[k]
        msmt.params['MW_BellStateOffset'] = 0.0
        bseq.pulse_defs_lt4(msmt)
    elif setup == 'lt3' :

        import measurement.scripts.bell.params_lt3 as params_lt3
        reload(params_lt3)

        for k in params_lt3.params_lt3:
            msmt.params[k] = params_lt3.params_lt3[k]
        msmt.params['MW_BellStateOffset'] = 0.0
        bseq.pulse_defs_lt3(msmt)
    elif setup == 'lt1' :

        msmt.params['setup']= 'lt4'

        # LDE Sequence in the AWGs # params taken from the previous LT1 params
        msmt.params['eom_pulse_amplitude']       = 1.9 
        msmt.params['eom_pulse_duration']        = 2e-9
        msmt.params['eom_off_duration']          = 50e-9
        msmt.params['eom_off_amplitude']         = -0.293 # calibration 2015-11-04
        msmt.params['eom_overshoot_duration1']   = 20e-9
        msmt.params['eom_overshoot1']            = -0.04
        msmt.params['eom_overshoot_duration2']   = 4e-9
        msmt.params['eom_overshoot2']            = -0.00
        msmt.params['aom_risetime']              = 17e-9
        msmt.params['aom_amplitude']             = 0.57#CR 31  

        msmt.eom_pulse = eom_pulses.OriginalEOMAOMPulse('Eom Aom Pulse', 
                        eom_channel = 'EOM_Matisse',
                        aom_channel = 'FM',
                        eom_pulse_duration      = msmt.params['eom_pulse_duration'],
                        eom_off_duration        = msmt.params['eom_off_duration'],
                        eom_off_amplitude       = msmt.params['eom_off_amplitude'],
                        eom_pulse_amplitude     = msmt.params['eom_pulse_amplitude'],
                        eom_overshoot_duration1 = msmt.params['eom_overshoot_duration1'],
                        eom_overshoot1          = msmt.params['eom_overshoot1'],
                        eom_overshoot_duration2 = msmt.params['eom_overshoot_duration2'],
                        eom_overshoot2          = msmt.params['eom_overshoot2'],
                        aom_risetime            = msmt.params['aom_risetime'],
                        aom_amplitude           = msmt.params['aom_amplitude'])

class seq_TPQI(pulsar_pq.PQPulsarMeasurement):

    mprefix = 'seq_TPQI'

    def autoconfig(self):

        pulsar_pq.PQPulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):

        '''        if self.params['setup'] == 'lt4':
            bseq.pulse_defs_lt4(self)
        elif self.params['setup'] == 'lt3':
            bseq.pulse_defs_lt3(self) 
        '''
        # Here is our pi pulse for excitation
        eom_pulse = self.eom_pulse

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
        print "Done"

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

if __name__ == '__main__':
    sequential_TPQI(SAMPLE_CFG)
    # darkesrp1(SAMPLE_CFG)
    