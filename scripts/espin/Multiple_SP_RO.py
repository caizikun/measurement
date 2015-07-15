"""
Script for repetitive SP and RO using the pulsar sequencer
"""
import numpy as np
import qt
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt

#reload(pulsar_msmt)
SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Multiple_SP_RO(name,upload=True):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.Multiple_SP_SSRO(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols']['Gretel_sil10']['Magnetometry'])
    stools.turn_off_all_lasers()
    
    m.params['wait_for_AWG_done']=1
    m.params['pts']=21
    m.params['repetitions']  = 1000
    m.params['sweep_pts'] = np.linspace(1,500,m.params['pts']) 
    
    m.autoconfig()
    m.generate_sequence(upload=upload)
    if upload==False:
        AWG.set_runmode('SEQ')
        qt.msleep(10)
        AWG.start()
        qt.msleep(20)   
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    Multiple_SP_RO(SAMPLE_CFG,upload=True)
