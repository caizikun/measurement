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
from measurement.lib.cavity.laser_scan import LaserScan 

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyCanvas(FigureCanvas):

    def __init__(self,  laserscan, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        # Clear axes every time plot() is called
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self._laserscan = laserscan
        self.refresh_time = 100
        self.name = self._laserscan.name

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
        ax.plot (self._laserscan.v_vals, self._laserscan.PD_signal+self.random_noise, 'b', linewidth = 2)
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



class LaserScanCanvas(MyCanvas):

    def __init__(self, *args, **kwargs):
        MyCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_laserscan)
        timer.start(self.refresh_time)

    def update_laserscan(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self._laserscan.scan()
        self.random_noise = 0.1*np.random.rand(len(self._laserscan.v_vals))
        self.axes.plot(self._laserscan.v_vals, self._laserscan.PD_signal+self.random_noise, 'b', linewidth =2)
        self.axes.set_xlabel ('voltage [V]')
        self.axes.set_ylabel('photodiode signal [a.u.]')
        self.draw()

class LaserScanGUI(QtGui.QMainWindow):
    def __init__(self, laserscan):
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

        l = QtGui.QVBoxLayout(self.main_widget)
        self.dc = LaserScanCanvas(parent=self.main_widget, width=5, height=4, dpi=100, laserscan = laserscan)
        l.addWidget(self.dc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def fileQuit(self):
        self.close()

    def fileSave(self):
        self.dc.save()

    def closeEvent(self, ce):
        self.fileQuit()


qApp = QtGui.QApplication(sys.argv)
lc = LaserScan (name='test')
lc.set_laser_params (wavelength = 637.1, power = 5)
lc.set_scan_params (v_min=0., v_max=5., nr_points=50)

aw = LaserScanGUI(laserscan = lc)
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
