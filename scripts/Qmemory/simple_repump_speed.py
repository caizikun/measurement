"""
Measures how fast we repump by elongating the repumping time for a given power.

NK 2015
"""
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps

reload(pulsar_mbi_espin)

execfile(qt.reload_current_setup)
import mbi.mbi_funcs as funcs
reload(funcs)


SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
do_m1_readout = False



def run(name, **kw):
    m = pulsar_mbi_espin.Simple_Electron_repumping(name)
    funcs.prepare(m)

    max_duration = kw.get('max_duration',3e-6)
    m.params['RO_pm1'] = kw.pop('do_MW_RO', False)

    pts = 50 # even number

    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 200
    m.params['detuning'] = 0e6 #artificial detuning

    ## not in use
    # m.params['init_in_zero'] = init_in_zero

    # laser beam; called dephasing, but does repump
    m.params['repump_AOM'] = 'NewfocusAOM' 

    m.params['laser_repump_amplitude'] = kw.get('newfocus_power',5e-9)
    # m.params['repumper_amplitude'] = kw.get('repumper_power',5e-9)
    m.params['repumping_time'] = np.linspace(0.0e-6,max_duration,pts)

    m.params['MW_repump_delay1'] = np.ones(pts) * 1000e-9
    m.params['MW_repump_delay2'] = np.ones(pts) * 2500e-9
    m.params['Repump_multiplicity'] = np.ones(pts)*1
    
    # for the autoanalysis
    m.params['sweep_name'] = 'Repump duration (us)'
    m.params['sweep_pts'] = m.params['repumping_time']/(1e-6)

    funcs.finish(m, debug = kw.pop('debug',False))

if __name__ == '__main__':
    print 
    newfocus_power_list = [120e-9]
    max_repump_duration = 2e-6
    #repump_power_list = np.arange(0.05e-6, 0.51e-6, 0.05e-6)#, 350e-9, 200e-9, 100e-9, 50e-9, 20e-9]

    repump_laser_config = 'A_linear_modulated'

    for sweep_element in range(len(newfocus_power_list)):
        if False: #do a mw pi pulse after repumping
            add_to_msmt_name ='1RO_'

            do_MW_RO = True

            filename = SAMPLE_CFG + '_ElectronRepump_'+ \
                        str(newfocus_power_list[sweep_element]*1e9)+'nW_' \
                        +repump_laser_config
            
            print filename
            
            run(name=filename,  
                                max_duration    = max_repump_duration,
                                newfocus_power  = newfocus_power_list[sweep_element], do_MW_RO = do_MW_RO,
                                debug           = False)

        if True:# no mw pulses after repumping
            add_to_msmt_name ='0RO_'

            do_MW_RO = False

            filename = SAMPLE_CFG + '_ElectronRepump_'+ \
                        str(newfocus_power_list[sweep_element]*1e9)+'nW_' \
                        +repump_laser_config
            
            print filename
            
            run(name=filename,  
                                max_duration    = max_repump_duration,
                                newfocus_power  = newfocus_power_list[sweep_element], do_MW_RO = do_MW_RO,
                                debug           = False)

