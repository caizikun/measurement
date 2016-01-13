"""
Measures how fast we repump by elongating the repumping time for a given power.

NK 2015
"""
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
reload(pulsar_mbi_espin)

execfile(qt.reload_current_setup)
import mbi.mbi_funcs as funcs
reload(funcs)


SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']
do_m1_readout = False



def run(name, **kw):
    m = pulsar_mbi_espin.ElectronRamsey_Dephasing(name)
    funcs.prepare(m)
    max_duration = kw.get('max_duration',3e-6)
    pts = 200 # even number
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['detuning'] = 0e6 #artificial detuning

    # MW pulses
    ## First pulse
    # m.params['MW_pulse_durations'] = np.ones(pts) * m.params['fast_pi_duration']
    # m.params['MW_pulse_amps'] = np.ones(pts) * m.params['fast_pi_amp']
    # m.params['MW_pulse_mod_frqs'] = np.ones(pts) * m.params['AWG_MBI_MW_pulse_mod_frq']
    # m.params['MW_pulse_1_phases'] = np.ones(pts) * 0
    
    m.params['init_with_second_source'] = init_with_second_source
    m.params['readout_with_second_source'] = readout_with_second_source
    m.params['init_in_zero'] = init_in_zero

    ## initialization microwave pulse
    if init_with_second_source:
        m.params['MW_pulse_durations'] = np.ones(pts) * m.params['mw2_fast_pi_duration']
        m.params['MW_pulse_amps'] = np.ones(pts) * m.params['mw2_fast_pi_amp']
    else:
        m.params['MW_pulse_durations']   = np.ones(pts) * m.params['fast_pi_duration']
        m.params['MW_pulse_amps'] = np.ones(pts) * m.params['fast_pi_amp']
        m.params['MW_pulse_mod_frqs'] = np.ones(pts) * m.params['AWG_MBI_MW_pulse_mod_frq']
        m.params['MW_pulse_1_phases'] = np.ones(pts) * 0

    ## Readout microwave pulse
    if do_pm1_readout:
        if readout_with_second_source:
            m.params['MW_pulse_2_durations'] = np.ones(pts) * m.params['mw2_fast_pi_duration']
            m.params['MW_pulse_2_amps']      = np.ones(pts) * m.params['mw2_fast_pi_amp'] 
        else:
            m.params['MW_pulse_2_durations'] = np.ones(pts) * m.params['fast_pi_duration']
            m.params['MW_pulse_2_amps']      = np.ones(pts) * m.params['fast_pi_amp'] 
            m.params['MW_pulse_mod_frqs'] = np.ones(pts) * m.params['AWG_MBI_MW_pulse_mod_frq']
            m.params['MW_pulse_2_phases']    = np.ones(pts) * 0
    else:
        m.params['MW_pulse_2_durations']    = np.ones(pts) * 0
        m.params['MW_pulse_2_amps']         = np.ones(pts) * 0 
        m.params['MW_pulse_2_phases']       = np.ones(pts) * 0 

    m.params['pump_using_repumper'] = pump_using_repumper
    m.params['pump_using_newfocus'] = pump_using_newfocus
    m.params['pump_using_MW2'] = pump_using_MW2
    
    if pump_using_MW2:
        m.params['pump_MW2_durations'] = np.linspace(0.0e-6,max_duration,pts)
        m.params['pump_MW2_delay'] = np.ones(pts) * pump_MW2_delay
        m.params['pump_MW2_falltime'] = np.ones(pts) * pump_MW2_falltime

    # laser beam; called dephasing, but does repump
    m.params['dephasing_AOM'] = 'NewfocusAOM' 
    #m.params['dephasing_AOM'] = 'RepumperAOM' 
    m.params['laser_dephasing_amplitude'] = kw.get('newfocus_power',100e-9)
    m.params['repumper_amplitude'] = kw.get('repumper_power',100e-9)
    m.params['repumping_time'] = np.linspace(0.0e-6,max_duration,pts) # np.r_[np.linspace(0.0e-6,0.2e-6,pts/2), np.linspace(1.2e-6,5e-6,pts/2)]
    #m.params['repumping_time'] = np.r_[np.linspace(0.03e-6,0.5e-6,pts/4.), np.linspace(0.2e-6,5e-6,3.*pts/4.)]
    
    m.params['MW_repump_delay1'] = np.ones(pts) * 500e-9
    m.params['MW_repump_delay2'] = np.ones(pts) * 2500e-9
    m.params['Repump_multiplicity'] = np.ones(pts)*1
    
    # for the autoanalysis
    m.params['sweep_name'] = 'Repump duration (us)'
    m.params['sweep_pts'] = m.params['repumping_time']/(1e-6)

    funcs.finish(m, debug = kw.get('debug',False))

if __name__ == '__main__':
    print 
    newfocus_power_list = [2500e-9]
    repumper_power_list = [100e-9]
    max_repump_duration = 1.5e-6
    #repump_power_list = np.arange(0.05e-6, 0.51e-6, 0.05e-6)#, 350e-9, 200e-9, 100e-9, 50e-9, 20e-9]

    init_with_second_source = False
    readout_with_second_source = True
    init_in_zero = False
    do_pm1_readout = False

    pump_using_MW2 = False
    pump_using_newfocus = True
    pump_using_repumper = True

    pump_MW2_delay = 150e-9
    pump_MW2_falltime = 50e-9 # makes sure that the laser is longer than the MW pulse such that pumping is complete

    repump_laser_config = 'A1m1_A2p1'

    add_to_msmt_name = 'pm1RO_' if do_pm1_readout else '0RO_'

    for sweep_element in range(len(newfocus_power_list)):
        if True:
            add_to_msmt_name ='0RO_'
            do_pm1_readout = False
            filename = 'ElectronRepump_'+str(newfocus_power_list[sweep_element]*1e9)+'nW_'+str(repumper_power_list[sweep_element]*1e9)+'nW_'+add_to_msmt_name+repump_laser_config
            print filename
            run(name=filename, max_duration=max_repump_duration,
                newfocus_power=newfocus_power_list[sweep_element], repumper_power = repumper_power_list[sweep_element],
                debug=False)

        if True:
            add_to_msmt_name = 'm1RO_'
            do_pm1_readout = True
            readout_with_second_source = False
            for sweep_element in range(len(newfocus_power_list)):
                filename = 'ElectronRepump_'+str(newfocus_power_list[sweep_element]*1e9)+'nW_'+str(repumper_power_list[sweep_element]*1e9)+'nW_'+add_to_msmt_name+repump_laser_config
                print filename
                run(name=filename, max_duration=max_repump_duration,
                    newfocus_power=newfocus_power_list[sweep_element], repumper_power = repumper_power_list[sweep_element],
                    debug=False)

        if True:
            add_to_msmt_name = 'p1RO_'
            do_pm1_readout = True
            readout_with_second_source = True
            for sweep_element in range(len(newfocus_power_list)):
                filename = 'ElectronRepump_'+str(newfocus_power_list[sweep_element]*1e9)+'nW_'+str(repumper_power_list[sweep_element]*1e9)+'nW_'+add_to_msmt_name+repump_laser_config
                print filename
                run(name=filename, max_duration=max_repump_duration,
                    newfocus_power=newfocus_power_list[sweep_element], repumper_power = repumper_power_list[sweep_element],
                    debug=False)
