

#Libraries
from pyueye import ueye
import numpy as np
import cv2
import sys
import threading

#---------------------------------------------------------------------------------------------------------------------------------------
def Cameras_stream():
    #Variables
    hCam1 = ueye.HIDS(1)             #0: first available camera;  1-254: The camera with the specified camera ID
    hCam2 = ueye.HIDS(2)             #0: first available camera;  1-254: The camera with the specified camera ID

    sInfo = ueye.SENSORINFO()
    cInfo = ueye.CAMINFO()
    pcImageMemory = ueye.c_mem_p()
    pcImageMemory2 = ueye.c_mem_p()
    MemID = ueye.int()
    MemID2 = ueye.int()

    rectAOI = ueye.IS_RECT()
    pitch = ueye.INT()
    nBitsPerPixel = ueye.INT(24)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
    channels = 3                    #3: channels for color mode(RGB); take 1 channel for monochrome
    m_nColorMode = ueye.INT()		# Y8/RGB16/RGB24/REG32
    bytes_per_pixel = int(nBitsPerPixel / 8)
    #---------------------------------------------------------------------------------------------------------------------------------------
    # print("START")
    # print()


    # Starts the driver and establishes the connection to the camera
    nRet1 = ueye.is_InitCamera(hCam1, None)
    if nRet1 != ueye.IS_SUCCESS:
        pass
        # print("is_InitCamera ERROR")
    else:
        print(f'Camera 1 : SUCCESS')

    nRet2 = ueye.is_InitCamera(hCam2, None)
    if nRet2 != ueye.IS_SUCCESS:
        pass
        # print("is_InitCamera ERROR")
    else:
        print(f'Camera 2 : SUCCESS')


    # Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
    nRet1 = ueye.is_GetCameraInfo(hCam1, cInfo)
    if nRet1 != ueye.IS_SUCCESS:
        print("is_GetCameraInfo ERROR")
        
    nRet2 = ueye.is_GetCameraInfo(hCam2, cInfo)
    if nRet2 != ueye.IS_SUCCESS:
        print("is_GetCameraInfo ERROR")

    # You can query additional information about the sensor type used in the camera
    nRet1 = ueye.is_GetSensorInfo(hCam1, sInfo)
    if nRet1 != ueye.IS_SUCCESS:
        print("is_GetSensorInfo ERROR")

    nRet1 = ueye.is_ResetToDefault( hCam1)
    if nRet1 != ueye.IS_SUCCESS:
        print("is_ResetToDefault ERROR")

    # Set display mode to DIB
    nRet1 = ueye.is_SetDisplayMode(hCam1, ueye.IS_SET_DM_DIB)
    nRet2 = ueye.is_SetDisplayMode(hCam2, ueye.IS_SET_DM_DIB)

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

    #---------------------------------------------------------------------------------------------------------------------------------------

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
        if nRet != ueye.IS_SUCCESS:
            print("is_SetImageMem ERROR")
        else:
            # Set the desired color mode
            nRet = ueye.is_SetColorMode(hCam2, m_nColorMode)
    # Allocates an image memory for an image having its dimensions defined by width and height and its color depth defined by nBitsPerPixel
    nRet = ueye.is_AllocImageMem(hCam2, width, height, nBitsPerPixel, pcImageMemory2, MemID2)
    if nRet != ueye.IS_SUCCESS:
        print("is_AllocImageMem ERROR")
    else:
        # Makes the specified image memory the active memory
        nRet = ueye.is_SetImageMem(hCam2, pcImageMemory2, MemID2)
        if nRet != ueye.IS_SUCCESS:
            print("is_SetImageMem ERROR")
        else:
            # Set the desired color mode
            nRet = ueye.is_SetColorMode(hCam2, m_nColorMode)
    nRet = ueye.is_AllocImageMem(hCam2, width, height, nBitsPerPixel, pcImageMemory2, MemID2)
    if nRet != ueye.IS_SUCCESS:
        print("is_AllocImageMem ERROR")
    else:
        # Makes the specified image memory the active memory
        nRet = ueye.is_SetImageMem(hCam2, pcImageMemory2, MemID2)
        if nRet != ueye.IS_SUCCESS:
            print("is_SetImageMem ERROR")
        else:
            # Set the desired color mode
            nRet = ueye.is_SetColorMode(hCam2, m_nColorMode)

    # Activates the camera's live video mode (free run mode)
    nRet = ueye.is_CaptureVideo(hCam1, ueye.IS_DONT_WAIT)
    if nRet != ueye.IS_SUCCESS:
        print("is_CaptureVideo ERROR")
    nRet = ueye.is_CaptureVideo(hCam2, ueye.IS_DONT_WAIT)
    if nRet != ueye.IS_SUCCESS:
        print("is_CaptureVideo ERROR")

    # Enables the queue mode for existing image memory sequences
    nRet = ueye.is_InquireImageMem(hCam1, pcImageMemory, MemID, width, height, nBitsPerPixel, pitch)
    if nRet != ueye.IS_SUCCESS:
        print("is_InquireImageMem ERROR")
    else:
        print("Press q to leave the programm")
    nRet2 = ueye.is_InquireImageMem(hCam2, pcImageMemory2, MemID, width, height, nBitsPerPixel, pitch)
    if nRet2 != ueye.IS_SUCCESS:
        print("is_InquireImageMem ERROR")
    else:
        print("Press q to leave the programm")
    #---------------------------------------------------------------------------------------------------------------------------------------

    # Continuous image display
    while(nRet == ueye.IS_SUCCESS) and (nRet2 == ueye.IS_SUCCESS):

        # In order to display the image in an OpenCV window we need to...
        # ...extract the data of our image memory
        array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)
        array2 = ueye.get_data(pcImageMemory2, width, height, nBitsPerPixel, pitch, copy=False)

        # bytes_per_pixel = int(nBitsPerPixel / 8)

        # ...reshape it in an numpy array...
        frame = np.reshape(array,(height.value, width.value, bytes_per_pixel))
        frame2 = np.reshape(array2,(height.value, width.value, bytes_per_pixel))

        # ...resize the image by a half
        # frame = cv2.resize(frame,(0,0),fx=0.5, fy=0.5)
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        #Include image data processing here

    #---------------------------------------------------------------------------------------------------------------------------------------

        #...and finally display it
        if __name__=="__main__":
            cv2.imshow("SimpleLive_Python_uEye_OpenCV", frame)
            cv2.imshow("SimpleLive_Python_uEye_OpenCV 2", frame2)

            # Press q if you want to end the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    #---------------------------------------------------------------------------------------------------------------------------------------

    # Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
    ueye.is_FreeImageMem(hCam1, pcImageMemory, MemID)
    ueye.is_FreeImageMem(hCam2, pcImageMemory2, MemID2)


    # Disables the hCam camera handle and releases the data structures and memory areas taken up by the uEye camera
    ueye.is_ExitCamera(hCam1)
    ueye.is_ExitCamera(hCam2)

    # Destroys the OpenCv windows
    cv2.destroyAllWindows()

    print()
    print("END")

if __name__=="__main__":
    t1= threading.Thread(target=Cameras_stream)        
    t1.start()
    