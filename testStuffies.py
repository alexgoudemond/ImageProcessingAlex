'''
The goal here is to get a GUI with stuff on left and right
'''
from tkinter import *
from tkinter import ttk, Button
import time
from turtle import left, right

# root = Tk()
# # root.state("zoomed")  #to make it full screen

# root.title("Vehicle Window Fitting - Management System")
# root.configure(bg="grey80")

# topFrame = Frame(root, width=1350, height=50)  # Added "container" Frame.
# topFrame.pack(side=TOP, fill=X, expand=1, anchor=N)

# titleLabel = Label(topFrame, font=('arial', 12, 'bold'),
#                    text="Vehicle Window Fitting - Management System",
#                    bd=5, anchor=W)
# titleLabel.pack(side=LEFT)

# clockFrame = Frame(topFrame, width=100, height=50, bd=4, relief="ridge")
# clockFrame.pack(side=RIGHT)
# clockLabel = Label(clockFrame, font=('arial', 12, 'bold'), bd=5, anchor=E)
# clockLabel.pack()

# Bottom = Frame(root, width=1350, height=50, bd=4, relief="ridge")
# Bottom.pack(side=BOTTOM, fill=X, expand=1, anchor=S)

# def tick(curtime=''):  #acts as a clock, changing the label when the time goes up
#     newtime = time.strftime('%H:%M:%S')
#     if newtime != curtime:
#         curtime = newtime
#         clockLabel.config(text=curtime)
#     clockLabel.after(200, tick, curtime)

# tick()  #start clock
# root.mainloop()

root = Tk()
root.title("main window")

b1 = Button(root, text='b1', width=30)
l1 = Label(root, text="DDD", width=30)
b2 = Button(root, text='b2', width=30)
b1.grid(column=0, row=0)
l1.grid(column=1, row=0)   # grid dynamically divides the space in a grid
b2.grid(column=2, row=0)

root.mainloop()