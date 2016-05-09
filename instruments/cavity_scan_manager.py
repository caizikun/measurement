###############
### original created by Cristian Bonato - 2015
### edited by Suzanne van Dam - 2016
### SvD: I am removing the experiment mangaer from it.... I don't see why we need it.
### SvD: I removed the buggy 2D scan. Find it back in the old cav_scan_gui_v8.py
################

import os
from datetime import datetime
import h5py 

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
from matplotlib import pyplot as plt

import qt
import time

import types
import numpy as np
from lib import config


class cavity_scan_manager(CyclopeanInstrument):
    def __init__ (self, name, adwin, physical_adwin,use_cfg=False):
        CyclopeanInstrument.__init__(self,name, tags=[])

        # self._exp_mngr = exp_mngr
        self._adwin = qt.instruments[adwin]
        self._physical_adwin = qt.instruments[physical_adwin]

        # self._scan_initialized = False
        # self.V_min = None
        # self.V_max = None
        # self.nr_V_points = None
        self._running_task = None

        self.sampling_interval = 100
        # self.nr_avg_scans = 1
        # self.nr_repetitions = 1

        #maybe this type of parameters can better be part of a dictionary..?
        self.add_parameter('nr_avg_scans',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET,)
        self.nr_avg_scans=1

        self.add_parameter('nr_repetitions',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET)
        self.nr_repetitions=1

        self.add_parameter('minV_lengthscan',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -2, maxval = 10)
        self.minV_lengthscan=-2

        self.add_parameter('maxV_lengthscan',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -2, maxval = 10)
        self.maxV_lengthscan=10

        self.add_parameter('nr_steps_lengthscan',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET)
        self.nr_steps_lengthscan=121

        self.add_parameter('minV_finelaser',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -3, maxval = 3)
        self.minV_finelaser=-3

        self.add_parameter('maxV_finelaser',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -3, maxval = 3)
        self.maxV_finelaser=3

        self.add_parameter('nr_steps_finelaser',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET)
        self.nr_steps_finelaser=121

        self.add_parameter('sync_delay_ms',
                type= types.IntType,
                flags=Instrument.FLAG_GETSET,
                units = 'ms',
                minval = 0, maxval = 2000)
        self.sync_delay_ms=0

        self.add_parameter('min_msyncdelay',
                type= types.IntType,
                flags=Instrument.FLAG_GETSET,
                units = 'ms',
                minval = 0, maxval = 2000)
        self.min_msyncdelay=0

        self.add_parameter('max_msyncdelay',
                type= types.IntType,
                flags=Instrument.FLAG_GETSET,
                units = 'ms',
                minval = 0, maxval = 2000)
        self.max_msyncdelay=1000

        self.add_parameter('nr_steps_msyncdelay',
                type= types.IntType,
                flags=Instrument.FLAG_GETSET)
        self.nr_steps_msyncdelay=6

        self.add_parameter('wait_cycles',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET)
        self.wait_cycles = 1

        self.add_parameter('use_sync',
                type= types.BooleanType, 
                flags = Instrument.FLAG_GETSET)
        self.use_sync = False

        self.add_parameter('autosave', 
                type= types.BooleanType,
                flags=Instrument.FLAG_GETSET)
        self.autosave=False

        self.add_parameter('autostop', 
                type= types.BooleanType,
                flags=Instrument.FLAG_GETSET)
        self.autostop=False

        self.add_parameter('file_tag', 
                type= types.StringType,
                flags=Instrument.FLAG_GETSET)
        self.file_tag=''
        self.add_parameter('status_label', 
                type= types.StringType,
                flags=Instrument.FLAG_GETSET)
        self.status_label='idle'

        self.add_parameter('task_is_running', 
                type= types.BooleanType,
                flags=Instrument.FLAG_GETSET)
        self.task_is_running = False

        self.add_parameter('running_task', 
                type= types.StringType,
                flags=Instrument.FLAG_GETSET)
        self.running_task = False

        self.data = None
        self.PD_signal = None
        self.tstamps_ms = None
        self.scan_params = None

        #variable properties are saved in the cfg file 
        if use_cfg:
            cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
            if not os.path.exists(cfg_fn):
                _f = open(cfg_fn, 'w')
                _f.write('')
                _f.close()        
            self.ins_cfg = config.Config(cfg_fn)   # this uses awesome QT lab properties, 
            #that automatically saves the config file when closing qtlab. I think, at least... #test it
            self.load_cfg()
            self.save_cfg()

        self.add_function('start_lengthscan')
        self.add_function('stop_lengthscan')
        self.add_function('laser_scan')
        self.add_function('length_scan')
        self.add_function('save')
        self.add_function('run_new_length_scan')
        self.add_function('run_new_fine_laser_scan')
        self.add_function('run_new_sweep_msyncdelay')

    ###########
    ### task management
    ###########

    def load_cfg(self):
        params = self.ins_cfg.get_all()
        if 'minV_lengthscan' in params:
            self.set_minV_lengthscan(params['minV_lengthscan'])
        if 'maxV_lengthscan' in params:
            self.set_maxV_lengthscan(params['maxV_lengthscan'])

    def save_cfg(self):
        self.ins_cfg['minV_lengthscan'] = self.minV_lengthscan
        self.ins_cfg['maxV_lengthscan'] = self.maxV_lengthscan

    def _sampling_event (self):
        '''
        Function that manages the tasks of the scan manager. 
        If the instrument is running this function is executed every sampling_interval.
        It makes sure that no two scans are executed at the same time.
        '''
        if not self._is_running:
            return False

        if self.get_task_is_running():
            #a task is already running, so do not start a new one.
            return True

        if (self._running_task == 'length_scan'):
            self.set_task_is_running(True)
            self.run_new_length_scan()
        elif (self._running_task == 'fine_laser_scan'):
            self.set_task_is_running(True)
            self.run_new_fine_laser_scan()
        # elif (self._running_task == 'update_2D_scan'):
        #     self.run_update_2D_scan()            
        # elif (self._running_task == 'sweep_msyncdelay'):
        #     self.run_new_sweep_msyncdelay()            
        else:
            print("no task specified. cavity scan manager instrument is stopping.")
            return False

        return True
    ######## start and stop functions of scans. These are linked to buttons on the can gui.
    ######## Work in Progress note: 
    ######## maybe I should only have this in the gui. 
    ######## but, I need the manager to know that he can only start a new task if the 
    ######## thing is not busy, also if you start something from the command line. 
    ######## and I want to be able to start something from the command line, while being able
    ######## to specify the parameters. Without having to set all parameters with set_.... 
    ######## but OK, that I can take care of later.
    def start_lengthscan(self):
        if (self.get_task_is_running()== False):
            self.set_is_running(True)
            self._running_task = 'length_scan'
        else:
            print('could not start lengthscan; a task is already running')
    def stop_lengthscan(self):
        if (self._running_task=='length_scan'):
            self.set_task_is_running(False)
            self.set_is_running(False)
        else:
            print('could not stop lengthscan; another task is running')

    def start_finelaser(self):
        if (self.get_task_is_running()== False):
            self.set_is_running(True)
            self._running_task = 'fine_laser_scan'
        else:
            print('could not start laserscan; a task is already running')

    def stop_finelaser(self):
        if (self._running_task == 'fine_laser_scan'):
            self.set_task_is_running(False)
            self.set_is_running (False)
        else:
            print('could not stop laserscan; another task is running')            
            # self._exp_mngr.set_piezo_voltage (V = self._exp_mngr._fine_piezos)###SvD: I do not see why we need to do this. 
            #maybe I need to do this later again, but somewhat differently?

    def start_sweep_msyncdelay(self):
        if (self._running_task==None):
            CyclopeanInstrument._start_running(self)
            self._running_task = 'sweep_msyncdelay'

    def stop_sweep_msyncdelay(self):
        if (self._running_task=='sweep_msyncdelay'):
            self._running_task==None
            self._is_running = False


    ##############
    ### initialization before measurement
    ##############
    def initialize_msmt_params(self):
        #TODO: add wavelength to the params!!
        self.msmt_params = {}
        self.msmt_params['nr_scans_per_sync'] = self._scan_mngr.nr_avg_scans
        return self.msmt_params

    def run(self,**kw):
        self.nr_avg_scans = kw.pop('nr_avg_scans', self.nr_avg_scans)
        self.nr_repetitions = kw.pop('nr_repetitions', self.nr_repetitions)
        self.get_nr_avg_scans()
        self.get_nr_repetitions()

    def run_new_length_scan(self, **kw):
        self.run(**kw)
        self._running_task = 'length_scan'

        self.minV_lengthscan=kw.pop('minV_lengthscan', self.minV_lengthscan)
        self.maxV_lengthscan=kw.pop('maxV_lengthscan', self.maxV_lengthscan)
        self.nr_steps_lengthscan = kw.pop('nr_steps_lengthscan',self.nr_steps_lengthscan)
        self.get_minV_lengthscan()
        self.get_maxV_lengthscan()
        self.get_nr_steps_lengthscan()

        enable_autosave = kw.pop('enable_autosave',True)
        self.reset_data('PD_signal', (self.nr_steps_lengthscan))
        self.reset_data('v_vals',  (self.nr_steps_lengthscan))

        # the core of the lengtscan function
        self.status_label = "<font style='color: red;'>length scan</font>"
        self.get_status_label()
        self.length_scan ()

        #set data in order for the UI to connect to it.       
        self.status_label = "<font style='color: red;'>idle</font>"
        self.get_status_label()

        # self.ui.label_status_display.setText("<font style='color: red;'>idle</font>")
        if self.success:
            self.set_data('v_vals', self.v_vals)
            qt.msleep(0.1)
            self.set_data('PD_signal', self.PD_signal)
            qt.msleep(0.1)

            self.saveX_values = self.v_vals
            self.saveY_values = self.PD_signal
            self.save_tstamps_ms = self.tstamps_ms                  
            self.saveX_label = 'piezo_voltage'
            self.saveY_label = 'PD_signal'
            self.save_scan_type = 'msync'
        else:        
            msg_text = 'Cannot Sync to Montana signal!'
            ex = MsgBox(msg_text = msg_text)
            ex.show()
            self.stop_lengthscan()
      
        if self.autosave and enable_autosave:
            self.save()
        if self.autostop:
            self.stop_lengthscan()

            # self._exp_mngr.set_piezo_voltage (V = self._exp_mngr._fine_piezos)#SvD: this seems unnecessary
        self.set_task_is_running(False)

    def run_new_fine_laser_scan(self, **kw):
        self._running_task = 'fine_laser_scan'

        self.minV_finelaser=kw.pop('minV_finelaser', self.minV_finelaser)
        self.maxV_finelaser=kw.pop('maxV_finelaser', self.maxV_finelaser)
        self.nr_steps_finelaser = kw.pop('nr_steps_finelaser',self.nr_steps_finelaser)
        self.wait_cycles = kw.pop('wait_cycles', self.wait_cycles)
        self.get_minV_finelaser()
        self.get_maxV_finelaser()
        self.get_nr_steps_finelaser()

        self.reset_data('PD_signal', (self.nr_steps_finelaser))
        self.reset_data('v_vals',  (self.nr_steps_finelaser))

        self.status_label = "<font style='color: red;'>laser scan</font>"
        self.get_status_label()
        self.laser_scan(use_wavemeter = False)

        self.set_data('PD_signal', self.data[0])
        qt.msleep(0.1)
        self.set_data('v_vals', self.v_vals)
        qt.msleep(0.1)

        self.saveX_values = self.v_vals
        self.saveY_values = self.PD_signal  
        self.saveX_label = 'laser_tuning_voltage'
        self.saveY_label = 'PD_signal'        
        self.status_label = "<font style='color: red;'>idle</font>"
        self.get_status_label()

        if self.autosave:
            self.save()
        if self.autostop:
            self.stop_finelaser()

        self.set_task_is_running(False)


    def run_new_sweep_msyncdelay(self):
        self._running_task='sweep_msyncdelay'
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
            fName =  datetime.now().strftime ('%H%M%S') + '_' + str(self._running_task)
            if self.file_tag:
                fName = fName + '_' + self.file_tag
        
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        f5 = h5py.File(os.path.join(directory, fName+'.hdf5'))

        if (self._running_task+'_processed_data_'+data_index) not in f5.keys():
            scan_grp = f5.create_group(self._running_task+'_processed_data_'+data_index)
        else:
            scan_grp = f5[self._running_task+'_processed_data_'+data_index]
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

    def laser_scan (self, use_wavemeter = False, force_single_scan = True):
        v_step = float(self.maxV_finelaser-self.minV_finelaser)/float(self.nr_steps_finelaser)
        self.v_vals = np.linspace(self.minV_finelaser, self.maxV_finelaser, self.nr_steps_finelaser)
        
        self.frequencies = np.zeros (self.nr_steps_finelaser)
        self.PD_signal = np.zeros (self.nr_steps_finelaser)

        if use_wavemeter:
            avg_nr_samples = self.nr_avg_scans
            if force_single_scan:
                avg_nr_samples = 1
            dac_no = self._adwin.dacs['newfocus_freqmod']
            self._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.minV_finelaser)
            qt.msleep (0.1)
            for n in np.arange (self.nr_V_steps):
                self._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.v_vals[n])
                value = 0
                for j in np.arange (avg_nr_samples):
                    self._adwin.start_read_adc (adc_no = self._adwin.adcs['photodiode'])
                    value = value + self._adwin.get_read_adc_var ('fpar')[0][1]
                value = value/avg_nr_samples
                self.PD_signal[n] = value
                qt.msleep (0.01)
                self.frequencies[n] = self._physical_adwin.Get_FPar (self._wm_port) 
                qt.msleep (0.05)
 
        else:
            self.success, self.data, self.tstamps_ms, self.scan_params = self._adwin.scan_photodiode (scan_type = 'laser',
                    nr_steps = self.nr_steps_finelaser, nr_scans = self.nr_avg_scans, wait_cycles = self.wait_cycles, 
                    start_voltage = self.minV_finelaser, end_voltage = self.maxV_finelaser, 
                    use_sync = self.use_sync, delay_ms = self.sync_delay_ms, scan_to_start = True)

            for j in np.arange (self.nr_avg_scans):
                if (j==0):
                    values = self.data[0]
                else:
                    values = values + self.data[j]
            self.PD_signal = values/float(self.nr_avg_scans)
        


    def length_scan (self):
        v_step = float(self.maxV_lengthscan-self.minV_lengthscan)/float(self.nr_steps_lengthscan)
        self.v_vals = np.linspace(self.minV_lengthscan, self.maxV_lengthscan, self.nr_steps_lengthscan)  
        self.PD_signal = np.zeros (self.nr_steps_lengthscan)

        self.success, self.data, self.tstamps_ms, self.scan_params = self._adwin.scan_photodiode (scan_type = 'fine_piezos',
                nr_steps = self.nr_steps_lengthscan, nr_scans = self.nr_avg_scans, wait_cycles = self.wait_cycles, 
                start_voltage = self.minV_lengthscan, end_voltage = self.maxV_lengthscan, scan_to_start=True,
                use_sync = self.use_sync, delay_ms = self.sync_delay_ms)

        for j in np.arange (self.nr_avg_scans):
            if (j==0):
                values = self.data[0]
            else:
                values = values + self.data[j]
        self.PD_signal = values/float(self.nr_avg_scans)


    ############
    ### get and set functions for parameters
    ############

    def do_get_task_is_running(self):
        return self.task_is_running

    def do_set_task_is_running(self,value):
        self.task_is_running = value

    def do_get_running_task(self):
        return self._running_task

    def do_set_running_task(self,value):
        self._running_task = value

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

    def do_get_status_label(self):
        return self.status_label

    def do_set_status_label(self,string):
        self.status_label = string

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

    def do_get_sync_delay_ms(self):
        return self.sync_delay_ms

    def do_set_sync_delay_ms(self,value):
        self.sync_delay_ms = value

    def do_get_min_msyncdelay(self):
        return self.min_msyncdelay

    def do_set_min_msyncdelay(self,value):
        self.min_msyncdelay = value

    def do_get_max_msyncdelay(self):
        return self.max_msyncdelay

    def do_set_max_msyncdelay(self,value):
        self.max_msyncdelay = value

    def do_get_nr_steps_msyncdelay(self):
        return self.nr_steps_msyncdelay

    def do_set_nr_steps_msyncdelay(self,value):
        self.nr_steps_msyncdelay = value


