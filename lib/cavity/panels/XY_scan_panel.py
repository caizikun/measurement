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
import measurement.lib.cavity.cavity_scan_v2
import measurement.lib.cavity.panels.scan_gui_panels 
import measurement.lib.cavity.panels.control_panel_2
import measurement.lib.cavity.panels.ui_scan_panel_v9
import measurement.lib.cavity.panels.slow_piezo_scan_panel
import measurement.lib.cavity.panels.XYscan_panel 

from measurement.lib.cavity.cavity_scan_v2 import CavityExpManager, CavityScan
from measurement.lib.cavity.panels.scan_gui_panels import MsgBox, ScanPlotCanvas
from measurement.lib.cavity.panels.control_panel_2 import Ui_Dialog as Ui_Form
from measurement.lib.cavity.panels.scan_panel_v9 import Ui_Form as Ui_Scan
from measurement.lib.cavity.panels.XYscan_panel import Ui_Form as Ui_XYScan


class XYScanGUI (Panel):
    def __init__(self, parent, *arg, **kw):

        self.ui = Ui_XYScan()
        self.ui.setupUi(self)
        self._exp_mngr = exp_mngr
        self.ui.dsb_set_x_min.setMinimum(-999.0)
        self.ui.dsb_set_x_max.setMinimum(-999.0)
        self.ui.dsb_set_y_min.setMinimum(-999.0)
        self.ui.dsb_set_y_max.setMinimum(-999.0)
        self.ui.dsb_set_x_min.setMaximum(999.0)
        self.ui.dsb_set_x_max.setMaximum(999.0)
        self.ui.dsb_set_y_min.setMaximum(999.0)
        self.ui.dsb_set_y_max.setMaximum(999.0)

        #SETTINGS EVENTS
        self.ui.dsb_set_nr_steps_x.valueChanged.connect(self.set_nr_steps_x)
        self.ui.dsb_set_nr_steps_y.valueChanged.connect(self.set_nr_steps_y)
        self.ui.dsb_set_x_min.valueChanged.connect(self.set_x_min)
        self.ui.dsb_set_x_max.valueChanged.connect(self.set_x_max)
        self.ui.dsb_set_y_min.valueChanged.connect(self.set_y_min)
        self.ui.dsb_set_y_max.valueChanged.connect(self.set_y_max)
        self.ui.dsb_set_acq_time.valueChanged.connect (self.set_acq_time)
        
        self.ui.pushButton_scan.clicked.connect (self.start_scan)
        self.ui.pushButton_stop.clicked.connect (self.stop_scan)
        self.ui.pushButton_save.clicked.connect (self.save_scan)

        #self.ui.button_save.clicked.connect (self.stop)

        self._curr_task = None
        self._x_min = 0
        self._x_max = 0
        self._y_min = 0
        self._y_max = 0
        self._nr_steps_x = 0
        self._nr_steps_y = 0

        #TIMER:
        self.refresh_time = 50
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.manage_tasks)
        self.timer.start(self.refresh_time)
        self._exp_mngr._ctr.set_is_running (True)


    def save_scan (self):
        fName = time.strftime ('%H%M%S') + '_XYScan'
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            f5 = h5py.File(os.path.join(directory, fName+'.hdf5'))
            scan_grp = f5.create_group('XYScan')
            scan_grp.create_dataset('X', data = self.X)
            scan_grp.create_dataset('Y', data = self.Y)
            scan_grp.create_dataset('cts', data = self._counts)
            f5.close()
        except:
            print("datafile not saved!")

        try:
            fig = plt.figure()
            plt.pcolor (self.X, self.Y, self._counts, cmap = 'gist_earth')
            plt.colorbar()
            plt.xlabel ('x [$\mu$m', fontsize = 15)
            plt.ylabel ('y [$\mu$m', fontsize = 15)
            plt.axis ('equal')
            plt.savefig (os.path.join(directory, fName+'.png'))
            plt.close(fig)
        except:
            print("figure not saved!")

    def manage_tasks (self):
        if (self._curr_task == 'scan'):
            self.acquire_new_point()
        else:
            idle = True

    def set_nr_steps_x (self, value):
        self._nr_steps_x = value

    def set_nr_steps_y (self, value):
        self._nr_steps_y = value

    def set_x_min (self, value):
        self._x_min = value

    def set_x_max (self, value):
        self._x_max = value

    def set_y_min (self, value):
        self._y_min = value

    def set_y_max (self, value):
        self._y_max = value

    def set_acq_time (self, value):
        self._acq_time = value
        self._exp_mngr._ctr.set_integration_time (value)

    def settings_correct (self):
        return (self._x_max>= self._x_min) and (self._y_max>= self._y_min) and (self._nr_steps_x > 0) and (self._nr_steps_y > 0)

    def initialize_arrays(self):
        self._x_points = np.linspace (self._x_min, self._x_max, self._nr_steps_x)
        self._y_points = np.linspace (self._y_min, self._y_max, self._nr_steps_y)
        self.X, self.Y = np.meshgrid (self._x_points, self._y_points)


        print self._x_points, self._y_points
        print "X:"
        print self.X
        print "Y:"
        print self.Y
        self._counts = np.zeros(np.shape (self.X))

    def start_scan (self):

        if (self._exp_mngr.room_T == None and self._exp_mngr.low_T == None):
            msg_text = 'Set temperature before moving PiezoKnobs!'
            ex = MsgBox(msg_text=msg_text)
            ex.show()
        else:            
            if self.settings_correct():
                print 'Settings correct!'
                self.initialize_arrays()
                self._curr_row = 0
                self._curr_col = 0
                self._scan_step = +1
                self._curr_task = 'scan'
            else:
                print 'Check settings!'

    def acquire_new_point (self):
        #print "Curr pos: ", self._curr_row, self._curr_col
        #
        # ---------- TO FIX: -------------
        #imgshow in scan_panel_gui, which plots the 2D plot, has "shifted axes"
        #need to calculate what to feed in, instaed of self._x_points and self._y_points
        x = self.X[self._curr_row, self._curr_col]
        y = self.Y[self._curr_row, self._curr_col]
        print 'Point:', x, y
        self.move_pzk (x=x, y=y)
        cts = self.get_counts ()
        self._counts [self._curr_row, self._curr_col] = cts
        self._curr_col = self._curr_col + self._scan_step
        if (self._curr_col>=self._nr_steps_x):
            self._curr_col = int(self._nr_steps_x-1)
            self._curr_row = int(self._curr_row + 1)
            self._scan_step = self._scan_step*(-1) #start scanning in the oposite direction
            self.ui.xy_plot.update_plot(x = self.X, y = self.Y, cts = self._counts)
        elif (self._curr_col<0):
            self._curr_col = 0
            self._curr_row = int(self._curr_row + 1)
            self._scan_step = self._scan_step*(-1)
            self.ui.xy_plot.update_plot(x = self.X, y = self.Y, cts = self._counts)
        if (self._curr_row >= self._nr_steps_y):
            #self.ui.xy_plot.colorbar()
            self._curr_task = None
            self.save_scan()

    def stop_scan (self):
        self._curr_task = None
        self.save_scan()

    def move_pzk (self, x, y):
        #x, yt are in microns. We need to divide by 1000 because MOC works in mm.
        curr_x, curr_y, curr_z = self._exp_mngr._moc.get_position() #here positions are in mm
        print "JPE MOVING!"
        print "Now we are in ", curr_x, curr_y, curr_z
        print "we will move to ", x/1000., y/1000., curr_z
        s1, s2, s3 = self._exp_mngr._moc.motion_to_spindle_steps (x=x/1000., y=y/1000., z=curr_z, update_tracker=False)
        self._exp_mngr._moc.move_spindle_steps (s1=s1, s2=s2, s3=s3, x=x/1000., y=y/1000., z=curr_z)
        self._exp_mngr._moc_updated = True

    def get_counts (self):
        #if not(self._exp_mngr._ctr.get_is_running()):
        #    self._exp_mngr._ctr.set_is_running()
        #cts = self._exp_mngr._ctr.get_cntr1_countrate()
        #cts = int(random.random()*1000)
        #print 'counts...', cts
        cts = self._exp_mngr._adwin.read_photodiode()
        return cts

