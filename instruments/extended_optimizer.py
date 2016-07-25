import qt
import numpy as np
from instrument import Instrument
import plot as plt
import time
import types
import os
import msvcrt
from lib import config
from analysis.lib.fitting import fit, common
import instrument_helper

class extended_optimizer(Instrument):

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
        initial_time = time.time();
        scan_min = initial_setpoint + self._scan_min/2.
        scan_max = initial_setpoint + self._scan_max/2.
        steps=int((scan_max - scan_min) / self._control_step_size)
        #print 'initial_setpoint {:.2f},scan_min {:.2f},scan_max {:.2f}, steps {}'.format(initial_setpoint,scan_min,scan_max, steps)
        udrange=np.append(np.linspace(initial_setpoint,scan_min+self._control_step_size,int(steps/2.)),
                np.linspace(scan_min, scan_max, steps))
        udrange=np.append(udrange,np.linspace(scan_max-self._control_step_size,initial_setpoint,int(steps/2.)))
        #print udrange #XXXXXX
        values=np.array([])#np.zeros(len(udrange))
        true_udrange=np.array([])#np.zeros(len(udrange))
        time_axis = np.array([]);
        finished = 0
        for i,sp in enumerate(udrange):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                self._set_control_f(initial_setpoint)
                break
            #print 'sp',sp
            self._set_control_f(sp)

            if self.get_dwell_after_set():

                st = time.time()
                if self._dwell_time > 0.04:
                    while (time.time() - st <= self._dwell_time) and (finished == 0):
                        true_udrange = np.append(true_udrange,self._get_control_f())
                        values = np.append(values,self.get_value_timed(0.02))
                        time_axis = np.append(time_axis, time.time() - initial_time);
                        if values[-1] > self.get_good_value():
                            finished = 1
                            print 'Finished, current red:', sp, 'current white:', self._get_control_f(), 'last measured f: ', true_udrange[-1]
                            break;
            else:
                
                qt.msleep(self._dwell_time)

                true_udrange = np.append(true_udrange,self._get_control_f())
                values = np.append(values,self.get_value())

                if values[-1] > self.get_good_value():
                    finished = 1
                    
            if finished == 1: 
                print 'Found good value during scan, at', values[-1]/self.get_good_value(), 'times threshold at frequency', true_udrange[-1];
                break

        valid_i=np.where(values>self._min_value)

        if self.get_do_plot(): 
            # Time scan plot
            p1 = plt.plot(name=(self._plot_name+'_time'))
            p1.clear()
            plt.plot(time_axis,true_udrange,'O',name=(self._plot_name+'_time'))            
            plt.plot(time_axis,values,'O',name=(self._plot_name+'_time'))          
            plt.plot(np.arange(len(udrange))*self._dwell_time, udrange,'O',name=(self._plot_name+'_time'))             
            # Frequency scan plot
            p2 = plt.plot(name=(self._plot_name+'_frequency'))
            p2.clear()
            plt.plot(true_udrange,values,'O', name=(self._plot_name+'_frequency'))   
        
        return (true_udrange,values)
    
    def optimize_OLD(self):
        value_before=self.get_value()
        x,y=self.scan()
        if y[-1] > self.get_good_value():
            success = True
        else:
            success = False
        #print 'x,y',x,y
        if len(y)>0 and not success:
            maxx=x[np.argmax(y)]
            if self.get_do_fit() and len(x)>5:
                fit_maxx=self._fit(x,y)
                if fit_maxx != None and fit_maxx > np.min(x) and fit_maxx < np.max(x):
                    print 'fit succes'
                    maxx = fit_maxx
            variance=np.sum(np.abs(np.ediff1d(y)))
            self.set_variance(variance)
            maxy=np.max(y)
            self.set_last_max(maxy)
            if maxy>value_before:
                print 'No value higher than threshold found during scan. Best value of scan,', maxy/self.get_good_value(), 'times theshold at frequency', maxx, ', is better than initial value', value_before, 'so go there.'
                self._set_control_f(maxx)
                success = True
            else:
                print 'No value higher than threshold found during scan. Best value of scan,', maxy/self.get_good_value(), 'times theshold at frequency', maxx, ', is worse than initial value', value_before,'so go back.'
        return success 
            
    def get_value(self):
        v1,n1=self._get_value_f(),self._get_norm_f()
        qt.msleep(self._dwell_time)
        v2,n2=self._get_value_f(),self._get_norm_f()
        if (n2-n1)!=0:
            return float((v2-v1))/(n2-n1)
        else:
            return 0.

    def get_value_timed(self,dwell):
        v1,n1=self._get_value_f(),self._get_norm_f()
        qt.msleep(dwell)
        v2,n2=self._get_value_f(),self._get_norm_f()
        if (n2-n1)!=0:
            return float((v2-v1))/(n2-n1)
        else:
            return 0.

    def get_value_ext(self,dwell,source):
        # Set parameters
        self._get_counts_yellow = lambda: qt.instruments['physical_adwin'].Get_Par(76);
        self._get_counts_gate = lambda: qt.instruments['physical_adwin'].Get_Par(70);
        self._get_attemps_yellow = lambda: qt.instruments['physical_adwin'].Get_Par(71);
        self._get_attemps_gate = lambda: qt.instruments['physical_adwin'].Get_Par(72);

        if source == 0: # gate
            get_counts = self._get_counts_gate;
            get_attemps = self._get_attemps_gate;
        elif source == 1: # yellow
            get_counts = self._get_counts_yellow;
            get_attemps = self._get_attemps_yellow;
        elif source == 2: # newfocus (= gate)
            get_counts = self._get_counts_gate;
            get_attemps = self._get_attemps_gate;

        v1,n1=get_counts(), get_attemps();
        qt.msleep(dwell)
        v2,n2=get_counts(), get_attemps();
        if (n2-n1)!=0:
            return float((v2-v1))/(n2-n1)
        else:
            return 0.  

    def optimize(self):  
        # Set parameters
        self._get_freq_yellow = lambda: qt.instruments['physical_adwin'].Get_FPar(42)
        self._set_freq_yellow = lambda x: qt.instruments['physical_adwin'].Set_FPar(52,x)
        self._opt_yellow_scan_min = self._scan_min;
        self._opt_yellow_scan_max = self._scan_max;
        self._opt_yellow_step = self._control_step_size;
        self._opt_yellow_good = self.get_good_value();

        self._get_freq_gate = lambda: qt.instruments['adwin'].get_dac_voltage('gate')
        self._set_freq_gate = lambda x: qt.instruments['adwin'].set_dac_voltage(('gate',x))
        self._opt_gate_scan_min = -0.1;
        self._opt_gate_scan_max = 0.1;
        self._opt_gate_step = 0.01;
        self._opt_gate_good = 15;       

        self._data_time = 0.04;

        # Initialize
        initial_time = time.time();        

        # Create yellow sweep            
        yellow_start = self._get_freq_yellow();
        scan_min = yellow_start + self._opt_yellow_scan_min/2.
        scan_max = yellow_start + self._opt_yellow_scan_max/2.
        steps=int((scan_max - scan_min) / self._opt_yellow_step)
        yellow_sweep=np.append(np.linspace(yellow_start,scan_min+self._opt_yellow_step,int(steps/2.)),
                np.linspace(scan_min, scan_max, steps))
        yellow_sweep=np.append(yellow_sweep,np.linspace(scan_max-self._opt_yellow_step,yellow_start,int(steps/2.)))

        # Create gate sweep
        gate_start = self._get_freq_gate();
        scan_min = gate_start + self._opt_gate_scan_min/2.
        scan_max = gate_start + self._opt_gate_scan_max/2.
        steps=int((scan_max - scan_min) / self._opt_gate_step)
        gate_sweep=np.append(np.linspace(gate_start,scan_min+self._opt_gate_step,int(steps/2.)),
                np.linspace(scan_min, scan_max, steps))
        gate_sweep=np.append(gate_sweep,np.linspace(scan_max-self._opt_gate_step,gate_start,int(steps/2.))) 

        # Initialize data arrays
        yellow_x = np.array([]);
        yellow_y = np.array([]);
        yellow_t = np.array([]);
        gate_x = np.array([]);
        gate_y = np.array([]);
        gate_t = np.array([]);

        finishedYellow = False;
        finishedGate = False;

        # Start yellow sweep
        currentYellowStep = 0;
        currentGateStep = 0;
        currentTime = time.time();
        currentYellowFreq = yellow_start;
        currentGateFreq = gate_start;
        yellowStepTime = time.time();
        gateStepTime = time.time();

        # Each for iteration is one sweep step (dwell)
        for currentYellowStep,currentYellowFreq in enumerate(yellow_sweep):
            # Set current yellow frequency to yellow sweep step            
            self._set_freq_yellow(currentYellowFreq)
            yellowStepTime = time.time()   
            # Debug
            print 'Starting yellow iteration', currentYellowStep, 'out of', len(yellow_sweep), 'at frequency', currentYellowFreq;           

            # Each while iteration is one yellow sweep substep
            while (time.time() - yellowStepTime <= self._dwell_time) and not finishedYellow:
                # Check if we are still in NV0: more than 1 zero in last 10 vals on gate
                if (sum(gate_y[-min(10,len(gate_y)):]<0.0001) > 1 or len(gate_y) < 10):  
                    # Debug
                    print 'Currently in NV0, checking yellow'

                    # Get yellow val
                    yellow_x = np.append(yellow_x,self._get_freq_yellow())
                    yellow_y = np.append(yellow_y,self.get_value_ext(self._data_time,1))
                    yellow_t = np.append(yellow_t, time.time() - initial_time);
                    # Get gate val
                    gate_x = np.append(gate_x,self._get_freq_gate())
                    gate_y = np.append(gate_y,self.get_value_ext(self._data_time,0))
                    gate_t = np.append(gate_t, time.time() - initial_time);

                    if yellow_y[-1] > self._opt_yellow_good:
                        finishedYellow = True
                        break;
                else: # We are in NV-. Check if gate is good
                    # Debug
                    print 'Currently in NV-'
                    print 'NV-, gate good:', gate_y[-min(5,len(gate_y)):], np.mean(gate_y[-min(5,len(gate_y)):])>self._opt_gate_good

                    if np.mean(gate_y[-min(5,len(gate_y)):])>self._opt_gate_good or finishedGate: # Gate is good. Continue yellow
                        # Debug
                        print 'Currently in NV-, but gate is OK, so go on checking yellow'

                        # Get yellow val
                        yellow_x = np.append(yellow_x,self._get_freq_yellow())
                        yellow_y = np.append(yellow_y,self.get_value_ext(self._data_time,1))
                        yellow_t = np.append(yellow_t, time.time() - initial_time);
                        # Get gate val
                        gate_x = np.append(gate_x,self._get_freq_gate())
                        gate_y = np.append(gate_y,self.get_value_ext(self._data_time,0))
                        gate_t = np.append(gate_t, time.time() - initial_time);

                        if yellow_y[-1] > self._opt_yellow_good:
                            self._set_freq_yellow(yellow_x[-1])
                            finishedYellow = True
                            break;
                    else: # Gate is bad. Optimize gate where we ended last time
                        # Debug
                        print 'Currently in NV-, gate is bad, optimize gate'
                        print 'NV-, gate bad:', currentGateStep < len(gate_sweep),finishedGate,gate_y[-min(10,len(gate_y)):],sum(gate_y[-min(10,len(gate_y)):]<0.0001) <= 1

                        while currentGateStep < len(gate_sweep) and not finishedGate and (sum(gate_y[-min(10,len(gate_y)):]<0.0001) <= 1):                           
                            # Set current gate frequency to gate sweep step
                            currentGateFreq = gate_sweep[currentGateStep];
                            self._set_freq_gate(currentGateFreq);
                            gateStepTime = time.time();

                            # Debug
                            print 'Currently in NV0, optimizing gate. Starting iteration', currentGateStep, 'out of', len(gate_sweep), 'at frequency', currentGateFreq;                           

                            while (time.time() - gateStepTime <= self._dwell_time) and not finishedGate and (sum(gate_y[-min(10,len(gate_y)):]<0.0001) <= 1):
                                # Get yellow val
                                yellow_x = np.append(yellow_x,self._get_freq_yellow())
                                yellow_y = np.append(yellow_y,self.get_value_ext(self._data_time,1))
                                yellow_t = np.append(yellow_t, time.time() - initial_time);
                                # Get gate val
                                gate_x = np.append(gate_x,self._get_freq_gate())
                                gate_y = np.append(gate_y,self.get_value_ext(self._data_time,0))
                                gate_t = np.append(gate_t, time.time() - initial_time);

                                if gate_y[-1] > self._opt_gate_good:
                                    self._set_freq_gate(gate_x[-1])
                                    finishedGate = True
                                    break; 
                            currentGateStep = currentGateStep + 1; 

            if finishedYellow:
                break;                                                            

        if finishedGate:
            print 'Gate: good value during scan, at', gate_y[-1]/self._opt_gate_good, 'times threshold at frequency', gate_x[-1];
        else:
            self._set_freq_gate(gate_x[np.argmax(gate_y)]);
            print 'Gate: scan failed, set to best value ', max(gate_y), 'at frequency', gate_x[np.argmax(gate_y)];

        if finishedYellow:
            print 'Yellow: good value during scan, at', yellow_y[-1]/self._opt_yellow_good, 'times threshold at frequency', yellow_x[-1];
        else:
            self._set_freq_yellow(yellow_x[np.argmax(yellow_y)]);
            print 'Yellow: scan failed, set to best value ', max(yellow_y), 'at frequency', gate_x[np.argmax(yellow_y)];

        if self.get_do_plot(): 
            # Sweeps plot
            p1 = plt.plot(name=(self._plot_name+'_sweeps'))
            p1.clear()
            print 'Start plotting sweep'
            #plt.subplot(211)
            plt.plot(np.arange(len(yellow_sweep))*self._dwell_time,yellow_sweep,'O',name=(self._plot_name+'_sweeps'))     
            #plt.subplot(212)                   
            plt.plot(np.arange(len(gate_sweep))*self._dwell_time,gate_sweep,'O',name=(self._plot_name+'_sweeps'))            
            print 'Finished plotting sweep'
            # Yellow plot
            p2 = plt.plot(name=(self._plot_name+'_yellow'))
            p2.clear()
            print 'Start plotting yellow'
            #plt.subplot(211)
            plt.plot(yellow_t,yellow_x,'O',name=(self._plot_name+'_yellow')) 
            plt.plot(np.arange(len(yellow_sweep))*self._dwell_time, yellow_sweep,'O',name=(self._plot_name+'_yellow'))             
            #plt.subplot(212)
            plt.plot(yellow_t,yellow_y,'O',name=(self._plot_name+'_yellow'))  
            print 'Finished plotting yellow'            
            # Gate plot
            p3 = plt.plot(name=(self._plot_name+'_gate'))
            p3.clear()
            print 'Start plotting gate'            
            #plt.subplot(211)
            plt.plot(gate_t,gate_x,'O',name=(self._plot_name+'_gate')) 
            plt.plot(np.arange(len(gate_sweep))*self._dwell_time, gate_sweep,'O',name=(self._plot_name+'_gate'))             
            #plt.subplot(212)
            plt.plot(gate_t,gate_y,'O',name=(self._plot_name+'_gate'))             
            print 'Finished plotting gate'            

    def _fit(self,X,Y):
        #fit_gauss(g_a, g_A, g_x0, g_sigma)
        fitres = fit.fit1d(X, Y, common.fit_gauss, 
                np.average(Y)*0.5,np.max(Y)-np.average(Y)*0.5,X[np.argmax(Y)], (X[-1]-X[0])/2., do_print = False, ret = True)

        if fitres['success'] != False:
            p1 = fitres['params_dict']
            fd = fitres['fitfunc'](X)
            if self.get_do_plot():
                p=plt.plot(name=self._plot_name)
                p.add(X, fd, '-b')   
        else:
            print '\tCould not fit curve!'
            return None
        return p1['x0']