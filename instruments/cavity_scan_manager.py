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


import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_pd import pd_msmt


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

        self.PD_signal = None

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
        self._running_task = 'length_scan'

        m = pd_msmt.AdwinPhotodiode('LengthScan_'+self.file_tag)

        m.params.from_dict(qt.exp_params['protocols']['AdwinPhotodiode'])
        m.params.from_dict(qt.exp_params['protocols']['AdwinPhotodiode']['cavlength_scan'])
        m.params['ADC_averaging_cycles'] = self.ADC_averaging_cycles

        m.params['start_voltage'] = self.minV_lengthscan
        m.params['end_voltage'] = self.maxV_lengthscan

        m.params['nr_scans'] = self.nr_avg_scans
        m.params['nr_steps'] = self.nr_steps_lengthscan

        # self.minV_lengthscan=kw.pop('minV_lengthscan', self.minV_lengthscan)
        # self.maxV_lengthscan=kw.pop('maxV_lengthscan', self.maxV_lengthscan)
        # self.nr_steps_lengthscan = kw.pop('nr_steps_lengthscan',self.nr_steps_lengthscan)

        m.params['voltage_step'] = abs((m.params['end_voltage'] - m.params['start_voltage']))/float(m.params['nr_steps']-1)
        m.params['start_voltage_1'] = m.params['start_voltage']
        m.params['start_voltage_2'] = m.params['start_voltage']
        m.params['start_voltage_3'] = m.params['start_voltage']

        m.params['nr_ms_per_point'] = m.params['ADC_averaging_cycles']/m.params['save_cycles']

        dac_channels = [m.params['DAC_ch_1']]
        m.params['dac_names'] = ['jpe_fine_tuning_1','jpe_fine_tuning_2','jpe_fine_tuning_3']
        m.params['start_voltages'] = [m.params['start_voltage'],m.params['start_voltage'],m.params['start_voltage']]

        if self.ADC_averaging_cycles>1000:
            print "ADC_averaging_cycles > 1000; aborting length scan"
            self.stop_lengthscan()
            self.set_task_is_running(False)
            return

        self.reset_data('PD_signal', (self.nr_steps_lengthscan))
        self.reset_data('v_vals',  (self.nr_steps_lengthscan))
        self.status_label = "<font style='color: red;'>length scan</font>"
        self.get_status_label()

        success = m.run()

        self.status_label = "<font style='color: red;'>idle</font>"
        self.get_status_label()
        self.v_vals = np.linspace(self.minV_lengthscan, self.maxV_lengthscan, self.nr_steps_lengthscan)
        raw_data = m.adwin_var(('photodiode_voltage',self.nr_avg_scans*self.nr_steps_lengthscan))
        data = np.reshape (raw_data, (self.nr_avg_scans, self.nr_steps_lengthscan))

        for j in np.arange (self.nr_avg_scans):
            if (j==0):
                values = data[0]
            else:
                values = values + data[j]
        self.PD_signal = values/float(self.nr_avg_scans)
        
        # self.ui.label_status_display.setText("<font style='color: red;'>idle</font>")
        if success:
            self.set_data('v_vals', self.v_vals)
            qt.msleep(0.1)
            self.set_data('PD_signal', self.PD_signal)
            qt.msleep(0.1)
        else:        
            print 'measurement unsuccesful'
            self.stop_lengthscan()
      
        if self.autosave:
            m.save('lengthscan')
        m.finish(save_stack=False)

        if self.autostop:
            self.stop_lengthscan()

        self.set_task_is_running(False)


    def run_new_fine_laser_scan(self, **kw):
        self._running_task = 'fine_laser_scan'

        m = pd_msmt.AdwinPhotodiode('LaserScan_'+self.file_tag)

        m.params.from_dict(qt.exp_params['protocols']['AdwinPhotodiode'])
        m.params.from_dict(qt.exp_params['protocols']['AdwinPhotodiode']['laserfrq_scan'])
        m.params['ADC_averaging_cycles'] = self.ADC_averaging_cycles

        m.params['start_voltage'] = self.minV_finelaser
        m.params['end_voltage'] = self.maxV_finelaser

        m.params['nr_scans'] = self.nr_avg_scans
        m.params['nr_steps'] = self.nr_steps_finelaser

        # self.minV_lengthscan=kw.pop('minV_lengthscan', self.minV_lengthscan)
        # self.maxV_lengthscan=kw.pop('maxV_lengthscan', self.maxV_lengthscan)
        # self.nr_steps_lengthscan = kw.pop('nr_steps_lengthscan',self.nr_steps_lengthscan)

        m.params['voltage_step'] = abs((m.params['end_voltage'] - m.params['start_voltage']))/float(m.params['nr_steps']-1)
        m.params['start_voltage_1'] = m.params['start_voltage']
        m.params['start_voltage_2'] = m.params['start_voltage']
        m.params['start_voltage_3'] = m.params['start_voltage']

        m.params['nr_ms_per_point'] = m.params['ADC_averaging_cycles']/m.params['save_cycles']

        dac_channels = [m.params['DAC_ch_1']]
        m.params['dac_names'] = ['newfocus_freqmod']
        m.params['start_voltages'] = [m.params['start_voltage']]

        self.reset_data('PD_signal', (self.nr_steps_finelaser))
        self.reset_data('v_vals',  (self.nr_steps_finelaser))
        self.status_label = "<font style='color: red;'>length scan</font>"
        self.get_status_label()

        success = m.run()

        self.status_label = "<font style='color: red;'>idle</font>"
        self.get_status_label()
        self.v_vals = np.linspace(self.minV_finelaser, self.maxV_finelaser, self.nr_steps_finelaser)
        raw_data = m.adwin_var(('photodiode_voltage',self.nr_avg_scans*self.nr_steps_finelaser))
        data = np.reshape (raw_data, (self.nr_avg_scans, self.nr_steps_finelaser))

        for j in np.arange (self.nr_avg_scans):
            if (j==0):
                values = data[0]
            else:
                values = values + data[j]
        self.PD_signal = values/float(self.nr_avg_scans)
        
        # self.ui.label_status_display.setText("<font style='color: red;'>idle</font>")
        if success:
            self.set_data('v_vals', self.v_vals)
            qt.msleep(0.1)
            self.set_data('PD_signal', self.PD_signal)
            qt.msleep(0.1)
        else:        
            print 'measurement unsuccesful'
            self.stop_finelaser()
      
        if self.autosave:
            m.save('laserscan')
        m.finish(save_stack=False)

        if self.autostop:
            self.stop_finelaser()

        self.set_task_is_running(False)


    def run_new_sweep_msyncdelay(self):
        ##############SvD 31-1-2017: revise this function. It might not work anymore with the new m2-based msmt style
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

