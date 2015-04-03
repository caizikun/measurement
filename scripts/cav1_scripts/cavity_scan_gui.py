from __future__ import unicode_literals
import os, sys, time
from PySide.QtCore import *
from PySide.QtGui import *
import random
from matplotlib.backends import qt4_compat
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

import pylab as plt
import h5py
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from measurement.lib.cavity.cavity_scan import CavityScan 

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MsgBox(QtGui.QWidget):
    
    def __init__(self):
        super(MsgBox, self).__init__()
        self.initUI()
        
        
    def initUI(self):               
        
        self.setGeometry(300, 300, 250, 150)        
        self.setWindowTitle('Calibration in progess... please wait!')    
        self.show()        


class MyCanvas(FigureCanvas):

    def __init__(self,  scan_manager, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        # Clear axes every time plot() is called
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self._scan_manager = scan_manager
        self.refresh_time = 100
        self.name = self._scan_manager.name

    def save(self):
        if self.name:
            name = '_'+self.name
        else:
            name = ''
        fName = time.strftime ('%Y%m%d_%H%M%S')+ '_laserscan_PD'+name
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)

        if not os.path.exists(directory):
            os.makedirs(directory)

        f = plt.figure()
        ax = f.add_subplot(1,1,1)
        ax.plot (self._laserscan.v_vals, self._laserscan.PD_signal, '.b', linewidth = 2)
        ax.set_xlabel ('voltage [V]')
        ax.set_ylabel ('photodiode signal [a.u.]')
        f.savefig(os.path.join(directory, fName+'.png'))
        
        f = h5py.File(os.path.join(directory, fName+'.hdf5'))
        #f.attrs ['laser_power'] = self._laserscan.laser_power
        #f.attrs ['laser_wavelength'] = self._laserscan.laser_wavelength
        scan_grp = f.create_group('laserscan')
        scan_grp.create_dataset('V', data = self._laserscan.v_vals)
        scan_grp.create_dataset('PD_signal', data = self._laserscan.PD_signal)
        f.close()



class ScanCanvas(MyCanvas):

    def __init__(self, *args, **kwargs):
        MyCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_plot)
        timer.start(self.refresh_time)

    def update_laserscan(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self._scan_manager.laser_scan(use_wavemeter = self.use_wm)
        #self.random_noise = 0*0.1*np.random.rand(len(self._laserscan.v_vals))
        if self.use_wm:
            print 'Use_wm!!'
            self.axes.plot(self._scan_manager.frequencies, self._scan_manager.PD_signal, '.b', linewidth =2)
            self.axes.set_xlabel ('frequency [GHz]')
        else:
            self.axes.plot(self._scan_manager.v_vals, self._scan_manager.PD_signal, '.b', linewidth =2)
            self.axes.set_xlabel ('voltage [V]')            
        self.axes.set_ylabel('photodiode signal [a.u.]')
        self.axes.set_ylim ([-0.1, 3])
        self.draw()

    def calibrate_laser_frequency(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        mb = QtGui.QMessageBox()
        mb.setText('Calibration in progress... please wait!')
        mb.exec_()
        self._scan_manager.laser_scan(use_wavemeter = True)
        mb.close()
        plt.plot(self._scan_manager.v_vals, self._scan_manager.PD_signal, '.b', linewidth =2)
        plt.show()

    def update_piezoscan(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self._scan_manager.piezo_scan()
        self.axes.plot(self._scan_manager.v_vals, self._scan_manager.PD_signal, '.b', linewidth =2)
        self.axes.set_xlabel ('piezo voltage')
        self.axes.set_ylabel('photodiode signal [a.u.]')
        self.axes.set_ylim ([-0.1, 3])
        self.draw()

    def update_plot(self):

        if self.scan_piezo_running:
            self.update_piezoscan()
        elif self.scan_laser_running:
            self.update_laserscan()
        elif self.calibrate:
            self.calibrate_laser_frequency()


class ScanGUI(QtGui.QMainWindow):
    def __init__(self, scan_manager):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Laser Scan GUI")

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Save', self.fileSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QGridLayout(self.main_widget)
        #self.setLayout (l)
        self.dc = ScanCanvas(parent=self.main_widget, width=5, height=4, dpi=100, scan_manager = scan_manager)
        l.addWidget(self.dc, 0, 0, 4, 4)
        self.btn_scan_laser = QtGui.QPushButton('Scan laser', self)
        self.btn_scan_laser.clicked.connect(self.scan_laser)
        l.addWidget(self.btn_scan_laser, 4,0)
        self.btn_scan_piezos = QtGui.QPushButton('Scan piezos', self)
        self.btn_scan_piezos.clicked.connect(self.scan_piezos)
        l.addWidget(self.btn_scan_piezos,4,1)
        self.btn_stop = QtGui.QPushButton('Stop scan', self)
        self.btn_stop.clicked.connect(self.stop_scan)
        l.addWidget(self.btn_stop,4,2)
        self.btn_calibr = QtGui.QPushButton('Calibration', self)
        self.btn_calibr.clicked.connect(self.calibration)
        l.addWidget(self.btn_calibr,4,3)
        self.cb_use_wm = QtGui.QCheckBox('Use wavemeter', self)
        self.cb_use_wm.stateChanged.connect(self.use_wm)
        l.addWidget(self.cb_use_wm,6,0)
        self.cb_use_calib = QtGui.QCheckBox('Use calibration', self)
        self.cb_use_calib.stateChanged.connect(self.use_calibration)
        l.addWidget(self.cb_use_calib,6,1)
        self.cb_normalize = QtGui.QCheckBox('Normalize', self)
        self.cb_normalize.stateChanged.connect(self.normalize)
        l.addWidget(self.cb_normalize,6,2)
        self.cb_coarse = QtGui.QCheckBox('coarse (freq laser scan)', self)
        self.cb_coarse.stateChanged.connect(self.laser_scan_type)
        l.addWidget(self.cb_coarse,6,3)
        self.v_min_box = QtGui.QDoubleSpinBox()
        self.v_min_box.setRange (-10, 10)
        self.v_min_box.setSingleStep (0.01)
        self.v_min_box.setSuffix(' V')
        self.v_min_box.setValue(0)
        self.v_min_box.valueChanged.connect(self.set_V_min)
        l.addWidget (self.v_min_box, 8, 0)
        self.v_max_box = QtGui.QDoubleSpinBox()
        self.v_max_box.setRange (-10, 10)
        self.v_max_box.setSingleStep (0.01)
        self.v_max_box.setSuffix(' V')
        self.v_max_box.setValue(4)
        self.v_max_box.valueChanged.connect(self.set_V_max)
        l.addWidget (self.v_max_box, 8, 1)
        self.nr_steps_box = QtGui.QSpinBox()
        self.nr_steps_box.setRange (1, 999)
        self.nr_steps_box.setSingleStep (1)
        self.nr_steps_box.setValue(10)
        self.nr_steps_box.valueChanged.connect(self.set_nr_steps)
        l.addWidget (self.nr_steps_box, 8, 3)

        qlb1 = QtGui.QLabel ('min voltage')
        l.addWidget (qlb1, 9, 0)
        qlb1 = QtGui.QLabel ('max voltage')
        l.addWidget (qlb1, 9, 1)
        qlb1 = QtGui.QLabel ('nr steps')
        l.addWidget (qlb1, 9, 3)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.dc.scan_piezo_running = False
        self.dc.scan_laser_running = False
        self.dc.calibrate = False
        self.dc.coarse = False
        self.dc.use_wm = False

    def fileQuit(self):
        self.close()

    def fileSave(self):
        self.dc.save()

    def closeEvent(self, ce):
        self.fileQuit()

    def scan_laser(self):
        self.dc.scan_laser_running = True
        if self.dc.coarse:
            self.v_min_box.setRange (0, 10)
            self.v_max_box.setRange (0, 10)
            if (self.dc._scan_manager.V_min < 0):
                self.dc._scan_manager.V_min = 0
                self.v_min_box.setValue (0)
            if (self.dc._scan_manager.V_max >10):
                self.dc._scan_manager.V_max = 9.9
                self.v_max_box.setValue (10)
        else:
            self.v_min_box.setRange (-2, 4)
            self.v_max_box.setRange (-2, 4)
            if (self.dc._scan_manager.V_min <-2):
                self.dc._scan_manager.V_min = -2
                self.v_min_box.setValue (-2)
            if (self.dc._scan_manager.V_max >4):
                self.dc._scan_manager.V_max = 4
                self.v_max_box.setValue (4)

    def scan_piezos(self):
        self.dc.scan_piezo_running = True
        self.v_min_box.setRange (-2, 10)
        self.v_max_box.setRange (-2, 10)
        if (self.dc._scan_manager.V_min <-2):
            self.dc._scan_manager.V_min = -2
            self.v_min_box.setValue (-2)
        if (self.dc._scan_manager.V_max >10):
            self.dc._scan_manager.V_max = 10
            self.v_max_box.setValue (10)


    def stop_scan(self):
        self.dc.scan_laser_running = False
        self.dc.scan_piezo_running = False

    def calibration(self):
        self.dc.scan_laser_running = False
        self.dc.scan_piezo_running = False
        self.dc.calibrate = True

    def use_wm (self, state):
        if state == QtCore.Qt.Checked:
                self.dc.use_wm = True
        else:
            self.dc.use_wm = False

    def use_calibration (self, state):
        if state == QtCore.Qt.Checked:
            if not(self.dc.scan_laser_running):
                self.dc.use_calibr = True
        else:
            self.dc.use_calibr = False

    def normalize (self, state):
        if state == QtCore.Qt.Checked:
            self.dc.normalize = True
        else:
            self.dc.normalize = False

    def laser_scan_type (self, state):
        if state == QtCore.Qt.Checked:
            self.dc.coarse = True
        else:
            self.dc.coarse = False

    def set_V_min (self, value):
        self.dc._scan_manager.V_min = value

    def set_V_max (self, value):
        self.dc._scan_manager.V_max = value

    def set_nr_steps (self, value):
        self.dc._scan_manager.nr_V_steps = value


qApp = QtGui.QApplication(sys.argv)
lc = CavityScan (name='test')
lc.set_laser_params (wavelength = 637.1, power = 5)
lc.set_scan_params (v_min=0., v_max=4., nr_points=10)

aw = ScanGUI(scan_manager = lc)
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
