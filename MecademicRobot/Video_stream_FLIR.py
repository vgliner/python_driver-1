import os
import pyspin as PySpin
from threading import Timer,Thread,Event
import time
import PyQt5
from PyQt5.QtWidgets import QDialog, QApplication, QTabWidget, QTableWidgetItem, QLabel, QGraphicsPixmapItem,QWidget, QSizePolicy
from PyQt5.QtCore import pyqtSlot,QThread, QObject, pyqtSignal,QSize, QTimer
from PyQt5.QtGui import *
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtTest



NUM_IMAGES = 10  # number of images to grab

def Timer_func():
    print('Timer activated')

def acquire_images(cam_list):
    """
    This function acquires and saves 10 images from each device.

    :param cam_list: List of cameras
    :type cam_list: CameraList
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***\n')
    try:
        result = True

        # Prepare each camera to acquire images
        #
        # *** NOTES ***
        # For pseudo-simultaneous streaming, each camera is prepared as if it
        # were just one, but in a loop. Notice that cameras are selected with
        # an index. We demonstrate pseduo-simultaneous streaming because true
        # simultaneous streaming would require multiple process or threads,
        # which is too complex for an example.
        #

        for i, cam in enumerate(cam_list):

            # Set acquisition mode to continuous
            node_acquisition_mode = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (node retrieval; camera %d). Aborting... \n' % i)
                return False

            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry \'continuous\' retrieval %d). \
                Aborting... \n' % i)
                return False

            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

            print('Camera %d acquisition mode set to continuous...' % i)

            # Begin acquiring images
            cam.BeginAcquisition()

            print('Camera %d started acquiring images...' % i)

            print()

        # Retrieve, convert, and save images for each camera
        #
        # *** NOTES ***
        # In order to work with simultaneous camera streams, nested loops are
        # needed. It is important that the inner loop be the one iterating
        # through the cameras; otherwise, all images will be grabbed from a
        # single camera before grabbing any images from another.
        for n in range(NUM_IMAGES):
            for i, cam in enumerate(cam_list):
                try:
                    # Retrieve device serial number for filename
                    node_device_serial_number = PySpin.CStringPtr(cam.GetTLDeviceNodeMap().GetNode('DeviceSerialNumber'))

                    if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                        device_serial_number = node_device_serial_number.GetValue()
                        print('Camera %d serial number set to %s...' % (i, device_serial_number))

                    # Retrieve next received image and ensure image completion
                    image_result = cam.GetNextImage()

                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ... \n' % image_result.GetImageStatus())
                    else:
                        # Print image information
                        width = image_result.GetWidth()
                        height = image_result.GetHeight()
                        print('Camera %d grabbed image %d, width = %d, height = %d' % (i, n, width, height))

                        # Convert image to mono 8
                        image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)

                        # Create a unique filename
                        if device_serial_number:
                            filename = 'AcquisitionMultipleCamera-%s-%d.jpg' % (device_serial_number, n)
                        else:
                            filename = 'AcquisitionMultipleCamera-%d-%d.jpg' % (i, n)

                        # Save image
                        image_converted.Save(filename)
                        print('Image saved at %s' % filename)

                    # Release image
                    image_result.Release()
                    print()

                except PySpin.SpinnakerException as ex:
                    print('Error: %s' % ex)
                    result = False

        # End acquisition for each camera
        #
        # *** NOTES ***
        # Notice that what is usually a one-step process is now two steps
        # because of the additional step of selecting the camera. It is worth
        # repeating that camera selection needs to be done once per loop.
        #
        # It is possible to interact with cameras through the camera list with
        # GetByIndex(); this is an alternative to retrieving cameras as
        # CameraPtr objects that can be quick and easy for small tasks.
        for cam in cam_list:

            # End acquisition
            cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def acquire_images_modified(cam_list):
    try:
        result = True
        image_converted=None
        for i, cam in enumerate(cam_list):
            image_result = cam.GetNextImage()
            image_converted[i] = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
            image_result.Release()
        return image_converted
        
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

def print_device_info(nodemap, cam_num):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :param cam_num: Camera number.
    :type nodemap: INodeMap
    :type cam_num: int
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('Printing device information for camera %d... \n' % cam_num)

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not available.')
        print()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def run_multiple_cameras(cam_list):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam_list: List of cameras
    :type cam_list: CameraList
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve transport layer nodemaps and print device information for
        # each camera
        # *** NOTES ***
        # This example retrieves information from the transport layer nodemap
        # twice: once to print device information and once to grab the device
        # serial number. Rather than caching the nodem#ap, each nodemap is
        # retrieved both times as needed.
        print('*** DEVICE INFORMATION ***\n')

        for i, cam in enumerate(cam_list):

            # Retrieve TL device nodemap
            nodemap_tldevice = cam.GetTLDeviceNodeMap()

            # Print device information
            result &= print_device_info(nodemap_tldevice, i)

        # Initialize each camera
        #
        # *** NOTES ***
        # You may notice that the steps in this function have more loops with
        # less steps per loop; this contrasts the AcquireImages() function
        # which has less loops but more steps per loop. This is done for
        # demonstrative purposes as both work equally well.
        #
        # *** LATER ***
        # Each camera needs to be deinitialized once all images have been
        # acquired.
        for i, cam in enumerate(cam_list):

            # Initialize camera
            cam.Init()

        # Acquire images on all cameras
        result &= acquire_images(cam_list)

        # Deinitialize each camera
        #
        # *** NOTES ***
        # Again, each camera must be deinitialized separately by first
        # selecting the camera and then deinitializing it.
        for cam in cam_list:

            # Deinitialize camera
            cam.DeInit()

        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        del cam

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def Multiple_cameras_acquisition_thread(label1, label2):
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    num_cameras = cam_list.GetSize()
    print('Number of cameras detected: %d' % num_cameras)
    # Finish if there are no cameras
    if num_cameras == 0:
        # Clear camera list before releasing system
        cam_list.Clear()
        # Release system instance
        system.ReleaseInstance()
        print('Not enough cameras!')
    for i, cam in enumerate(cam_list):
        # Initialize camera
        cam.Init()        
    for i, cam in enumerate(cam_list):
        # Set acquisition mode to continuous
        node_acquisition_mode = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (node retrieval; camera %d). Aborting... \n' % i)
            return False
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry \'continuous\' retrieval %d). \
            Aborting... \n' % i)
            return False
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
        print('Camera %d acquisition mode set to continuous...' % i)
        # Begin acquiring images
        cam.BeginAcquisition()    
        
    while True:        
        for i, cam in enumerate(cam_list):
            image_result = cam.GetNextImage()
            h= image_result.GetHeight()
            w = image_result.GetWidth()
            convertToQtFormat = QtGui.QImage(image_result.GetData(), w, h, QtGui.QImage.Format_Grayscale8) 
            if i==0:                
                label1.setPixmap(QPixmap.fromImage(convertToQtFormat))                      
            else:
                label2.setPixmap(QPixmap.fromImage(convertToQtFormat))  
        time.sleep(0.001)

def run_multiple_cameras_modified(cam_list):
    print('6')
    result = True
    for i, cam in enumerate(cam_list):
        print('7')
        # Retrieve TL device nodemap
        nodemap_tldevice = cam.GetTLDeviceNodeMap()
        # Print device information
        # result &= print_device_info(nodemap_tldevice, i)    
        for i, cam in enumerate(cam_list):
            # Initialize camera
            cam.Init()
        for i, cam in enumerate(cam_list):
            # Set acquisition mode to continuous
            node_acquisition_mode = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (node retrieval; camera %d). Aborting... \n' % i)
                return False
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry \'continuous\' retrieval %d). \
                Aborting... \n' % i)
                return False
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
            print('Camera %d acquisition mode set to continuous...' % i)
            # Begin acquiring images
            cam.BeginAcquisition()            



def main():
    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on all cameras
    print('Running example for all cameras...')

    result = run_multiple_cameras(cam_list)

    print('Example complete... \n')

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')
    return result

if __name__ == '__main__':
    main()