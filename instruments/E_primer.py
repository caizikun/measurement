import qt
from instrument import Instrument
import numpy as np
import gobject
import instrument_helper
import types
from analysis.lib.nv import nvlevels

class E_primer(Instrument):

    def __init__(self, name, set_eprime_func,get_eprime_func,get_E_func,get_Y_func, **kw):
        Instrument.__init__(self, name)
       
        ins_pars  = {'read_interval'    :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'is_running'       :   {'type':types.BooleanType,'flags':Instrument.FLAG_GETSET},
                    'E_y'              :   {'type':types.BooleanType,'flags':Instrument.FLAG_GETSET},
                    }           
        instrument_helper.create_get_set(self,ins_pars)
        
        self.add_function('start')        
        self.add_function('stop')
        
        self._get_E_func=get_E_func
        self._get_Y_func=get_Y_func
        self._set_eprime_func = set_eprime_func
        self._get_eprime_func = get_eprime_func

        
        self.set_is_running(False)
        self.set_E_y(True)
        self.set_read_interval(1) #s

        self._timer=-1

    #--------------get_set        

    def _optimize(self,*arg):
        
        F_E=self._get_E_func()
        F_Y =self._get_Y_func()
        if self.get_E_y():
            E_prime_freq = nvlevels.get_E_prime_Ey(strain_splitting_0 = self._strain_split,
                F_Ey_0=self._F_E_0,F_Y_0=self._F_Y_0,F_Ey = F_E,F_Y =F_Y)[0]
        else:
            E_prime_freq = nvlevels.get_E_prime_Ex(strain_splitting_0 = self._strain_split,
                F_Ex_0=self._F_E_0,F_Y_0=self._F_Y_0,F_Ex = F_E,F_Y =F_Y)[0]
        self._set_eprime_func(E_prime_freq)
        #print E_prime_freq,self._get_eprime_func()

        return True


    def start(self):

        if self.get_is_running():
            print 'ALREADY RUNNING'
            return False
        self.set_is_running(True)

        E_prime_0 = self._get_eprime_func()
        self._F_E_0 = self._get_E_func()
        self._F_Y_0 = self._get_Y_func()
        print E_prime_0, self._F_E_0
        ms0_level=2 if self.get_E_y() else 3
        print ms0_level
        Ex, Ey = nvlevels.get_ExEy_from_two_levels(E_prime_0,0,self._F_E_0,ms0_level,precision=0.1)
        print Ey,Ex
        self._strain_split = Ex-Ey
        self._timer=gobject.timeout_add(int(self.get_read_interval()*1e3),\
            self._optimize)
        #return True
                
    def stop(self):
        self.set_is_running(False)
        return gobject.source_remove(self._timer)

