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
from threading import Timer
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


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
        self.pushButton_2.toggled.connect(self.on_pushButton_2_clicked)  # Home button
        self.pushButton_3.toggled.connect(self.on_pushButton_3_clicked)  # Set Position button
        self.pushButton_4.toggled.connect(self.on_pushButton_4_clicked)  # Get Position button
        self.pushButton_6.toggled.connect(self.on_pushButton_6_clicked)  # Clean Error

        self.pushButton_7.toggled.connect(self.on_pushButton_7_clicked)  # Move Left
        self.pushButton_8.toggled.connect(self.on_pushButton_8_clicked)  # Move Right
        self.pushButton_9.toggled.connect(self.on_pushButton_9_clicked)  # Move Down
        self.pushButton_10.toggled.connect(self.on_pushButton_10_clicked)  # Move Up
        self.pushButton_11.toggled.connect(self.on_pushButton_11_clicked)  # Move Forward
        self.pushButton_12.toggled.connect(self.on_pushButton_12_clicked)  # Move Backward
        self.pushButton_13.toggled.connect(self.on_pushButton_13_clicked)  # Move a+
        self.pushButton_14.toggled.connect(self.on_pushButton_14_clicked)  # Move a-
        self.pushButton_15.toggled.connect(self.on_pushButton_15_clicked)  # Move b+
        self.pushButton_16.toggled.connect(self.on_pushButton_16_clicked)  # Move b-
        self.pushButton_17.toggled.connect(self.on_pushButton_17_clicked)  # Move g+
        self.pushButton_18.toggled.connect(self.on_pushButton_18_clicked)  # Move g-

        self.checkBox_10.stateChanged.connect(self.on_checkBox_10_valueChanged)      #Brakes release
        self.checkBox_11.stateChanged.connect(self.on_checkBox_11_valueChanged)      #Partial brakes release
        # Flags
        self.is_running = False 
        self.Robot_instance = None
        self.start_button_toggle_time = int(round(time.time() * 1000))
        self.show()
        
    @pyqtSlot()
    def on_dial_valueChanged(self):
        self.US_power=self.dial.value()/10
        self.spinBox_2.setValue(self.US_power)
        
    def speak(self,text='Default option'):
        if self.voice_indications==False:
            return

    def debug_print(self,msg):
        if msg == None:
            return
        if DEBUG>2:
            with open("Debug_log.txt", "a") as myfile:
                myfile.write(msg)
                myfile.write('\r\n')
        if DEBUG==4 or DEBUG==2:
            self.label_4.setText(msg)

    @pyqtSlot()
    def on_pushButton_3_clicked(self):  ###  Set position button ###
        if self.Robot_instance is not None:
            str_to_send='MoveLin('+self.plainTextEdit.toPlainText()+', '
            str_to_send+=self.plainTextEdit_2.toPlainText()+', '
            str_to_send+=self.plainTextEdit_3.toPlainText()+', '
            str_to_send+=self.plainTextEdit_4.toPlainText()+', '
            str_to_send+=self.plainTextEdit_5.toPlainText()+', '
            str_to_send+=self.plainTextEdit_6.toPlainText()+')'
            self.Robot_instance.send_str(str_to_send)

    @pyqtSlot()
    def on_pushButton_6_clicked(self):  ###  Clean Error button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('ResetError')


    @pyqtSlot()
    def on_pushButton_7_clicked(self):  ###  Move Left button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(1, 0, 0, 0, 0, 0)')

    @pyqtSlot()
    def on_pushButton_8_clicked(self):  ###  Move Right button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(-1, 0, 0, 0, 0, 0)')

    @pyqtSlot()
    def on_pushButton_9_clicked(self):  ###  Move Down button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, -1, 0, 0, 0, 0)')

    @pyqtSlot()
    def on_pushButton_10_clicked(self):  ###  Move Up button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, 1, 0, 0, 0, 0)')


    @pyqtSlot()
    def on_pushButton_11_clicked(self):  ###  Move Backward button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, 0, -1, 0, 0, 0)')

    @pyqtSlot()
    def on_pushButton_12_clicked(self):  ###  Move Forward button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, 0, 1, 0, 0, 0)')

    @pyqtSlot()
    def on_pushButton_13_clicked(self):  ###  Move a+ button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, 0, 0, 1, 0, 0)')

    @pyqtSlot()
    def on_pushButton_14_clicked(self):  ###  Move a- button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, 0, 0, -1, 0, 0)')

    @pyqtSlot()
    def on_pushButton_15_clicked(self):  ###  Move b+ button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, 0, 0, 0, 1, 0)')

    @pyqtSlot()
    def on_pushButton_16_clicked(self):  ###  Move b- button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, 0, 0, 0, -1, 0)')

    @pyqtSlot()
    def on_pushButton_17_clicked(self):  ###  Move g+ button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, 0, 0, 0, 0, 1)')

    @pyqtSlot()
    def on_pushButton_18_clicked(self):  ###  Move g- button ###
        if self.Robot_instance is not None:   
            self.Robot_instance.send_str('MoveLinRelTRF(0, 0, 0, 0, 0, -1)')

    @pyqtSlot()
    def on_pushButton_2_clicked(self):  ###  Home button ###
        if self.Robot_instance is not None:             
            self.Robot_instance.send_str('ResetError')
            self.Robot_instance.send_str('Home')


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

            self.local_timer=RepeatTimer(0.1, self.Robot_instance.get_response)    
            self.local_timer.start()    

            self.UI_update_timer=RepeatTimer(0.05, self.update)    
            self.UI_update_timer.start()  
            # self.thread = Robot_reader_thread(self, self.Robot_instance)
            # self.thread.Reader_update_signal.connect(self.update)
            # self.thread.run()
            self.Robot_instance.Initialize_Robot()

        else:
            if self.is_running== True:
                self.local_timer.stop()    
                self.UI_update_timer.stop()  
                self.Robot_instance.Disconnect()
                self.pushButton.setStyleSheet("background-color: red")
                self.is_running = False
                self.Robot_instance = None                

    @pyqtSlot()
    def update(self):
        self.debug_print(self.Robot_instance.last_Robot_response)


    @pyqtSlot()
    def on_pushButton_4_clicked(self):
        self.debug_print('Position request')
        if self.Robot_instance is not None:
            try:
                self.Robot_instance.send_str('GetPose')
                QtTest.QTest.qWait(10)
                if self.Robot_instance.last_Robot_pos is not None:
                    self.plainTextEdit.setPlainText(str(self.Robot_instance.last_Robot_pos[0]))           
                    self.plainTextEdit_2.setPlainText(str(self.Robot_instance.last_Robot_pos[1]))           
                    self.plainTextEdit_3.setPlainText(str(self.Robot_instance.last_Robot_pos[2]))           
                    self.plainTextEdit_4.setPlainText(str(self.Robot_instance.last_Robot_pos[3]))           
                    self.plainTextEdit_5.setPlainText(str(self.Robot_instance.last_Robot_pos[4]))           
                    self.plainTextEdit_6.setPlainText(str(self.Robot_instance.last_Robot_pos[5]))  
            except:
                self.Robot_instance.send_str('ResetError')
                QtTest.QTest.qWait(100)
                self.Robot_instance.send_str('GetPose')
                QtTest.QTest.qWait(10)
                if self.Robot_instance.last_Robot_pos is not None:
                    self.plainTextEdit.setPlainText(str(self.Robot_instance.last_Robot_pos[0]))           
                    self.plainTextEdit_2.setPlainText(str(self.Robot_instance.last_Robot_pos[1]))           
                    self.plainTextEdit_3.setPlainText(str(self.Robot_instance.last_Robot_pos[2]))           
                    self.plainTextEdit_4.setPlainText(str(self.Robot_instance.last_Robot_pos[3]))           
                    self.plainTextEdit_5.setPlainText(str(self.Robot_instance.last_Robot_pos[4]))           
                    self.plainTextEdit_6.setPlainText(str(self.Robot_instance.last_Robot_pos[5]))           



    @pyqtSlot()
    def on_checkBox_10_valueChanged(self): #  Brakes release
        if self.checkBox_10.isChecked():
            self.Robot_instance.send_str('DeactivateRobot')
            self.Robot_instance.send_str('BrakesOff')
        else:
            self.Robot_instance.send_str('BrakesOn')
            self.Robot_instance.send_str('ActivateRobot')
            QtTest.QTest.qWait(2000)
            self.Robot_instance.send_str('Home')


    @pyqtSlot()
    def on_checkBox_11_valueChanged(self): # Partial brakes release
        if self.checkBox_11.isChecked():
            self.Robot_instance.send_str('DeactivateRobot')
        else:
            self.Robot_instance.send_str('ActivateRobot')
            QtTest.QTest.qWait(2000)
            self.Robot_instance.send_str('Home')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.processEvents()
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())