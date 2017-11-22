########################################
# Lisanne Coenen, 2016
# coenen.lisanne@gmail.com
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

# import pylab as plt
# import h5py
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# from matplotlib import cm
# from analysis.lib.fitting import fit
from ui_cav_char_control_panel import Ui_Panel as Ui_Form

from panel import Panel
from panel import MsgBox


class CharControlPanel (Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.setWindowTitle("Laser-Piezo Scan Interface")
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.p1_V = 0
        print self.p1_V
        #Set all parameters and connect all events to actions

        # FINE PIEZOS
        self.ui.doubleSpinBox_p1.setRange (0, 10)
        self.ui.doubleSpinBox_p1.setDecimals (3)        
        self.ui.doubleSpinBox_p1.setSingleStep (0.001)
        self.ui.doubleSpinBox_p1.setValue(self.p1_V)
        self.ui.doubleSpinBox_p1.valueChanged.connect(self.set_p1)
        #SvD: can the range -2000 to 10000 work?
        self.ui.horizontalSlider_p1.setRange (0, 10000)#(0,10000)
        self.ui.horizontalSlider_p1.setSingleStep (1)        
        self.ui.horizontalSlider_p1.valueChanged.connect(self.set_slide_p1)
        self.set_p1 (self.p1_V)
        


    def _instrument_changed(self, changes):
        pass


    def set_p1 (self, value):
        self._ins.set_fine_piezo_voltages(value)
        print 'setting fine piezo voltage'
        self.ui.horizontalSlider_p1.setValue (int(value*1000))# (int(10000*(value+2.)/12.))

    def set_slide_p1 (self, value):
        value_V = value/1000. #convert slider position to voltage #12*value/10000.-2.
        self._ins.set_fine_piezo_voltages(value_V)
        self.ui.doubleSpinBox_p1.setValue(value_V)
 
    #remove this function; it is now incorporated in the two above.
    # def set_fine_piezos (self, value):
    #     self._moc.set_fine_piezo_voltages (v1 = self.p1_V, v2 = self.p1_V, v3 = self.p1_V)



