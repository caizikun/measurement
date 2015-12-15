# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'XYscan_panel.ui'
#
# Created: Mon Sep 28 11:08:08 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

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
from measurement.lib.cavity.panels.scan_gui_panels import MsgBox, XYCanvas


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(811, 744)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        Form.setFont(font)
        self.label_x_min = QtGui.QLabel(Form)
        self.label_x_min.setGeometry(QtCore.QRect(30, 590, 41, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_x_min.setFont(font)
        self.label_x_min.setObjectName(_fromUtf8("label_x_min"))
        self.dsb_set_x_min = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_x_min.setGeometry(QtCore.QRect(80, 590, 81, 21))
        self.dsb_set_x_min.setMaximum(999.0)
        self.dsb_set_x_min.setObjectName(_fromUtf8("dsb_set_x_min"))
        self.dsb_set_x_max = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_x_max.setGeometry(QtCore.QRect(230, 590, 81, 21))
        self.dsb_set_x_max.setObjectName(_fromUtf8("dsb_set_x_max"))
        self.label_x_max = QtGui.QLabel(Form)
        self.label_x_max.setGeometry(QtCore.QRect(180, 590, 41, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_x_max.setFont(font)
        self.label_x_max.setObjectName(_fromUtf8("label_x_max"))
        self.dsb_set_nr_steps_x = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_nr_steps_x.setGeometry(QtCore.QRect(390, 590, 71, 21))
        self.dsb_set_nr_steps_x.setDecimals(0)
        self.dsb_set_nr_steps_x.setMaximum(10000.0)
        self.dsb_set_nr_steps_x.setObjectName(_fromUtf8("dsb_set_nr_steps_x"))
        self.label_set_nr_steps_x = QtGui.QLabel(Form)
        self.label_set_nr_steps_x.setGeometry(QtCore.QRect(330, 590, 51, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_set_nr_steps_x.setFont(font)
        self.label_set_nr_steps_x.setObjectName(_fromUtf8("label_set_nr_steps_x"))
        self.dsb_set_acq_time = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_acq_time.setGeometry(QtCore.QRect(170, 660, 91, 21))
        self.dsb_set_acq_time.setDecimals(3)
        self.dsb_set_acq_time.setMaximum(99.0)
        self.dsb_set_acq_time.setProperty("value", 1.0)
        self.dsb_set_acq_time.setObjectName(_fromUtf8("dsb_set_acq_time"))
        self.label_set_dwell_time = QtGui.QLabel(Form)
        self.label_set_dwell_time.setGeometry(QtCore.QRect(30, 660, 131, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_set_dwell_time.setFont(font)
        self.label_set_dwell_time.setObjectName(_fromUtf8("label_set_dwell_time"))
        self.pushButton_scan = QtGui.QPushButton(Form)
        self.pushButton_scan.setGeometry(QtCore.QRect(670, 590, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_scan.setFont(font)
        self.pushButton_scan.setObjectName(_fromUtf8("pushButton_scan"))
        self.pushButton_stop = QtGui.QPushButton(Form)
        self.pushButton_stop.setGeometry(QtCore.QRect(670, 640, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_stop.setFont(font)
        self.pushButton_stop.setObjectName(_fromUtf8("pushButton_stop"))
        self.pushButton_save = QtGui.QPushButton(Form)
        self.pushButton_save.setGeometry(QtCore.QRect(670, 690, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_save.setFont(font)
        self.pushButton_save.setObjectName(_fromUtf8("pushButton_save"))
        self.dsb_set_nr_steps_y = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_nr_steps_y.setGeometry(QtCore.QRect(390, 620, 71, 21))
        self.dsb_set_nr_steps_y.setDecimals(0)
        self.dsb_set_nr_steps_y.setMaximum(10000.0)
        self.dsb_set_nr_steps_y.setObjectName(_fromUtf8("dsb_set_nr_steps_y"))
        self.label_x_max_2 = QtGui.QLabel(Form)
        self.label_x_max_2.setGeometry(QtCore.QRect(180, 620, 41, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_x_max_2.setFont(font)
        self.label_x_max_2.setObjectName(_fromUtf8("label_x_max_2"))
        self.label_y_min = QtGui.QLabel(Form)
        self.label_y_min.setGeometry(QtCore.QRect(30, 620, 41, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_y_min.setFont(font)
        self.label_y_min.setObjectName(_fromUtf8("label_y_min"))
        self.dsb_set_y_min = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_y_min.setGeometry(QtCore.QRect(80, 620, 81, 21))
        self.dsb_set_y_min.setMaximum(999.0)
        self.dsb_set_y_min.setObjectName(_fromUtf8("dsb_set_y_min"))
        self.dsb_set_y_max = QtGui.QDoubleSpinBox(Form)
        self.dsb_set_y_max.setGeometry(QtCore.QRect(230, 620, 81, 21))
        self.dsb_set_y_max.setObjectName(_fromUtf8("dsb_set_y_max"))
        self.label_set_nr_steps_y = QtGui.QLabel(Form)
        self.label_set_nr_steps_y.setGeometry(QtCore.QRect(330, 620, 51, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_set_nr_steps_y.setFont(font)
        self.label_set_nr_steps_y.setObjectName(_fromUtf8("label_set_nr_steps_y"))
        self.xy_plot = XYCanvas(parent=Form, width=900, height=370)
        self.xy_plot.setGeometry(QtCore.QRect(20, 50, 761, 521))
        self.xy_plot.setObjectName(_fromUtf8("graphicsView"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_x_min.setText(_translate("Form", "x_min", None))
        self.label_x_max.setText(_translate("Form", "x_max", None))
        self.label_set_nr_steps_x.setText(_translate("Form", "nr steps", None))
        self.label_set_dwell_time.setText(_translate("Form", "acquisitionl time [s]", None))
        self.pushButton_scan.setText(_translate("Form", "SCAN", None))
        self.pushButton_stop.setText(_translate("Form", "STOP", None))
        self.pushButton_save.setText(_translate("Form", "SAVE", None))
        self.label_x_max_2.setText(_translate("Form", "y_max", None))
        self.label_y_min.setText(_translate("Form", "y_min", None))
        self.label_set_nr_steps_y.setText(_translate("Form", "nr steps", None))

