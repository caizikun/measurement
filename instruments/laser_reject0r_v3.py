from instrument import Instrument
import types
import qt
import numpy as np
import msvcrt, os, sys, time, gobject
from analysis.lib.fitting import fit, common
import instrument_helper
from lib import config
from measurement.lib.config import rotation_mounts as rotcfg
reload(rotcfg)
from scipy import optimize

class laser_reject0r_v3(Instrument):  

    def __init__(self, name, rotator, rotation_config_name='',
                waveplates=['zpl_half','zpl_quarter'],
                get_value_f=None, get_norm_f=None, get_count_f=None, get_msmt_running_f = None):
        Instrument.__init__(self, name)


        self._rotator = qt.instruments[rotator]
        
        self._waveplates=waveplates
        self._rotation_cfg=rotcfg.config[rotation_config_name]
        self._prev_wp_channel='none'

        self._get_value_f = get_value_f
        self._get_norm_f = get_norm_f
        self._get_count_f = get_count_f
        self._get_msmt_running_f = get_msmt_running_f
        self._is_running = False
        self._timer = -1

        self._half_direction = 1
        self._quarter_direction = 1
        self._reject_cycles = 0

        ins_pars  = {
                    'integration_time_during_msmt'   : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10, 'units': 's'},
                    'integration_time'        : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':0.3, 'units': 's'},
                    'good_rejection'          : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':3},
                    'step_size'               : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':2}
                    }
        instrument_helper.create_get_set(self,ins_pars)

        self.add_function('move')
        self.add_function('get_waveplates')
        self.add_function('start')
        self.add_function('stop')
        self.add_function('get_value')
        self.add_function('get_noof_reject_cycles')

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
            
            try:
                self.set(p, value=val)
            except:
                pass

    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self._ins_cfg[param] = value

    def get_waveplates(self):
        return self._waveplates

    def get_is_running(self):
        return self._is_running

    def set_is_running(self,val):
        self._is_running = val

    def move(self,waveplate,degrees, quick_scan=False):
        if waveplate not in self._rotation_cfg.keys():
            print 'Unknown waveplate', waveplate
            return False
        if degrees == 0.:
            return


        wp_channel = self._rotation_cfg[waveplate]['channel']
        wp_axis = self._rotation_cfg[waveplate]['axis']
        #print 'boo1', wp_channel
        if self._prev_wp_channel!=wp_channel:
            #print 'boo2', wp_channel
            self._prev_wp_channel = wp_channel
            self._rotator.set_current_channel(wp_channel)
            qt.msleep(1)

        if quick_scan:
            if np.sign(degrees) == +1:
                steps = int(self._rotation_cfg[waveplate]['pos_calib_quick'] * degrees)
            elif np.sign(degrees) == -1:
                steps = int(self._rotation_cfg[waveplate]['neg_calib_quick'] *degrees)
            self._rotator.quick_scan(steps, wp_axis)
        else:
            if np.sign(degrees) == +1:
                steps = int(self._rotation_cfg[waveplate]['pos_calib_precise'] *degrees)
            elif np.sign(degrees) == -1:
                steps = int(self._rotation_cfg[waveplate]['neg_calib_precise'] *degrees)
            self._rotator.precise_scan(steps, wp_axis)
        return True


        ### taken from PID optimizers.
        ### public methods

    def start(self):
        if self.get_is_running():
            print self.get_name() + ': ALREADY RUNNING'
            return False
        self.set_is_running(True)

        ## necessary values for the minimum finding procedure during bell.

        self._current_waveplate = 'zpl_quarter'
        self._current_iteration = 0 #noof steps taken for the current wp
        self._reject_cycles = 0 #number of wp- rejection cycles since last start
        self._prev_v,self._prev_n = self.get_value()

        if self._get_msmt_running_f():
            integration_time = self.get_integration_time_during_msmt()
        else:
            integration_time = self.get_integration_time()

        self._timer = gobject.timeout_add(int(integration_time*1e3), self._update)

    def stop(self):
        self.set_is_running(False)
        return gobject.source_remove(self._timer)

    def get_value(self):
        if self._get_msmt_running_f():
            return self._get_value_f(),self._get_norm_f()
        else:
            return self._get_count_f(), -1

    def _get_rejection(self,cur_v,cur_n):
        if cur_n == -1:
            cur_rejection  = cur_v
        elif (cur_n-self._prev_n)!=0:
            cur_rejection = float((cur_v-self._prev_v))/(cur_n-self._prev_n)/125.*10000
        else:
            cur_rejection = -1

        return cur_rejection   

    def _update(self):

        if not self._is_running:
            return False

        if self._current_iteration == 0:
            self._reject_cycles += 1
            if self._current_waveplate=='zpl_quarter':
                print 'Im trying to go to the minimum of the Quarter waveplate... '
                self._current_direction = self._quarter_direction         
            else:
                print 'Im trying to go to the minimum of the Half waveplate... '
                self._current_direction = self._half_direction      
        
        cur_v,cur_n = self.get_value()
        cur_rejection = self._get_rejection(cur_v,cur_n)
        if cur_rejection <= 0:
            print 'no counts, stopping'
            self.stop()
            return False
        if cur_rejection <= self._good_rejection :
            print 'found a desireable amount of counts. I quit'
            self.stop()
            return False
        
        final_step=False
        if self._current_iteration > 0:
            ### print imrpovement and decide what to do
            improvement = (self._prev_rejection - cur_rejection) / float(cur_rejection)
            print 'previous value was: {:.1f}, new value is: {:.1f}, improvement is: {:.2f}'.format(self._prev_rejection,cur_rejection,improvement)

            if improvement == 0:
                print 'no change in rejection, stopping'
                self.stop()
                return False
            elif improvement > 0:
                print 'Im on the right track:',self._current_direction, '. I go on.'
            elif self._current_iteration == 1:
                self._current_direction  = - self._current_direction 
                print 'Wrong direction.'
            else:
                print 'Getting worse. I go one step back and hope that I found the minimum.'
                final_step = True
                self._current_direction  = -self._current_direction
   
        self.move(self._current_waveplate,self._current_direction*self._step_size)
        
        if final_step:
            if self._current_waveplate=='zpl_quarter':
                self._quarter_direction = -self._current_direction
                self._current_waveplate = 'zpl_half'
                self._current_iteration = -1
            else:
                self._half_direction = -self._current_direction
                self._current_waveplate = 'zpl_quarter'
                self._current_iteration = -1

        self._prev_rejection = cur_rejection
        self._prev_v,self._prev_n = self.get_value()
        self._current_iteration += 1
        
        return True

    def get_noof_reject_cycles(self):
        return self._reject_cycles

    def remove(self):
        self.save_cfg()
        self.stop()
        print 'removing'
        Instrument.remove(self)

    def reload(self):
        self.save_cfg()
        self.stop()
        print 'reloading'
        Instrument.reload(self)


