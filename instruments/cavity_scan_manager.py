###############
### original created by Cristian Bonato - 2015
### edited by Suzanne van Dam - 2016
################

import os
from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument

import qt
import time
import types
import numpy as np
from lib import config


class cavity_scan_manager(CyclopeanInstrument):
    def __init__ (self, name, exp_mngr):
        CyclopeanInstrument.__init__(self,name)

        self._exp_mngr = exp_mngr

        self._scan_initialized = False
        self.V_min = None
        self.V_max = None
        self.nr_V_points = None
        # self.nr_avg_scans = 1
        # self.nr_repetitions = 1

        #maybe this type of parameters can better be part of a dictionary..?
        self.add_parameter('nr_avg_scans',
                types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('nr_repetitions',
                types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('minV_lengthscan',
                types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -2, maxval = 10)
        
        self.add_parameter('maxV_lengthscan',
                types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -2, maxval = 10)

        self.add_parameter('nr_steps_lengthscan',
                types.IntType, 
                flags= Instrument.FLAG_GETSET)
       
        self.add_parameter('minV_finelaser',
                types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -3, maxval = 3)

        self.add_parameter('maxV_finelaser',
                types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -3, maxval = 3)

        self.add_parameter('nr_steps_finelaser',
                types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('minlambda_lrlaser',
                types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'nm',
                minval = 636, maxval = 640)

        self.add_parameter('maxlambda_lrlaser',
                types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'nm',
                minval = 636, maxval = 640)

        self.add_parameter('nr_steps_lrlaser',
                types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('nr_calib_pts_lrlaser',
                types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('sync_delay_ms',
                types.IntType,
                flags=Instrument.FLAG_GETSET,
                units = ms
                minval = 0, maxval = 2000)

        self.add_parameter('min_msyncdelay',
                types.IntType,
                flags=Instrument.FLAG_GETSET,
                units = ms
                minval = 0, maxval = 2000)

        self.add_parameter('max_msyncdelay',
                types.IntType,
                flags=Instrument.FLAG_GETSET,
                units = ms
                minval = 0, maxval = 2000)

        self.add_parameter('nr_steps_msyncdelay',
                types.IntType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('wait_cycles',
                types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('use_sync',
                types.BooleanType, 
                flags = Instrument.FLAG_GETSET)

        # self.use_sync = False
        self.sync_delay_ms = None

        # self.autostop = None
        # self.autosave = None
        # self.file_Tag = None

        self.add_parameter('autosave', 
                types.BooleanType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('autosave', 
                types.BooleanType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('file_tag', 
                types.StringType,
                flags=Instrument.FLAG_GETSET)

        self.data = None
        self.PD_signal = None
        self.tstamps_ms = None
        self.scan_params = None

        self.add_function('manage_tasks')
        self.add_function('start_lengthscan')
        self.add_function('stop_lengthscan')
        self.add_function('laser_scan')
        self.add_function('piezo_scan')
        self.add_function('initialize_piezos')
        self.add_function('save')
        self.add_function('save_2D_scan')
        self.add_function('status_label')


    ###########
    ### task management
    ###########

    def manage_tasks (self):
        '''
        Function that manages the tasks of the scan manager. 
        If the cavity_scan_gui is started this function is executed periodically.
        It makes sure that no two scans are executed at the same time.
        '''
        if (self._running_task == 'length_scan'):
            self.run_new_length_scan()
        elif (self._running_task == 'lr_laser_scan'):
            self.run_new_lr_laser_scan()
        elif (self._running_task == 'fine_laser_scan'):
            self.run_new_fine_laser_scan()
        elif (self._running_task == 'fine_laser_calib'):
            self.run_new_laser_calibration()
        elif (self._running_task == 'timeseries'):
            self.run_new_timeseries()
        elif (self._running_task == 'update_2D_scan'):
            self.run_update_2D_scan()            
        elif (self._running_task == 'sweep_msyncdelay'):
            self.run_new_sweep_msyncdelay()            
        else:
            idle = True

    ######## start and stop functions of scans. These are linked to buttons on the can gui.
    ######## Work in Progress note: 
    ######## maybe I should only have this in the gui. 
    ######## but, I need the manager to know that he can only start a new task if the 
    ######## thing is not busy, also if you start something from the command line. 
    ######## and I want to be able to start something from the command line, while being able
    ######## to specify the parameters. Without having to set all parameters with set_.... 
    ######## but OK, that I can take care of later.
    def start_lengthscan(self):
        if (self._running_task==None):
            self._running_task = 'length_scan'

    def stop_lengthscan(self):
        if (self._running_task=='length_scan'):
            self._running_task = None
            self._2D_scan_is_active = False

   def start_finelaser(self):
        if (self._running_task==None):
            self._running_task = 'fine_laser_scan'

    def stop_finelaser(self):
        if (self._running_task == 'fine_laser_scan'):
            self._running_task = None
            # self._exp_mngr.set_piezo_voltage (V = self._exp_mngr._fine_piezos)###SvD:this is a weird statement.

    def start_lr_scan(self):
        if (self._running_task==None):
            self.curr_l = self._scan_mngr.minlambda_lrlaser
            if (self.minlambda_lrlaser>self._scan_mngr.maxlambda_lrlaser):
                self._scan_direction = -1
            else:
                self._scan_direction = +1

            print 'Scan direction: ', self._scan_direction
            print self.curr_l
            self.lr_scan_frq_list = []
            self.lr_scan_sgnl_list = []
            self._running_task = 'lr_laser_scan'

    def resume_lr_scan(self):
        if (self._running_task==None):
            self._running_task = 'lr_laser_scan'

    def stop_lr_scan(self):
        if (self._running_task == 'lr_laser_scan'):
            self._running_task = None
            self._2D_scan_is_active = False
            print 'Stopping!'

    def start_2D_scan (self):
        '''
        function that starts a 2D scan sweeping both cavity length and laser frequency
        SvD: I think it needs debugging
        '''
        if (self._running_task==None):
            self.curr_pz_volt = self.minV_lengthscan
            self._exp_mngr.set_piezo_voltage (self.curr_pz_volt) 
            self.pzV_step = (self.maxV_lengthscan-self.minV_lengthscan)/float(self.nr_steps_lengthscan)
            self.dict_2D_scan = {}
            self.dict_pzvolt = {}
            self._2D_scan_is_active = True

            if (self._scan_mngr.minlambda_lrlaser>self._scan_mngr.maxlambda_lrlaser):
                self.curr_l = self._scan_mngr.minlambda_lrlaser
                self._scan_direction = -1
            else:
                self.curr_l = self._scan_mngr.minlambda_lrlaser
                self._scan_direction = +1            
            self.lr_scan_frq_list = np.array([])
            self.lr_scan_sgnl_list = np.array([])
            self._running_task = 'lr_laser_scan'
            self.idx_2D_scan = 0

    def start_sweep_msyncdelay(self):
        if (self._running_task==None):
            self._running_task = 'sweep_msyncdelay'

    def stop_sweep_msyncdelay(self):
        if (self._running_task=='sweep_msyncdelay'):
            self._running_task==None


    ##############
    ### initialization before measurement
    ##############
    def initialize_msmt_params(self):
        #TODO: add wavelength to the params!!
        self.msmt_params = {}
        self.msmt_params['nr_scans_per_sync'] = self._scan_mngr.nr_avg_scans
        return self.msmt_params

    def run_new_lengthscan(self, **kw):
        enable_autosave = kw.pop('enable_autosave',True)
        self.reset_data('PD_signal', (self.nr_steps_lengthscan))
        self.reset_data('v_vals',  (self.nr_steps_lengthscan))

        self.ui.label_status_display.setText("<font style='color: red;'>SCANNING PIEZOs</font>")
        self.set_scan_params (v_min=self.minV_lengthscan, v_max=self.maxV_lengthscan, nr_points=self.nr_steps_lengthscan)
        self.initialize_piezos(wait_time=1)

        #self.sync_delays_ms = np.ones(self.nr_avg_scans)*sync_delay_ms
        
        # the core of the lengtscan function
        self.length_scan ()

        #set data in order for the UI to connect to it.       
        self.status_label = "<font style='color: red;'>idle</font>")

        self.reset_data('PD_signal', (self.nr_steps_lengthscan))
        self.reset_data('v_vals',  (self.nr_steps_lengthscan))
        # self.ui.label_status_display.setText("<font style='color: red;'>idle</font>")
        if self.success:
            self.set_data('PD_signal', self.data[0])
            self.set_data('v_vals', self.v_vals)
            # self.ui.plot_canvas.update_plot (x = self.v_vals, y=self.data[0], x_axis = 'piezo voltage [V]', 
            #             y_axis = 'photodiode signal (a.u.)', color = 'RoyalBlue')
            self.saveX_values = self.v_vals
            self.saveY_values = self.PD_signal
            self.save_tstamps_ms = self.tstamps_ms                  
            self.saveX_label = 'piezo_voltage'
            self.saveY_label = 'PD_signal'
            self.save_scan_type = 'msync'
            self.curr_task = 'length_scan'
        else:        
            msg_text = 'Cannot Sync to Montana signal!'
            ex = MsgBox(msg_text = msg_text)
            ex.show()
            self.curr_task = None
      
        if self.autosave and enable_autosave:
            self.save()
        if self.autostop:
            self._running_task = None
            self._exp_mngr.set_piezo_voltage (V = self._exp_mngr._fine_piezos)

        return self.success

    def run_new_fine_laser_scan(self):

        self.reset_data('PD_signal', (self.nr_steps_lengthscan))
        self.reset_data('v_vals',  (self.nr_steps_lengthscan))

        self.status_label = "<font style='color: red;'>idle</font>"
        self.set_scan_params (v_min=self.minV_finelaser, v_max=self.maxV_finelaser, nr_points=self.nr_steps_finelaser)
        self.laser_scan(use_wavemeter = False)
        self.set_data('PD_signal', self.data[0])
        self.set_data('v_vals', self.v_vals)
        # self.ui.plot_canvas.update_plot (x = self.v_vals, y=self.data[0], x_axis = 'laser-tuning voltage [V]', 
        #             y_axis = 'photodiode signal (a.u.)', color = 'b')
        self.saveX_values = self.v_vals
        self.saveY_values = self.PD_signal  
        self.saveX_label = 'laser_tuning_voltage'
        self.saveY_label = 'PD_signal'        
        self.curr_task = 'fine_laser_scan'
        self.ui.label_status_display.setText("<font style='color: red;'>idle</font>")

        if self.autosave:
            self.save()
        if self.autostop:
            self._running_task = None



    def run_new_lr_laser_scan (self):

        #first decide how to approach the calibration, 
        #depending on the number of calibration pts.
        #This is the number of points actually measured on the wavemeter
        #(should be minimized to keep the scan fast)
        self.reset_data('PD_signal', (self.nr_steps_lengthscan))
        self.reset_data('v_vals',  (self.nr_steps_lengthscan))

        nr_calib_pts = self.nr_calib_pts
        b0 = -21.3
        c0 = -0.13
        d0 = 0.48
        self._exp_mngr.set_laser_wavelength(self.curr_l)
        qt.msleep (0.1)
        if self._2D_scan_is_active:
            self.status_label =  "<font style='color: red;'>LASER SCAN: "+str(self.curr_l)+"nm - pzV = "+str(self.curr_pz_volt)+"</font>"
        else:
            self.status_label = "<font style='color: red;'>LASER SCAN: "+str(self.curr_l)+"nm</font>"

        #acquire calibration points
        dac_no = self._exp_mngr._adwin.dacs['newfocus_freqmod']
        print "DAC no ", dac_no
        self._adwin.start_set_dac(dac_no=dac_no, dac_voltage=-3)
        qt.msleep (0.1)
        V_calib = np.linspace (-3, 3, nr_calib_pts)
        f_calib = np.zeros(nr_calib_pts)
        print "----- Frequency calibration routine:"
        for n in np.arange (nr_calib_pts):
            qt.msleep (0.3)
            self._exp_mngr._adwin.start_set_dac(dac_no = dac_no, dac_voltage = V_calib[n])
            print "Point nr. ", n, " ---- voltage: ", V_calib[n]
            qt.msleep (0.5)
            f_calib[n] = self._exp_mngr._wm_adwin.Get_FPar (self._exp_mngr._wm_port)
            qt.msleep (0.2)
            print "        ", n, " ---- frq: ", f_calib[n]

        print 'f_calib:', f_calib
        #finel laser scan
        self.set_scan_params (v_min=-3, v_max=3, nr_points=self.nr_steps_lr_scan) #real fine-scan
        self.laser_scan(use_wavemeter = False)
        V = self.v_vals
        if (nr_calib_pts==1):
            V_calib = int(V_calib)
            f_calib = int(f_calib)
            b = b0
            c = c0
            d = d0
            a = f_calib + 3*b - 9*c + 27*d
        elif ((nr_calib_pts>1) and (nr_calib_pts<4)):
            a, c = self.fit_calibration(V = V_calib, freq = f_calib, fixed=[1,3])
            b = b0
            d = d0
        else:
            a, b, c, d = self.fit_calibration(V = V_calib, freq = f_calib, fixed=[])
        freq = a + b*V + c*V**2 + d*V**3

        self.lr_scan_frq_list =  np.append(self.lr_scan_frq_list,freq)
        self.lr_scan_sgnl_list  = np.append(self.lr_scan_sgnl_list, self.PD_signal)

        if self._2D_scan_is_active and (self.idx_2D_scan != 0):
            if self.lr_scan_sgnl.ndim == 1:
                self.lr_scan_sgnl = np.array([self.lr_scan_sgnl])
            self.lr_scan_sgnl_list = np.array([self.lr_scan_sgnl_list])

            print 'appending ',np.shape(self.lr_scan_sgnl),' to ',np.shape(self.lr_scan_sgnl_list)

            self.lr_scan_sgnl = np.append(self.lr_scan_sgnl,self.lr_scan_sgnl_list,axis=0)
            print 'results in: ',np.shape(self.lr_scan_sgnl)
        else:
            self.lr_scan_frq = (np.array(self.lr_scan_frq_list)).flatten()
            self.lr_scan_sgnl = (np.array(self.lr_scan_sgnl_list)).flatten()

        self.ui.plot_canvas.update_multiple_plots (x = self.lr_scan_frq, y=self.lr_scan_sgnl, x_axis = 'laser frequency (GHz)', 
                y_axis = 'photodiode signal (a.u.)', autoscale=False, color = 'none')

        self.saveX_values = self.lr_scan_frq
        self.saveY_values = self.lr_scan_sgnl  
        self.saveX_label = 'frequency_GHz'
        self.saveY_label = 'PD_signal'
        self.curr_task = 'lr_scan'
        self.status_label = "<font style='color: red;'>idle</font>"

        self.curr_l = self.curr_l + self._scan_direction*self.coarse_wavelength_step
        print 'New wavelength: ', self.curr_l
        if (self._scan_direction > 0):
            print 'Scan cond: l>max_l'
            stop_condition = (self.curr_l>=self.max_lambda)
        else:
            print 'Scan cond: l<min_l'
            stop_condition = (self.curr_l<=self.max_lambda)

        if stop_condition:
            if self._2D_scan_is_active:
                self._running_task = 'update_2D_scan'
            else:
                self._running_task = None
                if self.autosave:
                    self.save()
        else:
            self._running_task = 'lr_laser_scan'


    def run_new_sweep_msyncdelay(self):
        print "starting a new sweep of the montana sync delay"
        self.initialize_msmt_params()
        #calculate nr of sync pulses in which nr_scans = nr_scans, and remainder nr_scans in last sync pulse
        nr_syncs_per_pt,nr_remainder = divmod(self.nr_repetitions, self.nr_avg_scans)
        #create the array with the sync_delay values to sweep
        sync_delays = np.linspace(self.min_msyncdelay,self.max_msyncdelay,self.nr_steps_msyncdelay)
        print sync_delays

        self.msmt_params['sync_delays'] = sync_delays
        self.msmt_params['sweep_pts'] = sync_delays
        self.msmt_params['sweep_name'] = 'sync delay (ms)'
        self.msmt_params['sweep_length'] = len(sync_delays)
        self.msmt_params['nr_repetitions'] = self.nr_repetitions
        if nr_remainder > 0: #then you need one more sync to finish all repetitions
            nr_syncs_per_pt = nr_syncs_per_pt+1
        self.msmt_params['nr_syncs_per_pt'] = nr_syncs_per_pt
        self.msmt_params['nr_remainder'] = nr_remainder

        #create a local variable of nr_avg_scans and sync_delay_ms to remember the setting
        nr_avg_scans = self.nr_avg_scans
        sync_delay_ms = self.sync_delay_ms
        print 'syncs per pt',nr_syncs_per_pt
        print 'remaining',nr_remainder
        print 'scans per sync',nr_avg_scans

        fname = None

        for i in np.arange(nr_syncs_per_pt):
            if self._running_task == None:
                print 'measurement stopping'
                break
            if (i == nr_syncs_per_pt-1): #the last one
                if nr_remainder>0:
                    #set the nr_avg_scans to the remainder number of scans
                    self.nr_avg_scans = nr_remainder
            print "sync nr ",i+1," of ", nr_syncs_per_pt


            for j,sync_delay_j in enumerate(sync_delays):
                self.sync_delay_ms = sync_delay_j
                print 'sync delay value ', j+1 ,' of ', len(sync_delays), ': ',sync_delay_j
                first_rep = str(int(i*nr_avg_scans+1))
                last_rep = str(int(i*nr_avg_scans+self.nr_avg_scans))
                data_index_name = 'sweep_pt_'+str(j)+'_reps_'+first_rep+'-'+last_rep
                self.run_new_lengthscan(enable_autosave=False)
                fname = self.save(fname=fname, 
                    data_index = data_index_name)
        
        #reset the nr_avg_scans in the scan_manager
        self.nr_avg_scans = nr_avg_scans
        self.sync_delay_ms = sync_delay_ms

        #always stop after the mmt
        self._running_task = None

    def run_update_2D_scan (self):

        #store current laserscan in dictionary
        self.dict_2D_scan ['pzv_'+str(self.idx_2D_scan)] = self.curr_pz_volt
        self.dict_2D_scan ['frq_'+str(self.idx_2D_scan)] = np.asarray(self.saveX_values).flatten()
        self.dict_2D_scan ['sgnl_'+str(self.idx_2D_scan)] = np.asarray(self.saveY_values).flatten()

        #update paramter values
        self.idx_2D_scan = self.idx_2D_scan + 1
        self.curr_pz_volt = self.curr_pz_volt + self.pzV_step

        if (self.curr_pz_volt<self.maxV_lengthscan):
            self._exp_mngr.set_piezo_voltage (self.curr_pz_volt)
            print 'New pzV = ', self.curr_pz_volt
            self.curr_l = self.min_lambda
            self.lr_scan_frq_list = np.array([])
            self.lr_scan_sgnl_list = np.array([])
            self._running_task = 'lr_laser_scan'
        else:
            self.curr_pz_volt = self.curr_pz_volt - self.pzV_step
            self.save_2D_scan()
            self._running_task = None
            self._2D_scan_is_active = False

    def save(self, **kw):
        '''
        Function that saves the data obtained in a 1-dimensional scan into an HDF5 file.
        Input:
        -keywords:
            data_index  -   the name of the to be saved data arrays
            fName       -   name of the file in which the data will be saved. is created if doesn'e exist
        Output:
        fName  -    name of the file in which data has been saved

        '''
        data_index = kw.pop('data_index', '')
        fName = kw.pop('fname', None)
        if fName == None:
            if (self.curr_task == 'lr_scan'):
                minL = str(int(10*self.minlambda_lrlaser))
                maxL = str(int(10*self.maxlambda_lrlaser))
                fName =  datetime.now().strftime ('%H%M%S%f')[:-2] + '_' + self.curr_task+'_'+minL+'_'+maxL
            else:
                fName =  datetime.now().strftime ('%H%M%S%f')[:-2] + '_' + self.curr_task
            if self.file_tag:
                fName = fName + '_' + self.file_tag
        
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        f5 = h5py.File(os.path.join(directory, fName+'.hdf5'))

        if (self.curr_task+'_processed_data_'+data_index) not in f5.keys():
            scan_grp = f5.create_group(self.curr_task+'_processed_data_'+data_index)
        else:
            scan_grp = f5[self.curr_task+'_processed_data_'+data_index]
        scan_grp.create_dataset(self.saveX_label, data = self.saveX_values)
        scan_grp.create_dataset(self.saveY_label, data = self.saveY_values)

        try:
            if 'raw_data_'+data_index not in f5.keys():
                data_grp = f5.create_group('raw_data_'+data_index)
            else:
                data_grp = f5['raw_data_'+data_index]
            for j in np.arange (self.nr_avg_scans):
                data_grp.create_dataset('scannr_'+str(j+1), data = self.data [j,:])
        except:
            print 'Unable to save data'
        
        try:
            if 'TimeStamps'+data_index not in f5.keys():
                time_grp = f5.create_group('TimeStamps'+data_index)
            else:
                time_grp = f5['TimeStamps'+data_index]
            time_grp.create_dataset('timestamps [ms]', data = self.tstamps_ms)
        except:
            print 'Unable to save timestamps'

        #The below could be in a function save_msmt_params or so
        try:
            for k in self.scan_params:
                f5.attrs [k] = self.scan_params[k]
            for l in self.msmt_params: #ideally msmt_params should replace scan_params.
                f5.attrs [l] = self.msmt_params[l]

        except:
            print 'Unable to save scan params'

        f5.close()
        
        fig = plt.figure(figsize = (15,10))
        plt.plot (self.saveX_values, self.saveY_values, 'RoyalBlue')
        plt.plot (self.saveX_values, self.saveY_values, 'ob')
        plt.xlabel (self.saveX_label, fontsize = 15)
        plt.ylabel (self.saveY_label, fontsize = 15)
        plt.savefig (os.path.join(directory, fName+'_avg.png'))
        plt.close(fig)

        if (self.nr_avg_scans > 1):
            fig = plt.figure(figsize = (15,10))
            colori = cm.gist_earth(np.linspace(0,0.75, self.nr_avg_scans))
            for j in np.arange(self.nr_avg_scans):
                plt.plot (self.saveX_values, self.data[j,:], color = colori[j])
                plt.plot (self.saveX_values, self.data[j,:], 'o', color = colori[j])
            plt.xlabel (self.saveX_label, fontsize = 15)
            plt.ylabel (self.saveY_label, fontsize = 15)
            plt.savefig (os.path.join(directory, fName+'.png'))
            plt.close(fig)     

        return fName

    def save_2D_scan(self):
        '''
        Function that saves a 2 dimensional scan into an HDF5 file.
        '''
        fName = time.strftime ('%H%M%S') + '_2Dscan'
        if self._scan_mngr.file_tag:
            fName = fName + '_' + self._scan_mngr.file_tag
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)
        if not os.path.exists(directory):
            os.makedirs(directory)

        f5 = h5py.File(os.path.join(directory, fName+'.hdf5'))
        for k in np.arange (self.idx_2D_scan):
            scan_grp = f5.create_group(str(k))
            scan_grp.create_dataset('frq', data = self.dict_2D_scan ['frq_'+str(k)])
            scan_grp.create_dataset('sgnl', data = self.dict_2D_scan ['sgnl_'+str(k)])
            scan_grp.attrs['pzV'] = self.dict_2D_scan ['pzv_'+str(k)]
        f5.close()


    def fit_calibration(self, V, freq, fixed):
        guess_b = -21.3
        guess_c = -0.13
        guess_d = 0.48
        guess_a = freq[0] +3*guess_b-9*guess_c+27*guess_d

        a = fit.Parameter(guess_a, 'a')
        b = fit.Parameter(guess_b, 'b')
        c = fit.Parameter(guess_c, 'c')
        d = fit.Parameter(guess_d, 'd')

        p0 = [a, b, c, d]
        fitfunc_str = ''

        def fitfunc(x):
            return a()+b()*x+c()*x**2+d()*x**3


        fit_result = fit.fit1d(V,freq, None, p0=p0, fitfunc=fitfunc, fixed=fixed,
                do_print=False, ret=True)
        if (len(fixed)==2):
            a_fit = fit_result['params_dict']['a']
            c_fit = fit_result['params_dict']['c']
            return a_fit, c_fit
        else:
            a_fit = fit_result['params_dict']['a']
            b_fit = fit_result['params_dict']['b']
            c_fit = fit_result['params_dict']['c']
            d_fit = fit_result['params_dict']['d']
            return a_fit, b_fit, c_fit, d_fit


    def set_scan_params (self, v_min, v_max, nr_points):
        #can probably remove this function, since I will make a dictionary with this.
        self.V_min = v_min
        self.V_max = v_max
        self.nr_V_steps = nr_points
        self._scan_initialized = True

    def laser_scan (self, use_wavemeter = False, force_single_scan = True):

        v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
        self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)
        
        self.frequencies = np.zeros (self.nr_V_steps)
        self.PD_signal = np.zeros (self.nr_V_steps)

        if use_wavemeter:
            avg_nr_samples = self.nr_avg_scans
            if force_single_scan:
                avg_nr_samples = 1
            dac_no = self._exp_mngr._adwin.dacs['newfocus_freqmod']
            self._exp_mngr._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.V_min)
            qt.msleep (0.1)
            for n in np.arange (self.nr_V_steps):
                self._exp_mngr._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.v_vals[n])
                value = 0
                for j in np.arange (avg_nr_samples):
                    self._exp_mngr._adwin.start_read_adc (adc_no = self._adwin.adcs['photodiode'])
                    value = value + self._exp_mngr._adwin.get_read_adc_var ('fpar')[0][1]
                value = value/avg_nr_samples
                self.PD_signal[n] = value
                qt.msleep (0.01)
                self.frequencies[n] = self._exp_mngr._wm_adwin.Get_FPar (self._wm_port)
                qt.msleep (0.05)
        else:
            self.success, self.data, self.tstamps_ms, self.scan_params = self._exp_mngr._adwin.scan_photodiode (scan_type = 'laser',
                     nr_steps = self.nr_V_steps, nr_scans = self.nr_avg_scans, wait_cycles = self._exp_mngr.wait_cycles, 
                    start_voltage = self.V_min, end_voltage = self.V_max, 
                    use_sync = self.use_sync, delay_ms = self.sync_delay_ms)

            for j in np.arange (self.nr_avg_scans):
                if (j==0):
                    values = self.data[0]
                else:
                    values = values + self.data[j]
            self.PD_signal = values/float(self.nr_avg_scans)


    def initialize_piezos (self, wait_time=0.2):
        self._exp_mngr._adwin.start_set_dac(dac_no=self._exp_mngr._adwin.dacs['jpe_fine_tuning_1'], dac_voltage=self.V_min)
        self._exp_mngr._adwin.start_set_dac(dac_no=self._exp_mngr._adwin.dacs['jpe_fine_tuning_2'], dac_voltage=self.V_min)
        self._exp_mngr._adwin.start_set_dac(dac_no=self._exp_mngr._adwin.dacs['jpe_fine_tuning_3'], dac_voltage=self.V_min)
        qt.msleep(wait_time)

    def length_scan (self):

        v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
        self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)  
        self.PD_signal = np.zeros (self.nr_V_steps)

        self.success, self.data, self.tstamps_ms, self.scan_params = self._exp_mngr._adwin.scan_photodiode (scan_type = 'fine_piezos',
                nr_steps = self.nr_V_steps, nr_scans = self.nr_avg_scans, wait_cycles = self.wait_cycles, 
                start_voltage = self.V_min, end_voltage = self.V_max, 
                use_sync = self.use_sync, delay_ms = self.sync_delay_ms)

        #output PD_signal as the average over nr_avg_scans
        for j in np.arange (self.nr_avg_scans):
            if (j==0):
                values = self.data[0]
            else:
                values = values + self.data[j]
        self.PD_signal = values/float(self.nr_avg_scans)


    ############
    ### get and set functions for parameters
    ############

    def do_get_autosave(self):
        return self.autosave

    def do_set_autosave(self,value):
        self.autosave = value

    def do_get_autostop(self):
        return self.autostop

    def do_set_autostop(self,value):
        self.autostop = value

    def do_get_file_tag(self):
        return self.file_tag

    def do_set_file_tag(self,string):
        self.file_tag = string

    def do_get_nr_avg_scans(self):
        return self.nr_avg_scans

    def do_set_nr_avg_scans(self, value):
        self.nr_avg_scans = value

    def do_get_nr_repetitions(self):
        return self.nr_repetitions

    def do_set_nr_repetitions(self, value):
        self.nr_repetitions = value

    def do_get_use_sync(self):
        return self.use_sync

    def do_set_use_sync(self,value):
        self.use_sync = value

    def do_get_minV_lengthscan(self):
        return self.minV_lengthscan

    def do_set_minV_lengthscan(self,value):
        self.minV_lengthscan = value

    def do_get_maxV_lengthscan(self):
        return self.maxV_lengthscan

    def do_set_maxV_lengthscan(self,value):
        self.maxV_lengthscan = value

    def do_get_nr_steps_lengthscan(self):
        return self.nr_steps_lengthscan

    def do_set_nr_steps_lengthscan(self,value):
        self.nr_steps_lengthscan = value
        
    def do_get_wait_cycles(self):
        return self.wait_cycles

    def do_set_wait_cycles(self,value):
        self.wait_cycles = value

    def do_get_minV_finelaser(self):
        return self.minV_finelaser

    def do_set_minV_finelaser(self,value):
        self.minV_finelaser = value

    def do_get_maxV_finelaser(self):
        return self.maxV_finelaser

    def do_set_maxV_finelaser(self,value):
        self.maxV_finelaser = value

    def do_get_nr_steps_finelaser(self):
        return self.nr_steps_finelaser

    def do_set_nr_steps_finelaser(self,value):
        self.nr_steps_finelaser = value

    def do_get_minlambda_lrlaser(self):
        return self.minlambda_lrlaser

    def do_set_minlambda_lrlaser(self,value):
        self.minlambda_lrlaser = value

    def do_get_maxlambda_lrlaser(self):
        return self.maxlambda_lrlaser

    def do_set_maxlambda_lrlaser(self,value):
        self.maxlambda_lrlaser = value

    def do_get_nr_steps_lrlaser(self):
        return self.nr_steps_lrlaser

    def do_set_nr_steps_lrlaser(self,value):
        self.nr_steps_lrlaser = value

    def do_get_nr_calib_pts_lrlaser(self):
        return self.nr_calib_pts_lrlaser

    def do_set_nr_calib_pts_lrlaser(self,value):
        self.nr_calib_pts_lrlaser = value

    def do_get_sync_delay_ms(self,value):
        return self.sync_delay_ms

    def do_set_sync_delay_ms(self,value):
        self.sync_delay_ms = value

    def do_get_min_msyncdelay(self,value):
        return self.min_msyncdelay

    def do_set_min_msyncdelay(self,value):
        self.min_msyncdelay = value

    def do_get_max_msyncdelay(self,value):
        return self.max_msyncdelay

    def do_set_max_msyncdelay(self,value):
        self.max_msyncdelay = value

    def do_get_nr_steps_msyncdelay(self,value):
        return self.nr_steps_msyncdelay

    def do_set_nr_steps_msyncdelay(self,value):
        self.nr_steps_msyncdelay = value


