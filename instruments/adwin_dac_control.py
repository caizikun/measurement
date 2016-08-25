# optimizer for LT2
#
# author: wolfgang <w dot pfaff at tudelft dot nl>

from instrument import Instrument
import types
import qt
import msvcrt
import os
from lib import config
import instrument_helper

class adwin_dac_control(Instrument):
    
   
    def __init__(self, name):
        Instrument.__init__(self, name)

        self.add_function('step_up')
        self.add_function('step_down')
        self.add_function('set_zero')

  
        ins_pars  ={'channel'              :   {'type':types.StringType,'flags':Instrument.FLAG_GETSET, 'val':''},
                    'min_value'          :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':0},
                    'max_value'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':2}, 
                    'step_size'           :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':0},
                 }           
        instrument_helper.create_get_set(self,ins_pars)

        self.add_parameter('current_value',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET)

        self._parlist = ins_pars.keys()

        self._adwin = qt.instruments['adwin']
        
        # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()

        self._do_get_current_value()
        
    def get_all_cfg(self):
        for n in self._parlist:
            self.get(n)
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in self._parlist:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self._parlist:
            value = self.get(param)
            self.ins_cfg[param] = value
            
            
    def _check_valid_channel(self):
        if self.get_channel() in self._adwin.get_dac_channels().keys():
            return True
        else:
            print "Invalid channel"
            return False

    def _do_set_current_value(self, val):
        
        if self._check_valid_channel():
            if val >= self._max_value:
                print 'Max value exceeded'
                return
            elif val <= self._min_value:
                print 'Min value exceeded'
            else:
                self._adwin.set_dac_voltage((self.get_channel(),val))
 
        self.get_current_value()

    def _do_get_current_value(self):
        if self._check_valid_channel():
            voltage = self._adwin.get_dac_voltage(self.get_channel())
            return voltage
    
    def step_up(self):

        self._do_set_current_value(self.get_current_value() + self.get_step_size())


    def step_down(self):

        self._do_set_current_value(self.get_current_value() - self.get_step_size())

    def set_zero(self):

        self._do_set_current_value(0)
