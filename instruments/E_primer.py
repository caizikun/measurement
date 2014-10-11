import qt
import os
from instrument import Instrument
import numpy as np
import gobject
import instrument_helper
import types
from lib import config
from analysis.lib.nv import nvlevels

class E_primer(Instrument):

    def __init__(self, name, set_eprime_func,get_eprime_func,get_E_func,get_Y_func,set_strain_splitting_func, **kw):
        Instrument.__init__(self, name)
       
        ins_pars  = {'read_interval'    :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET,'unit':'s', 'val': 1.},
                    'is_running'       :   {'type':types.BooleanType,'flags':Instrument.FLAG_GETSET, 'val': False},
                    'E_y'              :   {'type':types.BooleanType,'flags':Instrument.FLAG_GETSET, 'val': True},
                    'offset'           :   {'type':types.FloatType,  'flags':Instrument.FLAG_GETSET, 'unit':'GHz', 'val': 0.},
                    'strain_splitting' :   {'type':types.FloatType,  'flags':Instrument.FLAG_GET, 'unit':'GHz', 'val': 0.},
                    }           
        instrument_helper.create_get_set(self,ins_pars)
        
        self.add_function('start')        
        self.add_function('stop')
        
        self._get_E_func=get_E_func
        self._get_Y_func=get_Y_func
        self._set_eprime_func = set_eprime_func
        self._get_eprime_func = get_eprime_func
        self._set_strain_splitting_func = set_strain_splitting_func

        self._timer=-1

    # override from config    ----------   
        cfg_fn = os.path.abspath(
                os.path.join(qt.config['ins_cfg_path'], name+'.cfg'))
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        self._parlist = ['read_interval', 'E_y', 'offset']
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

    def _optimize(self,*arg):
        
        F_E=self._get_E_func()
        F_Y =self._get_Y_func()
        if self.get_E_y():
            levels = nvlevels.get_E_prime_Ey(strain_splitting_0 = self._strain_split_0,
                F_Ey_0=self._F_E_0,F_Y_0=self._F_Y_0,F_Ey = F_E,F_Y =F_Y)
        else:
            levels=nvlevels.get_E_prime_Ex(strain_splitting_0 = self._strain_split_0,
                F_Ex_0=self._F_E_0,F_Y_0=self._F_Y_0,F_Ex = F_E,F_Y =F_Y)
        E_prime_freq = levels[0]
        self._strain_splitting = levels[3]-levels[2] 
        self._set_strain_splitting_func(self._strain_splitting)
        self._set_eprime_func(E_prime_freq-self.get_offset())
        

        return True


    def start(self):

        if self.get_is_running():
            print 'ALREADY RUNNING'
            return False
        self.set_is_running(True)

        E_prime_0 = self._get_eprime_func()+self.get_offset()
        self._F_E_0 = self._get_E_func()
        self._F_Y_0 = self._get_Y_func()
        
        ms0_level=2 if self.get_E_y() else 3
        #print ms0_level
        Ex, Ey = nvlevels.get_ExEy_from_two_levels(E_prime_0,0,self._F_E_0,ms0_level,precision=0.01)
        #print Ey,Ex
        self._strain_split_0 = Ex-Ey
        self._strain_splitting = Ex-Ey
        #print E_prime_0, self._F_E_0
        print 'strain splitting: {:.2f}, (Ex, Ey) = ({:.2f},{:.2f})'.format(self._strain_splitting, Ex, Ey)
        self._timer=gobject.timeout_add(int(self.get_read_interval()*1e3),\
            self._optimize)
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