#using numpy arrays\
import os
import PySpin
import numpy as np
import matplotlib.pyplot as plt
import time
from PIL import Image
from numpy import array, empty, ravel, where, ones, reshape, arctan2
from matplotlib.pyplot import plot, draw, show, ion
from matplotlib import animation
from IPython.display import HTML #can't use this...


#User input of which Data folder they desire
Folder_Name = input("Enter the name of the file you wish to retrieve the images from: ") #Folder_Name in some previous save_aquire (versions newer than 191216)

#adding automation
#Find number of numpy array files within 'Folder_Name'
Data_dir = 'C:/Users/localadmin/Documents/pjflab/HetPhaseCam/Data/'
data_path = os.path.join(Data_dir,Folder_Name)
NUM_IMAGES_list = os.listdir(data_path) #Num(instensity images)=Num(numpy arrays), not the number of phase maps
NUM_IMAGES = len(NUM_IMAGES_list)
print("Number of intensity image numpy arrays present in " + Folder_Name + " is: ", NUM_IMAGES)


picList = []

#open image arrays
for i in range(NUM_IMAGES):
	#imgName = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/Data/' + File_Name + '-%d.npy' % i
	imgName = data_path +"/" + Folder_Name + '_%d.npy' % i
	IMG = np.load(imgName)
	picList.append(IMG)

cmap='gray'
interval=25
cbar_lim=None

fig = plt.gcf()
im = plt.imshow(np.real(picList[0]), cmap=cmap)
fig.colorbar(im)

if cbar_lim != None:
    plt.clim(vmin=0,vmax=cbar_lim)

plt.close()

def animate(i):
    im.set_data(np.real(picList[i]))
    return im,

anim = animation.FuncAnimation(fig, animate, frames=range(0,len(picList)), interval=interval, repeat=True)
display(HTML(anim.to_jshtml()))
