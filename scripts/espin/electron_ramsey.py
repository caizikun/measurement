import qt
import numpy as np
execfile(qt.reload_current_setup)
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)



name = 'HANS_sil1'
SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

def electronramseyCORPSE(name):
    m = pulsar_msmt.ElectronRamseyCORPSE(name)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    #m.params['evolution_times'] = np.linspace(0,(pts-1)*1/m.params['N_HF_frq'],pts)
    m.params['evolution_times'] = np.linspace(0,5000e-9,pts)

    # MW pulses
    m.params['detuning']  = 0.0e6
    m.params['CORPSE_pi2_mod_frq'] = m.params['MW_modulation_frequency']
    m.params['CORPSE_pi2_amps'] = np.ones(pts)*m.params['CORPSE_pi2_amp']
    m.params['CORPSE_pi2_phases1'] = np.ones(pts) * 0
    m.params['CORPSE_pi2_phases2'] = np.ones(pts) * 0#360 * m.params['evolution_times'] * 2e6

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9

    funcs.finish(m)

def electronramsey(name):
    m = pulsar_msmt.ElectronRamsey(name)
    #funcs.prepare(m)
    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    m.params['Ex_SP_amplitude']=0
    m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6
    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1
    pts = 51
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    #m.params['wait_for_AWG_done']=1
    m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)

    # MW pulses
    m.params['detuning']  = 0.0e6

    m.params['mw_frq'] = m.params['ms-1_cntr_frq'] -43e6      #for ms=-1
    #m.params['mw_frq'] = 3.45e9      #for ms=+1

    m.params['MW_pulse_frequency'] = m.params['ms-1_cntr_frq'] - m.params['mw_frq']
    m.params['pi2_amps'] = np.ones(pts)*1
    m.params['pi2_phases1'] = np.ones(pts) * 0
    m.params['pi2_phases2'] = np.ones(pts) * 0#360 * m.params['evolution_times'] * m.params['detuning']
    m.params['pi2_lengths'] = np.ones(pts) * 16e-9
    #m.params['pi2_lengths'] = np.linspace(15,30,pts)*1e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9

    funcs.finish(m)

if __name__ == '__main__':
    electronramseyCORPSE(name)

