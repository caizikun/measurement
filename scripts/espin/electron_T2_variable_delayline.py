"""
Script for e-spin Hahn echo. Uses pulsar sequencer
"""
import qt
import numpy as np
import msvcrt

#reload all parameters and modules


from measurement.scripts.espin import espin_funcs as funcs
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
reload(funcs)

# from darkesr, use of some of these is hidden. Not relevant
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps

execfile(qt.reload_current_setup)
#reload(funcs)

#name = 'HANS_sil4'
SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
name=SAMPLE_CFG

def upload_dummy_selftrigger_sequence(name, period=200e-6, on_time=2e-6, debug=True):
    m = pulsar_msmt.DummySelftriggerSequence(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    pts = 11

    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    m.params['delay_voltages'] = np.linspace(2.5,2.7,pts)
    m.params['delay_voltage_DAC_channel'] = 14
    m.params['do_delay_voltage_control'] = 1

    # Start measurement
    m.autoconfig()
    m.generate_sequence(upload=True, period=period, on_time=on_time)

    if not debug:
        m.run(autoconfig=False)
        m.finish()

if __name__ == '__main__':
    upload_dummy_selftrigger_sequence("SHOULDNT_EXIST", period=200e-6, on_time=2e-6, debug=True)