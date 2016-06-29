import qt
import os
import logging
from instrument import Instrument
import numpy as np
import gobject
import instrument_helper
import types
from lib import config

class CavitySlowLock(Instrument):

    def __init__(self, name, adwin='adwin',master_of_cavity='master_of_cavity', control_adc_no=32, value_adc_no=16, **kw):
        Instrument.__init__(self, name)
       
        ins_pars  = {'read_interval'   :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET,'unit':'s', 'val': 1.},
                    'is_running'       :   {'type':types.BooleanType,'flags':Instrument.FLAG_GETSET, 'val': False},
                    'step_size'        :   {'type':types.FloatType,  'flags':Instrument.FLAG_GETSET, 'unit':'V', 'val': 0.001},
                    'step_threshold'   :   {'type':types.FloatType,  'flags':Instrument.FLAG_GETSET, 'unit':'V', 'val': 8.},
                    'min_value'        :   {'type':types.FloatType,  'flags':Instrument.FLAG_GETSET, 'unit':'V', 'val': 0.1},
                    }           
        instrument_helper.create_get_set(self,ins_pars)
        

        self.add_parameter('control',
                flags = Instrument.FLAG_GET,
                units = 'V',
                type = types.FloatType)

        self.add_parameter('value',
                flags = Instrument.FLAG_GET,
                units = 'V',
                type = types.FloatType)

        self.add_function('start')        
        self.add_function('stop')
        self.add_function('manual_check')
        
        self._control_adc_no=control_adc_no
        self._value_adc_no=value_adc_no

        self._adwin = qt.instruments[adwin]
        self._moc = qt.instruments[master_of_cavity]

        self._timer=-1

    # override from config    ----------   
        cfg_fn = os.path.abspath(
                os.path.join(qt.config['ins_cfg_path'], name+'.cfg'))
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        self._parlist = ['read_interval', 'step_size', 'step_threshold']
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()


    def get_all(self):
        for n in self._parlist:
            self.get(n)
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in params_from_cfg:
            if p in self._parlist:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self._parlist:
            value = self.get(param)
            self.ins_cfg[param] = value 

    #--------------get_set        

    def do_get_value(self):
        return self._adwin.read_ADC(self._value_adc_no)

    def do_get_control(self):
        return self._adwin.read_ADC(self._control_adc_no)

    def _check(self,*arg):
        control_voltage = self.get_control()
        value = self.get_value()
        if control_voltage > self.get_step_threshold():
            step = 1.
        elif control_voltage < -self.get_step_threshold():
            step = -1.
        else:
            step=0.
        if step != 0.:    
            cur_voltages = self._moc.get_fine_piezo_voltages()
            new_voltages = cur_voltages+step*self.get_step_size()
            if value > self.get_min_value():
                print 'setting new voltages',new_voltages
                self._moc.ramp_fine_piezo_voltages(*new_voltages,voltage_steps=0.00001)
            else:
                print 'Value not sufficient to change control'

        return True

    def manual_check(self):
        if self.get_is_running():
            print 'ALREADY RUNNING'
            return False
        return self._check()

    def start(self):

        if self.get_is_running():
            print 'ALREADY RUNNING'
            return False
        self.set_is_running(True)

        self._timer=gobject.timeout_add(int(self.get_read_interval()*1e3),\
            self._check)
        #return True
                
    def stop(self):
        self.set_is_running(False)
        return gobject.source_remove(self._timer)

    def remove(self):
        self.stop()
        Instrument.remove(self)

    def reload(self):
        self.stop()
        Instrument.reload(self)