# execfile('qn1_scripts/setup_qn1.py') # Fix this in QTlab

# reload all parameters and modules, import classes
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
reload(pulsar_msmt)
from measurement.scripts.espin import espin_funcs
from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
execfile(qt.reload_current_setup)
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps; reload(ps)

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

MAX_SEQ = 16; # Max # of seq indices

class dynamicJump(pulsar_msmt.PulsarMeasurement):

    mprefix = 'dynamicJump'
    adwin_process = 'singleshot'

    def generate_sequence(self, upload=True, **kw):

        #Parts and their alternatives from MW calibration

        seq = pulsar.Sequence('SSRO calibration + MW Init, RO sequence')
        seq.set_djump(True)

        e1 = element.Element('seq_1', pulsar = qt.pulsar, global_time = True)
        e2 = element.Element('seq_2', pulsar = qt.pulsar, global_time = True)
        e3 = element.Element('seq_3', pulsar = qt.pulsar, global_time = True)
        ewait = element.Element('wait', pulsar = qt.pulsar, global_time = True)

        empty = pulse.SquarePulse(channel = 'adwin_sync', length = 0.5e-6, amplitude = 0)

        pi_pulse = pulse.cp(ps.X_pulse(self), phase = 0)
        pi2_pulse = pulse.cp(ps.X_pulse(self), phase = 90)

        ewait.add(empty, name = 'wait')
        seq.append(name=ewait.name, wfname=ewait.name, trigger_wait=True)

        e1.add(empty, name = 'empty1')
        e1.add(pi_pulse, name = 'pi_pulse', refpulse = 'empty1', start = 0.5e-6, refpoint = 'end', refpoint_new = 'center')
        e1.add(empty, name = 'empty2', refpulse = 'pi_pulse')
        seq.append(name=e1.name, wfname=e1.name, trigger_wait=False, goto_target = e3.name, repetitions = 1e4)
        seq.add_djump_address(0, e1.name)

        e2.add(empty, name = 'empty1')
        e2.add(pi2_pulse, name = 'pi2_pulse', refpulse = 'empty1', start = 0.5e-6, refpoint = 'end', refpoint_new = 'center')
        e2.add(empty, name = 'empty2', refpulse = 'pi2_pulse')
        seq.append(name=e2.name, wfname=e2.name, trigger_wait=False, goto_target = e1.name)
        seq.add_djump_address(1, e2.name)

        e3.add(empty, name = 'empty')
        seq.append(name=e3.name, wfname=e3.name, trigger_wait=False, goto_target=None)
        seq.add_djump_address(2, e3.name)

        qt.pulsar.program_awg(seq, *[ewait, e1, e2, e3]) 

def run_dynamicJump(name, debug = True):

    m = dynamicJump(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.generate_sequence(upload=False)

    qt.pulsar.AWG.start()

if __name__ == '__main__':

    run_dynamicJump(SAMPLE_CFG + 'dynamic_jump')

