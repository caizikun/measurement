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

class frequency_logger(Instrument):

    def __init__(self, name, get_freq_yellow=None, get_freq_gate=None, get_freq_newfocus=None):
        Instrument.__init__(self, name)        

        self._get_freq_yellow=get_freq_yellow
        self._get_freq_gate=get_freq_gate
        self._get_freq_newfocus=get_freq_newfocus
        
        ins_pars  ={'delta_t'           :   {'type':types.FloatType,  'val':1.0,'flags':Instrument.FLAG_GETSET},
                    'log_gate'          :   {'type':types.BooleanType,  'val':True,'flags':Instrument.FLAG_GETSET},
                    'log_yellow'        :   {'type':types.BooleanType,  'val':True,'flags':Instrument.FLAG_GETSET},
                    'log_newfocus'      :   {'type':types.BooleanType,  'val':True,'flags':Instrument.FLAG_GETSET},
                    'is_running'        :   {'type':types.BooleanType,'val':False,'flags':Instrument.FLAG_GETSET}                    
                    }
        
        instrument_helper.create_get_set(self,ins_pars)
                   
        self.add_function('start')
        self.add_function('stop')
        
    # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()

    def start(self):
        print 'Start frequency logger'
        if self._is_running:
            print 'Frequency logger already running'
        self._is_running = True            

        # Create data file
        self._dat = qt.Data(name=self._name)
        self._dat.add_coordinate('time')
        self._dat.add_value('gate frequency')
        self._dat.add_value('yellow frequency')
        self._dat.add_value('newfocus frequency')
        self._dat.create_file()

        # Start running logger
        self._startTime = time.time();
        self._timer=gobject.timeout_add(int(self._delta_t*1e3),self.run)

    def run(self):
        print 'Run'
        if not self._is_running:
            return False        
        # Get time
        currentTime = time.time() - self._startTime;
        print 'Measure frequency at time', currentTime;
        # Get frequencies
        if self._log_gate:
            freq_gate = self._get_freq_gate();
        else:
            freq_gate = -1;
        if self._log_yellow:
            freq_yellow = self._get_freq_yellow();
        else:
            freq_yellow = -1;
        if self._log_newfocus:
            freq_newfocus = self._get_freq_newfocus();
        else:
            freq_newfocus = -1;
        # Add data to data file
        self._dat.add_data_point(currentTime, freq_gate, freq_yellow, freq_newfocus)            
        return True;

    def stop(self):
        print 'Stop frequency logger'
        if not self._is_running:
            print 'Frequency logger is not currently running'
        self._is_running = False
        return gobject.source_remove(self._timer)

    def remove(self):
        self.stop()
        Instrument.remove(self)

    def reload(self):
        self.stop()
        Instrument.reload(self)        
        
    def get_all_cfg(self):
        for n in self._parlist:
            self.get(n)
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in params_from_cfg:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self.get_parameter_names():
            value = self.get(param)
            self.ins_cfg[param] = value
           