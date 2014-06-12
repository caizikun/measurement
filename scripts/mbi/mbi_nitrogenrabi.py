import qt
import numpy as np

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_nitrogenspin

execfile(qt.reload_current_setup)
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_nitrogenspin
reload(pulsar_mbi_nitrogenspin)


SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
print SAMPLE_CFG
print SAMPLE



def NRabi(name):
    m = pulsar_mbi_nitrogenspin.NitrogenRabi(name)
    funcs.prepare(m)

    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
    print 'MBI threshold =' + str(m.params['MBI_threshold'])
    print 'Ex_MBI_amplitude =' + str(m.params['Ex_MBI_amplitude'])
    print 'SSRO_duration =' + str(m.params['SSRO_duration'])

    pts = 11
    m.params['wait_for_AWG_done'] = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500
    B=(m.params['zero_field_splitting']-m.params['ms-1_cntr_frq'])/m.params['g_factor']
    f_ctr=m.params['Q_splitting'] - m.params['N_HF_frq'] - m.params['g_factor_N14']*B
    print f_ctr
    f_ctr=7.13429e6+100e3
    #f_ctr=2.667e6

    NR_of_pulses=1
    RF_pulse_length = 50e-6
    RF_pulse_amp = 1

    m.params['RF_pulse_multiplicities'] = np.ones(pts).astype(int)*NR_of_pulses
    m.params['RF_pulse_delays'] = np.ones(pts) * 50e-9
    # MW pulses
    m.params['RF_pulse_durations']  = np.linspace(1e-6,50e-6,pts)
    m.params['RF_pulse_amps']   = np.ones(pts) * RF_pulse_amp
    m.params['RF_pulse_frqs']   = np.ones(pts) * f_ctr

    m.params['sweep_name'] = 'RF pulse len (us)'
    m.params['sweep_pts']  = m.params['RF_pulse_durations'] * 1e6
    # for the autoanalysis

    funcs.finish(m, debug=False)

def NMR(name):
    m = pulsar_mbi_nitrogenspin.NitrogenRabi(name)
    funcs.prepare(m)

    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
    print 'MBI threshold =' + str(m.params['MBI_threshold'])
    print 'Ex_MBI_amplitude =' + str(m.params['Ex_MBI_amplitude'])
    print 'SSRO_duration =' + str(m.params['SSRO_duration'])

    pts = 51
    m.params['wait_for_AWG_done'] = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 300
   
    f_ctr=7.13429e6+100e3
    frq_range=15e3

    NR_of_pulses=1
    RF_pulse_length = 80e-6
    RF_pulse_amp = 1

    m.params['RF_pulse_multiplicities'] = np.ones(pts).astype(int)*NR_of_pulses
    m.params['RF_pulse_delays'] = np.ones(pts) * 50e-9
    # MW pulses
    m.params['RF_pulse_durations']  = np.ones(pts)*RF_pulse_length  
    m.params['RF_pulse_amps']   = np.ones(pts) * RF_pulse_amp
    m.params['RF_pulse_frqs']   = np.linspace(f_ctr-frq_range,f_ctr+frq_range,pts)

    m.params['sweep_name'] = 'RF pulse freq (MHz)'
    m.params['sweep_pts']  = m.params['RF_pulse_frqs'] * 1e-6

    # for the autoanalysis

    funcs.finish(m, debug=False)    

if __name__ == '__main__':
    #NMR('NMR_mIm1')
    NRabi('NRabi_mIp1')

