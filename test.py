import matplotlib.pyplot as plt
import numpy as np
import cv2

x = np.linspace(0, 2 * np.pi, 400)
y = np.sin(x ** 2)

img = cv2.imread("Images\\test.png")

# fig, axs = plt.subplots(2, 3)
# axs[0, 0].plot(x, y)
# axs[0, 0].set_title('Axis [0, 0]')
# axs[0, 1].plot(x, y, 'tab:orange')
# axs[0, 1].set_title('Axis [0, 1]')
# axs[0, 2].plot(x, y, 'tab:gray')
# axs[1, 0].plot(x, -y, 'tab:green')
# axs[1, 0].set_title('Axis [1, 0]')
# axs[1, 1].plot(x, -y, 'tab:red')
# axs[1, 1].set_title('Axis [1, 1]')

fig = plt.figure(figsize=(10, 7))

rows = 2
columns = 2

fig.add_subplot(rows, columns, 1)
plt.imshow(img)
plt.axis('off') #Removes axes
plt.title("1")
fig.add_subplot(rows, columns, 2)
plt.imshow(img)
plt.axis('off')
plt.title("2")
fig.add_subplot(rows, columns, 3)
plt.imshow(img)
plt.axis('off')
plt.title("3")
fig.add_subplot(rows, columns, 4)
plt.imshow(img)
plt.axis('off')
plt.title("4")
# fig.add_subplot(rows, columns, 4)

plt.show()