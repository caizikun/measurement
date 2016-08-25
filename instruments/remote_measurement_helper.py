import qt
from instrument import Instrument
import numpy as np
import instrument_helper
import types
from lib.network import object_sharer as objsh
import logging
from lib import config
import os
import gobject

class remote_measurement_helper(Instrument):
    
    def __init__(self, name, exec_qtlab_name, **kw):
        Instrument.__init__(self, name)
        self._exec_qtlab_name = exec_qtlab_name
        ins_pars  = {'measurement_name'     :   {'type':types.StringType,'val':'','flags':Instrument.FLAG_GETSET},
                    'is_running'            :   {'type':types.BooleanType,'val':False,'flags':Instrument.FLAG_GETSET},
                    'data_path'             :   {'type':types.StringType,'val':'','flags':Instrument.FLAG_GETSET},
                    'script_path'           :   {'type':types.StringType,'val':'','flags':Instrument.FLAG_GETSET},
                    'live_plot_interval'    :   {'type':types.FloatType, 'val':2,'flags':Instrument.FLAG_GETSET},
                    'do_live_plotting'      :   {'type':types.BooleanType, 'val':False,'flags':Instrument.FLAG_GETSET},
                    'completed_reps'        :   {'type':types.IntType, 'val':0,'flags':Instrument.FLAG_GETSET}
                    }
        instrument_helper.create_get_set(self,ins_pars)
        
        self.add_function('execute_script')
        self.add_function('get_measurement_params')
        self.add_function('set_measurement_params')

        self.add_function('start_adwin_live_plotting')
        self.add_function('get_adwin_data')
        self.add_function('plot_adwin_data')
        self.add_function('stop_adwin_live_plotting')

        self._measurement_params = {}

        # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')

        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self._ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg()

    def get_all(self):
        for n in self.get_parameter_names():
            self.get(n)
        
    
    def load_cfg(self):
        params_from_cfg = self._ins_cfg.get_all()

        for p in params_from_cfg:
            val = self._ins_cfg.get(p)
            if type(val) == unicode:
                val = str(val)
            
            self.set(p, value=val)


    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self._ins_cfg[param] = value

    def execute_script(self):

        script_dir = os.path.split(self.get_script_path())[0]
        remote_cmd=objsh.helper.find_object(self._exec_qtlab_name +':python_server')
        if remote_cmd!=None:
            inital_dir = remote_cmd.cmd("os.path.abspath('.')")
            remote_cmd.cmd("os.chdir('{}')".format(script_dir))
            remote_cmd.cmd("execfile('{}')".format(self.get_script_path()))
            remote_cmd.cmd("os.chdir('{}')".format(inital_dir))
        else:
            logging.warning(self.get_name() + ': Remote qtlab instance ' + self._exec_qtlab_name +' not found, client disconnected?')
        return True

    def start_adwin_live_plotting(self):
        if not self.get_do_live_plotting():
            self.set_do_live_plotting(True)
            gobject.timeout_add(int(self.get_live_plot_interval()*1e3),self.plot_adwin_data)
        else:
            print 'WARNING: Live plotting is already running!'

    def get_adwin_data(self,index,start,length):
        pass

    def plot_adwin_data(self):

        if not self.get_do_live_plotting():
            return False

        if self.get_is_running():
            try:
                self.sweep_pts = self._measurement_params['sweep_pts']
                self.total_reps = self._measurement_params['repetitions']
                # print 'these are the total reps',self.total_reps

            except:
                print 'Measurement helper: No sweep points found for live plotting'
                return True


            #### SSRO results are always assumed to be at DATA_27!

            return True

        else:
            self.sweep_pts = []
            self.ssro_results = []
            self.total_reps = 1
            return True
    def stop_adwin_live_plotting(self):
        self.set_do_live_plotting(False)

    def get_measurement_params(self):
        return self._measurement_params       

    #def set_measurement_params(self,**kw):
    #    self._measurement_params = {}
    #    for k in kw:
    #        self._measurement_params[k] = kw[k]

    def set_measurement_params(self,params):
        self._measurement_params = params
