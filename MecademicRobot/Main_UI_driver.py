# %gui qt
import sys
import PyQt5
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
import Video_stream_FLIR
import pyspin as PySpin
from pyueye import ueye
import cv2
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
        self.pushButton_19.toggled.connect(self.on_pushButton_19_clicked)  # Start video stream button

        self.checkBox_10.stateChanged.connect(self.on_checkBox_10_valueChanged)      #Brakes release
        self.checkBox_11.stateChanged.connect(self.on_checkBox_11_valueChanged)      #Partial brakes release
        # Flags
        self.is_running = False 
        self.Robot_instance = None
        self.start_button_toggle_time = int(round(time.time() * 1000))
        self.video_button_toggle_time = int(round(time.time() * 1000))
        # Video
        self.cam_list=None
        self.num_cameras=None


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


    def Real_camera_stream(self, camera_ID):
        hCam1 = ueye.HIDS(camera_ID)             #0: first available camera;  1-254: The camera with the specified camera ID
        sInfo = ueye.SENSORINFO()
        cInfo = ueye.CAMINFO()
        pcImageMemory = ueye.c_mem_p()        
        MemID = ueye.int()
        rectAOI = ueye.IS_RECT()
        pitch = ueye.INT()
        nBitsPerPixel = ueye.INT(24)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
        channels = 3                    #3: channels for color mode(RGB); take 1 channel for monochrome
        m_nColorMode = ueye.INT()		# Y8/RGB16/RGB24/REG32
        bytes_per_pixel = int(nBitsPerPixel / 8)
        nRet1 = ueye.is_InitCamera(hCam1, None)
        if nRet1 != ueye.IS_SUCCESS:
            print(f'is_InitCamera ERROR. ID: {camera_ID}')
        else:
            print(f'Camera {camera_ID} : SUCCESS')
        # Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
        nRet1 = ueye.is_GetCameraInfo(hCam1, cInfo)
        if nRet1 != ueye.IS_SUCCESS:
            print("is_GetCameraInfo ERROR")
        # You can query additional information about the sensor type used in the camera
        nRet1 = ueye.is_GetSensorInfo(hCam1, sInfo)
        if nRet1 != ueye.IS_SUCCESS:
            print("is_GetSensorInfo ERROR")
        # nRet1 = ueye.is_ResetToDefault( hCam1)
        # if nRet1 != ueye.IS_SUCCESS:
        #     print("is_ResetToDefault ERROR")
        # Set display mode to DIB
        nRet1 = ueye.is_SetDisplayMode(hCam1, ueye.IS_SET_DM_DIB)
        # Set the right color mode
        if int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_BAYER:
            # setup the color depth to the current windows setting
            ueye.is_GetColorDepth(hCam1, nBitsPerPixel, m_nColorMode)
            bytes_per_pixel = int(nBitsPerPixel / 8)
            print("IS_COLORMODE_BAYER: ", )
            print("\tm_nColorMode: \t\t", m_nColorMode)
            print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
            print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
            print()
        elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_CBYCRY:
            # for color camera models use RGB32 mode
            m_nColorMode = ueye.IS_CM_BGRA8_PACKED
            nBitsPerPixel = ueye.INT(32)
            bytes_per_pixel = int(nBitsPerPixel / 8)
            print("IS_COLORMODE_CBYCRY: ", )
            print("\tm_nColorMode: \t\t", m_nColorMode)
            print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
            print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
            print()

        elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_MONOCHROME:
            # for color camera models use RGB32 mode
            m_nColorMode = ueye.IS_CM_MONO8
            nBitsPerPixel = ueye.INT(8)
            bytes_per_pixel = int(nBitsPerPixel / 8)
            print("IS_COLORMODE_MONOCHROME: ", )
            print("\tm_nColorMode: \t\t", m_nColorMode)
            print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
            print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
            print()

        else:
            # for monochrome camera models use Y8 mode
            m_nColorMode = ueye.IS_CM_MONO8
            nBitsPerPixel = ueye.INT(8)
            bytes_per_pixel = int(nBitsPerPixel / 8)
            print("else")

        # Can be used to set the size and position of an "area of interest"(AOI) within an image
        nRet1 = ueye.is_AOI(hCam1, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
        if nRet1 != ueye.IS_SUCCESS:
            print("is_AOI ERROR")

        width = rectAOI.s32Width
        height = rectAOI.s32Height

        # Prints out some information about the camera and the sensor
        print("Camera model:\t\t", sInfo.strSensorName.decode('utf-8'))
        print("Camera serial no.:\t", cInfo.SerNo.decode('utf-8'))
        print("Maximum image width:\t", width)
        print("Maximum image height:\t", height)
        print()
        # Allocates an image memory for an image having its dimensions defined by width and height and its color depth defined by nBitsPerPixel
        nRet1 = ueye.is_AllocImageMem(hCam1, width, height, nBitsPerPixel, pcImageMemory, MemID)
        if nRet1 != ueye.IS_SUCCESS:
            print("is_AllocImageMem ERROR")
        else:
            # Makes the specified image memory the active memory
            nRet = ueye.is_SetImageMem(hCam1, pcImageMemory, MemID)
            if nRet != ueye.IS_SUCCESS:
                print("is_SetImageMem ERROR")
            else:
                # Set the desired color mode
                nRet = ueye.is_SetColorMode(hCam1, m_nColorMode)
            if nRet1 != ueye.IS_SUCCESS:
                print("is_AllocImageMem ERROR")
            else:
                # Makes the specified image memory the active memory
                nRet = ueye.is_SetImageMem(hCam1, pcImageMemory, MemID)
        nRet = ueye.is_CaptureVideo(hCam1, ueye.IS_DONT_WAIT)
        nRet = ueye.is_InquireImageMem(hCam1, pcImageMemory, MemID, width, height, nBitsPerPixel, pitch)
        _reference_image=0
        while(self.pushButton_19.isChecked()):    
            array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)          
            frame = np.reshape(array,(height.value, width.value, bytes_per_pixel))
            image= frame    
            rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)            
            h, w= grayImage.shape
            ch=3
            bytesPerLine = ch * w
            convertToQtFormat = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)     
            if camera_ID==1:                
                self.label_11.setPixmap(QPixmap.fromImage(convertToQtFormat))                      
            else:
                self.label_14.setPixmap(QPixmap.fromImage(convertToQtFormat))                                                                    
            time.sleep(0.05)


    @pyqtSlot()
    def on_pushButton_19_clicked(self):  ###  # Toggle video stream ###
        QApplication.processEvents() 
        if int(round(time.time() * 1000))- self.video_button_toggle_time <5000:
            return
        self.video_button_toggle_time= int(round(time.time() * 1000)) 
        t1= threading.Thread(target=self.Real_camera_stream,args=[1])        
        t1.start()
        time.sleep(0.1) 



        # t1= threading.Thread(target=self.Real_camera_stream,args=[2])        
        # t1.start()
        # time.sleep(0.1)                   



        
        # print('Push button 19 activated ')    
        # if self.pushButton_19.isChecked():  # Video stream is on
        #     try:
        #         self.t1= threading.Thread(target=Video_stream_FLIR.Multiple_cameras_acquisition_thread,args=[self.label_14,self.label_11])        
        #         self.t1.start()
        #         # Video_stream_FLIR.Multiple_cameras_acquisition_thread()      
        #         # QThread.msleep(1000)
        #         print('Debug end')
        #     except:
        #         print('Exception thrown')
          
        # else:  # Video stream is off
        #     self.t1.isAlive=False


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