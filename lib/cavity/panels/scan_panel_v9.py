########################################
# Cristian Bonato, 2015
# cbonato80@gmail.com
########################################

from __future__ import unicode_literals
import os, sys, time
from datetime import datetime
from PySide.QtCore import *
from PySide.QtGui import *
import random
from matplotlib.backends import qt4_compat
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore, uic
else:
    from PyQt4 import QtGui, QtCore, uic

import pylab as plt
import h5py
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm
from analysis.lib.fitting import fit
import measurement.lib.cavity.panels.scan_gui_panels 
import measurement.lib.cavity.panels.ui_scan_panel_v9
import measurement.lib.cavity.panels.XYscan_panel 

from measurement.lib.cavity.panels.scan_gui_panels import MsgBox, ScanPlotCanvas
from measurement.lib.cavity.panels.ui_scan_panel_v9 import Ui_Form as Ui_Scan


class ScanGUI(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self,parent,*arg,**kw)

        self.ui = Ui_Scan()
        self.ui.setupUi(self)

        self.ui.plot_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        #SETTINGS EVENTS
        self.ui.sb_avg.setRange(1, 999)
        self.ui.dsb_minV_pzscan.setRange(-2, 10)
        self.ui.dsb_minV_pzscan.setDecimals(2)
        self.ui.dsb_minV_pzscan.setSingleStep(0.1)
        self.ui.dsb_maxV_pzscan.setRange(-2, 10)
        self.ui.dsb_maxV_pzscan.setDecimals(2)
        self.ui.dsb_maxV_pzscan.setSingleStep(0.1)
        self.ui.dsb_minV_finelaser.setRange(-9, 9)
        self.ui.dsb_minV_finelaser.setDecimals(1)
        self.ui.dsb_minV_finelaser.setSingleStep(0.1)
        self.ui.dsb_maxV_finelaser.setRange(-9, 9)
        self.ui.dsb_maxV_finelaser.setDecimals(1)
        self.ui.dsb_maxV_finelaser.setSingleStep(0.1)
        self.ui.sb_nr_steps_pzscan.setRange(1, 99999)
        self.ui.sb_nr_steps_finelaser.setRange(1, 99999)
        self.ui.sb_fine_tuning_steps_LRscan.setRange(1,999)
        self.ui.dsb_min_lambda.setRange(636.0, 640.0)
        self.ui.dsb_min_lambda.setDecimals(2)
        self.ui.dsb_min_lambda.setSingleStep(0.01)
        self.ui.dsb_max_lambda.setRange(636.0, 640.0)
        self.ui.dsb_max_lambda.setDecimals(2)
        self.ui.dsb_max_lambda.setSingleStep(0.01)
        self.ui.sb_nr_calib_pts.setRange(1,99)
        self.ui.sb_wait_cycles.setRange(1,9999)
        self.ui.sb_delay_msync.setRange(0, 9999)
        self.ui.sb_mindelay_msync.setRange(0, 9999)
        self.ui.sb_mindelay_msync.setSingleStep(1)
        self.ui.sb_maxdelay_msync.setRange(0, 9999)
        self.ui.sb_maxdelay_msync.setSingleStep(1)
        self.ui.sb_nr_steps_msyncdelay.setRange(1,99)
        self.ui.sb_nr_scans_msync.setRange(1,999)
        self.ui.sb_nr_repetitions.setRange(1,999)
        #CONNECT SIGNALS TO EVENTS
        #general:
        self.ui.cb_autosave.stateChanged.connect (self.autosave)
        self.ui.cb_autostop.stateChanged.connect (self.autostop)
        self.ui.sb_avg.valueChanged.connect(self.set_avg)
        self.ui.button_save.clicked.connect(self.save_single)
        #JPE piezo-Scan:
        self.ui.dsb_minV_pzscan.valueChanged.connect(self.set_minV_lengthscan)
        self.ui.dsb_maxV_pzscan.valueChanged.connect(self.set_maxV_lengthscan)
        self.ui.sb_nr_steps_pzscan.valueChanged.connect(self.set_nr_steps_lengthscan)
        self.ui.sb_wait_cycles.valueChanged.connect(self.set_wait_cycles)
        self.ui.button_start_pzscan.clicked.connect(self.start_lengthscan)
        self.ui.button_stop_pzscan.clicked.connect(self.stop_lengthscan)
        #FineLaser-Scan:
        self.ui.dsb_minV_finelaser.valueChanged.connect(self.set_minV_finelaser)
        self.ui.dsb_maxV_finelaser.valueChanged.connect(self.set_maxV_finelaser)
        self.ui.sb_nr_steps_finelaser.valueChanged.connect(self.set_nr_steps_finelaser)
        self.ui.button_start_finelaser.clicked.connect(self.start_finelaser)
        self.ui.button_stop_finelaser.clicked.connect(self.stop_finelaser)
        self.ui.button_calibrate_finelaser.clicked.connect(self.calibrate_finelaser)
        #Long-Range Laser-Scan:
        self.ui.dsb_min_lambda.valueChanged.connect(self.set_min_lambda)
        self.ui.dsb_max_lambda.valueChanged.connect(self.set_max_lambda)
        self.ui.button_start_long_scan.clicked.connect(self.start_lr_scan)
        self.ui.button_resume_long_scan.clicked.connect(self.resume_lr_scan)
        self.ui.button_stop_long_scan.clicked.connect(self.stop_lr_scan)
        self.ui.sb_nr_calib_pts.valueChanged.connect(self.set_nr_calib_pts)
        self.ui.sb_fine_tuning_steps_LRscan.valueChanged.connect(self.set_steps_lr_scan)
        #Sweep sync montana delays:
        self.ui.sb_mindelay_msync.valueChanged.connect(self.set_min_msyncdelay)
        self.ui.sb_maxdelay_msync.valueChanged.connect(self.set_max_msyncdelay)
        self.ui.button_start_sweepdelay.clicked.connect(self.start_sweep_msyncdelay)
        self.ui.button_stop_sweepdelay.clicked.connect(self.stop_sweep_msyncdelay)
        self.ui.sb_nr_steps_msyncdelay.valueChanged.connect(self.set_nr_steps_msyncdelay)


        #Other buttons
        self.ui.lineEdit_fileName.textChanged.connect(self.set_file_tag)
        #self.ui.button_timeseries.clicked.connect (self.activate_timeseries)
        self.ui.button_2D_scan.clicked.connect (self.start_2D_scan)
        #self.ui.button_track.clicked.connect (self.activate_track)
        #self.ui.button_slowscan.clicked.connect (self.activate_slowscan)
        self.ui.cb_montana_sync.stateChanged.connect (self.montana_sync)
        self.ui.sb_delay_msync.valueChanged.connect(self.set_delay_msync)
        self.ui.sb_nr_scans_msync.valueChanged.connect(self.set_nr_scans_msync)
        self.ui.sb_nr_repetitions.valueChanged.connect(self.set_nr_repetitions)

        #INITIALIZATIONS:
        #JPE piezo-scan
        self.ui.dsb_minV_pzscan.setValue(1.00)
        self.set_minV_lengthscan(self._scan_mngr.get_minV_lengthscan())
        self.ui.dsb_maxV_pzscan.setValue(2.00)
        self.set_maxV_lengthscan(self._scan_mngr.get_maxV_lengthscan())
        self.ui.sb_nr_steps_pzscan.setValue(999)
        self.set_nr_steps_lengthscan(self._scan_mngr.get_nr_steps_lengthscan())
        #general
        self._running_task = None
        self._scan_mngr.averaging_samples = 1
        self.ui.sb_avg.setValue(1)
        self._scan_mngr.autosave = False
        self._scan_mngr.autostop = False
        #fine laser scan
        self.ui.dsb_minV_finelaser.setValue(-3)
        self._scan_mngr.minV_finelaser = -3
        self.ui.dsb_maxV_finelaser.setValue(3)
        self._scan_mngr.maxV_finelaser = 3
        self.ui.sb_nr_steps_finelaser.setValue(100)
        self._scan_mngr.nr_steps_finelaser = 100
        self.ui.sb_wait_cycles.setValue(1)
        self.set_wait_cycles(1)
        #long range laser scan
        self.ui.sb_fine_tuning_steps_LRscan.setValue(100)
        self._scan_mngr.nr_steps_lr_scan = 100
        self.ui.dsb_min_lambda.setValue (637.0)
        self.set_min_lambda(637.0)
        self.ui.dsb_max_lambda.setValue (637.1)
        self.set_max_lambda(637.1)
        self.ui.sb_nr_calib_pts.setValue(1)
        self.set_nr_calib_pts(1)
        self.coarse_wavelength_step = 0.1 
        #sweep montana sync delays
        self.ui.sb_mindelay_msync.setValue(0)
        self.set_min_msyncdelay (0)
        self.ui.sb_maxdelay_msync.setValue(1000)
        self.set_max_msyncdelay (1000)
        self.ui.sb_nr_steps_msyncdelay.setValue(11)
        self.set_nr_steps_msyncdelay(11)

        #others
        self._scan_mngr.file_tag = ''
        self._2D_scan_is_active = False
        self._use_sync = False
        self.ui.sb_nr_scans_msync.setValue(1)
        self.set_nr_scans_msync(1)
        self.ui.sb_delay_msync.setValue(0)
        self.set_delay_msync(0)
        self.ui.sb_nr_repetitions.setValue(1)
        self.set_nr_repetitions(1)

        #TIMER:
        self.refresh_time = 100
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.manage_tasks)
        self.timer.start(self.refresh_time)

    def _instrument_changed(self,changes):
        Panel._instrument_changed(self, changes)
        print changes
        if changes.has_key('status_label'):
            self.ui.label_status_display.setText(str(changes['status_label']))
        
        if 'data_update' in changes:
            d = changes['data_update']
            if 'v_vals' in d:
            self.ui.plot_canvas.set_x(self._data['v_vals'])
            #self.ui.plot_canvas.set_x_axis('piezo voltage (V)')
            try: 
                self.ui.plot_canvas.plot.delplot('PD_signal')
            except:
                pass

            if 'PD_signal' in d:
                self.ui.plot_canvas.set_y(self._data['PD_signal'])
                #self.ui.plot_canvas.set_y_axis('photodiode signal (a.u.)')

        
        #changes = self._scan_mngr.get_data_update()

    #I think I need to keep this for the refreshing.

    def manage_tasks(self):
        self._ins.manage_tasks()

    # def manage_tasks (self):
    #     if (self._running_task == 'lengthscan'):
    #         self.run_new_lengthscan()
    #     elif (self._running_task == 'lr_laser_scan'):
    #         self.run_new_lr_laser_scan()
    #     elif (self._running_task == 'fine_laser_scan'):
    #         self.run_new_fine_laser_scan()
    #     elif (self._running_task == 'fine_laser_calib'):
    #         self.run_new_laser_calibration()
    #     elif (self._running_task == 'timeseries'):
    #         self.run_new_timeseries()
    #     elif (self._running_task == 'update_2D_scan'):
    #         self.run_update_2D_scan()            
    #     elif (self._running_task == 'sweep_msyncdelay'):
    #         self.run_new_sweep_msyncdelay()            
    #     else:
    #         idle = True

    def autosave (self, state):
        if state == QtCore.Qt.Checked:
            self._ins.set_autosave(True)
        else:
            self._ins.set_autosave(False)

    def autostop (self, state):
        if state == QtCore.Qt.Checked:
            self._ins.set_autostop(True)
        else:
            self._ins.set_autostop(False)

    def montana_sync (self, state):
        if state == QtCore.Qt.Checked:
            self._ins.set_use_sync(True)
        else:
            self._ins.set_use_sync(False)

    def set_avg (self, value):
        '''
        this function seems to be a double of the 'msync_nr_avg_scans'. remove either.
        '''
        self._ins.set_nr_avg_scans(value)
        self.ui.sb_nr_scans_msync.setValue(value)

    def set_file_tag (self, text):
        self._ins.set_file_tag(str(text))

    def save_single(self):
        self._ins.save(data_index = '_single')

    # def save(self, **kw):
    #     data_index = kw.pop('data_index', '')
    #     fName = kw.pop('fname', None)
    #     if fName == None:
    #         if (self._scan_mngr.curr_task == 'lr_scan'):
    #             minL = str(int(10*self._scan_mngr.min_lambda))
    #             maxL = str(int(10*self._scan_mngr.max_lambda))
    #             fName =  datetime.now().strftime ('%H%M%S%f')[:-2] + '_' + self._scan_mngr.curr_task+'_'+minL+'_'+maxL
    #         else:
    #             fName =  datetime.now().strftime ('%H%M%S%f')[:-2] + '_' + self._scan_mngr.curr_task
    #         if self._scan_mngr.file_tag:
    #             fName = fName + '_' + self._scan_mngr.file_tag
        
    #     f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
    #     directory = os.path.join(f0, fName)
    #     if not os.path.exists(directory):
    #         os.makedirs(directory)
        
    #     f5 = h5py.File(os.path.join(directory, fName+'.hdf5'))

    #     if (self._scan_mngr.curr_task+'_processed_data_'+data_index) not in f5.keys():
    #         scan_grp = f5.create_group(self._scan_mngr.curr_task+'_processed_data_'+data_index)
    #     else:
    #         scan_grp = f5[self._scan_mngr.curr_task+'_processed_data_'+data_index]
    #     scan_grp.create_dataset(self._scan_mngr.saveX_label, data = self._scan_mngr.saveX_values)
    #     scan_grp.create_dataset(self._scan_mngr.saveY_label, data = self._scan_mngr.saveY_values)

    #     try:
    #         if 'raw_data_'+data_index not in f5.keys():
    #             data_grp = f5.create_group('raw_data_'+data_index)
    #         else:
    #             data_grp = f5['raw_data_'+data_index]
    #         for j in np.arange (self._scan_mngr.nr_avg_scans):
    #             data_grp.create_dataset('scannr_'+str(j+1), data = self._scan_mngr.data [j,:])
    #     except:
    #         print 'Unable to save data'
        
    #     try:
    #         if 'TimeStamps'+data_index not in f5.keys():
    #             time_grp = f5.create_group('TimeStamps'+data_index)
    #         else:
    #             time_grp = f5['TimeStamps'+data_index]
    #         time_grp.create_dataset('timestamps [ms]', data = self._scan_mngr.tstamps_ms)
    #     except:
    #         print 'Unable to save timestamps'

    #     #The below could be in a function save_msmt_params or so
    #     try:
    #         for k in self._scan_mngr.scan_params:
    #             f5.attrs [k] = self._scan_mngr.scan_params[k]
    #         for l in self.msmt_params: #ideally msmt_params should replace scan_params.
    #             f5.attrs [l] = self.msmt_params[l]

    #     except:
    #         print 'Unable to save scan params'

    #     f5.close()
        
    #     fig = plt.figure(figsize = (15,10))
    #     plt.plot (self._scan_mngr.saveX_values, self._scan_mngr.saveY_values, 'RoyalBlue')
    #     plt.plot (self._scan_mngr.saveX_values, self._scan_mngr.saveY_values, 'ob')
    #     plt.xlabel (self._scan_mngr.saveX_label, fontsize = 15)
    #     plt.ylabel (self._scan_mngr.saveY_label, fontsize = 15)
    #     plt.savefig (os.path.join(directory, fName+'_avg.png'))
    #     plt.close(fig)

    #     if (self._scan_mngr.nr_avg_scans > 1):
    #         fig = plt.figure(figsize = (15,10))
    #         colori = cm.gist_earth(np.linspace(0,0.75, self._scan_mngr.nr_avg_scans))
    #         for j in np.arange(self._scan_mngr.nr_avg_scans):
    #             plt.plot (self._scan_mngr.saveX_values, self._scan_mngr.data[j,:], color = colori[j])
    #             plt.plot (self._scan_mngr.saveX_values, self._scan_mngr.data[j,:], 'o', color = colori[j])
    #         plt.xlabel (self._scan_mngr.saveX_label, fontsize = 15)
    #         plt.ylabel (self._scan_mngr.saveY_label, fontsize = 15)
    #         plt.savefig (os.path.join(directory, fName+'.png'))
    #         plt.close(fig)     

    #     return fName

    # def save_2D_scan(self):

    #     fName = time.strftime ('%H%M%S') + '_2Dscan'
    #     if self._scan_mngr.file_tag:
    #         fName = fName + '_' + self._scan_mngr.file_tag
    #     f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
    #     directory = os.path.join(f0, fName)
    #     if not os.path.exists(directory):
    #         os.makedirs(directory)

    #     f5 = h5py.File(os.path.join(directory, fName+'.hdf5'))
    #     for k in np.arange (self.idx_2D_scan):
    #         scan_grp = f5.create_group(str(k))
    #         scan_grp.create_dataset('frq', data = self.dict_2D_scan ['frq_'+str(k)])
    #         scan_grp.create_dataset('sgnl', data = self.dict_2D_scan ['sgnl_'+str(k)])
    #         scan_grp.attrs['pzV'] = self.dict_2D_scan ['pzv_'+str(k)]
    #     f5.close()

    def set_minV_lengthscan(self, value):
        self._ins.set_minV_lengthscan(value)

    def set_maxV_lengthscan (self, value):
        self._ins.set_maxV_lengthscan(value)

    def set_nr_steps_lengthscan (self, value):
        self._ins.set_nr_steps_lengthscan(value)

    def set_minV_finelaser (self, value):
        self._ins.set_minV_finelaser(value)

    def set_maxV_finelaser (self, value):
        self._ins.set_maxV_finelaser(value)

    def set_nr_steps_finelaser (self, value):
        self._ins.set_nr_steps_finelaser(value)

    def set_wait_cycles (self, value):
        self._ins.set_wait_cycles(value)  


    def calibrate_finelaser(self):
        print 'CALIBRATE fine scan --- SvD: this function does ABSOLUTELY NOTHING. remove the button.' 

    def set_min_lambda (self, value):
        self._ins.set_minlambda_lrlaser(value)

    def set_max_lambda (self, value):
        self._ins.set_maxlambda_lrlaser(value)

    def set_nr_calib_pts (self, value):
        self._ins.set_nr_calib_pts_lrlaser(value)

    def set_steps_lr_scan (self, value):
        self._ins.set_nr_steps_lrlaser(value)

    def set_min_msyncdelay(self,value):
        self._ins.set_min_msyncdelay(value)

    def set_max_msyncdelay(self, value):
        self._ins.set_max_msyncdelay(value)

    def set_nr_steps_msyncdelay(self,value):
        self._ins.nr_steps_msyncdelay(value)

    def set_nr_scans_msync (self, value):
        '''
        this function seems to be a double of the 'nr_avg'. remove either.
        '''
        self._ins.set_nr_avg_scans(value)
        self.ui.sb_avg.setValue(value)

    def set_delay_msync (self, value):
        self._ins.set_sync_delay_ms(value)

    def set_nr_repetitions (self,value):
        self._ins.set_nr_repetitions(value)

        ############### start and stop functions
    def start_lengthscan(self):
        self._ins.start_lengthscan()

    def stop_lengthscan(self):
        self._ins.stop_lengthscan()

    def start_finelaser(self):
        self._ins.start_finelaser()

    def stop_finelaser(self):
        self._ins.stop_finelaser()
 
    def start_sweep_msyncdelay(self):
        self._ins.start_sweep_msyncdelay()

    def stop_sweep_msyncdelay(self):
        self._ins.stop_sweep_msyncdelay()

    def start_lr_scan(self):
        self._ins.start_lr_scan()

    def resume_lr_scan(self):
        self._ins.resume_lr_scan()

    def stop_lr_scan(self):
        self._ins.stop_lr_scan()

    # def start_lr_scan(self):
    #     if (self._running_task==None):
    #         if (self._scan_mngr.min_lambda>self._scan_mngr.max_lambda):
    #             self.curr_l = self._scan_mngr.min_lambda
    #             self._scan_direction = -1
    #         else:
    #             self.curr_l = self._scan_mngr.min_lambda
    #             self._scan_direction = +1

    #         print 'Scan direction: ', self._scan_direction
    #         print self.curr_l
    #         self.lr_scan_frq_list = []
    #         self.lr_scan_sgnl_list = []
    #         self._running_task = 'lr_laser_scan'

    # def resume_lr_scan(self):
    #     if (self._running_task==None):
    #         self._running_task = 'lr_laser_scan'

    # def stop_lr_scan(self):
    #     if (self._running_task == 'lr_laser_scan'):
    #         self._running_task = None
    #         self._2D_scan_is_active = False
    #         print 'Stopping!'

    def start_2D_scan(self):
        self._ins.start_2D_scan()

    # def activate_2D_scan (self):
    #     if (self._running_task==None):
    #         self.curr_pz_volt = self._ins.minV_lengthscan
    #         self._exp_mngr.set_piezo_voltage (self.curr_pz_volt) 
    #         self.pzV_step = (self._scan_mngr.maxV_lengthscan-self._scan_mngr.minV_lengthscan)/float(self._scan_mngr.nr_steps_lengthscan)
    #         self.dict_2D_scan = {}
    #         self.dict_pzvolt = {}
    #         self._2D_scan_is_active = True
    #         if (self._scan_mngr.min_lambda>self._scan_mngr.max_lambda):
    #             self.curr_l = self._scan_mngr.min_lambda
    #             self._scan_direction = -1
    #         else:
    #             self.curr_l = self._scan_mngr.min_lambda
    #             self._scan_direction = +1            
    #         self.lr_scan_frq_list = np.array([])
    #         self.lr_scan_sgnl_list = np.array([])
    #         self._running_task = 'lr_laser_scan'
    #         self.idx_2D_scan = 0

    # def run_update_2D_scan (self):

    #     #store current laserscan in dictionary
    #     self.dict_2D_scan ['pzv_'+str(self.idx_2D_scan)] = self.curr_pz_volt
    #     self.dict_2D_scan ['frq_'+str(self.idx_2D_scan)] = np.asarray(self._scan_mngr.saveX_values).flatten()
    #     self.dict_2D_scan ['sgnl_'+str(self.idx_2D_scan)] = np.asarray(self._scan_mngr.saveY_values).flatten()

    #     #update paramter values
    #     self.idx_2D_scan = self.idx_2D_scan + 1
    #     self.curr_pz_volt = self.curr_pz_volt + self.pzV_step

    #     if (self.curr_pz_volt<self._scan_mngr.maxV_lengthscan):
    #         self._exp_mngr.set_piezo_voltage (self.curr_pz_volt)
    #         print 'New pzV = ', self.curr_pz_volt
    #         self.curr_l = self._scan_mngr.min_lambda
    #         self.lr_scan_frq_list = np.array([])
    #         self.lr_scan_sgnl_list = np.array([])
    #         self._running_task = 'lr_laser_scan'
    #     else:
    #         self.curr_pz_volt = self.curr_pz_volt - self.pzV_step
    #         self.save_2D_scan()
    #         self._running_task = None
    #         self._2D_scan_is_active = False

    # def run_new_lengthscan(self, **kw):
    #     enable_autosave = kw.pop('enable_autosave',True)
    #     self.reinitialize()
    #     self.ui.label_status_display.setText("<font style='color: red;'>SCANNING PIEZOs</font>")
    #     self._scan_mngr.set_scan_params (v_min=self._scan_mngr.minV_lengthscan, v_max=self._scan_mngr.maxV_lengthscan, nr_points=self._scan_mngr.nr_steps_lengthscan)
    #     self._scan_mngr.initialize_piezos(wait_time=1)

    #     #self._scan_mngr.sync_delays_ms = np.ones(self._scan_mngr.nr_avg_scans)*sync_delay_ms

    #     self._scan_mngr.length_scan ()
    #     self.ui.label_status_display.setText("<font style='color: red;'>idle</font>")
    #     if self._scan_mngr.success:
    #         self.ui.plot_canvas.update_plot (x = self._scan_mngr.v_vals, y=self._scan_mngr.data[0], x_axis = 'piezo voltage [V]', 
    #                     y_axis = 'photodiode signal (a.u.)', color = 'RoyalBlue')
    #         self._scan_mngr.saveX_values = self._scan_mngr.v_vals
    #         self._scan_mngr.saveY_values = self._scan_mngr.PD_signal
    #         self._scan_mngr.save_tstamps_ms = self._scan_mngr.tstamps_ms                  
    #         self._scan_mngr.saveX_label = 'piezo_voltage'
    #         self._scan_mngr.saveY_label = 'PD_signal'
    #         self._scan_mngr.save_scan_type = 'msync'
    #         self._scan_mngr.curr_task = 'length_scan'
    #     else:        
    #         msg_text = 'Cannot Sync to Montana signal!'
    #         ex = MsgBox(msg_text = msg_text)
    #         ex.show()
    #         self._scan_mngr.curr_task = None
      
    #     if self._scan_mngr.autosave and enable_autosave:
    #         self.save()
    #     if self._scan_mngr.autostop:
    #         self._running_task = None
    #         self._exp_mngr.set_piezo_voltage (V = self._exp_mngr._fine_piezos)

    #     return self._scan_mngr.success

    # def run_new_fine_laser_scan(self):

    #     self.reinitialize()
    #     self.ui.label_status_display.setText("<font style='color: red;'>FINE LASER SCAN</font>")
    #     self._scan_mngr.set_scan_params (v_min=self._scan_mngr.minV_finelaser, v_max=self._scan_mngr.maxV_finelaser, nr_points=self._scan_mngr.nr_steps_finelaser)
    #     self._scan_mngr.laser_scan(use_wavemeter = False)
    #     self.ui.plot_canvas.update_plot (x = self._scan_mngr.v_vals, y=self._scan_mngr.data[0], x_axis = 'laser-tuning voltage [V]', 
    #                 y_axis = 'photodiode signal (a.u.)', color = 'b')
    #     self._scan_mngr.saveX_values = self._scan_mngr.v_vals
    #     self._scan_mngr.saveY_values = self._scan_mngr.PD_signal  
    #     self._scan_mngr.saveX_label = 'laser_tuning_voltage'
    #     self._scan_mngr.saveY_label = 'PD_signal'        
    #     self._scan_mngr.curr_task = 'fine_laser_scan'
    #     self.ui.label_status_display.setText("<font style='color: red;'>idle</font>")

    #     if self._scan_mngr.autosave:
    #         self.save()
    #     if self._scan_mngr.autostop:
    #         self._running_task = None

    # def run_new_sweep_msyncdelay(self):
    #     print "starting a new sweep of the montana sync delay"
    #     self.initialize_msmt_params()
    #     #calculate nr of sync pulses in which nr_scans = nr_scans, and remainder nr_scans in last sync pulse
    #     nr_syncs_per_pt,nr_remainder = divmod(self._scan_mngr.nr_repetitions, self._scan_mngr.nr_avg_scans)
    #     #create the array with the sync_delay values to sweep
    #     sync_delays = np.linspace(self._scan_mngr.min_msyncdelay,self._scan_mngr.max_msyncdelay,self._scan_mngr.nr_steps_msyncdelay)
    #     print sync_delays

    #     self.msmt_params['sync_delays'] = sync_delays
    #     self.msmt_params['sweep_pts'] = sync_delays
    #     self.msmt_params['sweep_name'] = 'sync delay (ms)'
    #     self.msmt_params['sweep_length'] = len(sync_delays)
    #     self.msmt_params['nr_repetitions'] = self._scan_mngr.nr_repetitions
    #     if nr_remainder > 0: #then you need one more sync to finish all repetitions
    #         nr_syncs_per_pt = nr_syncs_per_pt+1
    #     self.msmt_params['nr_syncs_per_pt'] = nr_syncs_per_pt
    #     self.msmt_params['nr_remainder'] = nr_remainder

    #     #create a local variable of nr_avg_scans and sync_delay_ms to remember the setting
    #     nr_avg_scans = self._scan_mngr.nr_avg_scans
    #     sync_delay_ms = self._scan_mngr.sync_delay_ms
    #     print 'syncs per pt',nr_syncs_per_pt
    #     print 'remaining',nr_remainder
    #     print 'scans per sync',nr_avg_scans

    #     fname = None

    #     for i in np.arange(nr_syncs_per_pt):
    #         if self._running_task == None:
    #             print 'measurement stopping'
    #             break
    #         if (i == nr_syncs_per_pt-1): #the last one
    #             if nr_remainder>0:
    #                 #set the nr_avg_scans to the remainder number of scans
    #                 self._scan_mngr.nr_avg_scans = nr_remainder
    #         print "sync nr ",i+1," of ", nr_syncs_per_pt


    #         for j,sync_delay_j in enumerate(sync_delays):
    #             self._scan_mngr.sync_delay_ms = sync_delay_j
    #             print 'sync delay value ', j+1 ,' of ', len(sync_delays), ': ',sync_delay_j
    #             first_rep = str(int(i*nr_avg_scans+1))
    #             last_rep = str(int(i*nr_avg_scans+self._scan_mngr.nr_avg_scans))
    #             data_index_name = 'sweep_pt_'+str(j)+'_reps_'+first_rep+'-'+last_rep
    #             self.run_new_lengthscan(enable_autosave=False)
    #             fname = self.save(fname=fname, 
    #                 data_index = data_index_name)
        
    #     #reset the nr_avg_scans in the scan_manager
    #     self._scan_mngr.nr_avg_scans = nr_avg_scans
    #     self._scan_mngr.sync_delay_ms = sync_delay_ms

    #     #always stop after the mmt
    #     self._running_task = None


    # def fit_calibration(self, V, freq, fixed):
    #     guess_b = -21.3
    #     guess_c = -0.13
    #     guess_d = 0.48
    #     guess_a = freq[0] +3*guess_b-9*guess_c+27*guess_d

    #     a = fit.Parameter(guess_a, 'a')
    #     b = fit.Parameter(guess_b, 'b')
    #     c = fit.Parameter(guess_c, 'c')
    #     d = fit.Parameter(guess_d, 'd')

    #     p0 = [a, b, c, d]
    #     fitfunc_str = ''

    #     def fitfunc(x):
    #         return a()+b()*x+c()*x**2+d()*x**3


    #     fit_result = fit.fit1d(V,freq, None, p0=p0, fitfunc=fitfunc, fixed=fixed,
    #             do_print=False, ret=True)
    #     if (len(fixed)==2):
    #         a_fit = fit_result['params_dict']['a']
    #         c_fit = fit_result['params_dict']['c']
    #         return a_fit, c_fit
    #     else:
    #         a_fit = fit_result['params_dict']['a']
    #         b_fit = fit_result['params_dict']['b']
    #         c_fit = fit_result['params_dict']['c']
    #         d_fit = fit_result['params_dict']['d']
    #         return a_fit, b_fit, c_fit, d_fit

    # def run_new_lr_laser_scan (self):

    #     #first decide how to approach the calibration, 
    #     #depending on the number of calibration pts.
    #     #This is the number of points actually measured on the wavemeter
    #     #(should be minimized to keep the scan fast)

    #     self.reinitialize()
    #     nr_calib_pts = self._scan_mngr.nr_calib_pts
    #     b0 = -21.3
    #     c0 = -0.13
    #     d0 = 0.48
    #     self._exp_mngr.set_laser_wavelength(self.curr_l)
    #     qt.msleep (0.1)
    #     if self._2D_scan_is_active:
    #         self.ui.label_status_display.setText("<font style='color: red;'>LASER SCAN: "+str(self.curr_l)+"nm - pzV = "+str(self.curr_pz_volt)+"</font>")
    #     else:
    #         self.ui.label_status_display.setText("<font style='color: red;'>LASER SCAN: "+str(self.curr_l)+"nm</font>")

    #     #acquire calibration points
    #     dac_no = self._exp_mngr._adwin.dacs['newfocus_freqmod']
    #     print "DAC no ", dac_no
    #     self._exp_mngr._adwin.start_set_dac(dac_no=dac_no, dac_voltage=-3)
    #     qt.msleep (0.1)
    #     V_calib = np.linspace (-3, 3, nr_calib_pts)
    #     f_calib = np.zeros(nr_calib_pts)
    #     print "----- Frequency calibration routine:"
    #     for n in np.arange (nr_calib_pts):
    #         qt.msleep (0.3)
    #         self._exp_mngr._adwin.start_set_dac(dac_no = dac_no, dac_voltage = V_calib[n])
    #         print "Point nr. ", n, " ---- voltage: ", V_calib[n]
    #         qt.msleep (0.5)
    #         f_calib[n] = self._exp_mngr._wm_adwin.Get_FPar (self._exp_mngr._wm_port)
    #         qt.msleep (0.2)
    #         print "        ", n, " ---- frq: ", f_calib[n]

    #     print 'f_calib:', f_calib
    #     #finel laser scan
    #     self._scan_mngr.set_scan_params (v_min=-3, v_max=3, nr_points=self._scan_mngr.nr_steps_lr_scan) #real fine-scan
    #     self._scan_mngr.laser_scan(use_wavemeter = False)
    #     V = self._scan_mngr.v_vals
    #     if (nr_calib_pts==1):
    #         V_calib = int(V_calib)
    #         f_calib = int(f_calib)
    #         b = b0
    #         c = c0
    #         d = d0
    #         a = f_calib + 3*b - 9*c + 27*d
    #     elif ((nr_calib_pts>1) and (nr_calib_pts<4)):
    #         a, c = self.fit_calibration(V = V_calib, freq = f_calib, fixed=[1,3])
    #         b = b0
    #         d = d0
    #     else:
    #         a, b, c, d = self.fit_calibration(V = V_calib, freq = f_calib, fixed=[])
    #     freq = a + b*V + c*V**2 + d*V**3

    #     self.lr_scan_frq_list =  np.append(self.lr_scan_frq_list,freq)
    #     self.lr_scan_sgnl_list  = np.append(self.lr_scan_sgnl_list, self._scan_mngr.PD_signal)

    #     if self._2D_scan_is_active and (self.idx_2D_scan != 0):
    #         if self.lr_scan_sgnl.ndim == 1:
    #             self.lr_scan_sgnl = np.array([self.lr_scan_sgnl])
    #         self.lr_scan_sgnl_list = np.array([self.lr_scan_sgnl_list])

    #         print 'appending ',np.shape(self.lr_scan_sgnl),' to ',np.shape(self.lr_scan_sgnl_list)

    #         self.lr_scan_sgnl = np.append(self.lr_scan_sgnl,self.lr_scan_sgnl_list,axis=0)
    #         print 'results in: ',np.shape(self.lr_scan_sgnl)
    #     else:
    #         self.lr_scan_frq = (np.array(self.lr_scan_frq_list)).flatten()
    #         self.lr_scan_sgnl = (np.array(self.lr_scan_sgnl_list)).flatten()

    #     self.ui.plot_canvas.update_multiple_plots (x = self.lr_scan_frq, y=self.lr_scan_sgnl, x_axis = 'laser frequency (GHz)', 
    #             y_axis = 'photodiode signal (a.u.)', autoscale=False, color = 'none')

    #     self._scan_mngr.saveX_values = self.lr_scan_frq
    #     self._scan_mngr.saveY_values = self.lr_scan_sgnl  
    #     self._scan_mngr.saveX_label = 'frequency_GHz'
    #     self._scan_mngr.saveY_label = 'PD_signal'
    #     self._scan_mngr.curr_task = 'lr_scan'
    #     self.ui.label_status_display.setText("<font style='color: red;'>idle</font>")

    #     self.curr_l = self.curr_l + self._scan_direction*self.coarse_wavelength_step
    #     print 'New wavelength: ', self.curr_l
    #     if (self._scan_direction > 0):
    #         print 'Scan cond: l>max_l'
    #         stop_condition = (self.curr_l>=self._scan_mngr.max_lambda)
    #     else:
    #         print 'Scan cond: l<min_l'
    #         stop_condition = (self.curr_l<=self._scan_mngr.max_lambda)

    #     if stop_condition:
    #         if self._2D_scan_is_active:
    #             self._running_task = 'update_2D_scan'
    #         else:
    #             self._running_task = None
    #             if self._scan_mngr.autosave:
    #                 self.save()
    #     else:
    #         self._running_task = 'lr_laser_scan'

    # def reinitialize (self):
    #     self._scan_mngr.data = None
    #     self._scan_mngr.PD_signal = None
    #     self._scan_mngr.tstamps_ms = None
    #     self._scan_mngr.scan_params = None


    #Ithink in the new Panel environment you don't need this
    # def fileQuit(self):
    #     self.close()

    # def fileSave(self):
    #     self.dc.save()

    # def closeEvent(self, ce):
    #     self.fileQuit()



