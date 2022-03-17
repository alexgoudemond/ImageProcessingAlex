"""
Author: Alexander Goudemond

Program name: gui_example.py

Goal: Create a GUI

Notes:
    Tkinter Widgets:
        Label
        Button
        Entry       (single line of text)
        Text 
        Frame
"""
#----------------------------------------------------------------------------------------------------------------Packages Below
import tkinter as tk
from tkinter import filedialog

#----------------------------------------------------------------------------------------------------------------Functions Below
def open():
    window.filename = filedialog.askopenfilename(initialdir="Images", title="Select an Image to Open", 
                                                    filetypes=(
                                                        ("All Files", "*.*"), ("jpg Files", "*.jpg"), 
                                                        ("png files", "*.png"), ("gif files", "*.gif"),
                                                        ("tiff files", "*.tiff"), ("bmp files", "*.bmp"),
                                                        ("raw files", "*.raw")
                                                    )
    )

#----------------------------------------------------------------------------------------------------------------Program Below
print("\n---Program Starting---\n\n")

# create a window
window = tk.Tk()
window.title("COMP702 Image Processing")

frame = tk.Frame()

# foreground == fg, background == bg
label = tk.Label(
    master = frame,
    text = "Hi There!",
    foreground = "white",
    background = "black",
    width = 100,
    height = 30
)

buttonOpen = tk.Button(
    master = frame,
    text = "Open an image",
    width = 25,
    height = 5, 
    bg = "silver",
    command = open
)

buttonClose = tk.Button(
    master = frame,
    text = "Exit the Program",
    width = 25,
    height = 5, 
    bg = "silver",
    command = window.quit
)

# place into the window
frame.pack()
label.pack()
buttonOpen.pack(side = tk.LEFT)
buttonClose.pack(side = tk.RIGHT)

# open the window - do at end
window.mainloop()

print("\n\n---End, thank you!---\n")