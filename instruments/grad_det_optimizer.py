import qt
import numpy as np
from instrument import Instrument
import plot as plt
import types
import os
import msvcrt
from lib import config
from analysis.lib.fitting import fit, common
import instrument_helper
from measurement.instruments.simple_optimizer import simple_optimizer

class grad_det_optimizer(simple_optimizer):

    def __init__(self, name, get_control_f=None, set_control_f=None, get_value_f=None, get_norm_f=None, plot_name=''):
        Instrument.__init__(self, name)        
        if plot_name=='': 
            plot_name='optimizer_'+name            
               
        self._get_control_f=get_control_f
        self._set_control_f=set_control_f
        self._get_value_f=get_value_f
        self._get_norm_f=get_norm_f
        
        ins_pars  ={'scan_min'          :   {'type':types.FloatType,  'val':0.0,'flags':Instrument.FLAG_GETSET},
                    'scan_max'          :   {'type':types.FloatType,  'val':0.0,'flags':Instrument.FLAG_GETSET},
                    'control_step_size' :   {'type':types.FloatType,  'val':0.0,'flags':Instrument.FLAG_GETSET},
                    'min_value'         :   {'type':types.FloatType,  'val':2.,'flags':Instrument.FLAG_GETSET},
                    'min_norm'          :   {'type':types.FloatType,  'val':200.,'flags':Instrument.FLAG_GETSET},
                    'dwell_time'        :   {'type':types.FloatType,  'val':0.1,'flags':Instrument.FLAG_GETSET}, #s
                    'wait_time'         :   {'type':types.FloatType,  'val':10,'flags':Instrument.FLAG_GETSET}, #s
                    'order_index'       :   {'type':types.IntType,    'val':1,'flags':Instrument.FLAG_GETSET},
                    'do_plot'           :   {'type':types.BooleanType,'val':True,'flags':Instrument.FLAG_GETSET},
                    'do_fit'            :   {'type':types.BooleanType,'val':False,'flags':Instrument.FLAG_GETSET},
                    'dwell_after_set'   :   {'type':types.BooleanType,'val':True,'flags':Instrument.FLAG_GETSET},
                    'plot_name'         :   {'type':types.StringType, 'val':plot_name,'flags':Instrument.FLAG_GETSET},
                    'variance'          :   {'type':types.FloatType,  'val':0.,'flags':Instrument.FLAG_GETSET},
                    'last_max'          :   {'type':types.FloatType,  'val':0.,'flags':Instrument.FLAG_GETSET},
                    'good_value'        :   {'type':types.FloatType,  'val':100,'flags':Instrument.FLAG_GETSET},
                    'threshold_for_decreasing' :   {'type':types.FloatType,  'val':0.7,'flags':Instrument.FLAG_GETSET},
                    'threshold_for_past_peak'  :   {'type':types.FloatType,  'val':0.5,'flags':Instrument.FLAG_GETSET},
                    'min_peak_value'      :   {'type':types.FloatType,  'val':3.0,'flags':Instrument.FLAG_GETSET},
                    'smoothing_N'       :   {'type':types.IntType,  'val':4,'flags':Instrument.FLAG_GETSET}
                    }
        
        instrument_helper.create_get_set(self,ins_pars)
                    
        self.add_function('scan')
        self.add_function('optimize')
        self.add_function('get_value')
        
    # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()
    
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

    def scan(self):
          
        initial_setpoint = self._get_control_f()
        scan_min = initial_setpoint + self._scan_min
        scan_max = initial_setpoint + self._scan_max
        
        #print 'initial_setpoint {:.2f},scan_min {:.2f},scan_max {:.2f}, steps {}'.format(initial_setpoint,scan_min,scan_max, steps)


        # First scan negative. See if is going up or down (or unclear)
        # If going down, switch to positive
        # If going up, keep going until goes down then break
        # If unclear, go to edge of scan range and return
        # Next do same for positive

        finished = 0

        ##########################################
        # Start with negative

        print "Scanning negative"

        steps=int((initial_setpoint - scan_min) / self._control_step_size)
        udrange_temp = np.linspace(initial_setpoint,scan_min,steps)
        
        values_temp=np.zeros(len(udrange_temp))
        true_udrange_temp=np.zeros(len(udrange_temp))

        smoothed_values = np.zeros(len(udrange_temp)-self.get_smoothing_N()+1)
        max_value = 0
        max_frac_change = 0

        for i,sp in enumerate(udrange_temp):
            print i
            
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                self._set_control_f(initial_setpoint)
                break
            #print 'sp',sp
            self._set_control_f(sp)
            if self.get_dwell_after_set():
                qt.msleep(self._dwell_time)
            true_udrange_temp[i]=self._get_control_f()
            values_temp[i]=self.get_value()

            # First of all, if above the threshold, thats us happy.
            if values_temp[i] > self.get_good_value():
                'Found good value!'
                finished = 1

                break

            if i >= (self.get_smoothing_N()-1): # Need to build up some values at start before considering whether decreasing or not
 
                smoothed_index = i-(self.get_smoothing_N()-1)

                smoothed_values[smoothed_index] = np.mean(values_temp[smoothed_index:(i+1)]) # very simple smoothing filter
                
                fractional_change = smoothed_values[smoothed_index]/smoothed_values[0] # fractional change from first smoothed value

                if values_temp[i] > max_value: # Track the max value reached so far
                    max_value = values_temp[i]
                    max_frac_change = fractional_change

                # Try and measure the 'noise' in the signal
                if smoothed_index > 0:
                    diff_smoothed = (smoothed_values[0:(smoothed_index-1)]-smoothed_values[1:smoothed_index])/smoothed_values[0]
                else:
                    diff_smoothed = 0

                # If nothing is changing, noise in diff might be high
                not_too_noisy_to_tell = np.stdev(diff_smoothed) < (1- self.get_threshold_for_decreasing())

                if fractional_change < self.get_threshold_for_decreasing() and not_too_noisy_to_tell : # Therefore must be decreasing from start
                    print "Decreasing in this direction!" 

                    break

                if (max_value > self.get_min_peak_value()) and (fractional_change < max_frac_change*self.get_threshold_for_past_peak()): # Must have gone past peak
                    print "Gone past peak!" 
                    finished = 1
                    
                    break

        if finished == 0: # If not finished yet
            
            print "Scanning positive"

            # Store measured values so far
            true_udrange = true_udrange_temp[0:i]
            values = values_temp[0:i]

            # Start by going back to start
            self._set_control_f(initial_setpoint)
            if self.get_dwell_after_set():
                for x in range(i+4):
                    qt.msleep(self._dwell_time) # Wait for a length of time determined by how far we got
                    if self._get_control_f() > initial_setpoint + 0.05* self._scan_min:
                        break
                    print x


            ##########################################
            # Do positive

            steps=int((scan_max - initial_setpoint) / self._control_step_size)
            udrange_temp = np.linspace(initial_setpoint,scan_max,steps)

            values_temp=np.zeros(len(udrange_temp))
            true_udrange_temp=np.zeros(len(udrange_temp))

            smoothed_values = np.zeros(len(udrange_temp)-self.get_smoothing_N()+1)
            max_value = 0
            max_frac_change = 0

            finished = 0

            for i,sp in enumerate(udrange_temp):
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                    self._set_control_f(initial_setpoint)
                    break
                #print 'sp',sp
                self._set_control_f(sp)
                if self.get_dwell_after_set():
                    qt.msleep(self._dwell_time)
                true_udrange_temp[i]=self._get_control_f()
                values_temp[i]=self.get_value()

                # First of all, if above the threshold, thats us happy.
                if values_temp[i] > self.get_good_value():
                    'Found good value!'
                    finished = 1

                    break

                if i >= (self.get_smoothing_N()-1): # Need to build up some values at start before considering whether decreasing or not
     
                    smoothed_index = i-(self.get_smoothing_N()-1)

                    smoothed_values[smoothed_index] = np.mean(values_temp[smoothed_index:(i+1)]) # very simple smoothing filter
                    
                    fractional_change = smoothed_values[smoothed_index]/smoothed_values[0] # fractional change from first smoothed value

                    if values_temp[i] > max_value: # Track the max value reached so far
                        max_value = values_temp[i]
                        max_frac_change = fractional_change

                    # Try and measure the 'noise' in the signal
                    if smoothed_index > 0:
                        diff_smoothed = (smoothed_values[0:(smoothed_index-1)]-smoothed_values[1:smoothed_index])/smoothed_values[0]
                    else:
                        diff_smoothed = 0

                    # If nothing is changing, noise in diff might be high
                    not_too_noisy_to_tell = np.stdev(diff_smoothed) < (1- self.get_threshold_for_decreasing())

                    #basically_dead = smoothed_values[smoothed_index] < self.get_dead_value()

                    if fractional_change < self.get_threshold_for_decreasing() and not_too_noisy_to_tell : # Therefore must be decreasing from start
                        print "Decreasing in this direction!" 

                        break

                    if (max_value > self.get_min_peak_value()) and (fractional_change < max_frac_change*self.get_threshold_for_past_peak()): # Must have gone past peak
                        print "Gone past peak!" 
                        finished = 1
                        
                        break

            if finished == 0:
                # If neccessary, end by going back to start
                self._set_control_f(initial_setpoint)
                if self.get_dwell_after_set():
                    for x in range(i+4):
                        qt.msleep(self._dwell_time) # Wait for a length of time determined by how far we got
                        if self._get_control_f() > initial_setpoint + 0.05* self._scan_min:
                            break
                        print x

            # Add on extra values
            np.append(true_udrange, true_udrange_temp[0:i])
            np.append(values, values_temp[0:i])

        else:
            true_udrange = true_udrange_temp[0:i]
            values = values_temp[0:i]

        valid_i=np.where(values>self._min_value)
        print true_udrange
        print values
        true_udrange = true_udrange[valid_i]
        values = values[valid_i]
        print true_udrange
        print values

        if self.get_do_plot():
            p=plt.plot(name=self._plot_name)
            p.clear()
            plt.plot(true_udrange,values,'O',name=self._plot_name)

        return (true_udrange,values)
    
 