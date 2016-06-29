# Virtual adwin instrument, adapted from rt2 to fit lt2, dec 2011 
import os
import types
import qt
import numpy as np
from instrument import Instrument
import time
from lib import config

from measurement.instruments.adwin import adwin
from measurement.lib.config import adwins as adwinscfg


class adwin_cav1(adwin):
    def __init__(self, name, physical_adwin ='physical_adwin', **kw):
        adwin.__init__(self, name, 
                adwin = qt.instruments[physical_adwin], 
                processes = adwinscfg.config['adwin_cav1_processes'],
                default_processes=['counter', 'set_dac', 'set_dio', 'linescan','read_adc', 'voltage_scan_sync'], 
                dacs=adwinscfg.config['adwin_cav1_dacs'], 
                adcs=adwinscfg.config['adwin_cav1_adcs'],            
                tags=['virtual'],
                use_cfg  = kw.pop('use_cfg',True),
                process_subfolder = qt.config['adwin_pro_subfolder'], **kw)
                

   
    def get_xyz_U(self):
        return self.get_dac_voltages(['scan_mirror_x','scan_mirror_y'])

    def move_to_xyz_U(self, target_voltages, speed=5000, blocking=False):
        current_voltages = self.get_xyz_U()
        dac_names = ['scan_mirror_x','scan_mirror_y']
        steps, pxtime = self.speed2px(dac_names, target_voltages, speed)
        self.linescan(dac_names, current_voltages, target_voltages,
                steps, pxtime, value='none', scan_to_start=False,
                blocking=blocking)
        
        return