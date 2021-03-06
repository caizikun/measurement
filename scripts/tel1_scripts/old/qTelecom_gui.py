########################################
# Cristian Bonato, 2015
# cbonato80@gmail.com
# Adapted by Anais Dreau
########################################

from __future__ import unicode_literals
import os, sys, time
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
#from measurement.lib.cavity.cavity_scan import CavityScanManager 
from measurement.scripts.qTelecom.temperature_ctrl_panel import Ui_Form as Ui_Temp_Ctrl

from analysis.lib.fitting import fit


class TempCtrlPanelGUI (QtGui.QMainWindow):
    def __init__(self,adwin, powermeter, parent=None):

        self._adwin = adwin
        self._pmeter = powermeter
        QtGui.QWidget.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.setWindowTitle("Laser-Piezo Scan Interface")
        self.ui = Ui_Temp_Ctrl()
        self.ui.setupUi(self)

        self.dac_no = 8
        self.adc_no = 2

        #Set all parameters and connect all events to actions
        self.ui.dsb_set_delta_T.setRange (-45.00, 145.00)
        self.ui.dsb_set_delta_T.setSingleStep (0.01)
        self.ui.dsb_set_delta_T.setDecimals (2)
        self.ui.dsb_set_delta_T.valueChanged.connect(self.set_delta_temperature)

        self.ui.dsb_set_knob_T.setRange (-45.00, 145.00)
        self.ui.dsb_set_knob_T.setSingleStep (0.01)
        self.ui.dsb_set_knob_T.setDecimals (2)
        self.ui.dsb_set_knob_T.valueChanged.connect(self.set_knob_T)

        self.ui.dsb_set_T_min.setRange (-45.00, 145.00)
        self.ui.dsb_set_T_min.setSingleStep (0.01)
        self.ui.dsb_set_T_min.setDecimals (2)
        self.ui.dsb_set_T_min.valueChanged.connect(self.set_T_min)
        self.ui.dsb_set_T_max.setRange (-45.00, 145.00)
        self.ui.dsb_set_T_max.setSingleStep (0.01)
        self.ui.dsb_set_T_max.setDecimals (2)
        self.ui.dsb_set_T_max.valueChanged.connect(self.set_T_max)
        self.ui.dsb_set_nr_steps.setRange (1, 1000)
        self.ui.dsb_set_nr_steps.setSingleStep (1)
        self.ui.dsb_set_nr_steps.setDecimals (0)
        self.ui.dsb_set_nr_steps.valueChanged.connect(self.set_nr_steps)
        self.ui.dsb_set_dwell_time.setRange (0, 100)  #ms
        self.ui.dsb_set_dwell_time.setSingleStep (1)
        self.ui.dsb_set_dwell_time.setDecimals (0)
        self.ui.dsb_set_dwell_time.valueChanged.connect(self.set_dwell_time)
        self.ui.pushButton_scan.clicked.connect (self.start_scan)
        self.ui.pushButton_stop.clicked.connect (self.stop_scan)
        self.ui.pushButton_save.clicked.connect (self.save_scan)
        self.curr_task = 'idle'

        self.refresh_time = 50

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.manage_tasks)
        timer.start(self.refresh_time)

    def save_scan (self):

    	fName = time.strftime ('%H%M%S') + '_TempScan'
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        f5 = h5py.File(os.path.join(directory, fName+'.hdf5'))
        scan_grp = f5.create_group('TScan')
        scan_grp.create_dataset('temperature', data = self.temperature)
        scan_grp.create_dataset('powermeter_readout', data = self.power_readout*1e6)
        f5.close()

        fig = plt.figure()
        fig_title = time.strftime ('%Y-%m-%d-%H:%M:%S') + '- Crystal Temperature Scan'
        plt.plot (self.temperature, self.power_readout*1e6, 'r--')
        plt.plot (self.temperature, self.power_readout*1e6, 'ok')
        plt.title(fig_title)
        plt.xlabel ('temperature [deg]', fontsize = 15)
        plt.ylabel ('power [$\mu$W]', fontsize = 15)
        plt.savefig (os.path.join(directory, fName+'.png'))
        plt.close(fig)


    def set_delta_temperature (self, value):
    	self.delta_T = value
        voltage = value/20.
        self._adwin.start_set_dac(dac_no=self.dac_no, dac_voltage=voltage)
        print "voltage: ", voltage


    def set_knob_T (self, value):
        self.knob_T = value


    def set_T_min (self, value):
    	self.T_min = value

    def set_T_max (self, value):
    	self.T_max = value

    def set_nr_steps (self, value):
    	self.nr_steps = value

    def set_dwell_time (self, value):
    	self.dwell_time = value*1e3
    	self.total_dwell = int(self.dwell_time/self.refresh_time)

    def read_temperature (self):
    	self._adwin.start_read_adc (adc_no = self.adc_no)
    	voltage = self._adwin.get_read_adc_var ('fpar')[0][1]
    	T = 0.01*int(voltage*20.*100)
    	self.ui.label_T_readout.setText(str(T))
        self.curr_temperature = T

    def read_DFG_power(self):
        self.ui.label_DFG_power.setText(format(self._pmeter.get_power()*1e6,'.3f'))

    def manage_tasks (self):
        self.read_temperature ()
        self.read_DFG_power()
        if (self.curr_task == 'scan'):
            self.run_new_temperature_point()
        elif (self.curr_task == 'dwell'):
            self.dwell = self.dwell + 1
            if (self.dwell > self.total_dwell):
                print 'Measuring datapoint nr ', self.curr_step
                self.temperature [self.curr_step] = self.curr_temperature
                self.power_readout [self.curr_step] = self._pmeter.get_power()
                print 'Values: ', self.temperature [self.curr_step], self.power_readout [self.curr_step]
                self.curr_step = self.curr_step + 1
                self.curr_task = 'scan'
                #number_data_points = 100
                #for i in range(0, number_data_points - 1):
                    #print 'Measuring datapoint nr ', self.curr_step
                    #self.temperature [self.curr_step] = self.curr_temperature
                    #self.power_readout [self.curr_step] = self._pmeter.get_power()
                    #print 'Values: ', self.temperature [self.curr_step], self.power_readout [self.curr_step]
                    #self.curr_step = self.curr_step + 1
                    #self.run_new_temperature_point_2()
                    #qt.msleep(0.01)
                #self.curr_task = 'scan'

    def start_scan (self):
    	print 'Start scan!!'
    	self.curr_temp_point = self.T_min - self.knob_T
    	self.temp_step = (self.T_max - self.T_min)/(self.nr_steps-1.)
    	self.curr_task = 'scan'
    	self.dwell = 0
    	self.temperature = np.zeros (self.nr_steps)# * number_data_points) #self.temperature = np.zeros (self.nr_steps)
    	self.power_readout = np.zeros (self.nr_steps)# * number_data_points) #self.power_readout = np.zeros (self.nr_steps)
    	self.curr_step = 0

    def stop_scan (self):
    	self.curr_task = 'idle'

    def run_new_temperature_point (self):
    	self.set_delta_temperature(self.curr_temp_point)
     	self.curr_temp_point = self.curr_temp_point + self.temp_step
    	self.dwell = 0
    	self.curr_task = 'dwell'
        if (self.curr_step >= self.nr_steps):
            self.set_delta_temperature(self.delta_T)  ## XXX change to the temperature set before the scan
            plt.figure()
            fig_title = time.strftime ('%Y-%m-%d-%H:%M:%S') + '- Crystal Temperature Scan'
            plt.title(fig_title)
            plt.plot (self.temperature, self.power_readout*1e6, 'r--')
            plt.plot (self.temperature, self.power_readout*1e6, 'ok')
            plt.xlabel ('temperature [deg]', fontsize = 15)
            plt.ylabel ('power [$\mu$W]', fontsize = 15)
            plt.show()
            self.curr_task = 'idle'



    def fileQuit(self):
    	print 'Closing!'
    	self.close()

    def closeEvent(self, ce):
    	self.fileQuit()

adwin = qt.instruments.get_instruments()['adwin']
powermeter = qt.instruments.get_instruments()['powermeter_telecom']
powermeter.set_wavelength (1587e-9) #(637e-9) changed to telecom... 

qApp = QtGui.QApplication(sys.argv)
TCtrlGUI = TempCtrlPanelGUI (adwin = adwin, powermeter = powermeter)   
TCtrlGUI.setWindowTitle('Temperature Control')
TCtrlGUI.show()

sys.exit(qApp.exec_())


