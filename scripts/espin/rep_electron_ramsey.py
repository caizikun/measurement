# one CR check followed by N ramseys.
# sequence: CR - |SP - AWG_ramsey - SSRO - SP_repump - delay_time - |^N
import qt
import numpy as np
#reload all parameters and modules
execfile(qt.reload_current_setup)

from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt



from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)

name = 'rep_ramseys_SIL1_Hans_with_CORPSE_3hf_delay=7000us_'
SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def repelectronramsey(name):
    m = pulsar_msmt.RepElectronRamseys(name)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params['SP_duration']=10
    m.params['A_SP_amplitude'] = 50e-9
    m.params['SSRO_duration']=10

    pts = 1

    m.params['pi2_amps'] = np.ones(pts)*1
    m.params['pi2_phases1'] = np.ones(pts) *1
    m.params['pi2_phases2'] = np.ones(pts) *1
    m.params['pi2_lengths'] = np.ones(pts) *1

    m.params['MW_pulse_frequency']=100e6
    m.params['wait_after_pulse_duration']=2
    m.params['wait_after_RO_pulse_duration']=2

    pts = 1
    m.params['pts'] = pts
    m.params['repetitions'] = 5000

    m.params['evolution_times'] = np.linspace(0,1*(pts-1)*1/2.165e6,pts)

    # MW pulses
    m.params['detuning']  = 0.0e6
    m.params['CORPSE_pi2_mod_frq'] = m.params['MW_modulation_frequency'] + m.params['detuning']-50e3
    m.params['CORPSE_pi2_amps'] = np.ones(pts)*m.params['CORPSE_pi2_amp']
    m.params['CORPSE_pi2_phases1'] = np.ones(pts) * 0
    m.params['CORPSE_pi2_phases2'] = np.ones(pts)*90#360 * m.params['evolution_times'] * 2e6

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9

    funcs.finish(m,upload=True)
    print m.adwin_var('completed_reps')

def repelectronramseyCORPSE(name,delay_time=1,repump_E=0,repump_A=0,nr_of_hyperfine_periods=3,upload=False):
    m = pulsar_msmt.RepElectronRamseysCORPSE(name)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])



    m.params['repump_E'] = repump_E
    m.params['repump_A'] = repump_A
    m.params['wait_time_between_msmnts']=  delay_time

    pts = 1
    m.params['pts'] = pts
    m.params['repetitions'] = 50000

    m.params['evolution_times'] = np.ones(1)*nr_of_hyperfine_periods/m.params['N_HF_frq']

    # MW pulses
    m.params['CORPSE_pi2_mod_frq'] = m.params['MW_modulation_frequency']
    m.params['CORPSE_pi2_amps'] = np.ones(pts)*1# np.ones(pts)*m.params['CORPSE_pi2_amp']
    m.params['CORPSE_pi2_phases1'] = np.ones(pts) * 0
    m.params['CORPSE_pi2_phases2'] = np.ones(pts)*90#360 * m.params['evolution_times'] * 2e6

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9

    m.autoconfig()
    return_e=m.generate_sequence()
    funcs.finish(m,upload=upload)
    print m.adwin_var('completed_reps')
    return return_e
def loop_rep_ramsey_CORPSE(delay_time=1,repump_E=0,repump_A=0,nr_of_hyperfine_periods=3,reps=2):
    name='SIL1_'+str(nr_of_hyperfine_periods)+'_hf'
    n=name+"_"+str(delay_time)+"us"+"A"+str(repump_A)+"E"+str(repump_E)+"nr"
    repelectronramseyCORPSE(n+"0",delay_time=delay_time,repump_E=repump_E,repump_A=repump_A,nr_of_hyperfine_periods=nr_of_hyperfine_periods,upload=True)

    for i in np.arange(reps-1):
        n=name+"_"+str(delay_time)+"us"+"A"+str(repump_A)+"E"+str(repump_E)+"nr"+str(i+1)
        repelectronramseyCORPSE(n,delay_time=delay_time,repump_E=repump_E,repump_A=repump_A,nr_of_hyperfine_periods=nr_of_hyperfine_periods,upload=False)
if __name__ == '__main__':
    delay_times=[1,5000,100,2000,250,1000,500,10,10000]
    hyperfine=[3,1,5]
    for hf in hyperfine:
        for dt in delay_times:
            GreenAOM.set_power(5e-6)
            optimiz0r.optimize(dims=['x','y','z','x','y','z'])
            GreenAOM.set_power(0e-6)
            loop_rep_ramsey_CORPSE(delay_time=dt,repump_E=0,repump_A=1,nr_of_hyperfine_periods=hf,reps=10)
            loop_rep_ramsey_CORPSE(delay_time=dt,repump_E=1,repump_A=0,nr_of_hyperfine_periods=hf,reps=10)
            loop_rep_ramsey_CORPSE(delay_time=dt,repump_E=0,repump_A=0,nr_of_hyperfine_periods=hf,reps=10)


