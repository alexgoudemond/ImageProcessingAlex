from tkinter import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
  
# plot function is created for 
# plotting the graph in 
# tkinter window
def plot():
    fig = Figure(figsize = (5, 5), dpi = 100)
    # list of squares
    y = [i**2 for i in range(101)]
  
    # adding the subplot
    plot1 = fig.add_subplot(111)
    # plotting the graph
    plot1.plot(y)

    canvas = FigureCanvasTkAgg(fig, master = window)  
    toolbar = NavigationToolbar2Tk(canvas,window)
    toolbar.update()
  
    canvas.draw()
    canvas.get_tk_widget().pack()
  
# the main Tkinter window
window = Tk()
window.title('Plotting in Tkinter')
window.geometry("500x500")
  
# button that displays the plot
plot_button = Button(master = window, 
                     command = plot,
                     height = 2, 
                     width = 10,
                     text = "Plot")
  
plot_button.pack()
  
# run the gui
window.mainloop()
