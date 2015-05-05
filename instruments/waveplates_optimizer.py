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

class waveplates_optimizer(Instrument):

    def __init__(self, name, set_half_control_f=None, set_quarter_control_f=None, get_value_f=None, get_norm_f=None,msmt_helper = 'lt3_measurement_helper' , plot_name=''):
        Instrument.__init__(self, name)        
        if plot_name=='': 
            self._plot_name='optimizer_'+name            
        else:
            self._plot_name =  plot_name

        self._set_half_control_f = set_half_control_f
        self._set_quarter_control_f = set_quarter_control_f
        self._set_control_f = set_quarter_control_f 
        self._get_value_f = get_value_f
        self._get_norm_f=get_norm_f
        self._msmt_helper = msmt_helper
        self._half_direction = 1
        self._quarter_direction = 1
        self._quarter_first = True
        ins_pars  ={'scan_min'          :   {'type':types.FloatType,  'val':0.0,'flags':Instrument.FLAG_GETSET},
                    'scan_max'          :   {'type':types.FloatType,  'val':0.0,'flags':Instrument.FLAG_GETSET},
                    'control_step_size' :   {'type':types.FloatType,  'val':0.0,'flags':Instrument.FLAG_GETSET},
                    'min_value'         :   {'type':types.FloatType,  'val':0.,'flags':Instrument.FLAG_GETSET},
                    'min_norm'          :   {'type':types.FloatType,  'val':200.,'flags':Instrument.FLAG_GETSET},
                    'dwell_time'        :   {'type':types.FloatType,  'val':0.1,'flags':Instrument.FLAG_GETSET}, #s
                    'do_plot'           :   {'type':types.BooleanType,'val':True,'flags':Instrument.FLAG_GETSET},
                    'dwell_after_set'   :   {'type':types.BooleanType,'val':True,'flags':Instrument.FLAG_GETSET},
                    }
        
        instrument_helper.create_get_set(self,ins_pars)
                    
        self.add_function('scan')
        self.add_function('optimize')
        self.add_function('get_value')
        self.add_function('go_one_step')
        self.add_function('optimize_rejection')

    # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()
        print 'creating waveplate optimizer'

    def get_value(self):
        if qt.instruments[self._msmt_helper].get_is_running():
            v1,n1=self._get_value_f(),self._get_norm_f()
            qt.msleep(self._dwell_time)
            v2,n2=self._get_value_f(),self._get_norm_f()
            if (n2-n1)!=0:
                return float((v2-v1))/(n2-n1)/125.*10000
            else:
                return 0.
        else:
            qt.msleep(1)
            counts=0
            averages = 10
            for i in range(0, averages):
                counts = counts + qt.instruments['physical_adwin'].Get_Par(43)/float(averages)
                print 'integrating counts'
                qt.msleep(0.1)
            return counts

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
            
    def scan(self, waveplate='Quarter'):
        if waveplate=='Quarter':
            self._set_control_f = self._set_quarter_control_f
        else:
            self._set_control_f = self._set_half_control_f

        initial_setpoint = 0
        scan_min = self._scan_min
        scan_max = self._scan_max
        if self._control_step_size > 0 :
            self.stepsdown = np.abs( int( scan_min / self._control_step_size))
            self.stepsup = np.abs( int( scan_max / self._control_step_size))
            self.totalsteps = self.stepsdown + self.stepsup
        else:
            self.stepsdown = 0
            self.stepsup = 0
            self.totalsteps = 0

        values_up = np.zeros( self.totalsteps )
        values_down = np.zeros( self.totalsteps )
        current_position = 0

        for stepscount in range( 0, self.stepsdown ): # first, go to the scan min
            self._set_control_f( - self._control_step_size ) 

        for i in range( 0, self.totalsteps ): # then go to the max
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                self._set_control_f(initial_setpoint)
                print 'Aborting scan!'
                break
            self._set_control_f( self._control_step_size )
            if self.get_dwell_after_set():
                qt.msleep(self._dwell_time)
            values_up[i]=self.get_value()

        for i in range( 0, self.totalsteps ): # then go back to the min
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                self._set_control_f(initial_setpoint)
                print 'Aborting scan!'
                break
            self._set_control_f( - self._control_step_size )

            if self.get_dwell_after_set():
                qt.msleep(self._dwell_time)
            values_down[self.totalsteps-i-1]=self.get_value()
        
        valid_i_down = np.where(values_down>self._min_value)
        print 'valid i down ', valid_i_down
        valid_i_up = np.where(values_up>self._min_value)
        print 'valid i up ', valid_i_up
        
        if self.get_do_plot():
            xaxis = np.arange( 0, self.totalsteps, 1 )
            p_up = plt.plot( xaxis[valid_i_up], values_up[valid_i_up] ,'O', name=self._plot_name, clear=True)
            plt.plot( xaxis[valid_i_down], values_down[valid_i_down],'O', name=self._plot_name)
            p_up.update()
        
        return (xaxis, values_up[xaxis], values_down[xaxis])
    
    def optimize(self, waveplate='Quarter'):
        if waveplate=='Quarter':
            print 'Quarter'
            self._set_control_f = self._set_quarter_control_f
        else:
            print 'Half'
            self._set_control_f = self._set_half_control_f
        
        x, y_up, y_down = self.scan(waveplate)
        success = False
        #print 'x, y_up, y_down ',x,y_up,y_down
            
        up_fit_A, up_fit_x0 = self._fit(x,y_up)
        down_fit_A, down_fit_x0 = self._fit(x,y_down)
        if up_fit_x0!= None and down_fit_x0 != None and up_fit_A > 0 and down_fit_A > 0:
            print 'Both fits succeeded!'
            steps_to_go = int(np.round(down_fit_x0 / np.sqrt(up_fit_A/down_fit_A)))
            print 'moving ', (-self.stepsdown+steps_to_go)*self._control_step_size, 'degrees from initial value'
            for stepscount in range( 0,steps_to_go): # go back up initial number of steps
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                    self._set_control_f(initial_setpoint)
                    print 'Aborting scan!'
                    break
                self._set_control_f( self.get_control_step_size() )     

        else:
            print 'Fits failed... I go to the minimum and hope for the best.'
            steps_to_go = int(np.round(x[np.argmin(y_down)])) 
            print 'moving ', (-self.stepsdown+steps_to_go)*self._control_step_size, 'degrees from initial value'
            for stepscount in range( 0, steps_to_go): # go back up initial number of steps
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                    self._set_control_f(initial_setpoint)
                    print 'Aborting scan!'
                    break
                self._set_control_f( self.get_control_step_size() ) 

        return success 

    def go_one_step(self, stepsize):
        self._set_control_f( stepsize )
        if self.get_dwell_after_set():
            qt.msleep(self._dwell_time)


    def go_to_min(self, waveplate='Quarter', initial_direction = -1):
        if waveplate=='Quarter':
            print 'Im trying to go to the minimum of the Quarter waveplate... '
            self._set_control_f = self._set_quarter_control_f
        else:
            print 'Im trying to go to the minimum of the Half waveplate... '
            self._set_control_f = self._set_half_control_f

        previous_value = self.get_value()
        first_run = True
        success = False
        directions = np.array([1,1,-1])
        direction_steps_taken= np.zeros(3)
        current_direction  = initial_direction
        new_value = previous_value
        
        while True:
            #print 'current direction is: ', current_direction 
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                print 'You pressed the emergency button. I stop here.'
                success=True
                break
            self.go_one_step( current_direction  * self._control_step_size)
            direction_steps_taken[current_direction]+=1
            new_value = self.get_value()
            if new_value <= 0 or new_value == previous_value:
                print 'no valid SP count value. I quit.'
                break
            improvement = (previous_value - new_value) / float(new_value)
            print 'previous value was: {:.1f}, new value is: {:.1f}, improvement is: {:.2f}'.format(previous_value,new_value,improvement)
            if new_value < self.get_min_value():
                print 'Value good enough'
                success = True
                break
            elif improvement > 0:
                print 'Im on the right track:',current_direction, '. I go on.'
            elif first_run:
                current_direction  = - current_direction  
                print 'Wrong direction.'
            else:
                print 'Getting worse. I go one step back and hope that I found the minimum.'
                self.go_one_step( - current_direction  * self._control_step_size)
                success = True
                break
            previous_value = new_value
            first_run = False
        return success , directions,  direction_steps_taken, new_value

    def optimize_rejection(self):
        while True:
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                print 'Aborting the rejection optimization!'
                break
            if self._quarter_first:
                quarter_success, directions, quarter_steps, quarter_value = self.go_to_min('Quarter',self._quarter_direction)
                if quarter_value > self.get_min_value():
                    half_success, directions, half_steps, half_value  = self.go_to_min('Half', self._half_direction)
                else:
                    print 'Quarter optimisation did the job'
                    self._quarter_first = True
                    self._quarter_direction = directions[np.argmax(quarter_steps)]
                    half_success = False
            else:
                half_success, directions, half_steps, half_value   = self.go_to_min('Half', self._half_direction)
                if half_value > self.get_min_value():
                    quarter_success, directions, quarter_steps, quarter_value = self.go_to_min('Quarter',self._quarter_direction)
                else:
                    print 'Half optimisation did the job'
                    self._quarter_first = False
                    self._half_direction = directions[np.argmax(half_steps)]
                    quarter_success = False

            if quarter_success and half_success:
                self._quarter_direction = directions[np.argmax(quarter_steps)]
                self._half_direction = directions[np.argmax(half_steps)]
                #self._quarter_first = not(self._quarter_first) or (np.max(quarter_steps) > np.max(half_steps)) #next time let's do the other waveplate first.
                print 'next optimisation settings: quarter first: ', self._quarter_first,'quarter direction: ', self._quarter_direction, 'half direction: ', self._half_direction

            if qt.instruments[self._msmt_helper].get_is_running():
                #During Bell, the Bell optimizor will decide what to do.
                break 
            elif self.get_value() < 100: 
                #Otherwise, we continue until we reach dark count level or the user aborts the operation.
                break

    def _fit(self,X,Y):
        #Fit parabole: o + A * (x-c)**2  ['g_o', 'g_A', 'g_c']
        guess_o = np.min(Y)
        guess_A = ( (np.max(Y) - np.min(Y)) / (X[np.argmax(Y)]-X[np.argmin(Y)])**2)
        guess_c = X[np.argmin(Y)]
        print 'fit guess ', guess_A, guess_c, guess_o
        fitres = fit.fit1d(X, Y, common.fit_parabole, guess_o, guess_A, guess_c, len(X), do_print = False, ret = True)

        if fitres['success'] != False:
            p1 = fitres['params_dict']
            print p1
            fd = fitres['fitfunc'](X)
            p=plt.plot(name=self._plot_name)
            p.add(X, fd, '-b')   
        else:
            print '\tCould not fit curve!'
            return None, None
        return p1['A'],p1['c']