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

def finish(m, upload=True, debug=False, **kw):
    m.autoconfig()
    m.generate_sequence(upload=upload, **kw)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()
