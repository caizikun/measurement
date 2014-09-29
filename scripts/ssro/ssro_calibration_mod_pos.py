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
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])

    m.params['pos_mod_scan_length'] = 200
    m.params['pos_mod_atto_x'] = m.adwin.get_dac_voltage('atto_x')
    m.params['pos_mod_atto_y'] = m.adwin.get_dac_voltage('atto_y')
    m.params['pos_mod_atto_z'] = m.adwin.get_dac_voltage('atto_z')
    
        # parameters
    e_sp = m.params['Ex_SP_amplitude'] 
    a_sp =  m.params['A_SP_amplitude']

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
    #print m.params['pos_mod_atto_x'],m.params['pos_mod_atto_y'],m.params['pos_mod_atto_z']
    m.adwin.set_dac_voltage(('atto_x',m.params['atto_positions_after'][0]))
    m.adwin.set_dac_voltage(('atto_y',m.params['atto_positions_after'][1]))
    m.adwin.set_dac_voltage(('atto_z',m.params['atto_positions_after'][2]))
    qt.instruments['master_of_space'].init_positions_from_adwin_dacs()

    #m.run()
    m.save('ms1')

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
    print 'moved [nm]:', int(x2-x), int(y2-y), int(z2-z)

