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
from cv2 import destroyAllWindows
import numpy as np
import os # Path reading, File Writing and Deleting
from matplotlib import pyplot  as plt
from pandas import array

# Global Vars below
global window 
global updateFrame
global labelUpdates

window = tk.Tk()
window.title("COMP702 Image Processing")

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
    return imgGrayscale, success
###

# responsible for converting any image, then saving as grayscale jpg in dedicated folder
def convertTheImage():
    window.filename = openGUI("Select an Image to Convert")

    try:
        currentDir = os.getcwd()
        os.mkdir(currentDir + "\Images\Converted")
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
        newName = updateFileName(window.filename, appendedString)
        cv2.imwrite(newName, imgGrayscale)
        tellUser("Image converted successfully", labelUpdates)
    else:
        tellUser("Something went wrong... Unable to open")
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
def updateFileName(imgName, appendedString):
    currentDir = os.getcwd()

    finalForwardSlashPos = imgName.rfind("/")
    position = imgName.index(".")
    extension = imgName[position + 1 : ]
    fileName = imgName[finalForwardSlashPos + 1 : position]

    # print(imgName,":::", finalForwardSlashPos, "fileName:", fileName)

    answer = currentDir + "\Images\Converted\\" + fileName + "_from_" + extension  + appendedString + ".jpg"
    
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

    fig.add_subplot(2, 3, 1)
    message = "B/W JPG Image of: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(img, cmap='gray')
    plt.title(message)
    plt.axis('off') #Removes axes
    
    fig.add_subplot(2, 3, 2)
    message = "Histogram of B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(img, message, 1)

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
    plt.title(message)
    plt.xlabel('Input Intensity Values')
    plt.ylabel('Output Intensity Values')
###

def gammaTransform(img, imgName, cValue, gammaValue, fig):
    imageEnhanced = np.array(cValue*np.power(img,gammaValue))

    fig.add_subplot(2, 3, 4)
    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(imageEnhanced, message, 2)

    fig.add_subplot(2, 3, 5)
    message = "Power law (Gamma) Transformation of Image: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(imageEnhanced, cmap='gray') 
    plt.title(message)
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
    imageEnhanced.reshape(512,512)

    fig.add_subplot(2, 3, 4)
    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(imageEnhanced, message, 2)

    fig.add_subplot(2, 3, 5)
    message = "Logarithmic Transformation of Image: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(imageEnhanced, cmap='gray')
    plt.title(message)
    plt.axis('off') #Removes axes
    
    fig.add_subplot(2, 3, 3)
    message = "Transformation Function: "
    TransformationFunction(message, img, imageEnhanced)
###

def thresholding(img, imgName, fig):
    imageEnhanced = cv2.adaptiveThreshold(src=img, maxValue=255, adaptiveMethod=cv2.BORDER_REPLICATE, thresholdType=cv2.THRESH_BINARY,blockSize=3, C=10)
    
    fig.add_subplot(2, 3, 4)
    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(imageEnhanced, message, 2)

    fig.add_subplot(2, 3, 5)
    message = "Thresholding of Image: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(imageEnhanced, cmap='gray')
    plt.title(message)
    plt.axis('off') #Removes axes
    
    fig.add_subplot(2, 3, 3)
    message = "Transformation Function: "
    TransformationFunction(message, img, imageEnhanced)
###

def negImage(img, imgName, fig):
    imageEnhanced = cv2.bitwise_not(img)
    
    fig.add_subplot(2, 3, 4)
    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(imageEnhanced, message, 2)

    
    fig.add_subplot(2, 3, 5)
    message = "Negative Image of: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(imageEnhanced, cmap='gray')
    plt.title(message)
    plt.axis('off') #Removes axes
    
    fig.add_subplot(2, 3, 3)
    message = "Transformation Function: "
    TransformationFunction(message, img, imageEnhanced)
###

def histEqualization(img, imgName, fig):    
    imgEnhanced = cv2.equalizeHist(img)

    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    fig.add_subplot(2, 3, 4)
    displayHist(imgEnhanced, message, 2)
    
    message = "Histogram Equalized Image of: " + getName(imgName) + "." + getExtension(imgName)
    fig.add_subplot(2, 3, 5)
    plt.imshow(imgEnhanced, cmap='gray')
    plt.title(message)
    plt.axis('off') #Removes axes

    message = "Transformation Function: "
    fig.add_subplot(2, 3, 3)
    TransformationFunction(message, img, imgEnhanced)
###

# bins are qty of histogram pieces, range is for width of graph
def displayHist(img, str, number):
    plt.hist(img.ravel(), bins=256, range=[0,256])
    plt.title(str)
    plt.xlabel('Gray Levels')
    plt.ylabel('Frequencies')
###

#------------------------------------------------------------------------------------Filtering Functions Below------------------

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

    # Lets us stick 5 plots in 1 window
    # plt.close('Smoothing')
    fig = plt.figure(num="Smoothing", figsize=(10, 5))

    fig.add_subplot(1, 2, 1)
    message = "B/W JPG Image of: " + getName(imgName) + "." + getExtension(imgName)
    plt.imshow(img, cmap='gray')
    plt.title(message)
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
    plt.title('Gaussian Smooth of '+ getName(imgName) + "." + getExtension(imgName) )
###

def gaussianSmooth(img, imgName, arraySize):
    blur = cv2.GaussianBlur(img,(arraySize,arraySize),0)
    plt.imshow(blur, cmap='gray')
    plt.title('Gaussian Smoothof '+ getName(imgName) + "." + getExtension(imgName) )
###

def movingAverageSmooth(img, imgName, arraySize):
    kernel = np.ones((arraySize,arraySize), np.float32)/(arraySize * arraySize) # fills with all 1s
    dst = cv2.filter2D(img,-1,kernel)
    
    plt.subplot(122)
    plt.imshow(dst, cmap='gray')
    plt.title('Moving Average Smooth of '+ getName(imgName) + "." + getExtension(imgName) )
###

def simpleSmooth(img, imgName, arraySize):
    kernel = kernel = np.full((arraySize,arraySize), 1/(arraySize * arraySize)) # fills with numbers in array
    dst = cv2.filter2D(img,-1,kernel)
    
    plt.subplot(122)
    plt.imshow(dst, cmap='gray')
    plt.title('Simple Smooth of '+ getName(imgName) + "." + getExtension(imgName) )
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