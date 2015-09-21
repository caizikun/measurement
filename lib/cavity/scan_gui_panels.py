
from __future__ import unicode_literals
import os, sys, time
from PySide.QtCore import *
from PySide.QtGui import *
import random
import numpy as np
from matplotlib.backends import qt4_compat
from matplotlib import cm
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore, uic
else:
    from PyQt4 import QtGui, QtCore, uic

import pylab as plt
import h5py
import time
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MsgBox(QtGui.QDialog):
    def __init__(self, msg_text = 'What to do?', parent=None):
        super(MsgBox, self).__init__(parent)

        msgBox = QtGui.QMessageBox()
        msgBox.setText(msg_text)
        msgBox.addButton(QtGui.QPushButton('Accept'), QtGui.QMessageBox.YesRole)
        msgBox.addButton(QtGui.QPushButton('Reject'), QtGui.QMessageBox.NoRole)
        self.ret = msgBox.exec_();

class TrackCanvas (FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def add_plot_matrix (self, x, y, nr_tracks, nr_steps):
        x1 = x.reshape (nr_tracks, nr_steps)
        y1 = y.reshape (nr_tracks, nr_steps)

        for i in np.arange (nr_tracks):
            self.axes.plot(x1[i,:], y1[i,:], linewidth = 2)
        self.axes.set_xlabel ('piezo voltage [V]')
        self.axes.set_ylabel ('photodiode signal')
        self.draw()


class ScanPlotCanvas (FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_plot (self, x, y, x_axis, y_axis, color, autoscale=False):
        self.axes.plot(x, y, '.', color=color, linewidth =2)
        self.axes.set_xlabel(x_axis)
        self.axes.set_ylabel(y_axis)
        if autoscale:
            self.axes.set_ylim ([min(y), max(y)])
        self.draw()

    def update_multiple_plots (self, x, y, x_axis, y_axis, autoscale=False):
        rows, cols = np.shape (y)
        colori = cm.gist_earth(np.linspace(0,0.75, rows))
        for j in np.arange(rows):
            
            self.axes.plot(x, y[j,:], linewidth =2)
            self.axes.set_xlabel(x_axis)
            self.axes.set_ylabel(y_axis)
            self.draw()
            time.sleep (0.01)


class MyCanvas(FigureCanvas):

    def __init__(self,  scan_manager, status_label, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        # Clear axes every time plot() is called
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        #FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self._scan_manager = scan_manager
        self._status_label = status_label
        self.refresh_time = 100
        self.name = self._scan_manager.name
        self._task = None

    def save(self):
        if self.name:
            name = '_'+self.name
        else:
            name = ''
        time_stamp = time.strftime ('%Y%m%d_%H%M%S')
        fName = time_stamp + '_scan_'+self._task
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)

        if not os.path.exists(directory):
            os.makedirs(directory)

        f = plt.figure()
        ax = f.add_subplot(1,1,1)
        ax.plot (self._scan_manager.v_for_saving, self._scan_manager.PD_for_saving, '.b', linewidth = 2)
        ax.set_xlabel ('voltage [V]')
        ax.set_ylabel ('photodiode signal [a.u.]')
        ax.set_title (time_stamp)
        f.savefig(os.path.join(directory, fName+'.png'))
        
        f = h5py.File(os.path.join(directory, fName+'.hdf5'))
        #f.attrs ['laser_power'] = self._laserscan.laser_power
        #f.attrs ['laser_wavelength'] = self._laserscan.laser_wavelength
        scan_grp = f.create_group('laserscan')
        scan_grp.create_dataset('V', data = self._scan_manager.v_for_saving)
        scan_grp.create_dataset('PD_signal', data = self._scan_manager.PD_for_saving)
        #scan_grp.create_dataset('wm_frequency', data = self._scan_manager.frequencies)
        f.close()



class ScanCanvas(MyCanvas):

    def __init__(self, *args, **kwargs):
        MyCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_plot)
        timer.start(self.refresh_time)

    def update_laserscan(self):
        self._status_label.setText("<font style='color: red;'>SCANNING LASER</font>")
        self._task = 'laser'
        self._scan_manager.laser_scan(use_wavemeter = self.use_wm, fine_scan=True, avg_nr_samples = self.averaging_samples)
        #self.random_noise = 0*0.1*np.random.rand(len(self._laserscan.v_vals))
        if self.use_wm:
            print 'Use_wm!!'
            self.axes.plot(self._scan_manager.frequencies, self._scan_manager.PD_signal, '.b', linewidth =2)
            self.axes.set_xlabel ('frequency [GHz]')
        else:
            self.axes.plot(self._scan_manager.v_vals, self._scan_manager.PD_signal, '.b', linewidth =2)
            self.axes.set_xlabel ('voltage [V]')            
        self.axes.set_ylabel('photodiode signal [a.u.]')
        self.axes.set_ylim ([min(self._scan_manager.PD_signal), max(self._scan_manager.PD_signal)])
        self._scan_manager.v_for_saving = self._scan_manager.v_vals
        self._scan_manager.PD_for_saving = self._scan_manager.PD_signal        
        self.draw()
        if self.autosave:
            print "Saving..."
            self.save()
        if self.autostop:
            self.scan_laser_running = False

    def calibrate_laser_frequency(self):
        self._status_label.setText("<font style='color: red;'>CALIBRATION... please wait!</font>")
        self._scan_manager.laser_scan(use_wavemeter = True, fine_scan = True)
        self.calibrate = False
        self._status_label.setText("<font style='color: red;'>IDLE</font>")

        if self.name:
            name = '_'+self.name
        else:
            name = ''
        fName = time.strftime ('%Y%m%d_%H%M%S')+ '_laser_calib'+name
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)

        if not os.path.exists(directory):
            os.makedirs(directory)

        f = plt.figure()
        ax = f.add_subplot(1,1,1)
        ax.plot (self._scan_manager.v_vals, self._scan_manager.frequencies, '.b', linewidth =2)
        ax.set_xlabel ('voltage [V]')
        ax.set_ylabel ('laser frequency [GHz]')
        f.savefig(os.path.join(directory, fName+'.png'))
        
        f5 = h5py.File(os.path.join(directory, fName+'.hdf5'))
        #f.attrs ['laser_power'] = self._laserscan.laser_power
        #f.attrs ['laser_wavelength'] = self._laserscan.laser_wavelength
        scan_grp = f5.create_group('calibration')
        scan_grp.create_dataset('V', data = self._scan_manager.v_vals)
        scan_grp.create_dataset('freq_GHz', data = self._scan_manager.frequencies)
        f5.close()
        plt.show()


    def update_piezoscan(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self._task = 'piezos'
        continuous_saving = True
        self._status_label.setText("<font style='color: red;'>SCANNING PIEZOs</font>")
        self._scan_manager.initialize_piezos(wait_time=1)
        self._scan_manager.piezo_scan(avg_nr_samples=self.averaging_samples)
        self.axes.plot(self._scan_manager.v_vals, self._scan_manager.PD_signal, '.b', linewidth =2)
        self.axes.set_xlabel ('piezo voltage')
        self.axes.set_ylabel('photodiode signal [a.u.]')
        self.axes.set_ylim ([min(self._scan_manager.PD_signal), max(self._scan_manager.PD_signal)])
        self._scan_manager.v_for_saving = self._scan_manager.v_vals
        self._scan_manager.PD_for_saving = self._scan_manager.PD_signal        
        #plt.tight_layout()
        self.draw()
        if self.autosave:
            self.save()
        if self.autostop:
            self.scan_piezo_running = False

    def update_plot(self):
        if self.scan_piezo_running:
            self.update_piezoscan()
        elif self.scan_laser_running:
            self.update_laserscan()
        elif self.calibrate:
            self.calibrate_laser_frequency()
        else:
            self._status_label.setText("<font style='color: red;'>IDLE</font>")



