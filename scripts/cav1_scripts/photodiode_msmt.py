"""
Cavity script for photodiode measurement
SvD 12-2016
"""
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_pd import photodiode_msmt


def scan_laser_freq(name):
    m = photodiode_msmt.AdwinPhotodiode('Photodiode')

    m.params.from_dict(qt.exp_params['protocols']['AdwinPhotodiode'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinPhotodiode']['laserfrq_scan'])


    m.params['start_voltage'] = 0
    m.params['end_voltage'] = 0.3

    m.params['nr_scans']=1
    m.params['nr_steps']=11


    m.params['voltage_step'] = abs((m.params['end_voltage'] - m.params['start_voltage']))/float(m.params['nr_steps']-1)
    m.params['start_voltage_1'] = m.params['start_voltage']
    m.params['start_voltage_2'] = m.params['start_voltage']
    m.params['start_voltage_3'] = m.params['start_voltage']

    #useful derived parameters useful for analysis
    m.params['nr_ms_per_point'] = m.params['ADC_averaging_cycles']/m.params['save_cycles']
    dac_channels = [m.params['DAC_ch_1'],m.params['DAC_ch_2'],m.params['DAC_ch_3']]
    dac_names = ['jpe_fine_tuning_1','jpe_fine_tuning_2','jpe_fine_tuning_3']
    start_voltages = [m.params['start_voltage'],m.params['start_voltage'],m.params['start_voltage']]

    ####scan to start###########
    if scan_to_start:
        print 'scan to start'
        speed = 2000#mV/s; scan slowly
        _steps,_pxtime = self._adwin.speed2px(dac_channels, start_voltages, speed=speed)
        print _steps,_pxtime
        self._adwin.linescan(dac_names, self._adwin.get_dac_voltages(dac_names),
                start_voltages, _steps, _pxtime, value='none', 
                scan_to_start=False, blocking = True)

    m.run()
    m.save('scan_laser_freq')
    m.finish()




def scan_cavity_length(name):
    m = photodiode_msmt.AdwinPhotodiode('Photodiode')

    m.params.from_dict(qt.exp_params['protocols']['AdwinPhotodiode'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinPhotodiode']['cavlength_scan'])


    m.params['start_voltage'] = 0
    m.params['end_voltage'] = 0.3

    m.params['nr_scans']=1
    m.params['nr_steps']=11


    m.params['voltage_step'] = abs((m.params['end_voltage'] - m.params['start_voltage']))/float(m.params['nr_steps']-1)
    m.params['start_voltage_1'] = m.params['start_voltage']
    m.params['start_voltage_2'] = m.params['start_voltage']
    m.params['start_voltage_3'] = m.params['start_voltage']

    #derived parameters useful for analysis
    m.params['nr_ms_per_point'] = m.params['ADC_averaging_cycles']/m.params['save_cycles']

    ####scan to start###########

    if scan_to_start:
        print 'scan to start'
        speed = 20000 #mV/s; scan a bit slowly
        _steps,_pxtime = self._adwin.speed2px([m.params['DAC_ch_1'],m.params['DAC_ch_2'],m.params['DAC_ch_3']], [m.params['start_voltage'],m.params['start_voltage'],m.params['start_voltage']],speed=speed)
        print _steps,_pxtime
        self._adwin.linescan(dac_names, self._adwin.get_dac_voltages(dac_names),
                start_voltages, _steps, _pxtime, value='none', 
                scan_to_start=False, blocking = True)
