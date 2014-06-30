"""
LT1/2 script for adwin ssro.
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

SAMPLE_CFG = qt.exp_params['protocols']['current']

def ssrocalibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])

    m.params['repump_mod_DAC_channel'] = m.adwin.get_dac_channels()['yellow_aom_frq']
    m.params['cr_mod_DAC_channel']     = m.adwin.get_dac_channels()['gate_mod']#ssro.AdwinSSRO.adwin.get_dac_channels()['gate']
    m.params['cr_mod_control_offset']  =  0.0
    m.params['cr_mod_control_amp']     =  0.05 #V
    m.params['repump_mod_control_offset']  =  5.4
    m.params['repump_mod_control_amp']     =  .5 #V
    m.params['atto_positions'] = [m.adwin.get_dac_voltage('atto_x'), m.adwin.get_dac_voltage('atto_y'), m.adwin.get_dac_voltage('atto_z')]
    m.set_adwin_process_variable_from_params('atto_positions')
    m.params['pos_mod_control_amp'] =  0.03
    m.params['pos_mod_fb'] = 0.1
    m.params['pos_mod_min_counts'] = 100.

    m.params['pos_mod_activate'] = 0
    m.params['repump_mod_activate'] = 1
    m.params['cr_mod_activate'] = 1

        # parameters
    e_sp = m.params['Ex_SP_amplitude'] 
    a_sp =  m.params['A_SP_amplitude']

    print m.params['Ex_CR_amplitude']

    # ms = 0 calibration
    m.params['SP_duration'] = m.params['SP_duration_ms0']
    m.params['Ex_SP_amplitude'] = 0.
    m.params['A_SP_amplitude'] = a_sp
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = m.params['SP_duration_ms1']
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = e_sp
    #m.run()
    #m.save('ms1')

    m.params['atto_positions_after'] = m.adwin_var(('atto_positions',3))
    #print m.params['atto_positions_after'] 
    m.adwin.set_dac_voltage(('atto_x',m.params['atto_positions_after'][0]))
    m.adwin.set_dac_voltage(('atto_y',m.params['atto_positions_after'][1]))
    m.adwin.set_dac_voltage(('atto_z',m.params['atto_positions_after'][2]))
    qt.instruments['master_of_space'].init_positions_from_adwin_dacs()

    #m.run()
    #m.save('ms1')

    m.finish()

if __name__ == '__main__':
    print 'Green off'
    qt.instruments['GreenAOM'].turn_off()
    x=qt.instruments['master_of_space'].get_x()*1000
    y=qt.instruments['master_of_space'].get_y()*1000
    z=qt.instruments['master_of_space'].get_z()*1000
    ssrocalibration(SAMPLE_CFG)
    qt.msleep(0.3)
    x2=qt.instruments['master_of_space'].get_x()*1000
    y2=qt.instruments['master_of_space'].get_y()*1000
    z2=qt.instruments['master_of_space'].get_z()*1000
    print 'moved [nm]:', int(x-x2), int(y-y2), int(z-z2)

