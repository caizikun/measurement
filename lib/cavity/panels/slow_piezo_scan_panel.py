# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'slow_piezo_scan_panel.ui'
#
# Created: Tue Jun 02 15:43:44 2015
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(208, 270)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        Form.setFont(font)
        self.label_ctr_V = QtGui.QLabel(Form)
        self.label_ctr_V.setGeometry(QtCore.QRect(20, 40, 61, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_ctr_V.setFont(font)
        self.label_ctr_V.setObjectName(_fromUtf8("label_ctr_V"))
        self.dsb_min_V = QtGui.QDoubleSpinBox(Form)
        self.dsb_min_V.setGeometry(QtCore.QRect(120, 40, 62, 22))
        self.dsb_min_V.setObjectName(_fromUtf8("dsb_min_V"))
        self.dsb_max_V = QtGui.QDoubleSpinBox(Form)
        self.dsb_max_V.setGeometry(QtCore.QRect(120, 80, 62, 22))
        self.dsb_max_V.setObjectName(_fromUtf8("dsb_max_V"))
        self.label_V_step = QtGui.QLabel(Form)
        self.label_V_step.setGeometry(QtCore.QRect(20, 80, 46, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_V_step.setFont(font)
        self.label_V_step.setObjectName(_fromUtf8("label_V_step"))
        self.label_avg = QtGui.QLabel(Form)
        self.label_avg.setGeometry(QtCore.QRect(0, 160, 111, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_avg.setFont(font)
        self.label_avg.setObjectName(_fromUtf8("label_avg"))
        self.sb_wait_time = QtGui.QSpinBox(Form)
        self.sb_wait_time.setGeometry(QtCore.QRect(120, 160, 71, 22))
        self.sb_wait_time.setObjectName(_fromUtf8("sb_wait_time"))
        self.label_steps = QtGui.QLabel(Form)
        self.label_steps.setGeometry(QtCore.QRect(20, 120, 61, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_steps.setFont(font)
        self.label_steps.setObjectName(_fromUtf8("label_steps"))
        self.sb_nr_steps = QtGui.QSpinBox(Form)
        self.sb_nr_steps.setGeometry(QtCore.QRect(120, 120, 61, 22))
        self.sb_nr_steps.setObjectName(_fromUtf8("sb_nr_steps"))
        self.button_start = QtGui.QPushButton(Form)
        self.button_start.setGeometry(QtCore.QRect(50, 200, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_start.setFont(font)
        self.button_start.setObjectName(_fromUtf8("button_start"))
        self.button_save = QtGui.QPushButton(Form)
        self.button_save.setGeometry(QtCore.QRect(50, 230, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_save.setFont(font)
        self.button_save.setObjectName(_fromUtf8("button_save"))
        self.label_ctr_V_2 = QtGui.QLabel(Form)
        self.label_ctr_V_2.setGeometry(QtCore.QRect(40, 0, 61, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_ctr_V_2.setFont(font)
        self.label_ctr_V_2.setObjectName(_fromUtf8("label_ctr_V_2"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_ctr_V.setText(_translate("Form", "min V", None))
        self.label_V_step.setText(_translate("Form", "max V", None))
        self.label_avg.setText(_translate("Form", "wait time [msec]", None))
        self.label_steps.setText(_translate("Form", "nr steps", None))
        self.button_start.setText(_translate("Form", "START", None))
        self.button_save.setText(_translate("Form", "STOP", None))
        self.label_ctr_V_2.setText(_translate("Form", "IDLE...", None))

