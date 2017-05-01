# reload all parameters and modules, import classes
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
reload(pulsar_msmt)
from measurement.scripts.espin import espin_funcs
from measurement.lib.pulsar import pulse
execfile(qt.reload_current_setup)
import pulse_select as ps; reload(ps)

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']



class dynamicJump(pulsar_msmt.PulsarMeasurement):

    mprefix = 'dynamicJump'
    adwin_process = 'singleshot'

    def generate_sequence(self, upload=True, **kw):
        pulsar_msmt.PulsarMeasurement.generate_sequence(self)

        #pulses
        Trig = pulse.SquarePulse(channel = 'adwin_sync', length = 10e-6, amplitude = 2)
        T = pulse.SquarePulse(channel='MW_Imod', length = 2e-6, amplitude = 0)
        X = pulse.cp(ps.pi_pulse_MW2(m), phase = 0) 

        #Parts and their alternatives from MW calibration
        elements = []
        seq = pulsar.Sequence('SSRO calibration + MW Init, RO) sequence')
        e = element.Element('pi_pulse', pulsar=qt.pulsar)

        if self.params['multiplicity'] != 0:
            # SPIN RO ELEMENT
            for j in range(int(self.params['multiplicity'])):
                e.append(T)
                e.append(X)
                e.append(Trig)
        
            #seq = pulsar.Sequence('{} pi calibration'.format(self.params['pulse_type']))
        else:
            e.append(T)
            e.append(Trig)
        elements.append(e)
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        qt.pulsar.program_awg(seq,*elements) 
       


def ssro_MWInit(name):

    m = dynamicJump(name)
    
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)

if __name__ == '__main__':

    ssro_MWInit(SAMPLE_CFG + 'ssro_MWInit_ms' + str(s))

