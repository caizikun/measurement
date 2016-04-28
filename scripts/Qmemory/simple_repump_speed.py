"""
Measures how fast we repump by elongating the repumping time for a given power.

NK 2015
"""
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
reload(pulsar_mbi_espin)
import mbi.mbi_funcs as funcs
reload(funcs)
execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
do_m1_readout = False



def run(name, **kw):
    m = pulsar_mbi_espin.Simple_Electron_repumping(name)
    funcs.prepare(m)

    max_duration = kw.get('max_duration',3e-6)
    more_data_until = kw.pop('more_data_until', 0)
    m.params['init_state'] = kw.pop('init_state', 'm1' )
    m.params['ro_state'] = kw.pop('ro_state', '0')

    pts = 50 # even number
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['detuning'] = 0e6 #artificial detuning

    m.params['repump_AOM'] = 'NewfocusAOM' 
    m.params['laser_repump_amplitude'] = kw.get('newfocus_power',5e-9)
    # m.params['repumper_amplitude'] = kw.get('repumper_power',5e-9)
    duration_sweep = True
    if duration_sweep:
        m.params['delay_before_MW'] = 0e-9 * np.ones(pts)
        m.params['delay_after_MW'] = 0e-9 * np.ones(pts)


        if more_data_until == 0 or more_data_until>max_duration:
            m.params['repumping_time'] = np.linspace(0.0e-6, max_duration,pts)
        else:
            m.params['repumping_time'] = np.append(
                np.linspace(0.0e-6,more_data_until,pts/2),np.linspace(more_data_until,max_duration,pts/2))
    else:
        m.params['repumping_time']  = np.ones(pts) *30e-9
        m.params['delay_after_MW'] = np.linspace(0e-9, 500e-9 ,pts)
        m.params['delay_before_MW'] = np.linspace(0e-9, 500e-9 ,pts)
        

    m.params['MW_repump_delay1'] = np.ones(pts) * 1000e-9
    m.params['MW_repump_delay2'] = np.ones(pts) * 2500e-9
    m.params['Repump_multiplicity'] = np.ones(pts)*1

    m.params['pumping_cycles'] = kw.get('pumping_cycles',1)

    
    # for the autoanalysis
    if duration_sweep:
        m.params['sweep_name'] = 'Repump duration (ns)'
        m.params['sweep_pts'] = m.params['repumping_time']/(1e-9)
    else:
        m.params['sweep_name'] = 'Repump MW delay (ns)'
        m.params['sweep_pts'] = m.params['delay_after_MW']/(1e-9)
    funcs.finish(m, debug = kw.pop('debug',False))

if __name__ == '__main__':
    print 
    newfocus_power_list = [1000e-9]
    pumping_cycles = 1
    #newfocus_power_list = np.arange(0.05e-6, 0.51e-6, 0.05e-6)#, 350e-9, 200e-9, 100e-9, 50e-9, 20e-9]

    max_repump_duration = 2500e-9
    more_data_until = 0.


    repump_laser_config = '_Eprime'
    # MW configuration is chosen such that mw1 drives to m1 and mw2 drives to p1
    init_states = ['m1']
    ro_states = ['0','m1']

    for power_sweep_element in range(len(newfocus_power_list)):
        for init_element in init_states:
            for ro_element in ro_states:
                filename = SAMPLE_CFG + repump_laser_config+'_Repump_'+ \
                        str(newfocus_power_list[power_sweep_element]*1e9)+'nW_' \
                        +ro_element+'RO_'+init_element+'init_'+str(pumping_cycles)+'cycles'
                print filename
                
                run(name=filename,  
                    max_duration    = max_repump_duration,
                    newfocus_power  = newfocus_power_list[power_sweep_element], 
                    init_state = init_element, ro_state = ro_element,
                    pumping_cycles = pumping_cycles,
                    debug = False,
                    more_data_until = more_data_until)