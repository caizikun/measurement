########################################
# Cristian Bonato, 2015
# cbonato80@gmail.com
########################################

from __future__ import unicode_literals
import os, sys, time
# from PySide.QtCore import *
# from PySide.QtGui import *
import random
from matplotlib.backends import qt4_compat
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore, uic
else:
    from PyQt4 import QtGui, QtCore, uic

# import pylab as plt
# import h5py
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# from matplotlib import cm
# from analysis.lib.fitting import fit
# import measurement.lib.cavity.panels.scan_gui_panels 
# import measurement.lib.cavity.panels.ui_scan_panel_v9
# import measurement.lib.cavity.panels.XYscan_panel 

from ui_cav_scan_panel import Ui_Panel as Ui_Scan 

from panel import Panel
from panel import MsgBox

class ScanPanel(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self,parent,*arg,**kw)

        self.ui = Ui_Scan()
        self.ui.setupUi(self)

        # self.ui.plot_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        #SETTINGS EVENTS
        self.ui.sb_avg.setRange(1, 999)
        #XXXself.ui.sb_integration_cycles.setRange(1, 999)
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
        #XXXself.ui.cb_scan_auto_reverse.stateChanged.connect(self.scan_auto_reverse)
        self.ui.sb_avg.valueChanged.connect(self.set_avg)
        self.ui.button_save.clicked.connect(self.save_single)
        #JPE piezo-Scan:
        self.ui.dsb_minV_pzscan.valueChanged.connect(self._ins.set_minV_lengthscan)
        self.ui.dsb_maxV_pzscan.valueChanged.connect(self._ins.set_maxV_lengthscan)
        self.ui.sb_nr_steps_pzscan.valueChanged.connect(self._ins.set_nr_steps_lengthscan)
        self.ui.sb_wait_cycles.valueChanged.connect(self._ins.set_wait_cycles)
        #XXXself.ui.sb_integration_cycles.valueChanged.connect(self._ins.set_ADC_averaging_cycles)
        self.ui.button_start_pzscan.clicked.connect(self.start_lengthscan)
        self.ui.button_stop_pzscan.clicked.connect(self.stop_lengthscan)
        #FineLaser-Scan:
        self.ui.dsb_minV_finelaser.valueChanged.connect(self._ins.set_minV_finelaser)
        self.ui.dsb_maxV_finelaser.valueChanged.connect(self._ins.set_maxV_finelaser)
        self.ui.sb_nr_steps_finelaser.valueChanged.connect(self._ins.set_nr_steps_finelaser)
        self.ui.button_start_finelaser.clicked.connect(self.start_finelaser)
        self.ui.button_stop_finelaser.clicked.connect(self.stop_finelaser)

        #Sweep sync montana delays:
        self.ui.sb_mindelay_msync.valueChanged.connect(self._ins.set_min_msyncdelay)
        self.ui.sb_maxdelay_msync.valueChanged.connect(self._ins.set_max_msyncdelay)
        self.ui.button_start_sweepdelay.clicked.connect(self.start_sweep_msyncdelay)
        self.ui.button_stop_sweepdelay.clicked.connect(self.stop_sweep_msyncdelay)
        self.ui.sb_nr_steps_msyncdelay.valueChanged.connect(self._ins.set_nr_steps_msyncdelay)


        #Other buttons
        self.ui.lineEdit_fileName.textChanged.connect(self._ins.set_file_tag)
        #self.ui.button_timeseries.clicked.connect (self.activate_timeseries)
        # self.ui.button_2D_scan.clicked.connect (self.start_2D_scan)
        #self.ui.button_track.clicked.connect (self.activate_track)
        #self.ui.button_slowscan.clicked.connect (self.activate_slowscan)
        self.ui.cb_montana_sync.stateChanged.connect (self.montana_sync)
        self.ui.sb_delay_msync.valueChanged.connect(self._ins.set_sync_delay_ms)
        self.ui.sb_nr_scans_msync.valueChanged.connect(self.set_nr_scans_msync)
        self.ui.sb_nr_repetitions.valueChanged.connect(self._ins.set_nr_repetitions)

        #INITIALIZATIONS:
        #JPE piezo-scan
        self.ui.dsb_minV_pzscan.setValue(self._ins.get_minV_lengthscan())
        self.ui.dsb_maxV_pzscan.setValue(self._ins.get_maxV_lengthscan())
        self.ui.sb_nr_steps_pzscan.setValue(self._ins.get_nr_steps_lengthscan())
        #general
        self._ins.averaging_samples = 1
        self.ui.sb_avg.setValue(self._ins.get_nr_avg_scans())
        self._ins.autosave = False
        self._ins.autostop = False
        #fine laser scan
        self.ui.dsb_minV_finelaser.setValue(self._ins.get_minV_finelaser())
        self.ui.dsb_maxV_finelaser.setValue(self._ins.get_maxV_finelaser())
        self.ui.sb_nr_steps_finelaser.setValue(self._ins.get_nr_steps_finelaser())
        self.ui.sb_wait_cycles.setValue(self._ins.get_wait_cycles())

        #sweep montana sync delays
        self.ui.sb_mindelay_msync.setValue(self._ins.get_min_msyncdelay())
        self.ui.sb_maxdelay_msync.setValue(self._ins.get_max_msyncdelay())
        self.ui.sb_nr_steps_msyncdelay.setValue(self._ins.get_nr_steps_msyncdelay())
        #others
        self._ins.file_tag = ''
        self._2D_scan_is_active = False
        self._use_sync = False
        self.ui.sb_nr_scans_msync.setValue(self._ins.get_nr_avg_scans())
        self.set_nr_scans_msync(self._ins.get_nr_avg_scans())
        self.ui.sb_delay_msync.setValue(self._ins.get_sync_delay_ms())
        self.ui.sb_nr_repetitions.setValue(self._ins.get_nr_repetitions())

        # set up plot
        self.ui.plot.bottom_axis.title = 'V [V]'
        self.ui.plot.left_axis.title = 'transmission [a.u.]'
        self.ui.plot.plot.padding = 5
        self.ui.plot.plot.padding_bottom = 70
        self.ui.plot.plot.padding_left = 50

        self._ins.set_task_is_running(False)
        #TIMER:
        # self.refresh_time = 100
        # self.timer = QtCore.QTimer(self)
        # self.timer.timeout.connect(self.manage_tasks)
        # self.timer.start(self.refresh_time)

    def _instrument_changed(self,changes):
        Panel._instrument_changed(self, changes)
        if changes.has_key('status_label'):
            self.ui.label_status_display.setText(str(changes['status_label']))
        if changes.has_key('minV_lengthscan'): 
            self.ui.dsb_minV_pzscan.setValue(changes['minV_lengthscan'])
        if changes.has_key('maxV_lengthscan'): 
            self.ui.dsb_maxV_pzscan.setValue(changes['maxV_lengthscan'])
        if changes.has_key('nr_steps_lengthscan'): 
            self.ui.sb_nr_steps_pzscan.setValue(changes['nr_steps_lengthscan'])


        if 'data_update' in changes:
            d = changes['data_update']
            if 'x' in d[0]:
                print 'not true!'          
            if 'v_vals' in d[0]:
                self.ui.plot.set_x(self._data['v_vals'])
            if 'PD_signal' in d[0]:
                self.ui.plot.add_y(self._data['PD_signal'],'PD_signal')
        return True
   
        
        #changes = self._scan_mngr.get_data_update()

    #I think I need to keep this for the refreshing.

    # def manage_tasks(self):
    #     self._ins.manage_tasks()

    # def manage_tasks (self):
    #     if (self._running_task == 'lengthscan'):
    #         self.run_new_lengthscan()
    #     elif (self._running_task == 'fine_laser_scan'):
    #         self.run_new_fine_laser_scan()
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

    def scan_auto_reverse (self, state):
        if state == QtCore.Qt.Checked:
            self._ins.set_scan_auto_reverse(True)
        else:
            self._ins.set_scan_auto_reverse(False)

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

    def set_nr_scans_msync (self, value):
        '''
        this function seems to be a double of the 'nr_avg'. remove either.
        '''
        self._ins.set_nr_avg_scans(value)
        self.ui.sb_avg.setValue(value)


    def save_single(self):
        self._ins.save(data_index = '_single')

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



