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
from measurement.lib.config import adwins as adcfg

class cavity_scan_manager(CyclopeanInstrument):
    def __init__ (self, name, adwin, physical_adwin,use_cfg=True):
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


        self.add_parameter('nr_repetitions',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('minV_lengthscan',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -2, maxval = 10)

        self.add_parameter('maxV_lengthscan',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -2, maxval = 10)

        self.add_parameter('nr_steps_lengthscan',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('minV_finelaser',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -9, maxval = 9)

        self.add_parameter('maxV_finelaser',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'V',
                minval = -9, maxval = 9)

        self.add_parameter('nr_steps_finelaser',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('sync_delay_ms',
                type= types.IntType,
                flags=Instrument.FLAG_GETSET,
                units = 'ms',
                minval = 0, maxval = 2000)

        self.add_parameter('min_msyncdelay',
                type= types.IntType,
                flags=Instrument.FLAG_GETSET,
                units = 'ms',
                minval = 0, maxval = 2000)

        self.add_parameter('max_msyncdelay',
                type= types.IntType,
                flags=Instrument.FLAG_GETSET,
                units = 'ms',
                minval = 0, maxval = 2000)

        self.add_parameter('nr_steps_msyncdelay',
                type= types.IntType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('wait_cycles',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET)

        self.add_parameter('ADC_averaging_cycles',
                type= types.IntType, 
                flags= Instrument.FLAG_GETSET) 
        self.ADC_averaging_cycles = 1

        self.add_parameter('scan_auto_reverse',
                type= types.BooleanType, 
                flags= Instrument.FLAG_GETSET)
        
        self.add_parameter('use_sync',
                type= types.BooleanType, 
                flags = Instrument.FLAG_GETSET)

        self.add_parameter('autosave', 
                type= types.BooleanType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('autostop', 
                type= types.BooleanType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('use_wavemeter', 
                type= types.BooleanType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('file_tag', 
                type= types.StringType,
                flags=Instrument.FLAG_GETSET)
        self.add_parameter('status_label', 
                type= types.StringType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('task_is_running', 
                type= types.BooleanType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('running_task', 
                type= types.StringType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('cycle_duration', 
                type= types.IntType,
                flags=Instrument.FLAG_GETSET)

        self.nr_avg_scans=1
        self.nr_repetitions=1
        # self.minV_lengthscan=0
        # self.maxV_lengthscan=10
        # self.nr_steps_lengthscan=121
        # self.minV_finelaser=-3
        # self.maxV_finelaser=3
        # self.nr_steps_finelaser=121
        self.sync_delay_ms=0
        self.min_msyncdelay=0
        self.max_msyncdelay=1000
        self.nr_steps_msyncdelay=6
        self.wait_cycles = 1
        self.scan_auto_reverse = False
        self.use_sync = False
        # self.autosave=False
        # self.autostop=False
        # self.use_wavemeter=True
        self.file_tag=''
        self.status_label='idle'
        self.task_is_running = False
        self.running_task = None
        

        self.cycle_duration = 1000 #means running at 300 kHz ;  3000 here corresponds to 100 kHz

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
            self._ins_cfg = config.Config(cfg_fn)   # this uses awesome QT lab properties, 
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

    # def load_cfg(self):
    #     params = self.ins_cfg.get_all()
    #     if 'minV_lengthscan' in params:
    #         self.set_minV_lengthscan(params['minV_lengthscan'])
    #     if 'maxV_lengthscan' in params:
    #         self.set_maxV_lengthscan(params['maxV_lengthscan'])
    
    def save_cfg(self):
        self._ins_cfg['minV_lengthscan'] = self.get_minV_lengthscan()
        self._ins_cfg['maxV_lengthscan'] = self.get_maxV_lengthscan()
        self._ins_cfg['minV_finelaser'] = self.get_minV_finelaser()
        self._ins_cfg['maxV_finelaser'] = self.get_maxV_finelaser()
        self._ins_cfg['nr_steps_lengthscan'] = self.get_nr_steps_lengthscan()
        self._ins_cfg['nr_steps_finelaser'] = self.get_nr_steps_finelaser()
        self._ins_cfg['ADC_averaging_cycles'] = self.get_ADC_averaging_cycles()        
        self._ins_cfg['use_wavemeter'] = self.get_use_wavemeter()        
        self._ins_cfg['autosave'] = self.get_autosave()        
        self._ins_cfg['autostop'] = self.get_autostop()        
        self._ins_cfg['wait_cycles'] = self.get_wait_cycles()        
        self._ins_cfg['cycle_duration'] = self.get_cycle_duration()

    def load_cfg(self):
        params_from_cfg = self._ins_cfg.get_all()
        if 'minV_lengthscan' in params_from_cfg:
            self.minV_lengthscan = self._ins_cfg.get('minV_lengthscan')
        if 'maxV_lengthscan' in params_from_cfg:
            self.maxV_lengthscan = self._ins_cfg.get('maxV_lengthscan')
        if 'minV_finelaser' in params_from_cfg:
            self.minV_finelaser = self._ins_cfg.get('minV_finelaser')
        if 'maxV_finelaser' in params_from_cfg:
            self.maxV_finelaser = self._ins_cfg.get('maxV_finelaser')
        if 'nr_steps_lengthscan' in params_from_cfg:
            self.nr_steps_lengthscan = self._ins_cfg.get('nr_steps_lengthscan')
        if 'nr_steps_finelaser' in params_from_cfg:
            self.nr_steps_finelaser = self._ins_cfg.get('nr_steps_finelaser')
        if 'ADC_averaging_cycles' in params_from_cfg:
            self.ADC_averaging_cycles = self._ins_cfg.get('ADC_averaging_cycles')
        if 'use_wavemeter' in params_from_cfg:
            self.use_wavemeter = self._ins_cfg.get('use_wavemeter')
        if 'autosave' in params_from_cfg:
            self.autosave = self._ins_cfg.get('autosave')
        if 'autostop' in params_from_cfg:
            self.autostop = self._ins_cfg.get('autostop')
        if 'wait_cycles' in params_from_cfg:
            self.wait_cycles = self._ins_cfg.get('wait_cycles')
        if 'cycle_duration' in params_from_cfg:
            self.cycle_duration = self._ins_cfg.get('cycle_duration')


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
            if self.was_use_wavemeter:
                self.use_wavemeter=True
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
        
        if self.ADC_averaging_cycles>1000:
            print "ADC_averaging_cycles > 1000; aborting length scan"
            self.stop_lengthscan()
            self.set_task_is_running(False)

        self.was_use_wavemeter= self.use_wavemeter
        self.use_wavemeter=False

        enable_autosave = kw.pop('enable_autosave',True)
        self.reset_data('PD_signal', (self.nr_steps_lengthscan))
        self.reset_data('v_vals',  (self.nr_steps_lengthscan))

        # the core of the lengtscan function
        self.status_label = "<font style='color: red;'>length scan</font>"
        self.get_status_label()
        self.length_scan (**kw)

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
            print 'cannot sync to Montana'
            # msg_text = 'Cannot Sync to Montana signal!'
            # ex = MsgBox(msg_text = msg_text)
            # ex.show()
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
        self.use_wavemeter = kw.pop('use_wavemeter', self.use_wavemeter)
        self.get_minV_finelaser()
        self.get_maxV_finelaser()
        self.get_nr_steps_finelaser()

        self.reset_data('PD_signal', (self.nr_steps_finelaser))
        self.reset_data('v_vals',  (self.nr_steps_finelaser))

        self.status_label = "<font style='color: red;'>laser scan</font>"
        self.get_status_label()
        self.laser_scan()

        self.set_data('PD_signal', self.data[0])
        qt.msleep(0.1)
        if self.use_wavemeter:
            self.set_data('v_vals', self.freq_data)
        else:
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
        #create the array with the sync_delay values to sweep
        sync_delays = np.linspace(self.min_msyncdelay,self.max_msyncdelay,self.nr_steps_msyncdelay)
        print sync_delays

        self.msmt_params['sync_delays'] = sync_delays
        self.msmt_params['sweep_pts'] = sync_delays
        self.msmt_params['sweep_name'] = 'sync delay (ms)'
        self.msmt_params['sweep_length'] = len(sync_delays)
        self.msmt_params['nr_repetitions'] = self.nr_repetitions

        #create a local variable of nr_avg_scans and sync_delay_ms to remember the setting
        sync_delay_ms = self.sync_delay_ms
        print 'syncs per pt',nr_syncs_per_pt
        print 'remaining',nr_remainder
        print 'scans per sync',nr_avg_scans

        fname = None

        for i in np.arange(self.nr_repetitions):
            if self._running_task == None:
                print 'measurement stopping'
                break
            print "sync nr ",i+1," of ", self.nr_repetitions


            for j,sync_delay_j in enumerate(sync_delays):
                self.sync_delay_ms = sync_delay_j
                print 'sync delay value ', j+1 ,' of ', len(sync_delays), ': ',sync_delay_j
                first_rep = str(int(i*self.nr_avg_scans+1))
                last_rep = str(int(i*self.nr_avg_scans+self.nr_avg_scans))
                data_index_name = 'sweep_pt_'+str(j)+'_reps_'+first_rep+'-'+last_rep
                self.run_new_lengthscan(enable_autosave=False)
                fname = self.save(fname=fname, 
                    data_index = data_index_name)
        
        #reset the sync_delay in the scan_manager to the inital value
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

        if fName not in f5.keys():
            scan_grp = f5.create_group(fName)
        else:
            scan_grp = f5[fName]
        scan_grp.create_dataset(self.saveX_label, data = self.saveX_values)
        if self.use_wavemeter:
            scan_grp.create_dataset('laser_frequency', data = self.freq_data)
        scan_grp.create_dataset(self.saveY_label, data = self.saveY_values)
        scan_grp.create_dataset('PD_signal_per_ms',data= self.PD_signal_per_ms)

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
            print 'Unable to save msmt params'

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
        initial_voltage = self._adwin.get_dac_voltage('newfocus_freqmod')

        self.success, self.data, self.tstamps_ms, self.freq_data, self.scan_params, self.data_ms = self.scan_photodiode (scan_type = 'laser',
                nr_steps = self.nr_steps_finelaser, nr_scans = self.nr_avg_scans, wait_cycles = self.wait_cycles, 
                start_voltage = self.minV_finelaser, end_voltage = self.maxV_finelaser, initial_voltage = initial_voltage,
                use_sync = self.use_sync, delay_ms = self.sync_delay_ms, scan_to_start = True, 
                ADC_averaging_cycles=self.ADC_averaging_cycles, scan_auto_reverse=self.scan_auto_reverse,
                cycle_duration=self.cycle_duration)

        for j in np.arange (self.nr_avg_scans):
            if (j==0):
                values = self.data[0]
                values_ms = self.data_ms[0]
            else:
                values = values + self.data[j]
                values_ms = values_ms + self.data_ms[j]
        self.PD_signal = values/float(self.nr_avg_scans)
        self.PD_signal_per_ms = values_ms/float(self.nr_avg_scans)
        


    def length_scan (self, **kw):
        v_step = float(self.maxV_lengthscan-self.minV_lengthscan)/float(self.nr_steps_lengthscan)
        self.v_vals = np.linspace(self.minV_lengthscan, self.maxV_lengthscan, self.nr_steps_lengthscan)  
        self.PD_signal = np.zeros (self.nr_steps_lengthscan)
        initial_voltage = self._adwin.get_dac_voltage('jpe_fine_tuning_1')



        scan_type = kw.pop('scan_type','fine_piezos')

        self.success, self.data, self.tstamps_ms, self.freq_data, self.scan_params, self.data_ms = self.scan_photodiode (scan_type = scan_type,
                nr_steps = self.nr_steps_lengthscan, nr_scans = self.nr_avg_scans, wait_cycles = self.wait_cycles, 
                start_voltage = self.minV_lengthscan, end_voltage = self.maxV_lengthscan, initial_voltage=initial_voltage,
                scan_to_start=True,ADC_averaging_cycles=self.ADC_averaging_cycles,scan_auto_reverse=self.scan_auto_reverse,
                use_sync = self.use_sync, delay_ms = self.sync_delay_ms,cycle_duration=self.cycle_duration, **kw)

        for j in np.arange (self.nr_avg_scans):
            if (j==0):
                values = self.data[0]
                values_ms = self.data_ms[0] 
            else:
                values = values + self.data[j]
                values_ms = values_ms + self.data_ms[j]
        self.PD_signal = values/float(self.nr_avg_scans)
        self.PD_signal_per_ms = values_ms/float(self.nr_avg_scans)

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


    def do_get_ADC_averaging_cycles(self):
        return self.ADC_averaging_cycles

    def do_set_ADC_averaging_cycles(self,value):
        self.ADC_averaging_cycles = value

    def do_get_scan_auto_reverse(self):
        return self.scan_auto_reverse

    def do_set_scan_auto_reverse(self,value):
        self.scan_auto_reverse = value

    def do_get_use_wavemeter(self):
        return self.use_wavemeter

    def do_set_use_wavemeter(self,value):
        self.use_wavemeter = value

    def do_get_cycle_duration(self):
        return self.cycle_duration

    def do_set_cycle_duration(self,value):
        self.cycle_duration = value


    def scan_photodiode(self, scan_type, nr_steps = 100, nr_scans = 5, wait_cycles = 50, 
            start_voltage = -3, end_voltage = 3, initial_voltage =0, use_sync = 0, 
            delay_ms = 0, scan_to_start=False, ADC_averaging_cycles = 50,scan_auto_reverse=1,
            cycle_duration=1000,**kw):
        voltage_step = abs((end_voltage - start_voltage))/float(nr_steps-1)
        montana_sync_ch = adcfg.config['adwin_cav1_dios']['montana_sync_ch']
        ADC_ch = self._adwin.get_adc_channels()['photodiode']

        delay_cycles = int(delay_ms/3.3e-6) # assumes running at 300 kHz (SvD: doesn't make sense to me that this is correct. should be 3.3e-3).
        save_cycles = 100 #Hardcoded now -> save every ms. SvD. Solve better later?
        nr_ms_per_point = int(ADC_averaging_cycles/save_cycles)
        print 'nr_ms_per_point',nr_ms_per_point
        do_scan = True

        if (scan_type == 'fine_piezos'):
            DAC_ch_1 = self._adwin.get_dac_channels()['jpe_fine_tuning_1']
            DAC_ch_2 = self._adwin.get_dac_channels()['jpe_fine_tuning_2']
            DAC_ch_3 = self._adwin.get_dac_channels()['jpe_fine_tuning_3']
            DAC_channels = [DAC_ch_1,DAC_ch_2,DAC_ch_3]
            dac_names = np.array(['jpe_fine_tuning_1', 'jpe_fine_tuning_2', 'jpe_fine_tuning_3'])
            start_voltages = np.array([start_voltage,start_voltage,start_voltage])
            stop_voltages = np.array([end_voltage,end_voltage,end_voltage])
            final_voltages = np.array([initial_voltage,initial_voltage,initial_voltage])
            if ((start_voltage <-2) or (end_voltage >10)):
                do_scan = False
                print 'Piezo voltage exceeds specifications! Scan aborted.'
        elif (scan_type == 'laser'):
            DAC_ch_1 = self._adwin.get_dac_channels()['newfocus_freqmod']
            DAC_ch_2 = 0
            DAC_ch_3 = 0
            DAC_channels = [DAC_ch_1,DAC_ch_2,DAC_ch_3]
            dac_names=np.array(['newfocus_freqmod'])
            start_voltages=np.array([start_voltage])
            stop_voltages = np.array([end_voltage])
            final_voltages = np.array([initial_voltage])

        elif scan_type == 'arbitrary':
            DAC_ch_1 = kw.pop('DAC_ch_1',0)
            DAC_ch_2 = kw.pop('DAC_ch_2',0)
            DAC_ch_3 = kw.pop('DAC_ch_3',0)
            DAC_channels = [DAC_ch_1,DAC_ch_2,DAC_ch_3]
            ADC_ch = kw.pop('ADC_ch',self._adwin.get_adc_channels()['photodiode'])
            scan_to_start = False
        else: 
            print "Scan type unknown! Scan aborted."
            do_scan = False

        if do_scan:
            scan_params = {}
            scan_params['DAC_ch_1'] = DAC_ch_1
            scan_params['DAC_ch_2'] = DAC_ch_2
            scan_params['DAC_ch_3'] = DAC_ch_3            
            scan_params['ADC channels'] = ADC_ch
            scan_params['use_montana_sync'] = use_sync
            scan_params['sync_ch'] = montana_sync_ch
            scan_params['sync_delay_ms'] = delay_ms            
            scan_params['start_voltage'] = start_voltage
            scan_params['end_voltage'] = end_voltage
            scan_params['step_voltage'] = voltage_step
            scan_params['nr_scans'] = nr_scans
            scan_params['nr_steps'] = nr_steps
            scan_params['ADC_averaging_cycles'] = ADC_averaging_cycles
            scan_params['wait_cycles'] = wait_cycles
            scan_params['cycle_duration'] = cycle_duration
            scan_params['save_cycles'] = save_cycles
            scan_params['nr_ms_per_point'] = nr_ms_per_point

            # tstamps,raw_data,freq_data = self._adwin.photodiodeRO_voltagescan(dac_names,DAC_channels,ADC_ch,montana_sync_ch,
            #     nr_steps,nr_scans,voltage_step,start_voltages,stop_voltages,final_voltages,
            #     wait_cycles = wait_cycles,ADC_averaging_cycles = ADC_averaging_cycles,
            #     use_sync = use_sync,delay_us = delay_cycles,
            #     scan_to_start = scan_to_start,scan_auto_reverse = scan_auto_reverse)

            if scan_to_start:
                print 'scan to start'
                if scan_type=='laser': #make sure the laser scans slowly to the start
                    speed = 2000#mV/s
                else:
                    speed = 20000 #actually I also want to sweep the other ones a bit slowly
                _steps,_pxtime = self._adwin.speed2px(dac_names, start_voltages,speed=speed)
                print _steps,_pxtime
                self._adwin.linescan(dac_names, self._adwin.get_dac_voltages(dac_names),
                        start_voltages, _steps, _pxtime, value='none', 
                        scan_to_start=False, blocking = True)

            qt.msleep(0.1)
            t0=time.time()
            print 'performing voltage scan'
            self._adwin.start_voltage_scan_sync(DAC_ch_1=DAC_ch_1, DAC_ch_2=DAC_ch_2, DAC_ch_3=DAC_ch_3, ADC_channel=ADC_ch, 
                    nr_steps=nr_steps, nr_scans=nr_scans, wait_cycles=wait_cycles, voltage_step=voltage_step,
                    start_voltage_1 = start_voltage, start_voltage_2 = start_voltage, start_voltage_3 = start_voltage,
                    use_sync=use_sync, sync_ch=montana_sync_ch, delay_us=delay_cycles, ADC_averaging_cycles = ADC_averaging_cycles,
                    scan_auto_reverse=scan_auto_reverse,cycle_duration=cycle_duration,save_cycles=save_cycles)

            while (self._adwin.is_voltage_scan_sync_running()):
                qt.msleep (0.1)

            t1 = time.time()-t0
            print 'voltage scan done, took ',t1

            tstamps = self._adwin.get_voltage_scan_sync_var('timestamps',length=nr_scans+1) #self.physical_adwin.Get_Data_Long(timestamps_idx, 1, nr_scans) 
            raw_data = self._adwin.get_voltage_scan_sync_var('photodiode_voltage',length=(nr_steps)*nr_scans)# self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps*nr_scans)
            freq_data = self._adwin.get_voltage_scan_sync_var('laser_frequency',length=(nr_steps)*nr_scans)# self.physical_adwin.Get_Data_Float(freqs_idx, 1, nr_steps*nr_scans)
            raw_ms_data = self._adwin.get_voltage_scan_sync_var('photodiode_voltage_ms',length=(nr_steps)*nr_scans*nr_ms_per_point)# self.physical_adwin.Get_Data_Float(freqs_idx, 1, nr_steps*nr_scans)

            for i,n in enumerate(dac_names):
                self._adwin.set_dac_voltage((n,stop_voltages[i]))

            # after a piezo scan return the piezo voltage to the initial voltage.
            if scan_type=='laser': #make sure the laser scans slowly to the start
                speed = 2000#mV/s
            else:
                speed = 20000 #actually I also want to sweep the other ones a bit slowly
            _steps,_pxtime = self._adwin.speed2px(dac_names, final_voltages,speed=speed)
            self._adwin.linescan(dac_names, self._adwin.get_dac_voltages(dac_names),
                    final_voltages, _steps, _pxtime, value='none', 
                    scan_to_start=False, blocking = True)

            tstamps_ms = tstamps [1:]*100# the adwin runs at 100 kHz = 10us per cycle.    #*3.3*1e-6
            success = tstamps[0]

            data = np.reshape (raw_data, (nr_scans, nr_steps))
            data_ms = np.reshape(raw_ms_data, (nr_scans, nr_steps, nr_ms_per_point))
            if success:
                scan_params['scan_successfull'] = True
            else:
                scan_params['scan_successfull'] = False

            self.save_cfg()

            return success, data, tstamps_ms,freq_data, scan_params, data_ms