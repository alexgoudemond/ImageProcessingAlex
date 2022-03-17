import math
from tkinter import Button, Entry, IntVar, Label, Radiobutton, Tk, Toplevel
from tkinter import filedialog
from matplotlib import pyplot  as plt
import cv2
import numpy as np



def View(flag = cv2.IMREAD_UNCHANGED):
    global image
    root.filename = filedialog.askopenfilename(initialdir=r"Images", title="Select A File",
                                               filetypes=(("png files", "*.png"), ("gif files", "*.gif"),
                                                          ("tiff files", "*.tiff"), ("bmp files", "*.bmp"),
                                                          ("raw files", "*.raw"), ("All Files", "*.*")))

    if root.filename.endswith(".gif"):
        cap = cv2.VideoCapture(root.filename)
        ret, image = cap.read()
        cap.release()
        if ret:
            if flag == cv2.IMREAD_GRAYSCALE:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            if flag == cv2.IMREAD_COLOR:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cv2.imshow(root.filename[root.filename.rfind("/") + 1:], image)
            #cv2.waitKey(0)
            return
        else:
            raise ValueError("image cannot be read")

    elif root.filename.endswith(".raw"):
        fd = open(root.filename, 'rb')
        rows = 512
        cols = 512

        f = np.fromfile(fd, dtype=np.uint8, count=rows * cols)
        image = f.reshape((rows, cols))
        fd.close()
        image = np.array(image)
        #if flag == cv2.IMREAD_GRAYSCALE:
        #    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imshow(root.filename[root.filename.rfind("/") + 1:], image)
        #cv2.waitKey(0)

    else:
        image = cv2.imread(root.filename, flag)
        cv2.imshow(root.filename[root.filename.rfind("/") + 1:], image)
        #cv2.waitKey(0)


def IntensityValue():
    global image
    View(cv2.IMREAD_GRAYSCALE)

    intensityValueWindow = Toplevel(root)
    intensityValueWindow.title("Intensity Values")
    rows, cols = image.shape
    intensityValueString = ""
    for row in range(0,rows, 15):
        for col in range(0,cols, 45):
            intensityValueString += str(image[row][col]) + '\t'
        intensityValueString += '\n'

    Label(intensityValueWindow, text = intensityValueString).pack()



def displayHist(img):
    plt.hist(img.ravel(), 256, [0,256])
    plt.title('Image Histogram')
    plt.xlabel('Grey Levels')
    plt.ylabel('Frequescies')
    plt.show()

def EnhanceImage(option, cValue=1, gammaValue=0.5):
    global image
    if option == 1:
        imageEnhanced = cv2.equalizeHist(image)
        cv2.imshow("equalizeHist", imageEnhanced)
        displayHist(image)
        displayHist(imageEnhanced)
        TransformationFunction(image, imageEnhanced)
    
    elif option == 2:
        imageEnhanced = cv2.bitwise_not(image)
        cv2.imshow("Negative Image", imageEnhanced)
        displayHist(image)
        displayHist(imageEnhanced)
        TransformationFunction(image, imageEnhanced)

    elif option == 3:
        #imageEnhanced = cv2.threshold(src=image, thresh=int(255/2), maxval=255, type= cv2.THRESH_BINARY)
        imageEnhanced = cv2.adaptiveThreshold(src=image, maxValue=255, adaptiveMethod=cv2.BORDER_REPLICATE, thresholdType=cv2.THRESH_BINARY,blockSize=3, C=10)
        cv2.imshow("Thresholding", imageEnhanced)
        displayHist(image)
        displayHist(imageEnhanced)
        TransformationFunction(image, imageEnhanced)

    elif option == 4:
        cValue = 255 / np.log(1 + np.max(image))
        imageEnhanced = cValue * np.log(1 + image) #(cValue* np.ones(image.size)) *
        imageEnhanced.reshape(512,512)
        plt.imshow(imageEnhanced)
        plt.show()
        displayHist(image)
        displayHist(imageEnhanced)
        TransformationFunction(image, imageEnhanced)

    elif option == 5:
        imageEnhanced = np.array(cValue*np.power(image,gammaValue))
        cv2.imshow("Power Law (Gamma) Transformations", imageEnhanced)
        displayHist(image)
        displayHist(imageEnhanced)
        TransformationFunction(image, imageEnhanced)


def Enhance():
    global image
    View(cv2.IMREAD_GRAYSCALE)

    enhanceValueWindow = Toplevel(root)
    enhanceValueWindow.title("Enhance an image")
    enhanceOption = IntVar()
    enhanceOption.set(0)

    Radiobutton(enhanceValueWindow, text="Histogram Equalisation", variable=enhanceOption, value=1).pack()
    Radiobutton(enhanceValueWindow, text="Point Processing: Negative Image", variable=enhanceOption, value=2).pack()
    Radiobutton(enhanceValueWindow, text="Point Processing: Thresholding", variable=enhanceOption, value=3).pack()
    Radiobutton(enhanceValueWindow, text="Logarithmic Transformations", variable=enhanceOption, value=4).pack()
    Radiobutton(enhanceValueWindow, text="Power Law (Gamma) Transformations", variable=enhanceOption, value=5).pack()
    Button(enhanceValueWindow, text="Enhance", padx=100, command=lambda: EnhanceImage(enhanceOption.get(), float(cValue.get()), float(gammmaValue.get()))).pack()
    cValue = Entry(enhanceValueWindow, text="C=")
    gammmaValue = Entry(enhanceValueWindow, text="gamma=")
    cValue.pack()
    gammmaValue.pack()


def TransformationFunction(input, output):
    plt.plot(input, output)
    plt.title('Transformation Function')
    plt.xlabel('Input Intensity Values')
    plt.ylabel('Output Intensity Values')
    plt.show()


root = Tk()
root.title("Image Processing and Computer Vision")
image = None
openButton = Button(root, text="View", padx=100, command=View)
intensityValueButton = Button(root, text="Intensity Values", padx=100, command=IntensityValue)
histogramButton = Button(root, text="Display Histogram", padx=100, command=displayHist)
enhanceButton = Button(root, text="Enhance", padx=100, command=Enhance)
quitButton = Button(root, text="Exit", padx=100, command=root.quit)

openButton.pack()
intensityValueButton.pack()
histogramButton.pack()
enhanceButton.pack()
quitButton.pack()

root.mainloop()