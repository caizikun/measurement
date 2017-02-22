"""
Script for e-spin ramsey, can be used to measure electron T2. Uses pulsar sequencer
"""
import qt
import numpy as np

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

def electronT2_NoTriggers(name, debug = False):
    m = pulsar_msmt.ElectronT2NoTriggers(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite'

    m.params['Ex_SP_amplitude']=0
    m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6  # commenting this out gives an erro
    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1

    pts = 21
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    #m.params['wait_for_AWG_done']=1
    #m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)
    m.params['evolution_times'] = np.linspace(0e-9,1e-3,pts)

    # MW pulses
    m.params['detuning']  = 0 #-1e6 #0.5e6
    X_pi2 = ps.Xpi2_pulse(m)
    X_pi = ps.X_pulse(m)
    m.params['pulse_sweep_pi2_phases1'] = np.ones(pts) * m.params['X_phase']    # First pi/2 = +X
    # m.params['pulse_sweep_pi2_phases2'] = np.ones(pts) * (m.params['X_phase']+180 )   # Second pi/2 = mX
    m.params['pulse_sweep_pi2_phases2'] = np.ones(pts) * m.params['X_phase']
    m.params['pulse_sweep_pi_phases'] = np.ones(pts) * m.params['X_phase']


    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = (m.params['evolution_times'] + 2*m.params['Hermite_pi2_length'] + m.params['Hermite_pi_length'])* 1e9

    # for the self-triggering through the delay line
    # m.params['self_trigger_delay'] = 500e-9 # 0.5 us
    # m.params['self_trigger_duration'] = 100e-9

    # Start measurement
    m.autoconfig()
    m.generate_sequence(upload=True, pulse_pi2 = X_pi2, pulse_pi = X_pi)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()

if __name__ == '__main__':
    
    # electronramsey(name)
    # electronramseyHermiteSelfTriggered(name, debug = False)
    electronT2_NoTriggers(name, debug=False)

