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

# import pylab as plt
# import h5py
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# from matplotlib import cm
# from analysis.lib.fitting import fit
from ui_cav_control_panel import Ui_Panel as Ui_Form

from panel import Panel
from panel import MsgBox


class ControlPanel (Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.setWindowTitle("Laser-Piezo Scan Interface")
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.p1_V = 0
        self.p2_V = 0
        self.p3_V = 0
        self.piezo_locked = False
        self.pzk_X = self._ins.get_track_curr_x()*1000
        self.pzk_Y = self._ins.get_track_curr_y()*1000
        self.pzk_Z = self._ins.get_track_curr_z()*1000
        self.use_wm = False
   
        self.ui.label_curr_pos_readout_x.setText(str(self.pzk_X))
        self.ui.label_curr_pos_readout_y.setText(str(self.pzk_Y))
        self.ui.label_curr_pos_readout_z.setText(str(self.pzk_Z))
        # self._exp_mngr.update_coarse_piezos (x=self.pzk_X, y=self.pzk_Y, z=self.pzk_Z)
        #Set all parameters and connect all events to actions
        # LASER
        self.ui.dSBox_coarse_lambda.setRange (635.00, 640.00)
        self.ui.dSBox_coarse_lambda.setSingleStep (0.01)
        self.ui.dSBox_coarse_lambda.setValue(self._ins.get_laser_wavelength())
        self.ui.dSBox_coarse_lambda.valueChanged.connect(self.set_laser_wavelength)
        self.ui.dsB_power.setRange (0.0, 15.0)
        self.ui.dsB_power.setSingleStep(0.1)     
        self.ui.dsB_power.setValue(0)   
        self.ui.dsB_power.valueChanged.connect(self.set_laser_power)


        # FINE PIEZOS
        self.ui.doubleSpinBox_p1.setRange (-2, 10)
        self.ui.doubleSpinBox_p1.setDecimals (3)        
        self.ui.doubleSpinBox_p1.setSingleStep (0.001)
        self.ui.doubleSpinBox_p1.setValue(self.p1_V)
        self.ui.doubleSpinBox_p1.valueChanged.connect(self.set_p1)
        #SvD: can the range -2000 to 10000 work?
        self.ui.horizontalSlider_p1.setRange (-2000, 10000)#(0,10000)
        self.ui.horizontalSlider_p1.setSingleStep (1)        
        self.ui.horizontalSlider_p1.valueChanged.connect(self.set_slide_p1)
        self.set_p1 (self.p1_V)
        
        # PiezoKnobs
        self.ui.spinBox_rel_step_size.setRange(0,100)
        self.ui.spinBox_rel_step_size.setValue(self._ins.get_rel_step_size())
        self.ui.spinBox_rel_step_size.valueChanged.connect(self.set_rel_step_size)
        self.ui.spinBox_JPE_freq.setRange(0,600)
        self.ui.spinBox_JPE_freq.setValue(self._ins.get_JPE_freq())
        self.ui.spinBox_JPE_freq.valueChanged.connect(self.set_JPE_freq)

        self.ui.spinBox_X.setRange (-999, 999)
        self.ui.spinBox_X.setValue(self.pzk_X)
        self.ui.spinBox_X.valueChanged.connect(self.set_pzk_X)
        self.ui.spinBox_Y.setRange (-999, 999)
        self.ui.spinBox_Y.setValue(self.pzk_Y)
        self.ui.spinBox_Y.valueChanged.connect(self.set_pzk_Y)
        self.ui.spinBox_Z.setRange (-999, 999)
        self.ui.spinBox_Z.setValue(self.pzk_Z)
        self.ui.spinBox_Z.valueChanged.connect(self.set_pzk_Z)
        self.ui.pushButton_activate.clicked.connect (self.move_pzk)
        self.ui.pushButton_set_as_origin.clicked.connect (self.pzk_set_as_origin)

        #Temperature
        self.ui.radioButton_roomT.toggled.connect (self.room_T_button)
        self.ui.radioButton_lowT.toggled.connect (self.low_T_button)
        self.room_T = None
        self.low_T = None

        #Wavemeter
        self.ui.checkBox_wavemeter.stateChanged.connect (self.use_wavemeter)
        # self._exp_mngr._system_updated = True
        self.refresh_time = 100

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(self.refresh_time)

        a = self._ins.status()
        if (a[:5]=='ERROR'):
            msg_text = 'JPE controller is OFF or in manual mode!'
            ex = MsgBox(msg_text=msg_text)
            ex.show()


    def _instrument_changed(self, changes):
        if changes.has_key('track_curr_x'):
            self.ui.label_curr_pos_readout_x.setText(str(changes['track_curr_x']))
        if changes.has_key('track_curr_y'):
            self.ui.label_curr_pos_readout_y.setText(str(changes['track_curr_y']))
        if changes.has_key('track_curr_z'):
            self.ui.label_curr_pos_readout_z.setText(str(changes['track_curr_z']))
        if changes.has_key('laser_wavelength'):
            self.ui.dSBox_coarse_lambda.setValue(changes['laser_wavelength'])
        if changes.has_key('laser_power'):
            self.ui.dSBox_coarse_lambda.setValue(changes['laser_power'])
        if changes.has_key('laser_wm_frequency'):
            self.ui.label_wavemeter_readout.setText (str(changes['laser_wm_frequency'])+ ' GHz')
        if changes.has_key('rel_step_size'):
            self.ui.spinBox_rel_step_size.setValue(changes['rel_step_size'])
        if changes.has_key('JPE_freq'):
            self.ui.spinBox_JPE_freq.setValue(changes['JPE_freq'])

    def set_laser_wavelength (self, value):
        self._ins.set_laser_wavelength(value)

    def set_laser_power (self, value):
        self._ins.set_power_level(value)

    def set_p1 (self, value):
        self._ins.set_fine_piezo_voltages(v1 = value, v2 = value, v3 = value)
        self.ui.horizontalSlider_p1.setValue (int(value*1000))# (int(10000*(value+2.)/12.))

    def set_slide_p1 (self, value):
        value_V = value/1000. #convert slider position to voltage #12*value/10000.-2.
        self._ins.set_fine_piezo_voltages(v1 = value_V, v2 = value_V, v3 = value_V)
        self.ui.doubleSpinBox_p1.setValue(value_V)
 
    #remove this function; it is now incorporated in the two above.
    # def set_fine_piezos (self, value):
    #     self._moc.set_fine_piezo_voltages (v1 = self.p1_V, v2 = self.p1_V, v3 = self.p1_V)

    def set_rel_step_size(self, value):
        self._ins.set_rel_step_size(value)

    def set_JPE_freq(self, value):
        self._ins.set_JPE_freq(value)

    def set_pzk_X (self, value):
        self.pzk_X = value

    def set_pzk_Y (self, value):
        self.pzk_Y = value

    def set_pzk_Z (self, value):
        self.pzk_Z = value

    def move_pzk(self):
        """function to move the piezoknobs.
        """
        a = self._ins.status()
        if (self.room_T == None and self.low_T == None):
            msg_text = 'Set temperature before moving PiezoKnobs!'
            ex = MsgBox(msg_text=msg_text)
            ex.show()
        elif (a[:5]=='ERROR'): #SvD: this error handling should perhaps be done in the JPE_CADM instrument itself
            msg_text = 'JPE controller is OFF or in manual mode!'
            ex = MsgBox(msg_text=msg_text)
            ex.show()
        else:
            self._ins.print_current_position()
            self._ins.print_tracker_params()
            s1, s2, s3 = self._ins.motion_to_spindle_steps (x=self.pzk_X/1000., y=self.pzk_Y/1000., z=self.pzk_Z/1000., 
                update_tracker=False)

            msg_text = 'Moving the spindles by ['+str(s1)+' , '+str(s2)+' , '+str(s3)+' ] steps. Continue?'
            ex = MsgBox(msg_text=msg_text)
            ex.show()

            if (ex.ret==0):
                self._ins.move_spindle_steps (s1=s1, s2=s2, s3=s3, x=self.pzk_X/1000., y=self.pzk_Y/1000., z=self.pzk_Z/1000.)
                self.ui.label_curr_pos_readout_x.setText(str(self.pzk_X))
                self.ui.label_curr_pos_readout_y.setText(str(self.pzk_Y))
                self.ui.label_curr_pos_readout_z.setText(str(self.pzk_Z))     
                # self._exp_mngr.update_coarse_piezos (x = self.pzk_X, y = self.pzk_Y, z = self.pzk_Z)

    def pzk_set_as_origin(self):
        self._ins.set_as_origin()
        self.ui.label_curr_pos_readout_x.setText(str(0))
        self.ui.label_curr_pos_readout_y.setText(str(0))
        self.ui.label_curr_pos_readout_z.setText(str(0))  

    def use_wavemeter (self):
        if self.ui.checkBox_wavemeter.isChecked():
            self.use_wm = True           
        else:
            self.use_wm = False

    # def update (self):
    #     if self.use_wm:
    #         wm_read = self._wm.Get_FPar (45)
    #         self.ui.label_wavemeter_readout.setText (str(wm_read)+ ' GHz')

    def room_T_button (self):
        if self.ui.radioButton_roomT.isChecked():
            self.ui.radioButton_lowT.setChecked(False)
            self._ins.set_temperature(300)
            self.room_T = True
            self.low_T = False
        else:
            self.ui.radioButton_lowT.setChecked(True)
            self._ins.set_temperature(4)
            self.low_T = True
            self.room_T = False

    def low_T_button (self):
        if self.ui.radioButton_lowT.isChecked():
            self.ui.radioButton_roomT.setChecked(False)
            self._ins.set_temperature(4)
            self.low_T = True
            self.room_T = False
        else:
            self.ui.radioButton_roomT.setChecked(True)
            self._ins.set_temperature(300)
            self.room_T = True
            self.low_T = False

    #I think I don't need these.
    # def fileQuit(self):
    #     print 'Closing!'
    #     self.set_dsb_p1 (0)
    #     self.close()

    # def closeEvent(self, ce):
    #     self.fileQuit()



