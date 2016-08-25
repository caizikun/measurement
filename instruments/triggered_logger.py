import os
import types
import gobject
import time
import numpy as np

import qt
from instrument import Instrument
from data import Data
import msvcrt
from lib import config
import instrument_helper
"""
This instrument allows for the triggered logging of data (e.g. NV frequencies if the CR counts are resonant etc.)
For examples see the purification optimizer and the usage of the logger there.
Example of initialization:
    _get_freq_yellow=lambda: qt.instruments['physical_adwin'].Get_FPar(42)
    _get_freq_gate=lambda:  qt.instruments['ivvi'].get_dac3()
    _get_freq_newfocus=lambda: qt.instruments['physical_adwin'].Get_FPar(41)
    # Logger takes '__name__' parameter as column header
    _get_freq_yellow.__name__ = 'yellow_freq'
    _get_freq_gate.__name__ = 'gate_voltage'
    _get_freq_newfocus.__name__ = 'newfocus_freq'
    _function_list = [_get_freq_yellow, _get_freq_gate, _get_freq_newfocus]
    frequency_logger = qt.instruments.create('frequency_logger', 'triggered_logger', function_list = _function_list) 
"""
class triggered_logger(Instrument):

    def __init__(self, name, function_list = []):
        Instrument.__init__(self, name)        

        self._function_list = function_list;
        self._time_start = time.time();
        self._create_datafile();
        
    def log(self):
        # print 'Logging now'
        # Get time value
        current_time = time.time() - self._time_start;
        # Get values returned by given functions        
        values = np.zeros(len(self._function_list));
        for i in np.arange(len(self._function_list)):
            current_function = self._function_list[i];
            values[i] = current_function();
        # Add data to data file. * operator unpacks values array to arguments
        self._dat.add_data_point(current_time, *values)            


    def _create_datafile(self):
        print 'Create dataset'
        # Initialize data file
        self._dat = qt.Data(name = self._name)
        # Create time column
        self._dat.add_coordinate('time');
        # Create columns for each function
        self._function_names = [];
        for i in np.arange(len(self._function_list)):
            current_function = self._function_list[i];
            self._function_names.append(current_function.__name__) 
            self._dat.add_value(current_function.__name__);            

