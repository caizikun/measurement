import qt
from instrument import Instrument
import numpy as np
import gobject
import instrument_helper
import types

class multiple_optimizer(Instrument):
    def __init__(self, name, **kw):
        Instrument.__init__(self, name)
        
       
        ins_pars  = {'read_interval'    :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'is_running'       :   {'type':types.BooleanType,'flags':Instrument.FLAG_GETSET},
                    }           
        instrument_helper.create_get_set(self,ins_pars)
        
        self.add_function('start')        
        self.add_function('stop')
        self.add_function('manual_check')
        
        self._optimizers=[]
        
        self.set_is_running(False)
        self.set_read_interval(60) #s
        self._is_waiting=False
        self._timer=-1

    #--------------get_set        
        
    def _check(self):
        if self._is_waiting:
            return True
        else:
            self.check()
        pass
    
    def manual_check(self):
        return self._check()

    def check(self):
        pass
        
    def start(self):
        if self.get_is_running():
            print 'ALREADY RUNNING'
            return False
        if self._is_waiting:
            print 'still waiting from previous run, will wait 20 sec extra.'
            qt.msleep(20)
            self._stop_waiting()
        self.set_is_running(True)
        self._timer=gobject.timeout_add(int(self.get_read_interval()*1e3),\
                self._check)
        return True
                
    def stop(self):
        self.set_is_running(False)
        return gobject.source_remove(self._timer)
    
    def start_waiting(self,time):
        self._is_waiting=True
        gobject.timeout_add(int(time*1e3),\
                self._stop_waiting)
                
    def _stop_waiting(self):
        self._is_waiting=False
        
        return False