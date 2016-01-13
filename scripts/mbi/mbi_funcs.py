import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import ssro, pulsar_mbi_espin,pulsar_mbi_nitrogenspin

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def prepare(m, sil_name=SAMPLE):
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    # print SA LE_CFG
    # m.params.from_dict(qt.exp_params['samples'][SAMPLE_CFG])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO+C13'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    #m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])

def finish(m, upload=True, debug=False):
    m.autoconfig()
    print 'finished autoconfig'
    m.params['E_RO_durations']      = [m.params['SSRO_duration']]
    m.params['E_RO_amplitudes']     = [m.params['Ex_RO_amplitude']]
    m.params['send_AWG_start']      = [1]
    m.params['sequence_wait_time']  = [0]
    print upload
    m.generate_sequence(upload=upload, debug=debug)


    if not debug:

        m.run(setup=True, autoconfig=False)
        m.save()
        m.finish()

