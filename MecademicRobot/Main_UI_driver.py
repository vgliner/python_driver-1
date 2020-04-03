# %gui qt
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QTabWidget, QTableWidgetItem, QLabel, QGraphicsPixmapItem,QWidget, QSizePolicy
from PyQt5.QtCore import pyqtSlot,QThread, QObject, pyqtSignal,QSize, QTimer
from PyQt5.QtGui import *
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtTest
import time
import os
import multiprocessing
import concurrent.futures
import numpy as np
import pathlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import threading
from My_Robot_Engine import *
import time

##########
import playsound
from gtts import gTTS
from io import BytesIO

import win32com.client as wincl
# import speech_recognition as sr



##########PRESETS#########
enable_sound=True
DEBUG=4   # 4 -Log and UI, 3 - Log , 2 - UI, 1 - None

##########################

class Robot_reader_thread(QThread):
    
    Reader_update_signal= QtCore.pyqtSignal()
    is_running=True

    def __init__(self, parent, Robot_instance):
        super(Robot_reader_thread, self).__init__(parent)
        self.Robot_instance = Robot_instance
        self._isRunning = True

    def run(self):
        # i = 0
        # while (i<self.n) and self._isRunning:
        #     if (time.time() % 1==0):
        #         i+=1
        #         print(str(i))
        #         self.Reader_update_signal.emit()
        self._timer_receiver = QTimer(self)
        self._timer_receiver.start(100)
        self._timer_receiver.timeout.connect(self.my_print) 

    def my_print(self):
        self.Robot_instance.get_response()
        print('Inner debug- thread fired')

    def stop(self):
        self._timer_receiver.stop()


class AppWindow(QDialog):
    def __init__(self):
        super(AppWindow,self).__init__()
        self.title = 'Vision AR&D VR Prototype'
        cwd=os.path.dirname(os.path.abspath(__file__))+'\\'
        loadUi(cwd+'UI_layout.ui',self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setPixmap(QtGui.QPixmap("jnj_vision_logo_rgb.png"))        
        self.pushButton.toggled.connect(self.on_pushButton_clicked)  # Start button
        self.checkBox_10.stateChanged.connect(self.on_checkBox_10_valueChanged)      #Brakes release
        self.checkBox_11.stateChanged.connect(self.on_checkBox_11_valueChanged)      #Partial brakes release
        # Flags
        self.is_running = False 
        self.start_button_toggle_time = int(round(time.time() * 1000))
        print(f'T: {self.start_button_toggle_time}')
        self.show()
        
    @pyqtSlot()
    def on_dial_valueChanged(self):
        self.US_power=self.dial.value()/10
        self.spinBox_2.setValue(self.US_power)
        
    def speak(self,text='Default option'):
        if self.voice_indications==False:
            return

    def debug_print(self,msg):
        if DEBUG>2:
            with open("Debug_log.txt", "a") as myfile:
                myfile.write(msg)
                myfile.write('\r\n')
        if DEBUG==4 or DEBUG==2:
            self.label_4.setText(msg)

    @pyqtSlot()
    def on_pushButton_clicked(self):  ###  Start button ###
        QApplication.processEvents() 
        if int(round(time.time() * 1000))- self.start_button_toggle_time <5000:
            return
        self.start_button_toggle_time= int(round(time.time() * 1000))
        if self.pushButton.isChecked() and self.is_running== False:  # Turn on
            self.is_running= True
            self.Robot_instance=RobotController()
            self.pushButton.setStyleSheet("background-color: red")
            self.debug_print('Establishing connection to robot')
            self.Robot_instance.establish_connection("192.168.0.100",10000)
            self.debug_print('Connection established')
            self.pushButton.setStyleSheet("background-color: green")
                # Establish feedback channels
            # self._timer_receiver = QTimer(self)
            # self._timer_receiver.start(50)
            # self._timer_receiver.timeout.connect(self.Robot_instance.get_response) 
            self.thread = Robot_reader_thread(self, self.Robot_instance)
            self.thread.Reader_update_signal.connect(self.update)
            self.thread.run()
            self.Robot_instance.Initialize_Robot()

        else:
            if self.is_running== True:
                self.thread.stop()
                self.Robot_instance.Disconnect()
                self.pushButton.setStyleSheet("background-color: red")
                self.is_running = False

    @pyqtSlot()
    def update(self):
        print('Thread fired')


    @pyqtSlot()
    def on_checkBox_10_valueChanged(self): #  Brakes release
        if self.checkBox_10.isChecked():
            self.Robot_instance.send_str('DeactivateRobot')
            self.Robot_instance.send_str('BrakesOff')
        else:
            self.Robot_instance.send_str('BrakesOn')
            self.Robot_instance.send_str('ActivateRobot')

    @pyqtSlot()
    def on_checkBox_11_valueChanged(self): # Partial brakes release
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.processEvents()
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())