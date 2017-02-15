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



class auto_optimizer_2(Instrument):

    def __init__(self, name, get_freq_yellow = None, set_freq_yellow = None, get_counts_yellow = None, get_attemps_yellow = None,
                             get_freq_gate = None, set_freq_gate = None, get_counts_gate = None, get_attemps_gate = None,
                             get_freq_newfocus = None, set_freq_newfocus = None, plot_name=''):
        Instrument.__init__(self, name)        
        if plot_name=='': 
            plot_name='optimizer_'+name            
               
        self._get_freq_yellow=get_freq_yellow
        self._set_freq_yellow=set_freq_yellow
        self._get_counts_yellow=get_counts_yellow
        self._get_attemps_yellow=get_attemps_yellow  

        self._get_freq_gate=get_freq_gate
        self._set_freq_gate=set_freq_gate
        self._get_counts_gate=get_counts_gate
        self._get_attemps_gate=get_attemps_gate       

        self._get_freq_newfocus=get_freq_newfocus
        self._set_freq_newfocus=set_freq_newfocus 

        self._yellow_went_up = False;
        self._gate_went_up = False;  
        self._nf_went_up = False

        self._newfocus_iterations = 0;
        self._gate_iterations = 0;
        self._yellow_iterations = 0; 
       
        self.adwin = qt.get_instruments()['adwin']

        ins_pars  ={'do_plot'               :   {'type':types.BooleanType,'val':True,'flags':Instrument.FLAG_GETSET},
                    'plot_name'             :   {'type':types.StringType, 'val':plot_name,'flags':Instrument.FLAG_GETSET},
                    'external_break'        :   {'type':types.BooleanType,'val':False,'flags':Instrument.FLAG_GETSET},                                                            
 
                    'detect_cycles'         :   {'type':types.IntType,    'val':10,'flags':Instrument.FLAG_GETSET},
                    'data_time'             :   {'type':types.FloatType,  'val':0.05,'flags':Instrument.FLAG_GETSET},
                    'flow_sleep'            :   {'type':types.FloatType,  'val':0.1,'flags':Instrument.FLAG_GETSET},                    

                    'yellow_delay'          :   {'type':types.FloatType,  'val':0.4,'flags':Instrument.FLAG_GETSET},                                        
                    'NV0_zeros'             :   {'type':types.IntType,    'val':4,'flags':Instrument.FLAG_GETSET}, 

                    'check_gate_threshold'  :   {'type':types.FloatType,  'val':5,'flags':Instrument.FLAG_GETSET},                    
                    'check_yellow_threshold':   {'type':types.FloatType,  'val':10,'flags':Instrument.FLAG_GETSET},                    
                    'check_newfocus_zeros'  :   {'type':types.IntType,    'val':3,'flags':Instrument.FLAG_GETSET},

                    'opt_gate_good'         :   {'type':types.FloatType,  'val':15,'flags':Instrument.FLAG_GETSET},                    
                    'opt_yellow_good'       :   {'type':types.FloatType,  'val':10,'flags':Instrument.FLAG_GETSET},                    
                    'opt_nf_good'           :   {'type':types.FloatType,  'val':25,'flags':Instrument.FLAG_GETSET},                                        
                    
                    'opt_gate_scan_min'     :   {'type':types.FloatType,  'val':-0.1,'flags':Instrument.FLAG_GETSET},                    
                    'opt_yellow_scan_min'   :   {'type':types.FloatType,  'val':-0.8,'flags':Instrument.FLAG_GETSET},                    
                    'opt_nf_scan_min'       :   {'type':types.FloatType,  'val':-0.5,'flags':Instrument.FLAG_GETSET},                                        

                    'opt_gate_scan_max'     :   {'type':types.FloatType,  'val':0.1,'flags':Instrument.FLAG_GETSET},                    
                    'opt_yellow_scan_max'   :   {'type':types.FloatType,  'val':0.8,'flags':Instrument.FLAG_GETSET},                    
                    'opt_nf_scan_max'       :   {'type':types.FloatType,  'val':0.5,'flags':Instrument.FLAG_GETSET},                                        
                    
                    'opt_gate_dwell'        :   {'type':types.FloatType,  'val':0.2,'flags':Instrument.FLAG_GETSET},                    
                    'opt_yellow_dwell'      :   {'type':types.FloatType,  'val':0.3,'flags':Instrument.FLAG_GETSET},                    
                    'opt_nf_dwell'          :   {'type':types.FloatType,  'val':0.1,'flags':Instrument.FLAG_GETSET},                                        

                    'opt_gate_step'         :   {'type':types.FloatType,  'val':0.01,'flags':Instrument.FLAG_GETSET},                    
                    'opt_yellow_step'       :   {'type':types.FloatType,  'val':0.04,'flags':Instrument.FLAG_GETSET},                    
                    'opt_nf_step'           :   {'type':types.FloatType,  'val':0.02,'flags':Instrument.FLAG_GETSET},                                        

                    'max_gate_iterations'   :   {'type':types.IntType,    'val':5,'flags':Instrument.FLAG_GETSET},                    
                    'max_yellow_iterations' :   {'type':types.IntType,    'val':5,'flags':Instrument.FLAG_GETSET},                    
                    'max_nf_iterations'     :   {'type':types.IntType,    'val':1,'flags':Instrument.FLAG_GETSET},                                        
                    }
        
        instrument_helper.create_get_set(self,ins_pars)

        self.add_parameter('is_pidgate_running',type=types.BooleanType, flags = Instrument.FLAG_GETSET)
        self.add_parameter('is_yellowfrq_running',type=types.BooleanType,flags = Instrument.FLAG_GETSET)   

        self.add_function('optimize_gate')
        self.add_function('optimize_yellow')
        self.add_function('optimize_newfocus')
        self.add_function('flow')
        
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

    def check_low_gate(self):
        # Acquire gate datastream
        datastream = np.zeros(self._detect_cycles);
        for i in np.arange(self._detect_cycles):
            datastream[i] = self.get_value_ext(self._data_time,0);
        # Filter out -1s: point without CR check
        datastream = datastream[datastream > -1];
        # If there are many points without CR check: gate is fine
        if (len(datastream) < self._detect_cycles / 2): 
            print len(datastream), '<', self._detect_cycles / 2, ': few cr checks needed, gate is fine.'                                
            return False;   
        # If average of datastream < threshold: low gate detected
        print 'Low gate:', np.mean(datastream), '<', self._check_gate_threshold
        if (np.mean(datastream) < self._check_gate_threshold):
            return True;
        else:
            return False;

    def check_deionization(self):
        # Acquire gate datastream
        datastream = np.zeros(self._detect_cycles);
        for i in np.arange(self._detect_cycles):
            datastream[i] = self.get_value_ext(self._data_time,0);
        # Filter out -1s: point without CR check
        datastream = datastream[datastream > -1];
        # If there are many points without CR check: ionization is fine
        if (len(datastream) < self._detect_cycles / 2):       
            print len(datastream), '<', self._detect_cycles / 2, ': few cr checks needed, ionization is fine.'                                    
            return False;        
        # If more than one zero in datastream: deionization (NV0) detected
        print 'Deionization:', np.sum(datastream == 0), '>', self._NV0_zeros
        if (np.sum(datastream==0) > self._NV0_zeros):
            return True;
        else:
            return False;         

    def check_low_yellow(self):
        # Acquire yellow datastream
        datastream = np.zeros(self._detect_cycles);
        for i in np.arange(self._detect_cycles):
            datastream[i] = self.get_value_ext(self._data_time,1);
        # Filter out -1s: point without repumps
        datastream = datastream[datastream > -1];
        # If there are many points without repump: yellow is fine
        if (len(datastream) <= 2):  
            print len(datastream), '<=', 2, ': few repumps needed, yellow is fine.'                                         
            return False;
        datastream_sorted = np.sort(datastream);
        # If lower half of data < threshold: low yellow detected
        print 'Low yellow:', np.mean(datastream_sorted[0:(np.floor(len(datastream)/2))]), '<', self._check_yellow_threshold      
        if (np.mean(datastream_sorted[0:(np.floor(len(datastream)/2))]) < self._check_yellow_threshold):
            return True;
        else:
            return False;   

    def check_high_yellow(self):
        # Acquire yellow datastream
        datastream = np.zeros(self._detect_cycles);
        for i in np.arange(self._detect_cycles):
            datastream[i] = self.get_value_ext(self._data_time,1);
        # Filter out -1s: point without repumps
        datastream = datastream[datastream > -1];
        # If there are many points without repump: yellow is fine
        if (len(datastream) <= 2):     
            print len(datastream), '<=', 2, ': few repumps needed, yellow is fine.'           
            return True;
        datastream_sorted = np.sort(datastream);
        # If higher half of data > threshold: low yellow detected
        print 'High yellow:', np.mean(datastream_sorted[(np.floor(len(datastream)/2)):]), '>', self._check_yellow_threshold      
        if (np.mean(datastream_sorted[(np.floor(len(datastream)/2)):]) > self._check_yellow_threshold):
            return True;
        else:
            return False;               

    def check_detuned_repump(self):
        # Acquire yellow datastream
        datastream = np.zeros(self._detect_cycles);
        for i in np.arange(self._detect_cycles):
            datastream[i] = self.get_value_ext(self._data_time,1);
        # Filter out -1s: points without repumps
        datastream = datastream[datastream > -1];
        # If there are no valid data points: no measurement is running, so never optimize newfocus
        if len(datastream) == 0:                       
            print 'No valid data. No ongoing measurement, so do not optimize newfocus'
            return False;
        # If max(yellow) > yellow_good but also zeros on newfocus: detuned repump laser (newfocus) detected
        print 'Detuned repump:', max(datastream), '>', self._opt_yellow_good, 'AND', np.sum(datastream==0) , '>', self._check_newfocus_zeros;
        if (max(datastream) > self._opt_yellow_good) and (np.sum(abs(datastream)<0.1) > self._check_newfocus_zeros):
            return True;
        else:
            return False;          

    def flow(self, state = 0):
        '''
        This is the main function that walks through the flowchart. Its current 'position' in the 
        flowchart is indicated by the parameter 'state'.
        Flowchart is as follows:

        0. Initialization state
        1. Do you have low counts on gate? YES: go to 2. NO: go to 4.
        2. Broaden Yellow and optimize gate, then go to 3.
        3. Yellow is off resonance. Optimize yellow, then go to 1.
        4. Do you have low counts on yellow? YES: go to 5. NO: go to 7. // Do you have high counts on yellow? YES: go to 5. NO: go to 3.
        5. Do you have both zeros and high counts on yellow? YES: go to 6. NO: go to 3 // Do you have zeros and high counts on yellow? YES: go to 6. NO: go to 7.
        6. NewFocus is off resonance. Optimize NewFocus, then go to 4.
        7. Finished succesfully.
        -1. Something went wrong. 
        '''
       
        # Allow to break
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
            print 'Quit by user'
            state = -1;
            return False;               
        # No switch statement in python :(
        if state == 0:
            # Allow to run
            qt.instruments['purification_optimizer'].set_stop_optimize(False)
            # Reset iterations
            self._newfocus_iterations = 0;
            self._gate_iterations = 0;
            self._yellow_iterations = 0; 
            # Start the real flowchart
            self.flow(state = 1);
        if state == 1:                
            print 'Low counts on gate?'
            # Check if there are low counts on the gate and otherwise on
            if self.check_low_gate():
                print 'YES'
                return self.flow(state = 2);
            else: 
                print 'NO'              
                return self.flow(state = 4);                
        elif state == 2:
            print 'adwin process on'
            if (self._gate_iterations == self._max_gate_iterations):
                print 'Should optimize gate, but maximum', self._max_gate_iterations, 'is reached. Try one newfocus optimization, then exit.'

                if self.optimize_newfocus():
                    # Allow laser to follow before going on
                    qt.msleep(self._flow_sleep)                  
                return self.flow(state = -1);
            else:           
                print 'Optimizing gate ABC';
                # Optimize gate
                if self.optimize_gate():
                    # Allow laser to follow before going on
                    qt.msleep(self._flow_sleep)          
                    return self.flow(state = 3);
                else:
                    # User exited ('q') optimization
                    return self.flow(state = -1);
        elif state == 3:
            if (self._yellow_iterations == self._max_yellow_iterations):
                print 'Should optimize yellow, but maximum', self._max_yellow_iterations, 'is reached. Try one newfocus optimization, then exit.'
                if self.optimize_newfocus():
                    # Allow laser to follow before going on
                    qt.msleep(self._flow_sleep)                          
                return self.flow(state = -1);
            else:
                print 'Optimizing yellow laser';
                # Optimize yellow laser
                if self.optimize_yellow():
                    # Allow laser to follow before going on
                    qt.msleep(self._flow_sleep)              
                    return self.flow(state = 1);
                else:
                    # User exited ('q') optimization
                    return self.flow(state = -1);                    
        elif state == 4:
            print 'High counts on yellow?'
            # Check if there are high counts on yellow
            if self.check_high_yellow():
                print 'YES'
                return self.flow(state = 5);
            else:
                print 'NO'
                return self.flow(state = 3);
        elif state == 5:
            print 'High counts and zeros on yellow?'
            # Check if there are zeros and high counts on yellow
            if self.check_detuned_repump():
                print 'YES'
                return self.flow(state = 6)
            else:
                print 'NO'
                return self.flow(state = 7)
        elif state == 6:
            if (self._newfocus_iterations == self._max_nf_iterations):
                print 'Should optimize newfocus, but maximum', self._max_nf_iterations, 'is reached. Exiting.'
                return self.flow(state = -1);
            else:                      
                print 'Optimizing newfocus'
                # Optimize newfocus
                if self.optimize_newfocus():
                    # Allow laser to follow before going on
                    qt.msleep(self._flow_sleep)            
                    return self.flow(state = 4)
                else:
                    # User exited ('q') optimization
                    return self.flow(state = -1);
        elif state == 7:
            print 'Auto optimization successful.'
            return True;
        elif state == -1:
            print 'Auto optimization exited before completion.'
            return False;            

    def optimize_newfocus(self):
        self._newfocus_iterations += 1;
        print 'Newfocus iters:', self._newfocus_iterations

        # Set initial time
        initial_time = time.time();
        # Create newfocus sweep            
        nf_start = self._get_freq_newfocus();
        print nf_start;
        scan_min = nf_start + self._opt_nf_scan_min/2.
        scan_max = nf_start + self._opt_nf_scan_max/2.
        steps=int((scan_max - scan_min) / self._opt_nf_step)


        nf_sweep=np.append(np.linspace(nf_start,scan_min+self._opt_nf_step,int(steps/2.)),
                np.linspace(scan_min, scan_max, steps))
        nf_sweep=np.append(nf_sweep,np.linspace(scan_max-self._opt_nf_step,nf_start,int(steps/2.)))       
        
        if self._nf_went_up:
            #if the laser went up the last time then invert the array
            nf_sweep = nf_sweep[::-1]

        # Initialize data arrays
        nf_x = np.array([]);
        nf_y = np.array([]);
        nf_t = np.array([]); 

        # set the other pids to be running:
        self.set_is_pidgate_running(True)
        self.set_is_yellowfrq_running(True)
        qt.msleep(0.1)

        # Start sweep
        finishedNF = False;  
        currentNFStep = 0;
        currentNFFreq = nf_start;
        NFStepTime = time.time();    
        # Each for iteration is one sweep step (dwell)
        for currentNFStep,currentNFFreq in enumerate(nf_sweep):
            # Allow to break
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                self._set_freq_newfocus(nf_start);
                print 'Quit by user'
                return False;
            # Set current gate frequency to gate sweep step            
            self._set_freq_newfocus(currentNFFreq)
            NFStepTime = time.time()   
            # Debug
            print 'Starting NF iteration', currentNFStep, 'out of', len(nf_sweep), 'at frequency', currentNFFreq;           

            # Each while iteration is one gate sweep substep
            while (time.time() - NFStepTime <= self._opt_nf_dwell) and not finishedNF:
                # Allow to break
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                    self._set_freq_newfocus(nf_start);
                    print 'Quit by user'
                    return False;              
                # Get nf val
                nf_x = np.append(nf_x,self._get_freq_newfocus())
                nf_y = np.append(nf_y,self.get_value_ext(self._data_time,2))
                nf_t = np.append(nf_t, time.time() - initial_time);
                if nf_y[-1] > self._opt_nf_good:
                    self._set_freq_newfocus(nf_x[-1])                      
                    finishedNF = True
                    break;
            if finishedNF:
                break; 

        if finishedNF:
            print 'Newfocus: good value during scan, at', nf_y[-1]/self._opt_nf_good, 'times threshold at frequency', nf_x[-1];
        else:
            self._set_freq_newfocus(nf_x[np.argmax(nf_y)]);
            print 'Newfocus: scan failed, set to best value ', max(nf_y), 'at frequency', nf_x[np.argmax(nf_y)];

        if self.get_do_plot(): 
            # Sweeps plot
            p1 = plt.plot(name=(self._plot_name+'_nf'))
            p1.clear()
            plt.plot(nf_t,nf_x,'O',name=(self._plot_name+'_nf')) 
            plt.plot(np.arange(len(nf_sweep))*self._opt_nf_dwell, nf_sweep,'O',name=(self._plot_name+'_nf'))             
            plt.plot(nf_t,nf_y,'O',name=(self._plot_name+'_nf'))  


        if nf_start < self._get_freq_newfocus():
            self._nf_went_up = True
        else:
            self.nf_went_up = False

        print 'Finished NewFocus optimization'
        return True;            
       
    def optimize_gate(self):  
        self._gate_iterations += 1;
        print 'Gate iters:', self._gate_iterations

        # Initialize
        initial_time = time.time();  

        # Start broadening of yellow
        self.adwin.load_test_sin_scan()                         # Load broadening
        self.adwin.start_test_sin_scan(delay=1000, amp=0.20)    # Start broadening      

        # Create yellow sweep            
        yellow_start = self._get_freq_yellow();
        scan_min = yellow_start + self._opt_yellow_scan_min/2.
        scan_max = yellow_start + self._opt_yellow_scan_max/2.
        steps=int((scan_max - scan_min) / self._opt_yellow_step)
        yellow_sweep=np.append(np.linspace(yellow_start,scan_min+self._opt_yellow_step,int(steps/2.)), np.linspace(scan_min, scan_max, steps))
        yellow_sweep=np.append(yellow_sweep,np.linspace(scan_max-self._opt_yellow_step,yellow_start,int(steps/2.)))
        # Reverse sweep if yellow went up last time
        if self._yellow_went_up:
            yellow_sweep = np.flipud(yellow_sweep);

        # Create gate sweep
        gate_start = self._get_freq_gate();
        scan_min = gate_start + self._opt_gate_scan_min/2.
        scan_max = gate_start + self._opt_gate_scan_max/2.
        steps=int((scan_max - scan_min) / self._opt_gate_step)
        gate_sweep=np.append(np.linspace(gate_start,scan_min+self._opt_gate_step,int(steps/2.)), np.linspace(scan_min, scan_max, steps))
        gate_sweep=np.append(gate_sweep,np.linspace(scan_max-self._opt_gate_step,gate_start,int(steps/2.)))
        # Reverse sweep if gate went up last time
        if self._gate_went_up:
            gate_sweep = np.flipud(gate_sweep);

        # Initialize data arrays
        yellow_x = np.array([]);
        yellow_y = np.array([]);
        yellow_t = np.array([]);
        gate_x = np.array([]);
        gate_y = np.array([]);
        gate_t = np.array([]);

        finishedYellow = False;
        finishedGate = False;


        self.set_is_pidgate_running(False)
        self.set_is_yellowfrq_running(True)
        qt.msleep(0.1)

        # Start yellow sweep
        currentYellowStep = 0;
        currentGateStep = 0;
        currentYellowFreq = yellow_start;
        currentGateFreq = gate_start;
        yellowStepTime = time.time();
        gateStepTime = time.time();

        # Each for iteration is one sweep step (dwell)
        for currentGateStep,currentGateFreq in enumerate(gate_sweep):
            # Allow to break
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                self._set_freq_yellow(yellow_start);
                self._set_freq_gate(gate_start);                
                print 'Quit by user'
                return False                 
            # Set current gate frequency to gate sweep step            
            self._set_freq_gate(currentGateFreq)
            gateStepTime = time.time()   
            # Debug
            print 'Starting gate iteration', currentGateStep, 'out of', len(gate_sweep), 'at frequency', currentGateFreq;           

            # Each while iteration is one gate sweep substep
            while (time.time() - gateStepTime <= self._opt_gate_dwell) and not finishedGate:
                # Allow to break
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                    self._set_freq_yellow(yellow_start);
                    self._set_freq_gate(gate_start);                
                    print 'Quit by user'
                    return False;                  
                # Check if we are still in NV-: no more than self._NV0_zeros zero in last 10 vals on gate
                if (sum(gate_y[-min(10,len(gate_y)):]==0) <= self._NV0_zeros or len(gate_y) < 10):  
                    # Debug
                    #print 'Currently in NV-, checking gate'
                    if self.get_is_pidgate_running():
                        self.set_is_pidgate_running(False)
                        self.set_is_yellowfrq_running(True)

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
                    # If yellow was good to begin with: leave it at current value, never scan it
                    if len(gate_y) == 9 and max(yellow_y) > self._opt_yellow_good:
                        finishedYellow = True
                else: # We are in NV0. Check if yellow is good
                    if np.mean(yellow_y[-min(5,len(yellow_y)):])>self._opt_yellow_good or finishedYellow or currentYellowStep == len(yellow_sweep): # Yellow is good. Continue gate
                        # Debug
                        print 'Currently in NV0, but yellow is OK, so go on checking gate'
                        if self.get_is_pidgate_running():
                            self.set_is_pidgate_running(False)
                            self.set_is_yellowfrq_running(True)
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
                    else: # Yellow is bad. Optimize yellow where we ended last time
                        # Debug
                        print 'Currently in NV0, yellow is bad, optimize yellow'
                        if self.get_is_yellowfrq_running():
                            self.set_is_pidgate_running(True)
                            self.set_is_yellowfrq_running(False)


                        self.adwin.stop_test_sin_scan() 
                        self.adwin.set_dac_voltage(('yellow_current', 0))
                        qt.msleep(1)

                        while currentYellowStep < len(yellow_sweep) and (not finishedYellow) and (sum(gate_y[-min(10,len(gate_y)):]==0) > self._NV0_zeros):                           
                            # Allow to break
                            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                                self._set_freq_yellow(yellow_start);
                                self._set_freq_gate(gate_start);                
                                print 'Quit by user'
                                return False;                                
                            # Set current gate frequency to gate sweep step
                            currentYellowFreq = yellow_sweep[currentYellowStep];
                            self._set_freq_yellow(currentYellowFreq);
                            yellowStepTime = time.time();

                            # Debug
                            print 'Currently in NV0, optimizing yellow. Starting iteration', currentYellowStep, 'out of', len(yellow_sweep), 'at frequency', currentYellowFreq;                           

                            while (time.time() - yellowStepTime <= self._opt_yellow_dwell) and not finishedYellow and (sum(gate_y[-min(10,len(gate_y)):]==0) > self._NV0_zeros):
                                # Allow to break
                                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                                    self._set_freq_yellow(yellow_start);
                                    self._set_freq_gate(gate_start);                
                                    print 'Quit by user'
                                    return False;                                 
                                # Get yellow val
                                yellow_x = np.append(yellow_x,self._get_freq_yellow())
                                yellow_y = np.append(yellow_y,self.get_value_ext(self._data_time,1))
                                yellow_t = np.append(yellow_t, time.time() - initial_time);
                                # Get gate val
                                gate_x = np.append(gate_x,self._get_freq_gate())
                                gate_y = np.append(gate_y,self.get_value_ext(self._data_time,0))
                                gate_t = np.append(gate_t, time.time() - initial_time);

                                if yellow_y[-1] > self._opt_yellow_good:                                    
                                    qt.msleep(self._yellow_delay) # Stupid waiting time to correct for delayed readout of frequency                        
                                    self._set_freq_yellow(self._get_freq_yellow())                      
                                    finishedYellow = True

                            currentYellowStep = currentYellowStep + 1; 
                        # If yellow sweep has finished without exceeding the threshold: immediately set yellow to optimal value.
                        if currentYellowStep == len(yellow_sweep):
                            # Scan didn't exceed threshold at any point. Take optimum value from scan, taking delay into account.
                            optTime = yellow_t[np.argmax(yellow_y)] + self._yellow_delay;
                            optFreq = yellow_x[np.argmin(abs(yellow_t - optTime))];
                            if abs(optFreq - yellow_start) > 10.:
                                print 'Something is wrong! Large step in yellow frequency detected. Back to start for safety.'
                                self._set_freq_yellow(yellow_start);
                            else:
                                print 'Yellow: scan failed, set to best value ', max(yellow_y), 'at frequency', optFreq;
                                self._set_freq_yellow(optFreq);

            if finishedGate:
                break;                                                            

        if finishedGate:
            print 'Gate: good value during scan, at', gate_y[-1]/self._opt_gate_good, 'times threshold at frequency', gate_x[-1];
        else:
            self._set_freq_gate(gate_x[np.argmax(gate_y)]);
            print 'Gate: scan failed, set to best value ', max(gate_y), 'at frequency', gate_x[np.argmax(gate_y)];

        if gate_x[np.argmax(gate_y)] > gate_start:
            self._gate_went_up = True;
        else:
            self._gate_went_up = False;

        if yellow_x[np.argmax(yellow_y)] > yellow_start:
            self._yellow_went_up = True;
        else:
            self._yellow_went_up = False;            

        if self.get_do_plot(): 
            # Sweeps plot
            p1 = plt.plot(name=(self._plot_name+'_sweeps'))
            p1.clear()
            plt.plot(np.arange(len(yellow_sweep))*self._opt_yellow_dwell,yellow_sweep,'O',name=(self._plot_name+'_sweeps'))     
            plt.plot(np.arange(len(gate_sweep))*self._opt_gate_dwell,gate_sweep,'O',name=(self._plot_name+'_sweeps'))            
            # Yellow plot
            p2 = plt.plot(name=(self._plot_name+'_yellow'))
            p2.clear()
            plt.plot(yellow_t,yellow_x,'O',name=(self._plot_name+'_yellow')) 
            plt.plot(np.arange(len(yellow_sweep))*self._opt_yellow_dwell, yellow_sweep,'O',name=(self._plot_name+'_yellow'))             
            plt.plot(yellow_t,yellow_y,'O',name=(self._plot_name+'_yellow'))  
            # Gate plot
            p3 = plt.plot(name=(self._plot_name+'_gate'))
            p3.clear()
            plt.plot(gate_t,gate_x,'O',name=(self._plot_name+'_gate')) 
            plt.plot(np.arange(len(gate_sweep))*self._opt_gate_dwell, gate_sweep,'O',name=(self._plot_name+'_gate'))             
            plt.plot(gate_t,gate_y,'O',name=(self._plot_name+'_gate'))

        # Stop broadening
        self.adwin.stop_test_sin_scan()
        self.adwin.set_dac_voltage(('yellow_current', 0))   

        print 'Finished gate optimization.'
        return True;

    def optimize_yellow(self):  
        self._yellow_iterations += 1;
        print 'Yellow iters:', self._yellow_iterations

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
        # Reverse sweep if yellow went up last time
        if self._yellow_went_up:
            yellow_sweep = np.flipud(yellow_sweep);

        # Create gate sweep
        gate_start = self._get_freq_gate();
        scan_min = gate_start + self._opt_gate_scan_min/2.
        scan_max = gate_start + self._opt_gate_scan_max/2.
        steps=int((scan_max - scan_min) / self._opt_gate_step)
        gate_sweep=np.append(np.linspace(gate_start,scan_min+self._opt_gate_step,int(steps/2.)),
                np.linspace(scan_min, scan_max, steps))
        gate_sweep=np.append(gate_sweep,np.linspace(scan_max-self._opt_gate_step,gate_start,int(steps/2.))) 
        # Reverse sweep if gate went up last time
        if self._gate_went_up:
            gate_sweep = np.flipud(gate_sweep);

        # Initialize data arrays
        yellow_x = np.array([]);
        yellow_y = np.array([]);
        yellow_t = np.array([]);
        gate_x = np.array([]);
        gate_y = np.array([]);
        gate_t = np.array([]);

        finishedYellow = False;
        finishedGate = False;


        self.set_is_pidgate_running(True)
        self.set_is_yellowfrq_running(False)
        qt.msleep(0.1)
        # Start yellow sweep
        currentYellowStep = 0;
        currentGateStep = 0;
        currentYellowFreq = yellow_start;
        currentGateFreq = gate_start;
        yellowStepTime = time.time();
        gateStepTime = time.time();


        # Each for iteration is one sweep step (dwell)
        for currentYellowStep,currentYellowFreq in enumerate(yellow_sweep):
            # Allow to break
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                self._set_freq_yellow(yellow_start);
                self._set_freq_gate(gate_start);                
                print 'Quit by user'
                return False;             
            # Set current yellow frequency to yellow sweep step            
            self._set_freq_yellow(currentYellowFreq)
            yellowStepTime = time.time()   
            # Debug
            print 'Starting yellow iteration', currentYellowStep, 'out of', len(yellow_sweep), 'at frequency', currentYellowFreq;           

            # Each while iteration is one yellow sweep substep
            while (time.time() - yellowStepTime <= self._opt_yellow_dwell) and not finishedYellow:
                # Allow to break
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                    self._set_freq_yellow(yellow_start);
                    self._set_freq_gate(gate_start);                
                    print 'Quit by user'
                    return False;                 
                # Check if we are still in NV0: more than 1 zero in last 10 vals on gate
                if (sum(gate_y[-min(10,len(gate_y)):]==0) > 1 or len(gate_y) < 10):  
                    # Debug
                    # print 'Currently in NV0, checking yellow'

                    # Get yellow val
                    yellow_x = np.append(yellow_x,self._get_freq_yellow())
                    yellow_y = np.append(yellow_y,self.get_value_ext(self._data_time,1))
                    yellow_t = np.append(yellow_t, time.time() - initial_time);
                    # Get gate val
                    gate_x = np.append(gate_x,self._get_freq_gate())
                    gate_y = np.append(gate_y,self.get_value_ext(self._data_time,0))
                    gate_t = np.append(gate_t, time.time() - initial_time);

                    if yellow_y[-1] > self._opt_yellow_good:
                        qt.msleep(self._yellow_delay) # Stupid waiting time to correct for delayed readout of frequency                        
                        self._set_freq_yellow(self._get_freq_yellow())                      
                        finishedYellow = True
                        break;
                    # If gate was good to begin with: leave it at current value, never scan it
                    if len(gate_y) == 9 and np.mean(gate_y) > self._opt_gate_good:
                        finishedGate = True                        
                else: # We are in NV-. Check if gate is good
                    if max(gate_y[-min(5,len(gate_y)):])>self._opt_gate_good or finishedGate or currentGateStep == len(gate_sweep): # Gate is good. Continue yellow
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
                            qt.msleep(self._yellow_delay) # Stupid waiting time to correct for delayed readout of frequency                        
                            self._set_freq_yellow(self._get_freq_yellow())                      
                            finishedYellow = True
                            break;
                    else: # Gate is bad. Optimize gate where we ended last time
                        # Debug
                        print 'Currently in NV-, gate is bad, optimize gate'

                        while currentGateStep < len(gate_sweep) and not finishedGate and (sum(gate_y[-min(10,len(gate_y)):]==0) <= self._NV0_zeros):                           
                            # Allow to break
                            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                                self._set_freq_yellow(yellow_start);
                                self._set_freq_gate(gate_start);                
                                print 'Quit by user'
                                return False;                             

                            # Set current gate frequency to gate sweep step
                            currentGateFreq = gate_sweep[currentGateStep];
                            self._set_freq_gate(currentGateFreq);
                            gateStepTime = time.time();

                            # Debug
                            print 'Currently in NV-, optimizing gate. Starting iteration', currentGateStep, 'out of', len(gate_sweep), 'at frequency', currentGateFreq;                           

                            self.set_is_pidgate_running(False)
                            qt.msleep(0.1)
                            while (time.time() - gateStepTime <= self._opt_gate_dwell) and not finishedGate and (sum(gate_y[-min(10,len(gate_y)):]==0) <= self._NV0_zeros):
                                # Allow to break
                                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or qt.instruments['purification_optimizer'].get_stop_optimize(): 
                                    self._set_freq_yellow(yellow_start);
                                    self._set_freq_gate(gate_start);                
                                    print 'Quit by user'
                                    return False;                                 
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
                        # If gate sweep has finished without exceeding the threshold: immediately set gate to optimal value.
                        if currentGateStep == len(gate_sweep):
                            # Scan didn't exceed threshold at any point. Take optimum value from scan.
                            self._set_freq_gate(gate_x[np.argmax(gate_y)]);
                            print 'Gate: scan failed, set to best value ', max(gate_y), 'at frequency', gate_x[np.argmax(gate_y)];
            if finishedYellow:
                break;                                                            

        if gate_x[np.argmax(gate_y)] > gate_start:
            self._gate_went_up = True;
        else:
            self._gate_went_up = False;

        if finishedYellow:
            print 'Yellow: good value during scan, at', yellow_y[-1]/self._opt_yellow_good, 'times threshold at frequency', yellow_x[-1];
        else:
            # Scan didn't exceed threshold at any point. Take optimum value from scan, taking delay into account.
            optTime = yellow_t[np.argmax(yellow_y)] + self._yellow_delay;
            optFreq = yellow_x[np.argmin(abs(yellow_t - optTime))];
            if abs(optFreq - yellow_start) > 10.:
                print 'Something is wrong! Large step in yellow frequency detected. Back to start for safety.'
                self._set_freq_yellow(yellow_start);
            else:
                print 'Yellow: scan failed, set to best value ', max(yellow_y), 'at frequency', optFreq;
                self._set_freq_yellow(optFreq);

        if yellow_x[np.argmax(yellow_y)] > yellow_start:
            self._yellow_went_up = True;
        else:
            self._yellow_went_up = False; 

        if self.get_do_plot(): 
            # Sweeps plot
            p1 = plt.plot(name=(self._plot_name+'_sweeps'))
            p1.clear()
            plt.plot(np.arange(len(yellow_sweep))*self._opt_yellow_dwell,yellow_sweep,'O',name=(self._plot_name+'_sweeps'))     
            plt.plot(np.arange(len(gate_sweep))*self._opt_gate_dwell,gate_sweep,'O',name=(self._plot_name+'_sweeps'))            
            # Yellow plot
            p2 = plt.plot(name=(self._plot_name+'_yellow'))
            p2.clear()
            plt.plot(yellow_t,yellow_x,'O',name=(self._plot_name+'_yellow')) 
            plt.plot(np.arange(len(yellow_sweep))*self._opt_yellow_dwell, yellow_sweep,'O',name=(self._plot_name+'_yellow'))             
            plt.plot(yellow_t,yellow_y,'O',name=(self._plot_name+'_yellow'))  
            # Gate plot
            p3 = plt.plot(name=(self._plot_name+'_gate'))
            p3.clear()
            plt.plot(gate_t,gate_x,'O',name=(self._plot_name+'_gate')) 
            plt.plot(np.arange(len(gate_sweep))*self._opt_gate_dwell, gate_sweep,'O',name=(self._plot_name+'_gate'))             
            plt.plot(gate_t,gate_y,'O',name=(self._plot_name+'_gate'))  

        print 'Finished yellow optimization.'
        return True;
                    
    def get_value_ext(self,dwell,source):
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
            # When there are zero attemps, should be distinguishable from zero counts
            return -1.  
        
    def _do_set_is_pidgate_running(self,val):
        if val:
            qt.instruments['pidgate'].start()
        else:
            qt.instruments['pidgate'].stop()


    def _do_get_is_pidgate_running(self):
        return qt.instruments['pidgate'].get_is_running()



    def _do_set_is_yellowfrq_running(self,val):
        if val:
            qt.instruments['pidyellowfrq'].start()
        else:
            qt.instruments['pidyellowfrq'].stop()

    def _do_get_is_yellowfrq_running(self):
        return qt.instruments['pidyellowfrq'].get_is_running()