# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:tud276198\Desktop\temperature_controller.ui'
#
# Created: Wed Mar 02 16:50:43 2016
#      by: PyQt4 UI code generator 4.10.3
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
        Panel.resize(557, 655)
        self.displayMessage = QtGui.QLineEdit(Panel)
        self.displayMessage.setGeometry(QtCore.QRect(20, 120, 141, 20))
        self.displayMessage.setObjectName(_fromUtf8("displayMessage"))
        self.readButton = QtGui.QPushButton(Panel)
        self.readButton.setGeometry(QtCore.QRect(100, 150, 151, 23))
        self.readButton.setObjectName(_fromUtf8("readButton"))
        self.setTempButton = QtGui.QPushButton(Panel)
        self.setTempButton.setGeometry(QtCore.QRect(130, 50, 151, 23))
        self.setTempButton.setObjectName(_fromUtf8("setTempButton"))
        self.fontComboBox = QtGui.QFontComboBox(Panel)
        self.fontComboBox.setGeometry(QtCore.QRect(-220, 280, 188, 22))
        self.fontComboBox.setObjectName(_fromUtf8("fontComboBox"))
        self.setTemp = QtGui.QLineEdit(Panel)
        self.setTemp.setGeometry(QtCore.QRect(232, 120, 131, 20))
        self.setTemp.setObjectName(_fromUtf8("setTemp"))
        self.doubleSpinBox = QtGui.QDoubleSpinBox(Panel)
        self.doubleSpinBox.setGeometry(QtCore.QRect(40, 50, 62, 22))
        self.doubleSpinBox.setObjectName(_fromUtf8("doubleSpinBox"))
        self.label = QtGui.QLabel(Panel)
        self.label.setGeometry(QtCore.QRect(50, 90, 111, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Panel)
        self.label_2.setGeometry(QtCore.QRect(240, 90, 111, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Panel)
        self.label_3.setGeometry(QtCore.QRect(150, 190, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.displayMessage_2 = QtGui.QLineEdit(Panel)
        self.displayMessage_2.setGeometry(QtCore.QRect(110, 220, 141, 20))
        self.displayMessage_2.setObjectName(_fromUtf8("displayMessage_2"))
        self.graphicsView = QtGui.QGraphicsView(Panel)
        self.graphicsView.setGeometry(QtCore.QRect(60, 290, 431, 321))
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))

        self.retranslateUi(Panel)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(_translate("Panel", "Widget", None))
        self.readButton.setText(_translate("Panel", "Reset Voltage to 0", None))
        self.setTempButton.setText(_translate("Panel", "Set Temperature", None))
        self.label.setText(_translate("Panel", "Actual Temperature", None))
        self.label_2.setText(_translate("Panel", "Target Temperature", None))
        self.label_3.setText(_translate("Panel", "DFG power", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Panel = QtGui.QWidget()
    ui = Ui_Panel()
    ui.setupUi(Panel)
    Panel.show()
    sys.exit(app.exec_())

