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

def electronramseyCORPSE(name):
    m = pulsar_msmt.ElectronRamseyCORPSE(name)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['Hans_sil4']['Magnetometry'])

    pts = 101
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    print 1/m.params['N_HF_frq']

    
    #m.params['evolution_times'] = np.linspace(0,(pts-1)*1/m.params['N_HF_frq'],pts)
    m.params['evolution_times'] = np.linspace(0,10000e-9,pts)
    #m.params['evolution_times'] = 5*np.ones (pts)*1e-9

    print 'corspe frq', m.params['CORPSE_frq']
    # MW pulses
    m.params['detuning']  = 0e3
    m.params['CORPSE_pi2_mod_frq'] = m.params['MW_modulation_frequency']-m.params['detuning']
    m.params['CORPSE_pi2_amps'] = np.ones(pts)*m.params['CORPSE_pi2_amp']
    m.params['CORPSE_pi2_phases1'] = np.ones(pts) * 0
    m.params['CORPSE_pi2_phases2'] = 0*np.ones(pts) * (90.+15) ##np.linspace(0,360,pts) #np.ones(pts) * 0#

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9
    #m.params['sweep_name'] = 'phase second pi2'
    #m.params['sweep_pts'] = m.params['CORPSE_pi2_phases2']

    funcs.finish(m)

def electronramsey(name):
    m = pulsar_msmt.ElectronRamsey(name)
    #funcs.prepare(m)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params['Ex_SP_amplitude']=0
    m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6
    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1
    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    #m.params['wait_for_AWG_done']=1
    #m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)
    m.params['evolution_times'] = np.linspace(0,1000e-9,pts)

    # MW pulses
    m.params['detuning']  = 1.0e6

    # m.params['mw_frq'] = m.params['f_msm1_cntr'] #for ms=-1
    #m.params['mw_frq'] = 3.45e9      #for ms=+1

    # m.params['MW_pulse_frequency'] = m.params['msm1_cntr_frq'] - m.params['mw_frq']
    m.params['MW_pulse_frequency'] = m.params['mw_frq']
    m.params['pi2_amps'] = np.ones(pts)*0.017
    m.params['pi2_phases1'] = np.ones(pts) * 0
    m.params['pi2_phases2'] = np.ones(pts) * 360 * m.params['evolution_times'] * m.params['detuning']
    m.params['pi2_lengths'] = np.ones(pts) * 1250e-9
    #m.params['pi2_lengths'] = np.linspace(15,30,pts)*1e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9

    funcs.finish(m)

def electronramseyHermite(name, debug = False):
    m = pulsar_msmt.GeneralElectronRamsey(name)
    print m.adwin
    # funcs.prepare(m)
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

    pts = 61
    m.params['pts'] = pts
    m.params['repetitions'] = 1500
    #m.params['wait_for_AWG_done']=1
    #m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)
    m.params['evolution_times'] = np.linspace(0,7000e-9,pts)

    # MW pulses
    m.params['detuning']  = 0.5e6
    X_pi2 = ps.Xpi2_pulse(m)
    m.params['pulse_sweep_pi2_phases1'] = np.ones(pts) * m.params['X_phase']    # First pi/2 = +X
    m.params['pulse_sweep_pi2_phases2'] = np.ones(pts) * (m.params['X_phase'] )   # Second pi/2 = mX
    m.params['pulse_sweep_pi2_phases2'] = np.ones(pts) * (m.params['X_phase']  + 180 + 360 * (m.params['evolution_times'] + m.params['Hermite_pi2_length']) * m.params['detuning'])


    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = (m.params['evolution_times'] + m.params['Hermite_pi2_length'] )* 1e9

    # Start measurement
    m.autoconfig()
    m.generate_sequence(upload=True, pulse_pi2 = X_pi2)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()

if __name__ == '__main__':
    
    # electronramsey(name)
    electronramseyHermite(name, debug = False)

