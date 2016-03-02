# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'temperature_controller_v2.ui'
#
# Created: Wed Sep 23 15:30:33 2015
#      by: PyQt4 UI code generator 4.11.3
#
# Modified by Anais _21-01-2016. QtDesigner is not installed on this computer. 

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(230, 559)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        Form.setFont(font)


        #Font definitions
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)

        font_title = QtGui.QFont()
        font_title.setFamily(_fromUtf8("Calibri"))
        font_title.setPointSize(11)
        font_title.setBold(True)
        font_title.setWeight(75)

        font_button = QtGui.QFont()
        font_button.setPointSize(12)

        font_big = QtGui.QFont()
        font_big.setFamily(_fromUtf8("Calibri"))
        font_big.setPointSize(24)

        #first box
        self.label_title = QtGui.QLabel(Form)
        self.label_title.setGeometry(QtCore.QRect(40, 0, 131, 21))
        self.label_title.setFont(font_title)
        self.label_title.setObjectName(_fromUtf8("label_title"))

        self.label_set_knob_T = QtGui.QLabel(Form)
        self.label_set_knob_T.setGeometry(QtCore.QRect(10, 40, 120, 21))
        self.label_set_knob_T.setFont(font)
        self.label_set_knob_T.setObjectName(_fromUtf8("label_set_knob_T"))

        self.dsb_set_knob_T = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_knob_T.setGeometry(QtCore.QRect(150, 40, 71, 21))
        self.dsb_set_knob_T.setObjectName(_fromUtf8("dsb_set_knob_T"))

        
        self.label_set_delta_T = QtGui.QLabel(Form)
        self.label_set_delta_T.setGeometry(QtCore.QRect(10, 70, 120, 21))
        self.label_set_delta_T.setFont(font)
        self.label_set_delta_T.setObjectName(_fromUtf8("label_set_T"))

        self.dsb_set_delta_T = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_delta_T.setGeometry(QtCore.QRect(150, 70, 71, 21))
        self.dsb_set_delta_T.setObjectName(_fromUtf8("dsb_set_T"))

        self.label_T_readout = QtGui.QLabel(Form)
        self.label_T_readout.setGeometry(QtCore.QRect(40, 90, 101, 51))
        self.label_T_readout.setFont(font_big)
        self.label_T_readout.setObjectName(_fromUtf8("label_T_readout"))

        self.label_T_readout_2 = QtGui.QLabel(Form)
        self.label_T_readout_2.setGeometry(QtCore.QRect(140, 90, 101, 51))
        self.label_T_readout_2.setFont(font_big)
        self.label_T_readout_2.setObjectName(_fromUtf8("label_T_readout_2"))

        
        #Formating the second box
        self.line = QtGui.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(0, 140, 221, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        
        self.label_title_2 = QtGui.QLabel(Form)
        self.label_title_2.setGeometry(QtCore.QRect(40, 150, 131, 21))
        self.label_title_2.setFont(font_title)
        self.label_title_2.setObjectName(_fromUtf8("label_title_2"))

        self.label_DFG_power = QtGui.QLabel(Form)
        self.label_DFG_power.setGeometry(QtCore.QRect(40, 180, 101, 51))
        self.label_DFG_power.setFont(font_big)
        self.label_DFG_power.setObjectName(_fromUtf8("label_DFG_power"))

        self.label_DFG_power_unit = QtGui.QLabel(Form)
        self.label_DFG_power_unit.setGeometry(QtCore.QRect(140, 180, 101, 51))
        self.label_DFG_power_unit.setFont(font_big)
        self.label_DFG_power_unit.setObjectName(_fromUtf8("DFG_power_unit"))

        #Formating the third box
        self.line = QtGui.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(0, 230, 221, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        
        self.label_title_3 = QtGui.QLabel(Form)
        self.label_title_3.setGeometry(QtCore.QRect(40, 240, 131, 21))
        self.label_title_3.setFont(font_title)
        self.label_title_3.setObjectName(_fromUtf8("label_title_3"))
        
        self.label_T_min = QtGui.QLabel(Form)
        self.label_T_min.setGeometry(QtCore.QRect(10, 270, 111, 21))
        self.label_T_min.setFont(font)
        self.label_T_min.setObjectName(_fromUtf8("label_T_min"))
        
        self.dsb_set_T_min = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_T_min.setGeometry(QtCore.QRect(150, 270, 71, 21))
        self.dsb_set_T_min.setObjectName(_fromUtf8("dsb_set_T_min"))
        
        self.dsb_set_T_max = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_T_max.setGeometry(QtCore.QRect(150, 300, 71, 21))
        self.dsb_set_T_max.setObjectName(_fromUtf8("dsb_set_T_max"))
        
        self.label_set_T_max = QtGui.QLabel(Form)
        self.label_set_T_max.setGeometry(QtCore.QRect(10, 300, 111, 21))
        self.label_set_T_max.setFont(font)
        self.label_set_T_max.setObjectName(_fromUtf8("label_set_T_max"))
        
        self.dsb_set_nr_steps = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_nr_steps.setGeometry(QtCore.QRect(150, 330, 71, 21))
        self.dsb_set_nr_steps.setObjectName(_fromUtf8("dsb_set_nr_steps"))
        
        self.label_set_nr_steps = QtGui.QLabel(Form)
        self.label_set_nr_steps.setGeometry(QtCore.QRect(10, 330, 111, 21))
        self.label_set_nr_steps.setFont(font)
        self.label_set_nr_steps.setObjectName(_fromUtf8("label_set_nr_steps"))
        
        self.dsb_set_dwell_time = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_dwell_time.setGeometry(QtCore.QRect(150, 360, 71, 21))
        self.dsb_set_dwell_time.setObjectName(_fromUtf8("dsb_set_dwell_time"))
        
        self.label_set_dwell_time = QtGui.QLabel(Form)
        self.label_set_dwell_time.setGeometry(QtCore.QRect(10, 360, 111, 21))
        self.label_set_dwell_time.setFont(font)
        self.label_set_dwell_time.setObjectName(_fromUtf8("label_set_dwell_time"))
        
        self.pushButton_scan = QtGui.QPushButton(Form)
        self.pushButton_scan.setGeometry(QtCore.QRect(50, 400, 111, 41))
        self.pushButton_scan.setFont(font_button)
        self.pushButton_scan.setObjectName(_fromUtf8("pushButton_scan"))

        self.pushButton_stop = QtGui.QPushButton(Form)
        self.pushButton_stop.setGeometry(QtCore.QRect(50, 450, 111, 41))
        self.pushButton_stop.setFont(font_button)
        self.pushButton_stop.setObjectName(_fromUtf8("pushButton_stop"))

        self.pushButton_save = QtGui.QPushButton(Form)
        self.pushButton_save.setGeometry(QtCore.QRect(50, 500, 111, 41))
        self.pushButton_save.setFont(font_button)
        self.pushButton_save.setObjectName(_fromUtf8("pushButton_save"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        #first box
        self.label_title.setText(_translate("Form", "Crystal Temperature", None))
        self.label_set_knob_T.setText(_translate("Form", "knob Temperature", None))
        self.label_set_delta_T.setText(_translate("Form", "delta Temperature", None))
        self.label_T_readout.setText(_translate("Form", "#####", None))
        self.label_T_readout_2.setText(_translate("Form", "deg", None))

        #second box
        self.label_title_2.setText(_translate("Form", "DFG power", None))
        self.label_DFG_power.setText(_translate("Form", "#####", None))
        self.label_DFG_power_unit.setText(_translate("Form", "uW", None))

        #third box
        self.label_title_3.setText(_translate("Form", "Scan Temperature", None))
        self.label_T_min.setText(_translate("Form", "T_min", None))
        self.label_set_T_max.setText(_translate("Form", "T_max", None))
        self.label_set_nr_steps.setText(_translate("Form", "nr steps", None))
        self.label_set_dwell_time.setText(_translate("Form", "dwell time [s]", None))
        self.pushButton_scan.setText(_translate("Form", "SCAN", None))
        self.pushButton_stop.setText(_translate("Form", "STOP", None))
        self.pushButton_save.setText(_translate("Form", "SAVE", None))

