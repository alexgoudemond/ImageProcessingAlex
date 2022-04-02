"""
Author: Alexander Goudemond

Program name: openAnyImage.py

Goal:   Open any image, using OpenCV and Tkinter
        And, Convert any image to grayscale
        And, find Matrix Intensity Values from Grayscale
        And, apply enhancement technique using Histogram of Greyscale Image

Images I can open:  JPG working
                    PNG working
                    Tiff working
                    BMP working
                    GIF working
                    RAW working

Hmmm:   cv2.imread() cannot read .gif, because animation
        VideoCapture() works for .gif
        
        cv2.imread() cannot read .raw
        numpy works for .raw


Note: 
    RAW files - we can discover what the shape of a file looks like using Numpy
        lena_gray.raw has shape (262144)==(512 X 512), other examples online have (2359296)==(768, 1024, 3)

        

Sources: 
        Image for GUI: https://learnopencv.com/read-display-and-write-an-image-using-opencv/
        Lena images:   UKZN Learn2022, COMP702

# Notice:
            There is a lot of code in 1 place, so I have tried to structure it together. 
                Functions are in a seperate file and grouped where possible

Please ensure the file functions_all.py is in the same location as this program
Create a folder called Images in the same directory as this and place Pics
"""
#----------------------------------------------------------------------------------------------------------------Packages Below
# Encapsulating functions from our dedicated functions file
from functions_all import chooseEnhancement, chooseSharpeningOption, chooseSmoothingOption, openTheImage, convertTheImage, getBWIntensityValues, downloadBWIntensityValues
# global Vars to use
from functions_all import window, labelUpdates, updateFrame

# PIL to find Image Path for image in GUI, tkinter for GUI
from PIL import Image, ImageTk
import tkinter as tk

#------------------------------------------------------------------------------------------------------------------Program Below

print("\n---Program Starting---\n\n")

#------------------------------------------------------------------------------------Frames Below-------------------------------

frame = tk.Frame()
buttonFrameTop = tk.Frame()
buttonFrameMiddle = tk.Frame()
buttonFrameBottom = tk.Frame()

#------------------------------------------------------------------------------------Labels Below-------------------------------

# Below lets us add image inside Label
photoPath = Image.open("E:/OpenCV/Images/test.jpg")
photo = ImageTk.PhotoImage(photoPath)
label = tk.Label(
    master = frame, 
    text = "Welcome! Please choose a button below to begin",
    font = ("Helvetica", 14),
    compound = 'top',
    image = photo,
    width = 700,
    height = 500,
    bg = "silver"
)

#------------------------------------------------------------------------------------Buttons Below------------------------------

buttonOpen = tk.Button(
    master = buttonFrameTop,
    text = "Open an image",
    width = 25,
    height = 5, 
    bg = "silver",
    command = openTheImage
)
buttonConvert = tk.Button(
    master = buttonFrameTop,
    text = "Convert Image to ...",
    width = 25,
    height = 5, 
    bg = "silver",
    command = convertTheImage
)
buttonIntensityValues = tk.Button(
    master = buttonFrameTop,
    text = "Get Grayscale Intensity Values",
    width = 25,
    height = 5, 
    bg = "silver",
    command = getBWIntensityValues
)
buttonAllIntensityValues = tk.Button(
    master = buttonFrameTop,
    text = "Download B&W Intensity Values",
    width = 25,
    height = 5, 
    bg = "silver",
    command = downloadBWIntensityValues
)
buttonEnhance = tk.Button(
    master = buttonFrameMiddle,
    text = "Enhance an Image",
    width = 25,
    height = 5, 
    bg = "silver",
    command = chooseEnhancement
)
buttonSmooth = tk.Button(
    master = buttonFrameMiddle,
    text = "Smooth an Image",
    width = 25,
    height = 5, 
    bg = "silver",
    command = chooseSmoothingOption
)
buttonSharpen = tk.Button(
    master = buttonFrameMiddle,
    text = "Sharpen an Image",
    width = 25,
    height = 5, 
    bg = "silver",
    command = chooseSharpeningOption
)
buttonMorphology = tk.Button(
    master = buttonFrameMiddle,
    text = "Alter Image Shape (Morphology)",
    width = 25,
    height = 5, 
    bg = "silver"
)
button9 = tk.Button(
    master = buttonFrameBottom,
    text = "9",
    width = 25,
    height = 5, 
    bg = "silver",
)
button10 = tk.Button(
    master = buttonFrameBottom,
    text = "10",
    width = 25,
    height = 5, 
    bg = "silver",
)
button11 = tk.Button(
    master = buttonFrameBottom,
    text = "11",
    width = 25,
    height = 5, 
    bg = "silver",
)
buttonClose = tk.Button(
    master = buttonFrameBottom,
    text = "Exit the Program",
    width = 25,
    height = 5, 
    bg = "silver",
    command = window.quit
)

#------------------------------------------------------------------------------------pack() below-------------------------------

frame.pack()
updateFrame.pack()
buttonFrameTop.pack()
buttonFrameMiddle.pack()
buttonFrameBottom.pack()

label.pack()
labelUpdates.pack()

buttonOpen.pack(side = tk.LEFT)
buttonConvert.pack(side = tk.LEFT)
buttonIntensityValues.pack(side = tk.LEFT)
buttonAllIntensityValues.pack(side = tk.RIGHT)

buttonEnhance.pack(side = tk.LEFT)
buttonSmooth.pack(side = tk.LEFT)
buttonSharpen.pack(side = tk.LEFT)
buttonMorphology.pack(side = tk.RIGHT)

button9.pack(side = tk.LEFT)
button10.pack(side = tk.LEFT)
button11.pack(side = tk.LEFT)
buttonClose.pack(side = tk.RIGHT)

#------------------------------------------------------------------------------------Open Below---------------------------------

# open the window
window.mainloop()

#----------------------------------------------------------------------------------------------------------------------------End
print("\n\n---End, thank you!---\n")
