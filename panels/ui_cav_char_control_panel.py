# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/char_cav_control_panel.ui'
#
# Created: Fri Jul 22 11:11:21 2016
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

class Ui_Panel(object):
    def setupUi(self, Panel):
        Panel.setObjectName(_fromUtf8("Panel"))
        Panel.resize(337, 106)
        self.label_11 = QtGui.QLabel(Panel)
        self.label_11.setGeometry(QtCore.QRect(20, 20, 162, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalSlider_p1 = QtGui.QSlider(Panel)
        self.horizontalSlider_p1.setGeometry(QtCore.QRect(20, 50, 231, 19))
        self.horizontalSlider_p1.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_p1.setObjectName(_fromUtf8("horizontalSlider_p1"))
        self.doubleSpinBox_p1 = QtGui.QDoubleSpinBox(Panel)
        self.doubleSpinBox_p1.setGeometry(QtCore.QRect(260, 30, 53, 20))
        self.doubleSpinBox_p1.setObjectName(_fromUtf8("doubleSpinBox_p1"))

        self.retranslateUi(Panel)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(_translate("Panel", "Panel", None))
        self.label_11.setText(_translate("Panel", "FINE POSITIONING", None))

