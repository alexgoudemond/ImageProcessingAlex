"""
Author: Alexander Goudemond

Program name: functions_all.py

# Notice:
            There is a lot of code in 1 place, so I have tried to structure it together. Functions are grouped where possible
            Right Now we have the following sections:
            - Function Sections:
                - Open / Display
                - Convert
                - Changing Names
                - Intensity values
                - Enhancement
                - Other

Please ensure the file openAnyImage.py is in the same location as this program
"""

#----------------------------------------------------------------------------------------------------------------Packages Below
# tkinter is GUI, numpy is for RAW images, cv2 for other videos, 
# os for deleting files
import tkinter as tk
from tkinter import filedialog, Toplevel
from tkinter import Radiobutton, Label, IntVar, Button, W
import cv2
import numpy as np
import os # Path reading, File Writing and Deleting
from matplotlib import pyplot  as plt
from math import floor
from skimage.segmentation import felzenszwalb # type of segmentation method
from skimage.util import random_noise # several noise options
from skimage import img_as_bool, morphology # Skeleton Code
from skimage.feature import graycomatrix, graycoprops # Co-Occurence Matrix and Haralick Features
from PIL import Image
from mahotas import haar # used for haar transform
from scipy import fft # used for dct transform
from numpy import r_ # used in DCT compression
from scipy.fftpack import dct, idct

# Global Vars below
global window 
global updateFrame
global labelUpdates

window = tk.Tk()
window.title("COMP702 Image Processing")
window.geometry("950x870+0+0")

updateFrame = tk.Frame()

labelUpdates = tk.Label(
    master = updateFrame, 
    text = "Updates will be placed in this box, when necessary",
    font = ("Helvetica", 12),
    compound = 'top',
    width = 78,
    bg = "gray"
)
#----------------------------------------------------------------------------------------------------------------Functions Below
#------------------------------------------------------------------------------------Open / Display Functions-------------------
def openTheImage():
    window.filename = openGUI("Select an Image to Open")

    if window.filename.endswith(".gif"):
        success = displayGIF(window.filename)
    elif window.filename.endswith(".raw"):
        image, success = convertRAW(window.filename)
        cv2.imshow(window.filename, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows() #Upon Keypress, close window
    elif ("binary" in window.filename):
        success = displayBinary(window.filename)
    else:
        success = displayImage(window.filename)

    if (success):
        tellUser("Image opened successfully", labelUpdates)
    else:
        tellUser("Something went wrong... Unable to open", labelUpdates)
###

def displayGIF(imgName):
    vid_capture = cv2.VideoCapture(imgName)

    if (vid_capture.isOpened() == False):
        print("Error opening the video file")
        return False
    else:
        fps = vid_capture.get(5)
        # print('Frames per second : ', fps, 'FPS')

        frameCount = vid_capture.get(7)
        # print('Frame count : ', frame_count)

    while(vid_capture.isOpened()):
        readyToRead, frame = vid_capture.read()

        if readyToRead:
            cv2.imshow(imgName, frame)

            # non aminated gifs need 1 frame displayed
            if (frameCount == 1.0):
                cv2.waitKey(0)
            else:
                cv2.waitKey(500)
        else:
            break

    # Release the video capture object
    vid_capture.release()
    cv2.destroyAllWindows()

    return True
###

def displayBinary(imgName):
    try:
        image = cv2.imread(imgName, 0)

        # Weird Bug! OpenCV somehow adds 2 to binary images when reading...
        # Loop below removes such cases manually
        (x, y) = image.shape
        for a in range(x):
            for b in range(y):
                if (image[a][b] > 1):
                    image[a][b] = 1

        # Show in Matplotlib as opencv treats as grayscale (all black to human eye)
        fig = plt.figure(imgName)
        plt.imshow(image, cmap="gray")
        plt.axis('off')
        plt.show()

        return True
    except Exception as uhoh:
        print("New Error:", uhoh)
        return False

def displayImage(imgName):
    try:
        image = cv2.imread(imgName)
        cv2.imshow(imgName, image)
        cv2.waitKey(0)

        cv2.destroyAllWindows()

        return True
    except Exception as uhoh:
        print("New Error:", uhoh)
        return False
###

#------------------------------------------------------------------------------------Convert Functions Below--------------------
def getGray():
    if window.filename.endswith(".gif"):
        imageArray, success = convertGrayscaleGIF(window.filename) # working!
        imgGrayscale = imageArray[0] # !Only processes first frame
        
    elif window.filename.endswith(".raw"):
        imgGrayscale, success = convertRAW(window.filename) 
        
    else:
        imgGrayscale, success = convertOtherImages(window.filename)

    # handles bug for all other functions that invoke getGray()
    if ("binary" in window.filename):
        # Weird Bug! OpenCV somehow adds 2 to binary images when reading...
        # Loop below removes such cases manually
        (x, y) = imgGrayscale.shape
        for a in range(x):
            for b in range(y):
                if (imgGrayscale[a][b] > 1):
                    imgGrayscale[a][b] = 1

    return imgGrayscale, success
###

def imgToGrayscale():
    window.filename = openGUI("Select an Image to Convert")

    try:
        currentDir = os.getcwd()
        os.mkdir(currentDir + "\Images\Converted_Grayscale")
    except FileExistsError as uhoh:
        pass
    except Exception as uhoh:
        print("New Error:", uhoh)
        pass

    appendedString = "_converted_to_grayscale"
    imgGrayscale, success = getGray()

    if window.filename.endswith(".gif"):
        appendedString += "_frame_0"
        
    
    if (success):
        newName = updateFileName(window.filename, appendedString, "\Images\Converted_Grayscale\\")
        cv2.imwrite(newName, imgGrayscale)
        tellUser("Image converted successfully", labelUpdates)
    else:
        tellUser("Something went wrong... Unable to open")
###

def getBinary():
    window.filename = openGUI("Select an Image to Convert")

    imgGrayscale, success = getGray()

    if (success):
        (x, y) = imgGrayscale.shape
        # print(x, y)
        imgArray = np.array(imgGrayscale)
        binaryArray = np.array( [[0 for i in range(y)] for j in range(x)] )
        # print(imgArray) # Works!

        minNum = np.min(imgArray)
        maxNum = np.max(imgArray)
        midpoint = floor( (maxNum - minNum) / 2)
        # print(midpoint)

        # create binaryArray
        for i in range(x):
            for j in range(y):
                if (imgArray[i][j] >= midpoint):
                    binaryArray[i][j] = 1
    
        return binaryArray, success
    else:
        return [], success
###

# We are going to need scan the image. Numbers above midpoint are 1, numbers below are 0
def imgToBinary():
    # window.filename = openGUI("Select an Image to Convert")

    binaryArray, success = getBinary()


    if (success):
        try:
            currentDir = os.getcwd()
            os.mkdir(currentDir + "\Images\Converted_Binary")
        except FileExistsError as uhoh:
            pass
        except Exception as uhoh:
            print("New Error:", uhoh)
            pass

        appendedString = "_converted_to_binary"

        if window.filename.endswith(".gif"):
            appendedString += "_frame_0"
            
        # binaryImage = cv2.imread(binaryArray, 0)

        newName = updateFileName(window.filename, appendedString, "\Images\Converted_Binary\\")
        cv2.imwrite(newName, binaryArray)
        tellUser("Image converted successfully", labelUpdates)

    else:
        tellUser("Something went wrong... Unable to get grayscale")
###

# responsible for converting any image, then saving as grayscale jpg in dedicated folder
def convertTheImage():
    # open new window - choose Grayscale or Binary
    convertWindow = Toplevel(window)
    convertWindow.title("Convert to...")
    convertWindow.geometry("300x300")

    enhanceOption = IntVar()
    enhanceOption.set(0)

    Radiobutton(convertWindow, text="Grayscale Conversion", variable=enhanceOption, value=1).pack(anchor=W)
    Radiobutton(convertWindow, text="Binary Conversion", variable=enhanceOption, value=2).pack(anchor=W)

    Button(convertWindow, text="convert", width=35, bg='silver',
            command=lambda: executeConversion(intVal=enhanceOption.get() ) 
        ).pack()
###

def executeConversion(intVal):
    # grayscale
    if (intVal == 1):
        imgToGrayscale()
    else:
        imgToBinary()
###

def convertOtherImages(imgName):
    try:
        # 0 for greyscale
        return cv2.imread(imgName, 0), True 
    except Exception as uhoh:
        print("New Error:", uhoh)
        return False
###

def convertRAW(imgName):
    try:
        # open file in text format, 'rb' == binary format for reading
        fd = open(imgName, 'rb') # BufferedReader Stream

        # uint8 --> 8 bit image
        # originalFile = np.fromfile(imgName, dtype=np.uint8)
        # print("Shape:", originalFile.shape) # shows us shape

        # TODO how flexibly discover this? For now, only worry about lena_gray.raw...
        rows = 512
        cols = 512

        # construct array from data in binary file
        f = np.fromfile(fd, dtype = np.uint8, count = rows * cols)
        image = f.reshape((rows, cols)) # (rows, cols) == 1st parameter

        # print(image) #Array containing values

        fd.close()
        return image, True

    except Exception as uhoh:
        print("New Error:", uhoh)
        return False
###

#Very similar to displayGif(), but saves frames of animation as jpgs
# Returns an array of each frame as an image
def convertGrayscaleGIF(imgName):
    vid_capture = cv2.VideoCapture(imgName)

    if (vid_capture.isOpened() == False):
        print("Error opening the video file")
        return False
    else:
        # success is used in our while loop - checks animation is open
        success, frame = vid_capture.read() 
    
    # print("Success?:", success)

    count = 0
    imageArray = []
    while(success):
        cv2.imwrite("./Images/name%d.jpg" % count, frame)

        print("Read Frame %d from GIF?:" % count, success)

        # if we get to this point, we have a jpg! now convert it
        if (success):
            imageGrayscale = cv2.imread("./Images/name%d.jpg" % count, 0)
            imageArray.append(imageGrayscale) 

        # code below tries remove file
        try:
            os.remove("./Images/name%d.jpg" % count)
        except:
            pass

        success, frame = vid_capture.read() 
        count += 1

    # Release the video capture object
    vid_capture.release()
    cv2.destroyAllWindows()
    
    return imageArray, True
###

#------------------------------------------------------------------------------------Changing names Below-----------------------
# used to place converted files into dedicated folder
def updateFileName(imgName, appendedString, directory):
    currentDir = os.getcwd()

    finalForwardSlashPos = imgName.rfind("/")
    position = imgName.index(".")
    extension = imgName[position + 1 : ]
    fileName = imgName[finalForwardSlashPos + 1 : position]

    # print(imgName,":::", finalForwardSlashPos, "fileName:", fileName)

    answer = currentDir + directory + fileName + "_from_" + extension  + appendedString + ".jpg"
    
    # print(answer)

    return(answer)
###

def getName(imgName):
    finalForwardSlashPos = imgName.rfind("/")
    position = imgName.index(".")
    return imgName[finalForwardSlashPos + 1 : position]
###

def getExtension(imgName):
    position = imgName.index(".")
    return imgName[position + 1 : ]
###


#------------------------------------------------------------------------------------Intensity Value Functions Below------------


# First - convert to B&W, then get Intensity Values
# ! Note - Only considers first frame in GIF Array. Can extend Later
def getBWIntensityValues():
    window.filename = openGUI("Select an Image to get B\W Intensity Values")

    imgGrayscale, success = getGray()
    (x, y) = imgGrayscale.shape
    
    if (success):
        tellUser("Intensity Values Found successfully", labelUpdates)

        imageDescription = getPartOfMatrix(imgGrayscale, x, y, getName(window.filename) + "_" + getExtension(window.filename))

        # new window - TopLevel allows a second window to popup
        windowIntensityValues = Toplevel(window)
        windowIntensityValues.title("Intensity Values for Black and White Image")

        labelIntensityValues = tk.Label(
            master = windowIntensityValues, 
            text = imageDescription,
            font = ("Helvetica", 14),
            compound = 'top',
            width = 70
        )

        labelIntensityValues.pack()
        windowIntensityValues.mainloop()
        # kills once window is closed, to avoid multiple "exit" presses on Exit button
        windowIntensityValues.quit() 
    else:
        tellUser("Something went wrong... Unable to open")
###

# Prints only part of a Matrix
def getPartOfMatrix(image, x, y, name):
    text = "Black and White Image Array for: " + name
    text += "; Size: (" + str(x) + ", " + str(y) + ")\n"
    text += "[ ["

    # Hard coded rows and columns to convey some info
    for a in range(0, x):
        for b in range(0, y):
            if (a == 3):
                text += "...\n   "
                break
            elif (a > 3):
                break
            else:
                text += str(image[a, b]) + " "

            if(b == 3):
                text += " ... "
                text += str(image[b, y-1]) + " ]"
                text += "\n   "
                break

        if(a == 4):
                text += str(image[x-1, 0]) + " "
                text += str(image[x-1, 1]) + " "
                text += str(image[x-1, 2]) + " "
                text += str(image[x-1, 3]) + " "
                text += " ...  "
                text += str(image[x-1, y-1]) + " ] ]"
                break

    return text
###

def downloadBWIntensityValues():
    window.filename = openGUI("Select an Image to Download Intensity Values")

    imgGrayscale, success = getGray()
    (x, y) = imgGrayscale.shape
    
    # print("success:", success, ", Got Here", x, " ", y)
    if (success):
        currentDir = os.getcwd()
        path = currentDir + "\Images\Reports"
        try:
            os.mkdir(path)
        except:
            pass

        imgName = window.filename
        fileName = "Report_" + getName(imgName)
        fileName += "_" + getExtension(imgName) + ".txt"

        completeName = os.path.join(path, fileName)
        imageDescription = getAllOfMatrix(imgGrayscale, x, y, getName(window.filename) + "_" + getExtension(window.filename))
        text_file = open(completeName, "w")
        text_file.write(completeName+"\n\n")
        text_file.write(imageDescription)

        if(os.path.exists(completeName)):
            tellUser("Intensity Values Downloaded successfully", labelUpdates) # Update
        else:
            tellUser("Unable to create file")

    else:
        tellUser("Something went wrong... Unable to open")
###

# Prints only part of a Matrix
def getAllOfMatrix(image, x, y, name):
    text = "Black and White Image Array for: " + name
    text += "; Size: (" + str(x) + ", " + str(y) + ")\n"
    text += "[ [\n"

    for a in range(0, x):
        for b in range(0, y):
            text += str(image[a, b]) + " "
        text += " <end>\n"
    text += " ] ]"

    return text
###

#------------------------------------------------------------------------------------Enhancement Functions Below----------------

def chooseEnhancement():
    window.filename = openGUI("Select an Image to Enhance")
    imgGrayscale, success = getGray()

    if (success):
        # Open new window to choose enhancement
        choicesWindow = Toplevel(window)
        choicesWindow.title("Image Enhancements Below")
        choicesWindow.geometry("300x300")

        enhanceOption = IntVar()
        enhanceOption.set(0)
        
        Radiobutton(choicesWindow, text="Histogram Equalisation", variable=enhanceOption, value=1).pack(anchor=W)
        Radiobutton(choicesWindow, text="Point Processing: Negative Image", variable=enhanceOption, value=2).pack(anchor=W)
        Radiobutton(choicesWindow, text="Point Processing: Thresholding", variable=enhanceOption, value=3).pack(anchor=W)
        Radiobutton(choicesWindow, text="Logarithmic Transformations", variable=enhanceOption, value=4).pack(anchor=W)
        Radiobutton(choicesWindow, text="Power Law (Gamma) Transformations", variable=enhanceOption, value=5).pack(anchor=W)

        Button(
            choicesWindow, text="Enhance", width=35, bg='silver',
            command=lambda: executeEnhancement(
                                intVal=enhanceOption.get(), img=imgGrayscale, 
                                imgName=window.filename
                            ) 
        ).pack()
        # Button above sends the user elsewhere

        Button(choicesWindow, text="Close All Plots", bg="gray", command=lambda: (plt.close('all')) ).pack()
        
    else:
        tellUser("Unable to Get Grayscale Image for Enhancement Window...", labelUpdates)
###

def executeEnhancement(intVal, img, imgName):
    tellUser("Opening now...", labelUpdates)

    # Lets us stick 5 plots in 1 window
    fig = plt.figure(num="Enhancement", figsize=(15, 8))
    plt.clf() # Should clear last plot but keep window open? 

    fig.add_subplot(2, 3, 1)
    message = "B/W JPG Image of: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(img, cmap='gray')
    plt.title(message, wrap=True)
    plt.axis('off') #Removes axes
    
    fig.add_subplot(2, 3, 2)
    message = "Histogram of B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(img, message)

    if (intVal == 1):
        histEqualization(img, imgName, fig)
    elif (intVal == 2):
        negImage(img, imgName, fig)
    elif (intVal == 3):
        thresholding(img, imgName, fig)
    elif (intVal == 4):
        logTransform(img, imgName, fig)
    else:
        textBoxWindow = Toplevel(window)
        textBoxWindow.title("Image Enhancements Below")
        textBoxWindow.geometry("300x300")

        cLabel = Label(textBoxWindow, text="c = ...").pack() #used for reading instructions
        cValue = tk.Entry(textBoxWindow)
        cValue.insert(0, "1.0")
        cValue.pack() #must be seperate for some reason...
        gammaLabel = Label(textBoxWindow, text="gamma = ...").pack() #used for reading instructions
        gammaValue = tk.Entry(textBoxWindow)
        gammaValue.insert(0, "0.5")
        gammaValue.pack() #must be seperate for some reason...

        Button(textBoxWindow, text="Power Law (Gamma) Transformation", 
                bg="silver", command=lambda: gammaTransform(img, imgName,
                                                            float(cValue.get()), float(gammaValue.get()), fig)
                                            ).pack()
        Button(textBoxWindow, text="Close All Plots", bg="gray", command=lambda: (plt.close('all')) ).pack()

    # Because second panel needed for Gamma Transform, plt.show() appears in gammaTransformation()
    if (intVal != 5):
        plt.tight_layout() # Prevents title overlap in display
        plt.show()       
###

def TransformationFunction(message, input, output):
    plt.plot(input, output)
    plt.title(message, wrap=True)
    plt.xlabel('Input Intensity Values')
    plt.ylabel('Output Intensity Values')
###

def gammaTransform(img, imgName, cValue, gammaValue, fig):
    imageEnhanced = np.array(cValue*np.power(img,gammaValue))

    fig.add_subplot(2, 3, 4)
    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(imageEnhanced, message)

    fig.add_subplot(2, 3, 5)
    message = "Gamma Transformation of Image: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(imageEnhanced, cmap='gray') 
    plt.title(message, wrap=True)
    plt.axis('off') #Removes axes

    fig.add_subplot(2, 3, 3)
    message = "Transformation Function: "
    TransformationFunction(message, img, imageEnhanced)

    plt.tight_layout() # Prevents title overlap in display
    plt.show()
###

def logTransform(img, imgName, fig):
    cValue = 255 / np.log(1 + np.max(img))
    imageEnhanced = cValue * np.log(1 + img) 
    # imageEnhanced.reshape(512,512)

    fig.add_subplot(2, 3, 4)
    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(imageEnhanced, message)

    fig.add_subplot(2, 3, 5)
    message = "Logarithmic Transformation of Image: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(imageEnhanced, cmap='gray')
    plt.title(message, wrap=True)
    plt.axis('off') #Removes axes
    
    fig.add_subplot(2, 3, 3)
    message = "Transformation Function: "
    TransformationFunction(message, img, imageEnhanced)
###

def thresholding(img, imgName, fig):
    imageEnhanced = cv2.adaptiveThreshold(src=img, maxValue=255, adaptiveMethod=cv2.BORDER_REPLICATE, thresholdType=cv2.THRESH_BINARY,blockSize=3, C=10)
    
    fig.add_subplot(2, 3, 4)
    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(imageEnhanced, message)

    fig.add_subplot(2, 3, 5)
    message = "Thresholding of Image: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(imageEnhanced, cmap='gray')
    plt.title(message, wrap=True)
    plt.axis('off') #Removes axes
    
    fig.add_subplot(2, 3, 3)
    message = "Transformation Function: "
    TransformationFunction(message, img, imageEnhanced)
###

def negImage(img, imgName, fig):
    imageEnhanced = cv2.bitwise_not(img)
    
    fig.add_subplot(2, 3, 4)
    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(imageEnhanced, message)

    
    fig.add_subplot(2, 3, 5)
    message = "Negative Image of: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(imageEnhanced, cmap='gray')
    plt.title(message, wrap=True)
    plt.axis('off') #Removes axes
    
    fig.add_subplot(2, 3, 3)
    message = "Transformation Function: "
    TransformationFunction(message, img, imageEnhanced)
###

def histEqualization(img, imgName, fig):    
    imgEnhanced = cv2.equalizeHist(img)

    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    fig.add_subplot(2, 3, 4)
    displayHist(imgEnhanced, message)
    
    message = "Histogram Equalized Image of: " + getName(imgName) + "." + getExtension(imgName)
    fig.add_subplot(2, 3, 5)
    plt.imshow(imgEnhanced, cmap='gray')
    plt.title(message, wrap=True)
    plt.axis('off') #Removes axes

    message = "Transformation Function: "
    fig.add_subplot(2, 3, 3)
    TransformationFunction(message, img, imgEnhanced)
###

# bins are qty of histogram pieces, range is for width of graph
def displayHist(img, str):
    plt.title(str, wrap=True)
    plt.hist(img.ravel(), bins=256, range=[0,256])
    plt.xlabel('Gray Levels')
    plt.ylabel('Frequencies')
###

#------------------------------------------------------------------------------------Filtering Functions Below------------------

def chooseSharpeningOption():
    window.filename = openGUI("Select an Image to Sharpen")
    imgGrayscale, success = getGray()

    if (success):
        # Open new window to choose enhancement
        # sharpenWindow = Toplevel(window)
        # sharpenWindow.title("Image Sharpened Below")
        # sharpenWindow.geometry("300x300")

        figure = plt.figure(num="Sharpening", figsize=(10, 5))

        executeSharpening(imgGrayscale, imgName=window.filename, fig=figure) 
        
    else:
        tellUser("Unable to Get Grayscale Image for Sharpening Window...", labelUpdates)
###

def executeSharpening(imgGrayscale, imgName, fig):
    # This filter is enough!
    # kernel = np.array([ [0, -1, 0], 
    #                     [-1, 5, -1], 
    #                     [0, -1, 0] ])
    # blur = cv2.filter2D(imgGrayscale,-1,kernel)
    
    blur = cv2.medianBlur(imgGrayscale, 3)
    edgesOnly = imgGrayscale - blur
    sharpenedImage = imgGrayscale + edgesOnly

    fig.add_subplot(1, 3, 1)
    plt.imshow(imgGrayscale, cmap='gray')
    plt.title('B\W Image of: '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    plt.axis('off')

    fig.add_subplot(1, 3, 2)
    plt.imshow(edgesOnly, cmap='gray')
    plt.title('Edges of: '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    plt.axis('off')

    fig.add_subplot(1, 3, 3)
    plt.imshow(sharpenedImage, cmap='gray')
    plt.title('Sharpened Image of: '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    plt.axis('off')

    plt.tight_layout() # Prevents title overlap in display
    plt.show()
###

def chooseSmoothingOption():
    window.filename = openGUI("Select an Image to Smooth")
    imgGrayscale, success = getGray()

    if (success):
        # Open new window to choose enhancement
        smoothingWindow = Toplevel(window)
        smoothingWindow.title("Image Enhancements Below")
        smoothingWindow.geometry("300x300")

        enhanceOption = IntVar()
        enhanceOption.set(0)
        
        Radiobutton(smoothingWindow, text="Simple Smoothing", variable=enhanceOption, value=1).pack(anchor=W)
        Radiobutton(smoothingWindow, text="Moving Average Smoothing", variable=enhanceOption, value=2).pack(anchor=W)
        Radiobutton(smoothingWindow, text="Gaussian Smoothing", variable=enhanceOption, value=3).pack(anchor=W)
        Radiobutton(smoothingWindow, text="Median Smoothing", variable=enhanceOption, value=4).pack(anchor=W)
        # Radiobutton(smoothingWindow, text="Power Law (Gamma) Transformations", variable=enhanceOption, value=5).pack(anchor=W)

        arrayLabel = Label(smoothingWindow, text="Array Square Size = ...").pack() #used for reading instructions
        arrayValue = tk.Entry(smoothingWindow)
        arrayValue.insert(0, "3")
        arrayValue.pack() #must be seperate for some reason...

        Button(
            smoothingWindow, text="Smooth", width=35, bg='silver',
            command=lambda: executeSmoothing(
                                intVal=enhanceOption.get(), 
                                arraySize=int(arrayValue.get()),
                                img=imgGrayscale, 
                                imgName=window.filename
                            ) 
        ).pack()
        # Button above sends the user elsewhere

        Button(smoothingWindow, text="Close All Plots", bg="gray", command=lambda: (plt.close('all')) ).pack()
        
    else:
        tellUser("Unable to Get Grayscale Image for Smoothing Window...", labelUpdates)
###

def executeSmoothing(intVal, arraySize, img, imgName):
    tellUser("Opening now...", labelUpdates)

    fig = plt.figure(num="Smoothing", figsize=(8, 5))
    plt.clf() # Should clear last plot but keep window open? 

    fig.add_subplot(1, 2, 1)
    message = "B\W JPG Image of: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(img, cmap='gray')
    plt.title(message, wrap=True)
    plt.axis('off') #Removes axes

    fig.add_subplot(1, 2, 2)
    if (intVal == 1):
        # histEqualization(img, imgName, fig)
        simpleSmooth(img, imgName, arraySize)
    elif (intVal == 2):
        movingAverageSmooth(img, imgName, arraySize)
    elif (intVal == 3):
        gaussianSmooth(img, imgName, arraySize)
    else:
        medianSmooth(img, imgName, arraySize)

    plt.tight_layout() # Prevents title overlap in display
    plt.show()   
###

def medianSmooth(img, imgName, arraySize):
    median = cv2.medianBlur(img,arraySize)
    plt.imshow(median, cmap='gray')
    plt.title('Median Smooth of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    plt.axis('off') #Removes axes
###

def gaussianSmooth(img, imgName, arraySize):
    blur = cv2.GaussianBlur(img,(arraySize,arraySize),0)
    plt.imshow(blur, cmap='gray')
    plt.title('Gaussian Smooth of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    plt.axis('off') #Removes axes
###

def movingAverageSmooth(img, imgName, arraySize):
    kernel = np.ones((arraySize,arraySize), np.float32)/(arraySize * arraySize) # fills with all 1s
    dst = cv2.filter2D(img,-1,kernel)
    
    plt.subplot(122)
    plt.imshow(dst, cmap='gray')
    plt.title('Moving Average Smooth of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    plt.axis('off') #Removes axes
###

def simpleSmooth(img, imgName, arraySize):
    kernel = np.full((arraySize,arraySize), 1/(arraySize * arraySize)) # fills with numbers in array
    dst = cv2.filter2D(img,-1,kernel)
    
    plt.subplot(122)
    plt.imshow(dst, cmap='gray')
    plt.title('Simple Smooth of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    plt.axis('off') #Removes axes
###

#------------------------------------------------------------------------------------Morphological Functions Below--------------

def chooseMorphologyOption():
    imgBinary, success = getBinary()

    if (success):
        # Open new window to choose enhancement
        morphWindow = Toplevel(window)
        morphWindow.title("Choose an option...")
        morphWindow.geometry("300x300")

        enhanceOption = IntVar()
        enhanceOption.set(0)
        
        Radiobutton(morphWindow, text="Dilation", variable=enhanceOption, value=1).pack(anchor=W)
        Radiobutton(morphWindow, text="Erosion", variable=enhanceOption, value=2).pack(anchor=W)
        Radiobutton(morphWindow, text="Opening", variable=enhanceOption, value=3).pack(anchor=W)
        Radiobutton(morphWindow, text="Closing", variable=enhanceOption, value=4).pack(anchor=W)
        Radiobutton(morphWindow, text="Boundary Extraction", variable=enhanceOption, value=5).pack(anchor=W)
        # Radiobutton(smoothingWindow, text="Power Law (Gamma) Transformations", variable=enhanceOption, value=5).pack(anchor=W)

        Button(morphWindow, text="morph", width=35, bg='gray',
            command=lambda: executeMorphOption(intVal=enhanceOption.get(), binaryArray=imgBinary, imgName=window.filename) 
        ).pack()
        
    else:
        tellUser("Unable to Get Grayscale Image for Morphological Window...", labelUpdates)
    return True
###

def executeMorphOption(intVal, binaryArray, imgName):
    fig = plt.figure(num="Morphological Changes", figsize=(8, 4))
    plt.clf() # Should clear last plot but keep window open? 

    fig.add_subplot(1, 2, 1)

    plt.imshow(binaryArray, cmap='gray')
    plt.title('Binary Image of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)

    fig.add_subplot(1, 2, 2)

    if (intVal == 1):
        dilatedArray = executeDilation(array=binaryArray)
        
        plt.imshow(dilatedArray, cmap='gray')
        plt.title('Dilated Binary Image of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    elif (intVal == 2):
        dilatedArray = executeErosion(array=binaryArray)
        
        plt.imshow(dilatedArray, cmap='gray')
        plt.title('Eroded Binary Image of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    elif (intVal == 3):
        dilatedArray = executeOpening(array=binaryArray)
        
        plt.imshow(dilatedArray, cmap='gray')
        plt.title('Opening Binary Image of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    elif (intVal == 4):
        dilatedArray = executeClosing(array=binaryArray)
        
        plt.imshow(dilatedArray, cmap='gray')
        plt.title('Closing Binary Image of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    else:
        dilatedArray = executeBoundaryExtraction(array=binaryArray)
        
        plt.imshow(dilatedArray, cmap='gray')
        plt.title('Boundary of Binary Image of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)

    plt.show()
###

# here, we get boundary of an image
def executeBoundaryExtraction(array):
    erodedArray = executeErosion(array)
    
    (x, y) = (array.shape)

    newArray = np.array( [[0 for i in range(y)] for j in range(x)] )
    
    for i in range(x):
        for j in range(y):
            temp = array[i][j] - erodedArray[i][j]

            if (temp >= 0):
                newArray[i][j] = temp

    return newArray
###

# here, we close an image
def executeClosing(array):
    dilatedArray = executeDilation(array)
    closedArray = executeErosion(dilatedArray)
    return closedArray
###

# here, we open an image
def executeOpening(array):
    erodedArray = executeErosion(array)
    openedArray = executeDilation(erodedArray)
    return openedArray
###

# here, we erode an image
def executeErosion(array):
    # pattern used in for loop, this is here for reference
    # structuringElement =   [ [0, 1, 0],
    #                          [1, 1, 1],
    #                          [0, 1, 0] ]

    paddedArray = np.pad(array, (1, 1), 'constant', constant_values=(0, 0))
    (x, y) = (paddedArray.shape)

    # This will be dilated - slice later
    newArray = np.array( [[0 for i in range(y)] for j in range(x)] )

    for i in range(1, x-1):
        for j in range(1, y-1):
            if (paddedArray[i-1][j] == 1) and (paddedArray[i][j-1] == 1) and (paddedArray[i][j+1] == 1) and (paddedArray[i+1][j] == 1):
                newArray[i][j] = 1

    return newArray[ 1 : x , 1 : y ] # slice and return
###

# here, we dilate an image
def executeDilation(array):
    # pattern used in for loop, this is here for reference
    # structuringElement =   [ [0, 1, 0],
    #                          [1, 1, 1],
    #                          [0, 1, 0] ]

    paddedArray = np.pad(array, (1, 1), 'constant', constant_values=(0, 0))
    (x, y) = (paddedArray.shape)

    # This will be dilated - slice later
    newArray = np.array( [[0 for i in range(y)] for j in range(x)] )

    for i in range(1, x-1):
        for j in range(1, y-1):
            if (paddedArray[i-1][j] == 1) or (paddedArray[i][j-1] == 1) or (paddedArray[i][j+1] == 1) or (paddedArray[i+1][j] == 1):
                newArray[i][j] = 1

    return newArray[ 1 : x , 1 : y ] # slice and return
###

#------------------------------------------------------------------------------------Mask Functions Below-----------------------

def chooseMaskOption():
    window.filename = openGUI("Select an Image...")

    imgGrayscale, success = getGray()

    if (success):
        # Open new window to choose enhancement
        maskWindow = Toplevel(window)
        maskWindow.title("Choose a mask...")
        maskWindow.geometry("300x400")

        maskOption1 = IntVar()
        maskOption1.set(0)

        R1 = Radiobutton(maskWindow, text="Laplacian 3x3", variable=maskOption1, value=1)
        R1.pack(anchor=W, side="top")
        R2 = Radiobutton(maskWindow, text="\'Standard\' Horizontal", variable=maskOption1, value=2)
        R2.pack(anchor=W, side="top")
        R3 = Radiobutton(maskWindow, text="\'Standard\' Vertical", variable=maskOption1, value=3)
        R3.pack(anchor=W, side="top")
        R4 = Radiobutton(maskWindow, text="\'Standard\' +45 degrees", variable=maskOption1, value=4)
        R4.pack(anchor=W, side="top")
        R5 = Radiobutton(maskWindow, text="\'Standard\' -45 degrees", variable=maskOption1, value=5)
        R5.pack(anchor=W, side="top")
        R6 = Radiobutton(maskWindow, text="\'Prewitt\' Horizontal", variable=maskOption1, value=6)
        R6.pack(anchor=W, side="top")
        R7 = Radiobutton(maskWindow, text="\'Prewitt\' Vertical", variable=maskOption1, value=7)
        R7.pack(anchor=W, side="top")
        R8 = Radiobutton(maskWindow, text="\'Prewitt\' +45 degrees", variable=maskOption1, value=8)
        R8.pack(anchor=W, side="top")
        R9 = Radiobutton(maskWindow, text="\'Prewitt\' -45 degrees", variable=maskOption1, value=9)
        R9.pack(anchor=W, side="top")
        R10 = Radiobutton(maskWindow, text="\'Sobel\' Horizontal", variable=maskOption1, value=10)
        R10.pack(anchor=W, side="top")
        R11 = Radiobutton(maskWindow, text="\'Sobel\' Vertical", variable=maskOption1, value=11)
        R11.pack(anchor=W, side="top")
        R12 = Radiobutton(maskWindow, text="\'Sobel\' +45 degrees", variable=maskOption1, value=12)
        R12.pack(anchor=W, side="top")
        R13 = Radiobutton(maskWindow, text="\'Sobel\' -45 degrees", variable=maskOption1, value=13)
        R13.pack(anchor=W, side="top")

        Button(maskWindow, text="Apply Mask", width=35, bg='gray',
            command=lambda: executeMaskOption(intVal=maskOption1.get(), img=imgGrayscale, imgName=window.filename) 
        ).pack()
        Button(maskWindow, text="Close Plots", width=35, bg='gray',
            command=lambda: (plt.close("Mask Changes"))
        ).pack()

    else:
        tellUser("Unable to Get Grayscale Image for Sharpening Window...", labelUpdates)
    
    return True
###

def executeMaskOption(intVal, img, imgName):

    fig = plt.figure(num="Mask Changes", figsize=(8, 4))
    plt.clf() # Should clear last plot but keep window open? 

    fig.add_subplot(1, 3, 1)

    plt.imshow(img, cmap='gray')
    plt.title('Original Image of '+ getName(imgName) + "." + getExtension(imgName), wrap=True)

    # 7 options
    if (intVal == 1):
        # Laplacian Mask
        newImg, mask = applyLaplacianMask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 2):
        # Horizontal Mask
        newImg, mask = applyStandardHorizontalMask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 3):
        # Vertical Mask
        newImg, mask = applyStandardVerticalMask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 4):
        # +45 degree Mask
        newImg, mask = applyStandardPositive45Mask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 5):
        # -45 degree Mask
        newImg, mask = applyStandardNegative45Mask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 6):
        # Horizontal Mask
        newImg, mask = applyPrewittHorizontalMask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 7):
        # Vertical Mask
        newImg, mask = applyPrewittVerticalMask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 8):
        # +45 degree Mask
        newImg, mask = applyPrewittPositive45Mask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 9):
        # -45 degree Mask
        newImg, mask = applyPrewittNegative45Mask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 10):
        # Horizontal Mask
        newImg, mask = applySobelHorizontalMask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 11):
        # Vertical Mask
        newImg, mask = applySobelVerticalMask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 12):
        # +45 degree Mask
        newImg, mask = applySobelPositive45Mask(img)
        plotMask(fig, newImg, mask, imgName)
    elif (intVal == 13):
        # -45 degree Mask
        newImg, mask = applySobelNegative45Mask(img)
        plotMask(fig, newImg, mask, imgName)
    else:
        tellUser("Select an option...", labelUpdates)
 

    plt.tight_layout() # Prevents title overlap in display
    plt.show()  

    return True
###

def plotMask(fig, newImg, mask, imgName):
    fig.add_subplot(1, 3, 2)
    plt.imshow(newImg, cmap='gray')
    plt.title('Laplacian Mask over '+ getName(imgName) + "." + getExtension(imgName), wrap=True)
    plt.axis('off') #Removes axes

    fig.add_subplot(1, 3, 3)
    plt.text(0.3, 0.7, "Mask")
    plt.table(cellText=mask, loc='center')
    plt.axis('off') #Removes axes
###

def applySobelNegative45Mask(img):
    mask = np.array(    [[ 2, -1,  0],
                         [-1,  0,  1],
                         [ 0,  1,  2]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applySobelPositive45Mask(img):
    mask = np.array(    [[ 0,  1,  2],
                         [-1,  0,  1],
                         [-2, -1,  0]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applySobelVerticalMask(img):
    mask = np.array(    [[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applySobelHorizontalMask(img):
    mask = np.array(    [[-1, -2, -1],
                         [ 0,  0,  0],
                         [ 1,  2,  1]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applyPrewittNegative45Mask(img):
    mask = np.array(    [[-1, -1,  0],
                         [-1,  0,  1],
                         [ 0,  1,  1]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applyPrewittPositive45Mask(img):
    mask = np.array(    [[ 0,  1,  1],
                         [-1,  0,  1],
                         [-1, -1,  0]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applyPrewittVerticalMask(img):
    mask = np.array(    [[-1, 0, 1],
                         [-1, 0, 1],
                         [-1, 0, 1]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applyPrewittHorizontalMask(img):
    mask = np.array(    [[-1, -1, -1],
                         [ 0,  0,  0],
                         [ 1,  1,  1]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applyStandardNegative45Mask(img):
    mask = np.array(    [[-1, -1,  2],
                         [-1,  2, -1],
                         [ 2, -1, -1]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applyStandardPositive45Mask(img):
    mask = np.array(    [[ 2, -1, -1],
                         [-1,  2, -1],
                         [-1, -1,  2]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applyStandardVerticalMask(img):
    mask = np.array(    [[-1, 2, -1],
                         [-1, 2, -1],
                         [-1, 2, -1]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applyStandardHorizontalMask(img):
    mask = np.array(    [[-1, -1, -1],
                         [ 2,  2,  2],
                         [-1, -1, -1]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask 
###

def applyLaplacianMask(img):
    mask = np.array(    [[1,  1, 1],
                         [1, -8, 1],
                         [1,  1, 1]] 
            )

    newImg = cv2.filter2D(img, -1, mask)

    return newImg, mask
###
    
#------------------------------------------------------------------------------------Segmentation Functions Below---------------

def chooseSegmentOption():
    # print("Inside segmentation option")
    window.filename = openGUI("Select an Image...")

    imgGrayscale, success = getGray()

    if (success):

        # Open a window and show all the options to choose from

        # segmentWindow = tk.Tk(baseName = "segment_Window")
        segmentWindow = Toplevel(window)
        segmentWindow.title("Choose a kind of segmentation...")
        segmentWindow.geometry("500x200")

        segmentOption = IntVar()
        segmentOption.set(1)

        # left side buttons
        R1 = Radiobutton(segmentWindow, text="Edge Detection", variable=segmentOption, value=1, width=30)
        R3 = Radiobutton(segmentWindow, text="Watershed Method", variable=segmentOption, value=3, width=30)

        # right side buttons
        R4 = Radiobutton(segmentWindow, text="Thresholding", variable=segmentOption, value=4, width=30)
        R5 = Radiobutton(segmentWindow, text="Region Splitting and Merging", variable=segmentOption, value=5, width=30)
        R6 = Radiobutton(segmentWindow, text="Clustering", variable=segmentOption, value=6, width=30)

        # top labels
        L1 = Label(segmentWindow, text="Discontinuity Options", width=30)
        L2 = Label(segmentWindow, text="Continuity Options", width=30)

        B1 = Button(segmentWindow, text="Choose Segmentation Option", width=50, bg='gray',
            command=lambda: executeSegmentOption(intVal=segmentOption.get(), img=imgGrayscale, imgName=window.filename)
        )
        B2 = Button(segmentWindow, text="Close Plots", width=50, bg='gray',
            command=lambda: ( plt.close("Watershed Changes") )
        )

        # grid layout
        L1.grid(row=0, column=0)
        L2.grid(row=0, column=2)
        R1.grid(row=1, column=0)
        R3.grid(row=2, column=0)
        R4.grid(row=1, column=2)
        R5.grid(row=2, column=2)
        R6.grid(row=3, column=2)
        B1.grid(columnspan=3)
        B2.grid(columnspan=3)

    else:
        tellUser("Unable to Get Grayscale Image for Segmentation Window...", labelUpdates)
    
    return True
###

def executeSegmentOption(intVal, img, imgName):
    # give the user more options based on their choice:
    if (intVal == 1):
        # Edge Detection
        chooseEdgeDetectionMethod(intVal, img, imgName)

    elif (intVal == 3):
        # Watershed Method
        chooseWatershedMethod(intVal, img, imgName)

    elif (intVal == 4):
        # Thresholding
        chooseThresholdingMethod(intVal, img, imgName)

    elif (intVal == 5):
        # Region Splitting and Merging
        chooseRegionBasedMethod(intVal, img, imgName)

    elif (intVal == 6):
        # Clustering
        chooseClusteringMethod(intVal, img, imgName)

    else:
        # should never execute
        tellUser("Select an option...", labelUpdates)

    # print("Inside executeSegmentOption()")  
###

def chooseEdgeDetectionMethod(intVal, img, imgName):
    # print("inside ChooseEdgeDetectionMethod")

    '''
    Canny Edge Detection
    Simple Contour
    Complete Contour Detection
    Felzenszwalb's Segmentation
    '''
    
    edgeDetectionWindow = Toplevel(window)
    edgeDetectionWindow.title("Choose a kind of edgeDetection...")
    edgeDetectionWindow.geometry("300x300")

    threshOption = IntVar()
    threshOption.set(0)

    Radiobutton(edgeDetectionWindow, text="Canny Edge Detection", variable=threshOption, value=1, width=30).pack(anchor=W, side="top")
    Radiobutton(edgeDetectionWindow, text="Simple Contour Detection", variable=threshOption, value=2, width=30).pack(anchor=W, side="top")
    Radiobutton(edgeDetectionWindow, text="Complete Contour Detection", variable=threshOption, value=3, width=30).pack(anchor=W, side="top")
    Radiobutton(edgeDetectionWindow, text="Felzenswalbs Contour Detection", variable=threshOption, value=4, width=30).pack(anchor=W, side="top")

    Button(edgeDetectionWindow, text="Choose Segmentation Option", width=50, bg='gray',
        command=lambda: executeEdgeDetectionChoice(intVal=threshOption.get(), img=img, imgName=imgName)
    ).pack(anchor=W, side="top")
    Button(edgeDetectionWindow, text="Close Plots", width=50, bg='gray',
        command=lambda: ( plt.close("Edge Detection Changes") )
    ).pack(anchor=W, side="top")
###

def chooseWatershedMethod(intVal, img, imgName):
    # print("inside ChooseWatershedMethod")

    fig = plt.figure(num="Watershed Changes", figsize=(10, 6))
    plt.clf() # Should clear last plot but keep window open? 
    numRows = 3
    numColumns = 3

    # threshold
    ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # noise removal
    kernel = np.ones((3,3),np.uint8)
    # print(kernel)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 2)

    # sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

    # Finding unknown region
    unsure_pic = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, unsure_pic)

    # Marker labelling
    ret, markers = cv2.connectedComponents(unsure_pic)

    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1

    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0

    # NOW - Watershed method
    watershedImage = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    finalMarkers = cv2.watershed(watershedImage, markers) #! needs colour image

    watershedImage[finalMarkers == -1] = [255, 0, 0]
    watershedImage = cv2.cvtColor(watershedImage, cv2.COLOR_BGR2GRAY) #! convert back to grayscale

    modifiedImageArray = [img, thresh, opening, sure_bg, sure_fg, unknown, markers, watershedImage]
    labelArray = ["Original Image", "Thresholded Image", "Morphological Opened Image", "Known Background (black)", "Known Foreground (white)", 
                    "Unknown Aspects", "Unknown Aspects after Connecting Components (gray)", "Watershed Image"]

    plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)
###

def chooseClusteringMethod(intVal, img, imgName):
    print("inside ChooseClusteringMethod")

    '''
    K-means

    more can be implemented if we discover them
    '''
    clusteringWindow = Toplevel(window)
    clusteringWindow.title("Choose a kind of clustering...")
    clusteringWindow.geometry("300x300")

    threshOption = IntVar()
    threshOption.set(0)

    Radiobutton(clusteringWindow, text="Iterative K-Means clustering", variable=threshOption, value=1, width=30).pack(anchor=W, side="top")
    # Radiobutton(clusteringWindow, text="Fuzzy-C clustering", variable=threshOption, value=2, width=30).pack(anchor=W, side="top")
    # Radiobutton(clusteringWindow, text="Linear Iterative clustering", variable=threshOption, value=3, width=30).pack(anchor=W, side="top")

    Button(clusteringWindow, text="Choose Segmentation Option", width=50, bg='gray',
        command=lambda: executeClusteringChoice(intVal=threshOption.get(), img=img, imgName=imgName)
    ).pack(anchor=W, side="top")
    Button(clusteringWindow, text="Close Plots", width=50, bg='gray',
        command=lambda: ( plt.close("Clustering Changes") )
    ).pack(anchor=W, side="top")

###

def chooseRegionBasedMethod(intVal, img, imgName):
    print("inside ChooseRegionBasedMethod")
    '''
    Region Based
    Region growing - implement later, big algorithm
    Region splitting and merging - implement later, big algorithm
    '''

    regionWindow = Toplevel(window)
    regionWindow.title("Choose a kind of region...")
    regionWindow.geometry("300x300")

    option = IntVar()
    option.set(0)

    Radiobutton(regionWindow, text="Region Filling", variable=option, value=1, width=30).pack(anchor=W, side="top")
    # Radiobutton(regionWindow, text="Region Growing", variable=option, value=2, width=30).pack(anchor=W, side="top")
    # Radiobutton(regionWindow, text="Region Splitting and Merging", variable=option, value=3, width=30).pack(anchor=W, side="top")

    Button(regionWindow, text="Choose Segmentation Option", width=50, bg='gray',
        command=lambda: executeRegionChoice(intVal=option.get(), img=img, imgName=imgName)
    ).pack(anchor=W, side="top")
    Button(regionWindow, text="Close Plots", width=50, bg='gray',
        command=lambda: ( plt.close("Region Based Changes") )
    ).pack(anchor=W, side="top")
###

def chooseThresholdingMethod(intVal, img, imgName):
    print("inside ChooseThresholdingMethod")
    '''
    Simple
    Manual / Iterative Thresholding
    Adaptive
    Otsus method
    '''

    thresholdingWindow = Toplevel(window)
    thresholdingWindow.title("Choose a kind of Thresholding...")
    thresholdingWindow.geometry("300x300")

    threshOption = IntVar()
    threshOption.set(0)

    Radiobutton(thresholdingWindow, text="Simple Thresholding", variable=threshOption, value=1, width=30).pack(anchor=W, side="top")
    Radiobutton(thresholdingWindow, text="Iterative Thresholding", variable=threshOption, value=2, width=30).pack(anchor=W, side="top")
    Radiobutton(thresholdingWindow, text="Adaptive Thresholding", variable=threshOption, value=3, width=30).pack(anchor=W, side="top")
    Radiobutton(thresholdingWindow, text="Otsu's Method", variable=threshOption, value=4, width=30).pack(anchor=W, side="top")

    Button(thresholdingWindow, text="Choose Segmentation Option", width=50, bg='gray',
        command=lambda: executeThresholdingChoice(intVal=threshOption.get(), img=img, imgName=imgName)
    ).pack(anchor=W, side="top")
    Button(thresholdingWindow, text="Close Plots", width=50, bg='gray',
        command=lambda: ( plt.close("Segmentation Changes") )
    ).pack(anchor=W, side="top")
###

def executeRegionChoice(intVal, img, imgName): 
    print("Inside executeRegionChoice")

    fig = plt.figure(num="Region Based Changes", figsize=(10, 6))
    plt.clf() # Should clear last plot but keep window open? 
    numRows = 1
    numColumns = 2

    if (intVal == 1):
        # region filling
        from skimage.feature import canny
        from scipy.ndimage import binary_fill_holes

        numRows = 2
        numColumns = 2

        cannyImage = canny(img)
        regionFilled = binary_fill_holes(cannyImage)

        modifiedImageArray = [img, cannyImage, regionFilled]
        labelArray = ["Original Image", "Canny Edge Detection", "Region Filled Image"]
        
        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    # elif (intVal == 2):
    #     # region growing
    #     # seperate algorithm to implement
        
    # elif (intVal == 3):
    #     # Region Splitting and Merging
    #     # seperate algorithm to implement

    else:
        # should never execute
        tellUser("Select an option...", labelUpdates)
###

def executeEdgeDetectionChoice(intVal, img, imgName):

    fig = plt.figure(num="Edge Detection Changes", figsize=(10, 6))
    plt.clf() # Should clear last plot but keep window open? 
    numRows = 1
    numColumns = 2

    if (intVal == 1):
        # Canny Edge Detection
        edge = cv2.Canny(img,100,200)

        modifiedImageArray = [img, edge]
        labelArray = ["Original Image", "Canny Edge Detection"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 2):
        # Simple Contour
        numRows = 3
        numColumns = 2

        (x, y) = img.shape
        resizedImg = cv2.resize(img,(256,256))
        # Compute the threshold of the grayscale image
        value1 , threshImg = cv2.threshold(resizedImg, np.mean(resizedImg), 255, cv2.THRESH_BINARY_INV)
        # canny edge detection
        cannyImg = cv2.Canny(threshImg, 0,255)
        # dilate edges detected.
        edges = cv2.dilate(cannyImg, None)

        modifiedImage = cv2.resize(edges, (y, x)) # resize

        modifiedImageArray = [img, resizedImg, threshImg, cannyImg, edges, modifiedImage]
        labelArray = ["Original Image", "Resized Image", "Thresholded Image", "Canny Edges of Thresholded Image", "Dilated Edges", "Restore Sizes"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 3):
        # Complete Contour
        numRows = 4
        numColumns = 2

        (x, y) = img.shape
        resizedImg = cv2.resize(img,(256,256))

        # Compute the threshold of the grayscale image
        value1 , threshImg = cv2.threshold(resizedImg, np.mean(resizedImg), 255, cv2.THRESH_BINARY_INV)

        # canny edge detection
        cannyImg = cv2.Canny(threshImg, 0,255)

        # dilate edges detected.
        edges = cv2.dilate(cannyImg, None)

        # find all the open/closed regions in the image and store (cnt). (-1 subscript since the function returns a two-element tuple)
        # The - pass them through the sorted function to access the largest contours first.
        cnt = sorted(cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2], key=cv2.contourArea)[-1]

        # Create a zero pixel mask that has equal shape and size to the original image.
        mask = np.zeros((256,256), np.uint8)

        # Draw the detected contours on the created mask.
        masked = cv2.drawContours(mask, [cnt], -1, 255, -1)

        # bitwise AND operation on the original image (img) and the mask
        dst = cv2.bitwise_and(resizedImg, resizedImg, mask=mask)
        
        modifiedImage = cv2.resize(dst, (y, x)) # resize

        modifiedImageArray = [img, resizedImg, threshImg, cannyImg, edges, masked, dst, modifiedImage]
        labelArray = ["Original Image", "Resized Image", "Thresholded Image", "Canny Edges of Thresholded Image", 
                        "Dilated Edges", "Image after mask", "Image Contours Detected", "resized Image"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)


    elif (intVal == 4):
        # Felzenszwalb's Segmentation
        numRows = 2
        numColumns = 2

        # from skimage.segmentation import felzenszwalb

        res1 = felzenszwalb(img, scale=50)
        res2 = felzenszwalb(img, scale=100)

        modifiedImageArray = [img, res1, res2]
        labelArray = ["Original Image", "Felzenswalb Image, Scale=50", "Felzenswalb Image, Scale=100"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    else:
        # should never execute
        tellUser("Select an option...", labelUpdates)
###

def executeClusteringChoice(intVal, img, imgName):

    fig = plt.figure(num="Clustering Changes", figsize=(10, 6))
    plt.clf() # Should clear last plot but keep window open? 
    numRows = 1 # used in matplotlib function below
    numColumns = 2 # used in matplotlib function below

    if (intVal == 1):
        # K-Means Clustering
        twoDimage = img.reshape((-1,1)) # Transform into a 1D matrix
        # print(twoDimage.shape)
        # print(twoDimage[0])
        twoDimage = np.float32(twoDimage) # float32 data type needed for this function
        # print(twoDimage[0])

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        attempts=10

        modifiedImageArray = [img]
        labelArray = ["Original Image"]
        numRows = 2
        numColumns = 2

        for i in range(2, 5):
            K = i

            ret, label, center = cv2.kmeans(twoDimage, K, None, criteria, attempts, cv2.KMEANS_PP_CENTERS)
            center = np.uint8(center)
            res = center[label.flatten()]
            result_image = res.reshape((img.shape))

            modifiedImageArray.append(result_image)
            labelArray.append("K-Means Clustering, Size=" + str(i))

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    # elif (intVal == 2):
    #     #

    # elif (intVal == 3):
    #     #
    else:
        # should never execute
        tellUser("Select an option...", labelUpdates)

###

def executeThresholdingChoice(intVal, img, imgName):
    # print("Inside executeThresholdingChoice()")

    fig = plt.figure(num="Segmentation Changes", figsize=(8, 4))
    plt.clf() # Should clear last plot but keep window open? 
    numRows = 1 # used in matplotlib function below
    numColumns = 2 # used in matplotlib function below

    # 7 choices
    if (intVal == 1):
        # Simple 
        returnValue, modifiedImage = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        modifiedImageArray = [img, modifiedImage]
        labelArray = ["Original Image", "Simple Thresholding"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 2):
        # Iterative Thresholding
        modifiedImageArray = [img]
        labelArray = ["Original Image"]
        numRows = 3
        numColumns = 2

        for i in range(2, 6):
            returnValue, modifiedImage = cv2.threshold(img, (255 // i), 255, cv2.THRESH_BINARY)
            modifiedImageArray.append(modifiedImage)
            labelArray.append("Simple Thresholding using \'" + str(255 // i) + "\'")

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 3):
        # Adaptive Thresholding
        returnValue1, modifiedImage1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        # last 2 parameters below: block size of neighbourhood and constant used
        modifiedImage2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2) 
        modifiedImage3 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        modifiedImageArray = [img, modifiedImage1, modifiedImage2, modifiedImage3]
        labelArray = ["Original Image", "Simple Thresholding", "Adaptive Mean Thresholding", "Adaptive Gaussian Thresholding"]

        numRows = 2
        numColumns = 2

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 4):
        # Otsu's Method

        # global thresholding
        ret1,th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

        # Otsu's thresholding
        ret2,th2 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Otsu's thresholding after Gaussian filtering
        blur = cv2.GaussianBlur(img, (5, 5), 0)
        ret3,th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # plot all the images and their histograms
        modifiedImageArray = [img, th1, img, th2, blur, th3]
        labelArray = ['Original Image','Global Thresholding (v=127)','Original Image',"Otsu's Thresholding",'Gaussian filtered Image',"Otsu's Thresholding"]

        numRows = 3
        numColumns = 3
        
        x = 0
        for i in range(3):
            x += 1
            fig.add_subplot(numRows, numColumns, x)

            plt.imshow(modifiedImageArray[i*2], cmap='gray')
            plt.title(labelArray[i], wrap=True)
            plt.axis('off') #Removes axes

            x += 1
            fig.add_subplot(numRows, numColumns, x)
            plt.hist(modifiedImageArray[i*2].ravel(), 256)
            plt.title("Histogram", wrap=True)

            x += 1
            fig.add_subplot(numRows, numColumns, x)
            plt.imshow(modifiedImageArray[i + 1], cmap='gray')
            plt.title(labelArray[i*2 +1], wrap=True)
            plt.axis('off') #Removes axes

        plt.tight_layout()
        plt.show()

    else:
        # should never execute
        tellUser("Select an option...", labelUpdates)
###

# allows for any number of images to be placed in a grid
def plotImagesSideBySide(fig, imgArray, imgName, labelArray, numRows, numColumns):
    for i in range(len(imgArray)):
        fig.add_subplot(numRows, numColumns, i+1)
        plt.imshow(imgArray[i], cmap='gray')
        plt.title(labelArray[i], wrap=True)
        plt.axis('off') #Removes axes

    plt.tight_layout()
    plt.show()

    tellUser("Changes displayed...", labelUpdates)
###

#------------------------------------------------------------------------------------Malice Functions Below---------------------

def chooseMaliceOption():
    # print("Inside chooseMaliceOption()")

    window.filename = openGUI("Select an Image...")

    imgGrayscale, success = getGray()

    if (success):
        maliceWindow = Toplevel(window)
        maliceWindow.title("Choose a kind of malice...")
        maliceWindow.geometry("300x300")

        threshOption = IntVar()
        threshOption.set(0)

        Radiobutton(maliceWindow, text="Brighten an Image", variable=threshOption, value=1, width=30).pack(anchor=W, side="top")
        Radiobutton(maliceWindow, text="Darken an Image", variable=threshOption, value=2, width=30).pack(anchor=W, side="top")
        Radiobutton(maliceWindow, text="Inject Noise", variable=threshOption, value=3, width=30).pack(anchor=W, side="top")
        Radiobutton(maliceWindow, text="Flip Vertically", variable=threshOption, value=4, width=30).pack(anchor=W, side="top")
        Radiobutton(maliceWindow, text="Flip Horizontally", variable=threshOption, value=5, width=30).pack(anchor=W, side="top")
        Radiobutton(maliceWindow, text="Flip Diagonally", variable=threshOption, value=6, width=30).pack(anchor=W, side="top")
        Radiobutton(maliceWindow, text="Rotate +90 Degrees", variable=threshOption, value=7, width=30).pack(anchor=W, side="top")

        Button(maliceWindow, text="Choose Segmentation Option", width=50, bg='gray',
            command=lambda: executeMaliceChoice(intVal=threshOption.get(), img=imgGrayscale, imgName=window.filename)
        ).pack(anchor=W, side="top")
        Button(maliceWindow, text="Close Plots", width=50, bg='gray',
            command=lambda: ( plt.close("Malice Changes") )
        ).pack(anchor=W, side="top")
    else:
        tellUser("Unable to Get Grayscale Image for Malice Window...", labelUpdates)
    
    return True
###

def executeMaliceChoice(intVal, img, imgName):
    # print("Inside executeMaliceChoice")

    fig = plt.figure(num="Malice Changes", figsize=(8, 4))
    plt.clf() # Should clear last plot but keep window open? 
    numRows = 1 # used in matplotlib function below
    numColumns = 2 # used in matplotlib function below

    if (intVal == 1):
        # Brighten an Image

        tempImage = img # make a copy of intensity values before modification

        # notation is a shorthand to bulk change all values!
        newImage = ( img + int(255 * 0.3) ) # 30% brighter 
        
        # notation is a shorthand to bulk change all values!
        # (240 + 76 == 316 --> 61) --> This wrapping happens with this shorthand, so we need to reset the bright points! 
        newImage[tempImage > int(255 * 0.7)] = 255

        modifiedImageArray = [img, newImage]
        labelArray = ["Original Image", "Brighter Image"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)
        

    elif (intVal == 2):
        # Darken an Image
        tempImage = img # make a copy of intensity values before modification

        # notation is a shorthand to bulk change all values!
        newImage = ( img - int(255 * 0.3) ) # 30% darker
        
        # notation is a shorthand to bulk change all values!
        # (12 - 76 == -64 --> 191) --> This wrapping happens with this shorthand, so we need to reset the dark points! 
        newImage[tempImage < int(255 * 0.3)] = 0

        modifiedImageArray = [img, newImage]
        labelArray = ["Original Image", "Darker Image"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 3):
        # Inject Noise
        
        numRows = 2
        numColumns = 3

        # convert PIL Image to ndarray
        img_arr = np.asarray(img)

        # random_noise() method will convert image in [0, 255] to [0, 1.0],
        
        gauss_noise = random_noise(img_arr, mode='gaussian')
        gauss_noise = (255 * gauss_noise)

        salt_pepper_noise = random_noise(img_arr, mode='s&p') # salt and pepper
        salt_pepper_noise = (255 * salt_pepper_noise)

        poisson_noise = random_noise(img_arr, mode='poisson')
        poisson_noise = (255 * poisson_noise)

        speckle_noise = random_noise(img_arr, mode='speckle')
        speckle_noise = (255 * speckle_noise)

        gauss_img = Image.fromarray(gauss_noise)
        salt_pepper_img = Image.fromarray(salt_pepper_noise)
        poisson_img = Image.fromarray(poisson_noise)
        speckle_img = Image.fromarray(speckle_noise)

        modifiedImageArray = [img, gauss_img, salt_pepper_img, poisson_img, speckle_img]
        labelArray = ["Original Image", "Gaussian Noise", "Salt and Pepper Noise", "Poisson Noise", "Speckle Noise"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)
        

    elif (intVal == 4):
        # Flip Vertically
        img_flip_ud = cv2.flip(img, 0)

        modifiedImageArray = [img, img_flip_ud]
        labelArray = ["Original Image", "Flipped Vertically"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 5):
        # Flip Horizontally
        img_flip_lr = cv2.flip(img, 1)

        modifiedImageArray = [img, img_flip_lr]
        labelArray = ["Original Image", "Flipped Horizontally"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 6):
        # Flip Diagonally
        img_flip_diag = cv2.flip(img, 0)
        img_flip_diag = cv2.flip(img_flip_diag, 1)

        modifiedImageArray = [img, img_flip_diag]
        labelArray = ["Original Image", "Flipped Diagonally"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 7):
        # Rotate +90 Degrees
        img_rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        modifiedImageArray = [img, img_rotated]
        labelArray = ["Original Image", "Rotated Image"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    else:
        # should never execute
        tellUser("Select an option...", labelUpdates)
###

#------------------------------------------------------------------------------------Feature Representation Functions-----------

def chooseFeatureRepresentationOption():
    # print("Inside chooseFeatureRepresentationOption()")

    window.filename = openGUI("Select an Image...")

    imgGrayscale, success = getGray()

    if (success):
        featureRepWindow = Toplevel(window)
        featureRepWindow.title("Choose a kind of Feature Representation...")
        featureRepWindow.geometry("300x300")

        featRepOption = IntVar()
        featRepOption.set(0)

        Radiobutton(featureRepWindow, text="Get Skeleton", variable=featRepOption, value=1, width=30).pack(anchor=W, side="top")
        Radiobutton(featureRepWindow, text="Download Co-Occurence Matrix", variable=featRepOption, value=2, width=30).pack(anchor=W, side="top")
        Radiobutton(featureRepWindow, text="Get Haralick Features", variable=featRepOption, value=3, width=30).pack(anchor=W, side="top")

        Button(featureRepWindow, text="Choose Segmentation Option", width=50, bg='gray',
            command=lambda: executeFeatureRepresentationChoice(intVal=featRepOption.get(), img=imgGrayscale, imgName=window.filename)
        ).pack(anchor=W, side="top")
        Button(featureRepWindow, text="Close Plots", width=50, bg='gray',
            command=lambda: ( plt.close("Feature Representation Changes") )
        ).pack(anchor=W, side="top")
    else:
        tellUser("Unable to Get Grayscale Image for Feature Representation Window...", labelUpdates)
    
    return True
###

def executeFeatureRepresentationChoice(intVal, img, imgName):
    # print("Inside executeFeatureRepresentationChoice()")

    fig = plt.figure(num="Feature Representation Changes", figsize=(8, 4))
    plt.clf() # Should clear last plot but keep window open? 
    numRows = 1 # used in matplotlib function below
    numColumns = 2 # used in matplotlib function below

    if (intVal == 1):
        # get skeleton

        imageBoolean = img_as_bool(img)
        skel = morphology.medial_axis(imageBoolean)

        modifiedImageArray = [img, skel]
        labelArray = ["Original Image", "Skeleton"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 2):
        # Co Occurence Matrix

        # Test
        # arr = [ [0, 0, 1, 1],
        #         [0, 0, 1, 1],
        #         [0, 2, 2, 2],
        #         [2, 2, 3, 3] ]
        # glcm = graycomatrix(np.array(arr), distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], levels=4)
        # print(glcm[:, :, 0, 0])

        glcm = graycomatrix(np.array(img), distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], levels=256)

        # [:, :, 0, 0] --> [i, j, d, theta] ; in other words, d==distance away==0, theta==angle==0
        # print(glcm[:, :, 0, 0])

        currentDir = os.getcwd()
        path = currentDir + "\Images\Reports"
        try:
            os.mkdir(path)
        except:
            pass

        imgName = window.filename
        fileName = "Co_Occurence_Report_" + getName(imgName)
        fileName += "_" + getExtension(imgName) + ".txt"

        completeName = os.path.join(path, fileName)
        # x, y == 256 because glcm is a square matrix!
        imageDescription = getMatrix(glcm[:, :, 0, 0], 256, 256, getName(window.filename) + "_" + getExtension(window.filename), "Co Occurence Matrix")
        text_file = open(completeName, "w")
        text_file.write(completeName+"\n\n")
        text_file.write(imageDescription)

        if(os.path.exists(completeName)):
            tellUser("Co Occurence Matrix Downloaded successfully", labelUpdates) # Update
        else:
            tellUser("Unable to create file")

    elif (intVal == 3):
        # Get Haralick Features

        # Test
        # arr = [ [0, 0, 1, 1],
        #         [0, 0, 1, 1],
        #         [0, 2, 2, 2],
        #         [2, 2, 3, 3] ]
        # glcm = graycomatrix(np.array(arr), distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], levels=4)
        # properties = ['contrast', 'dissimilarity', 'homogeneity', 'ASM', 'energy', 'correlation', ]

        # print(graycoprops(glcm, properties[0])[0]) # first value of result

        glcm = graycomatrix(np.array(img), distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], levels=256)
        properties = ['contrast','dissimilarity','homogeneity','ASM','energy','correlation' ]
        haralickVector = [0, 0, 0, 0, 0, 0]

        for i in range(6):
            haralickVector[i] = ( graycoprops(glcm, properties[i] )[0][0] )
        
        # print(properties)
        # print(haralickVector)

        string = "\t Haralick Features: \n"

        for i in range(6):
            string += "{0:20}: {1} \n".format(properties[i], haralickVector[i])
        print(string)


        fig.add_subplot(numRows, numColumns, 1)
        plt.imshow(img, cmap='gray')
        plt.title("Original Image", wrap=True)
        plt.axis('off') #Removes axes

        fig.add_subplot(numRows, numColumns, 2)
        # set the font globally
        plt.rcParams.update({'font.family':'sans-serif'})
        plt.text(0, 0.7, string, fontsize=12,verticalalignment='top')
        plt.axis('off') #Removes axes

        plt.tight_layout()
        plt.show()


    else:
        # should never execute
        tellUser("Select an option...", labelUpdates)
###

def getMatrix(matrix, x, y, fileName, message):
    text = message + " " + fileName
    text += "; Size: (" + str(x) + ", " + str(y) + ")\n"
    text += "[ [\n"

    for a in range(0, x):
        for b in range(0, y):
            text += str(matrix[a, b]) + " "
        text += " <end>\n"
    text += " ] ]"
    
    return text
###

#------------------------------------------------------------------------------------Image Transformation Functions-------------

def chooseImageTransformation():
    # print("Inside chooseImageTransformationOption()")

    window.filename = openGUI("Select an Image...")

    imgGrayscale, success = getGray()

    if (success):
        imageTransformationWindow = Toplevel(window)
        imageTransformationWindow.title("Choose a kind of Image Transformation...")
        imageTransformationWindow.geometry("300x300")

        imageTransformOption = IntVar()
        imageTransformOption.set(0)

        Radiobutton(imageTransformationWindow, text="Apply Fourier Transform", variable=imageTransformOption, value=1, width=30).pack(anchor=W, side="top")
        Radiobutton(imageTransformationWindow, text="Apply Haar Transform", variable=imageTransformOption, value=2, width=30).pack(anchor=W, side="top")
        Radiobutton(imageTransformationWindow, text="Apply Discrete Cosine Transform", variable=imageTransformOption, value=3, width=30).pack(anchor=W, side="top")

        Button(imageTransformationWindow, text="Choose Segmentation Option", width=50, bg='gray',
            command=lambda: executeImageTransformationChoice(intVal=imageTransformOption.get(), img=imgGrayscale, imgName=window.filename)
        ).pack(anchor=W, side="top")
        Button(imageTransformationWindow, text="Close Plots", width=50, bg='gray',
            command=lambda: ( plt.close("Image Transformation Changes") )
        ).pack(anchor=W, side="top")
    else:
        tellUser("Unable to Get Grayscale Image for Image Transformation Window...", labelUpdates)
###

def executeImageTransformationChoice(intVal, img, imgName):
    # print("Inside executeImageTransformationOption()")

    fig = plt.figure(num="Image Transformation Changes", figsize=(8, 4))
    plt.clf() # Should clear last plot but keep window open? 
    numRows = 1 # used in matplotlib function below
    numColumns = 2 # used in matplotlib function below

    if (intVal == 1):
        # Fourier Transform
        numRows = 2
        numColumns = 2

        # discrete fourier transformation
        dft = cv2.dft(np.float32(img),flags = cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:,:,0],dft_shift[:,:,1])) # fourier transformed image

        rows, cols = img.shape
        crow, ccol = rows//2 , cols//2

        # create a mask first, center square is 1, remaining all zeros
        mask1 = np.zeros((rows,cols,2),np.uint8)
        mask1[crow-30:crow+30, ccol-30:ccol+30] = 1

        # apply mask and inverse DFT --> Low Pass Filter
        fshift_low_pass = dft_shift*mask1
        f_ishift_low_pass = np.fft.ifftshift(fshift_low_pass)
        img_back_low_pass = cv2.idft(f_ishift_low_pass)
        img_back_low_pass = cv2.magnitude(img_back_low_pass[:,:,0],img_back_low_pass[:,:,1])

        # High Pass Filter
        mask2 = np.fft.fftshift(np.fft.fft2(img))
        mask2[crow-30:crow+30, ccol-30:ccol+30] = 0
        f_ishift_high_pass = np.fft.ifftshift(mask2)
        img_back_high_pass = np.fft.ifft2(f_ishift_high_pass)
        img_back_high_pass = np.log(np.abs(img_back_high_pass))

        modifiedImageArray = [img, magnitude_spectrum, img_back_low_pass, img_back_high_pass]
        labelArray = ["Original Image", "Magnitude Spectrum", "Low Pass Filter", "High Pass Filter"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 2):
        #Haar Transform

        # haar method comes from mahotas package
        haar_transform = haar(img)

        modifiedImageArray = [img, haar_transform]
        labelArray = ["Original Image", "Haar Transform"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    elif (intVal == 3):
        # Discrete Cosine Transform, from scipy package
        dct_img = fft.dct(img)

        modifiedImageArray = [img, dct_img]
        labelArray = ["Original Image", "DCT Image"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    else:
        # should never execute
        tellUser("Select an option...", labelUpdates)
###

#------------------------------------------------------------------------------------Compression Functions Below----------------

def chooseCompression():
    # print("Inside chooseImageTransformationOption()")

    window.filename = openGUI("Select an Image...")

    imgGrayscale, success = getGray()

    if (success):
        compressionWindow = Toplevel(window)
        compressionWindow.title("Choose a kind of Image Transformation...")
        compressionWindow.geometry("300x300")

        compressOption = IntVar()
        compressOption.set(0)

        Radiobutton(compressionWindow, text="Apply DCT Compression", variable=compressOption, value=1, width=30).pack(anchor=W, side="top")

        Button(compressionWindow, text="Choose Compresion Option", width=50, bg='gray',
            command=lambda: executeCompressionChoice(intVal=compressOption.get(), img=imgGrayscale, imgName=window.filename)
        ).pack(anchor=W, side="top")
        Button(compressionWindow, text="Close Plots", width=50, bg='gray',
            command=lambda: ( plt.close("Compression Changes") )
        ).pack(anchor=W, side="top")
    else:
        tellUser("Unable to Get Grayscale Image for Compression Window...", labelUpdates)
###



def executeCompressionChoice(intVal, img, imgName):
    print("Inside executeCompressionOption()")

    fig = plt.figure(num="Compression Changes", figsize=(8, 4))
    plt.clf() # Should clear last plot but keep window open? 
    numRows = 1 # used in matplotlib function below
    numColumns = 2 # used in matplotlib function below

    if (intVal == 1):
        # DCT compression

        imgsize = img.shape
        dct = np.zeros(imgsize)

        # Do 8x8 DCT on image (in-place)
        for i in r_[:imgsize[0]:8]:
            for j in r_[:imgsize[1]:8]:
                dct[i:(i+8),j:(j+8)] = dct2( img[i:(i+8),j:(j+8)] )

        pos = 128
        # 8X8 image block
        img_slice = img[pos:pos+8,pos:pos+8]
        # An 8X8 dct block
        dct_slice = dct[pos:pos+8,pos:pos+8]

        # Threshold our dct image
        thresh = 0.012
        dct_thresh = dct * (abs(dct) > (thresh*np.max(dct)))

        # Use thresholded image to compress
        img_idct = np.zeros(imgsize)

        for i in r_[:imgsize[0]:8]:
            for j in r_[:imgsize[1]:8]:
                img_idct[i:(i+8),j:(j+8)] = idct2( dct_thresh[i:(i+8),j:(j+8)] )

        numRows = 2
        numColumns = 3
        modifiedImageArray = [img, dct, img_slice, dct_slice, dct_thresh, img_idct]
        labelArray = ["Original Image", "DCT Image", "An 8X8 Image block", "An 8X8 DCT Block", "DCT Thresholding", "Using DCT to compress"]

        plotImagesSideBySide(fig, modifiedImageArray, imgName, labelArray, numRows, numColumns)

    else:
        # should never execute
        tellUser("Select an option...", labelUpdates)
###

def dct2(a):
    return dct( dct( a, axis=0, norm='ortho' ), axis=1, norm='ortho' )
###

def idct2(a):
    return idct( idct( a, axis=0 , norm='ortho'), axis=1 , norm='ortho')
###

#------------------------------------------------------------------------------------Bulk Resize Functions Below----------------

def bulkResize():
    print("Inside bulkResize()")

    currentDir = os.getcwd()
    folder = "\\Images\\Notes_DataSet"
    path = os.walk(currentDir + folder)
    destinationFolder = currentDir + "\\Images\\Resized_Notes_DataSet"

    # create directory
    try:
        os.mkdir(destinationFolder)
    except FileExistsError as uhoh:
        pass
    except Exception as uhoh:
        print("New Error:", uhoh)
        pass
    
    i = 0
    for root, directories, files in path:
        for file in files:
            temp = currentDir + folder + "\\" + file
            image = cv2.imread(temp, cv2.IMREAD_COLOR)
            print(i)
            resizedImage = cv2.resize(image, (1024, 512))
            cv2.imwrite(destinationFolder + "\\" + file, resizedImage)
            i += 1
###

#------------------------------------------------------------------------------------Other Functions Below----------------------

# places updated label for user
def tellUser(str, label):
    oldText = label.cget("text")
    endStr = " - Watch this space for more updates..."
    newText = str + endStr

    #updates incase user sees same message twice
    if (oldText == newText):
        newText += "(NEW)"
    label.config(text = newText) #global var
###

def openGUI(message):
    temp = filedialog.askopenfilename(initialdir="Images", title=message, 
                                                    filetypes=(
                                                        ("All Files", "*.*"), ("jpg Files", "*.jpg"), 
                                                        ("png files", "*.png"), ("gif files", "*.gif"),
                                                        ("tiff files", "*.tiff"), ("bmp files", "*.bmp"),
                                                        ("raw files", "*.raw")
                                                    )
    )

    return temp
###