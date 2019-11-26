#using weird numpy arrays\
import os
import PySpin
import numpy
import matplotlib.pyplot as plt
import time
from PIL import Image
from numpy import array, empty, ravel, where, ones, reshape, arctan2
from matplotlib.pyplot import plot, draw, show, ion

#read in some number of images 
File_Name = input("Enter the name of the file you wish to retrieve the images from: ") #File_Name in save_aquire 
NUM_IMAGES = int(input("Please enter the number of images in the file: "))

picList = []
NOVAK_PHA_PLT =[]	

#open image arrays 
for i in range(NUM_IMAGES):
	imgName = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/Data/' + File_Name + '-%d.npy' % i
	IMG = numpy.load(imgName)
	picList.append(IMG)
	
		
#average carre phase map
carre_avg = numpy.empty(388800)
carre_no_Mask = numpy.empty(388800) #maybe later. compare to mask
c = 0

for i in range(NUM_IMAGES):	
	if i % 4 == 0 and i > 0:
		c += 1
		arr1 = numpy.ravel(numpy.array(picList[i],dtype='int'))
		arr2 = numpy.ravel(numpy.array(picList[i-1],dtype='int')) #converts to numpy arrays for faster operation
		arr3 = numpy.ravel(numpy.array(picList[i-2],dtype='int'))
		arr4 = numpy.ravel(numpy.array(picList[i-3],dtype='int'))

		phase = numpy.empty(388800)

		mask = numpy.ones(388800,dtype=bool)
		 
		cuts = numpy.where(arr1 < 15)

		mask[cuts] = False

		p1 = arr1#[mask]
		p2 = arr2#[mask]
		p3 = arr3#[mask]
		p4 = arr4#[mask]
				
		B = p1-p4
		A = p2-p3 
		num = (A+B) * (3*A-B)
		num = numpy.sqrt(abs(num))
		pm = numpy.sign(A)
		den = p2 + p3 - p1 - p4 
		pha = numpy.arctan2(pm*num,den)
		#phase[~mask] = 0
		#phase[mask] = pha
		
		carre_avg += pha#se

	
carre_avg = carre_avg / c
carre_avg = numpy.reshape(carre_avg,(540,720))

plt.ion()						
plt.imshow(carre_avg, cmap = 'jet')
cbar = plt.colorbar()#
plt.clim(vmin=-numpy.pi,vmax=numpy.pi)#
cbar.set_label("Phase Shift (rad)")#
plt.xlabel("Pixels(x)")
plt.ylabel("Pixels(y)")
#plt.xlim([300,500])
#plt.ylim([200,400])
plt.pause(0.00001)
name = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/' + File_Name + '_carre_no_Mask.png' #it's an average of ten so not mega
plt.savefig(name)
plt.show()
plt.clf()