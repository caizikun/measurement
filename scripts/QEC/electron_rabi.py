
"""
Script for e-spin manipulations using the pulsar sequencer
"""
import qt
import numpy as np

#reload all parameters and modules
execfile(qt.reload_current_setup)

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def erabi_m1(name):
    m = pulsar_msmt.ElectronRabi(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    m.params['mw_power'] = 23

    pump_on_Ex = False
    if pump_on_Ex:
        m.params['SP_duration'] = 300
        m.params['A_SP_amplitude'] = 0.
        m.params['Ex_SP_amplitude'] = 10e-9

    m.params['pts'] = 101
    pts = m.params['pts']
    m.params['repetitions'] = 1000

    m.params['wait_after_pulse_duration']=0
    m.params['wait_after_RO_pulse_duration']=0

    m.params['mw_frq'] = m.params['ms-1_cntr_frq'] - 43e6      #for ms=-1
    m.params['MW_pulse_frequency'] = m.params['ms-1_cntr_frq'] - m.params['mw_frq']


    m.params['MW_pulse_durations'] =  np.linspace(0, 400, pts) * 1e-9
    #m.params['MW_pulse_durations'] =  80e-9*np.ones(pts)#np.linspace(0, 200, pts) * 1e-9

    m.params['MW_pulse_amplitudes'] = np.ones(pts) *1
    #m.params['MW_pulse_amplitudes'] = np.linspace(0,1.,pts)#0.55*np.ones(pts)

    # for autoanalysis
    #m.params['sweep_name'] = 'Pulse duration (ns)' #'Pulse amps (V)'
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9

    m.params['sweep_name'] = 'Pulse durations (ns)'
    #m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'

    m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
    #m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10) #Redundant because defined in m.autoconfig? Tim

    m.autoconfig() #Redundant because executed in m.run()? Tim
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()


def erabi_p1(name):
    m = pulsar_msmt.ElectronRabi(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])


    pump_on_Ex = False
    if pump_on_Ex:
        m.params['SP_duration'] = 300
        m.params['A_SP_amplitude'] = 0.
        m.params['Ex_SP_amplitude'] = 10e-9

    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 1000

    m.params['wait_after_pulse_duration']=0
    m.params['wait_after_RO_pulse_duration']=0

    m.params['mw_frq'] = m.params['ms+1_cntr_frq']-43e6      #for ms=+1
    m.params['MW_pulse_frequency'] = m.params['ms+1_cntr_frq'] - m.params['mw_frq']
    print m.params['ms-1_cntr_frq']
    m.params['mw_power'] = 23


    # m.params['MW_pulse_durations'] =  np.linspace(0, 600, pts) * 1e-9
    m.params['MW_pulse_durations'] =  5500e-9*np.ones(pts)#np.linspace(0, 200, pts) * 1e-9

    # m.params['MW_pulse_amplitudes'] = np.ones(pts) *1
    m.params['MW_pulse_amplitudes'] = np.linspace(0,0.02,pts) #0.85*np.ones(pts)

    # for autoanalysis
    #m.params['sweep_name'] = 'Pulse duration (ns)' #'Pulse amps (V)'
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9

    # m.params['sweep_name'] = 'Pulse durations (ns)'
    m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'

    # m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    m.params['sequence_wait_time'] = \
            int(np.ceil(np.max(m.params['MW_pulse_durations'])*1e6)+10) #Redundant because defined in m.autoconfig? Tim

    m.autoconfig() #Redundant because executed in m.run()? Tim
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()


if __name__ == '__main__':
    erabi_p1(SAMPLE+'_'+'Rabi+1')
    cont = raw_input ('Do the fitting for ms=+1... Continue with ms=-1 y/n?')
    if cont =='y':
        erabi_m1(SAMPLE+'_'+'Rabi-1')
