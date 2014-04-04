import qt
from instrument import Instrument
import numpy as np
import gobject
import instrument_helper
import types

class remote_measurement_helper(Instrument):
    
    def __init__(self, name, **kw):
        Instrument.__init__(self, name)
        
#        self.add_parameter('measurement_parameters',
#                           type=types.DictType,
#                           flags=Instrument.FLAG_GETSET)
#        self.add_parameter('data_path',
#                           type=types.StringType,
#                           flags=Instrument.FLAG_GETSET)
       
        ins_pars  = {'measurement_params'    :   {'type':types.DictType,'val':{},'flags':Instrument.FLAG_GETSET},
                    'is_running'       :   {'type':types.BooleanType,'val':False,'flags':Instrument.FLAG_GETSET},
                    'data_path'         :   {'type':types.StringType,'val':'','flags':Instrument.FLAG_GETSET}
                    }           
        instrument_helper.create_get_set(self,ins_pars)
        
        self.add_function('execute_script')

    def execute_script(self,path):
        execfile(path)