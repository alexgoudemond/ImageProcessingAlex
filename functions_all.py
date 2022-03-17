"""
Author: Alexander Goudemond

Program name: functions_all.py

# Notice:
            There is a lot of code in 1 place, so I have tried to structure it together. Functions are grouped where possible
            Right Now we have the following sections:
            - Packages
            - Functions:
                - Open / Display
                - Convert
                - Changing Names
                - Intensity values
                - Other
            - Program:
                - Frames and Window
                - Labels
                - Buttons
                - pack()
                - Open
            - End

Please ensure the file openAnyImage.py is in the same location as this program
"""

#----------------------------------------------------------------------------------------------------------------Packages Below
# 2 objects below are global variables in my main file
# from openAnyImage import window, labelUpdates

# tkinter is GUI, numpy is for RAW images, cv2 for other videos, 
# os for deleting files
from json import tool
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import turtle
from types import NoneType
import cv2
import numpy as np
import os
from PIL import Image, ImageTk
from matplotlib import pyplot  as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from pandas import DataFrame


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
    window.filename = openGUI()

    if window.filename.endswith(".gif"):
        success = displayGIF(window.filename)
    elif window.filename.endswith(".raw"):
        image, success = convertRAW(window.filename)
        cv2.imshow(window.filename, image)
        cv2.waitKey(0)
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
    window.filename = openGUI()

    try:
        currentDir = os.getcwd()
        os.mkdir(currentDir + "\Images\Converted")
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
    window.filename = openGUI()

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
    window.filename = openGUI()

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
# bins are qty of histogram pieces, range is for width of graph
def displayHist(img, str, number):
    plt.figure(number) #changing the number means distinct window
    plt.hist(img.ravel(), bins=256, range=[0,256])
    plt.title(str)
    plt.xlabel('Gray Levels')
    plt.ylabel('Frequencies')
    # plt.show()
###

def chooseEnhancement():
    window.filename = openGUI()
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
        cLabel = Label(choicesWindow, text="c = ...").pack()
        cValue = tk.Entry(choicesWindow)
        cValue.pack() #must be seperate for some reason...
        gammaLabel = Label(choicesWindow, text="gamma = ...").pack()
        gammaValue = tk.Entry(choicesWindow)
        gammaValue.pack() #must be seperate for some reason...

        # TODO handle NoneType issue
        Button(
            choicesWindow, text="Enhance", width=35, bg='silver',
            command=lambda: executeEnhancement(
                                intVal=enhanceOption.get(), img=imgGrayscale, 
                                imgName=window.filename, c=float(cValue.get() ), gamma=float(gammaValue.get() )
                            ) 
        ).pack()
        # Button above sends the user elsewhere
        
    else:
        tellUser("Unable to Get Grayscale Image for Enhancement Window...", labelUpdates)

def executeEnhancement(intVal, img, imgName, c, gamma):
    tellUser("Opening now...", labelUpdates)
    
    if (intVal == 1):
        histEqualization(img, imgName)
    plt.show()
            
###

def histEqualization(img, imgName):
    message = "B/W JPG Image of: " + getName(imgName) + "." + getExtension(imgName)
    cv2.imshow(message, img)

    message = "Histogram of B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(img, message, 1)
    
    imgEnhanced = cv2.equalizeHist(img)

    message = "Histogram of **Enhanced** B/W JPG of: " + getName(imgName) + "." + getExtension(imgName)
    displayHist(imgEnhanced, message, 2)
    
    message = "Histogram Equalized Image of: " + getName(imgName) + "." + getExtension(imgName)
    cv2.imshow(message, imgEnhanced)

# # Select an image to enhance, then prep window, then enhance
# def chooseEnhancement():
#     window.filename = openGUI()

#     imgGrayscale, success = getGray()

#     if(success):
#         prepLayout(imgGrayscale, window.filename)
#     else:
#         tellUser("Unable to Open Enhancement Window...", labelUpdates)
# ###

# def prepLayout(img, windowFilename):
#     windowEnhancements = Toplevel(window)
#     windowEnhancements.title("Image Enhancements Below")
#     windowEnhancements.geometry("1000x1000")

#     topFrame = tk.Frame(master=windowEnhancements) 
#     bottomFrame = tk.Frame(master=windowEnhancements)

#     cv2.imwrite("temp.jpg", img)
#     # Below lets us add image inside Label
#     photoPath = Image.open("temp.jpg")
#     photo = ImageTk.PhotoImage(photoPath)

#     labelNames1 = tk.Label(
#         master = topFrame, 
#         text = "Original BW Image", 
#         compound = 'bottom',
#         width = 50,
#         bg = 'gray'
#     )
#     labelPic1 = tk.Label(
#         master = topFrame, 
#         font = ("Helvetica", 14),
#         width = photo.width(),
#         image = photo
#     )
#     labelNames2 = tk.Label()
#     labelNames3 = tk.Label(
#         master = bottomFrame, 
#         text = "New BW Image",
#         font = ("Helvetica", 14),
#         compound = 'bottom',
#         width = 50,
#         bg = 'gray'
#     )
#     labelPic2 = tk.Label()
#     labelNames4 = tk.Label()

#     topFrame.pack()
#     bottomFrame.pack()

#     labelNames1.pack()
#     labelPic1.pack(side=tk.LEFT)
#     labelNames2.pack()
#     labelNames3.pack()
#     labelPic2.pack(side=tk.LEFT)
#     labelNames4.pack()

#     applyEnhancements(img, windowFilename, labelPic1, labelPic2)

#     windowEnhancements.mainloop()
#     # kills once window is closed, to avoid multiple "exit" presses on Exit button
#     windowEnhancements.quit() 
#     # pic is created before this function - delete
#     try:
#         os.remove("temp.jpg")
#     except:
#         pass
# ###

# def displayHist2(img, imgName, label):
#     fig = Figure(figsize = (5, 5), dpi = 100)
#     # y = [i**2 for i in range(101)]

#     # plot1 = fig.add_subplot(111)
#     # plot1.plot(y)
    

#     canvas = FigureCanvasTkAgg(fig, master = label) 
#     toolbar = NavigationToolbar2Tk(canvas, label)
#     toolbar.update()
#     canvas.get_tk_widget().pack(side=tk.RIGHT)
  
#     p = fig.gca()
#     # p.title('BW Image Histogram for: ' + getName(imgName))
#     p.hist(img.ravel(), bins=256, range=[0,256])
#     p.set_xlabel('Gray Levels')
#     p.set_ylabel('Frequencies')
#     canvas.draw()

#     canvas.draw()
#     canvas.get_tk_widget().pack(side=tk.RIGHT)

# def applyEnhancements(imgGrayscale, windowFilename, labelPic1, labelPic2):
#     # TODO add buttons here for additional options - pass via GET?

#     # 1 option for now
#     displayHist2(imgGrayscale, windowFilename, labelPic1)


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

def openGUI():
    temp = filedialog.askopenfilename(initialdir="Images", title="Select an Image to Open", 
                                                    filetypes=(
                                                        ("All Files", "*.*"), ("jpg Files", "*.jpg"), 
                                                        ("png files", "*.png"), ("gif files", "*.gif"),
                                                        ("tiff files", "*.tiff"), ("bmp files", "*.bmp"),
                                                        ("raw files", "*.raw")
                                                    )
    )

    return temp