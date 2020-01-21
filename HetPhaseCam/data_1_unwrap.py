#using numpy arrays\
import os
import PySpin
import numpy
import matplotlib.pyplot as plt
import time
from PIL import Image
from numpy import array, empty, ravel, where, ones, reshape, arctan2
from matplotlib.pyplot import plot, draw, show, ion

#User input of which Data folder they desire
Folder_Name = input("Enter the name of the file you wish to retrieve the images from: ") #Folder_Name in some previous save_aquire (versions newer than 191216)

#adding automation
#Find number of numpy array files within 'Folder_Name'
Data_dir = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/Data/'
data_path = os.path.join(Data_dir,Folder_Name)
NUM_IMAGES_list = os.listdir(data_path) #Num(instensity images)=Num(numpy arrays), not the number of phase maps
NUM_IMAGES = len(NUM_IMAGES_list)
print("Number of intensity image numpy arrays present in " + Folder_Name + " is: ", NUM_IMAGES)
#File_Name = input("Enter the name of the file you wish to retrieve the images from: ") #File_Name in save_aquire 
#NUM_IMAGES = int(input("Please enter the number of images in the file: "))
 
# Unwrap single phase map, subtract out the mean, rewrap, average all single rewraped phase maps 
picList = []
NOVAK_PHA_PLT =[]	

#open image arrays 
for i in range(NUM_IMAGES):
	#imgName = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/Data/' + File_Name + '-%d.npy' % i
	imgName = data_path +"/" + Folder_Name + '_%d.npy' % i
	IMG = numpy.load(imgName)
	picList.append(IMG)
	
		
#average PM 
PM_avg = numpy.empty(388800) 
MPP = numpy.empty(388800) #Mega phase plot, un/re averaged

#counter for averaging individual phase plots
c = 0

def contrast (arr1, arr2, arr3, arr4,mask): #this is from Guzman paper. we are using novak insteasd of 4point, however these contrast values should still be valid
	C = 0
	a = 0
	b = 0 
	d = 0
	for i in range (388800):
		if (mask[i] == False):
			a += arr1[i] - arr3[i]
			b += arr4[i] - arr2[i]
			d += arr1[i] + arr3[i] + arr4[i] + arr2[i]
	C = 2 * numpy.sqrt(a**2 + b**2) / d	
	return C
	
for i in range(NUM_IMAGES):	
	if i % 8 == 0 and i > 0 and i < NUM_IMAGES - 4:  #MAKE SURE OVERLAP IS RIGHT... (%8 FOR NOVAK, %4 FOR 4P AND CARRE)
		c += 1
		#phase of each pixel, assuming: list of five images read in, equally centered and sized
		arr1 = numpy.ravel(numpy.array(picList[0+i],dtype='int')) #add i to take appropriate image for each phase plot
		arr2 = numpy.ravel(numpy.array(picList[1+i],dtype='int')) #converts to numpy arrays for faster operation
		arr3 = numpy.ravel(numpy.array(picList[2+i],dtype='int'))
		arr4 = numpy.ravel(numpy.array(picList[3+i],dtype='int'))
		arr5 = numpy.ravel(numpy.array(picList[4+i],dtype='int'))
		phase = numpy.empty(388800)

		mask = numpy.ones(388800,dtype=bool)

		cuts = numpy.where(arr1 < 15)

		mask[cuts] = False

		p1 = arr1[mask]
		p2 = arr2[mask]
		p3 = arr3[mask]
		p4 = arr4[mask]
		p5 = arr5[mask]	
		
		#Novak PSA arithmetic
		den = 2*p3-p1-p5
		A = p2-p4
		B = p1-p5
		num = numpy.sqrt(abs(4*A**2-B**2))
		pm = numpy.sign(A)
		pha = numpy.arctan2(pm*num,den)

		phase[~mask] = 0
		phase[mask] = pha #phase is 1D phase array (negative pi to pi)
		
		#adding 1D PM values to average PM 
		PM_avg += phase
		
		#contrast of first phase map\
		if c == 1:
			C = contrast(arr1,arr2,arr3,arr4,mask) 
			print ('Contrast of first PM: ' + str(C))
			
		#saving single phase map. good reference 
		if c == 1:
			STD=numpy.std(phase) #I do not know how to include this in the data/images. I will record this in my notebook
			print("STD of single phase map: " + str(STD))
			phase = numpy.reshape(phase,(540,720)) # reshape to save single PM
			plt.ion()						
			plt.imshow(phase, cmap = 'jet')
			cbar = plt.colorbar()#
			plt.clim(vmin=-numpy.pi*1,vmax=numpy.pi*1)#multiply by five? all values are between +- pi
			cbar.set_label("Phase Shift (rad)")#
			plt.xlabel("Pixels(x)")
			plt.ylabel("Pixels(y)")
			plt.xlim([0,720])
			plt.ylim([540,0])
			plt.pause(0.00001)
			name = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/phase_maps/' + Folder_Name + '_single_PM.png' #it's an average of ten so not mega
			plt.savefig(name)
			plt.show()
			plt.clf()
			phase = numpy.ravel(phase) #must re-ravel to 1D array 
			

		#unwrap. 1D array at this point 
		if c == 1: #if is only to test and see how it is going. move unwrapping put. keep save in? 
			#new array for storing unwrapped bits
			pha_un = numpy.zeros(388800)
			
			#mask to avoid trailing unwrapping 
			arr1 = numpy.ravel(numpy.array(picList[i],dtype='int'))	#would it be better to use the first image of the whole set or of the PM set	
			mask = numpy.ones(388800,dtype=bool)
			cuts = numpy.where(arr1 < 15)
			mask[cuts] = False
			
			#works. could probably be better? really slow. 
			for i in range(540):
				for j in range(719):
					k = 0
					a = phase[720*i+j+1]
					b = phase[i*720+j]
					if (a + numpy.pi*1.5 < b) and (mask[720*i+j+1+k] == False): #what happens if only one of a or b is unmasked (both are, phase is not boolean)
						for k in range(719-j):
							phase[720*i+j+1+k] += 2*numpy.pi
					elif (a > 1.5*numpy.pi + b) and (mask[720*i+j+1+k] == False):
						for k in range (719-j):
							phase[720*i+j+1+k] -= 2*numpy.pi
			pha_un[~mask] = 0
			pha_un[mask] = phase[mask]
			
			
		#view single unwrapped phase map 
		if c == 1:
			pha_un = numpy.reshape(pha_un,(540,720)) # reshape to save single unwrapped PM
			plt.ion()						
			plt.imshow(pha_un, cmap = 'jet')
			cbar = plt.colorbar()#
			plt.clim(vmin=-numpy.pi*3,vmax=numpy.pi*3)#
			cbar.set_label("Phase Shift (rad)")#
			plt.xlabel("Pixels(x)")
			plt.ylabel("Pixels(y)")
			plt.xlim([0,720])
			plt.ylim([540,0])
			plt.pause(0.00001)
			name = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/phase_maps/' + Folder_Name + '_single_unwrapped_PM_mask.png' 
			plt.savefig(name)
			plt.show()
			plt.clf()
			pha_un = numpy.ravel(pha_un)
				
		#subtract out mean of unwrapped phase map. 
		x = numpy.mean(pha_un)
		pha_un = pha_un - x
		
		#rewrap
		pha_re = numpy.empty(388800)
		pha_re = numpy.ravel(pha_un) #turns back into 1D array, rewrapping can be done on pixel by pixel basis
		for i in range(pha_un.size):
			while pha_re[i] < -numpy.pi:
				pha_re[i] += 2*numpy.pi
			while pha_re[i] > numpy.pi:
				pha_re[i] -= 2*numpy.pi
		
		#saving one un/re phase map 
		if c == 1:
			pha_re = numpy.reshape(pha_re,(540,720)) # reshape to save single re wrapped phase map 
			plt.ion()						
			plt.imshow(pha_re, cmap = 'jet')
			cbar = plt.colorbar()#
			plt.clim(vmin=-numpy.pi*1,vmax=numpy.pi*1)#should fit in single range
			cbar.set_label("Phase Shift (rad)")#
			plt.xlabel("Pixels(x)")
			plt.ylabel("Pixels(y)")
			plt.xlim([0,720])
			plt.ylim([540,0])
			plt.pause(0.00001)
			name = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/phase_maps/' + Folder_Name + '_single_rewrapped_PM.png' 
			plt.savefig(name)
			plt.show()
			plt.clf()
			pha_re = numpy.ravel(pha_re)
			STD=numpy.std(pha_re) #I do not know how to include this in the data/images. I will record this in my notebook
			print('STD of single un/re phase plot: ' + str(STD))
		
		#add manipulated phase map to MPP
		MPP += pha_re

#average of all phase maps 	
PM_avg = PM_avg / c 
PM_avg = numpy.reshape(PM_avg,(540,720))

#Mega Phase Plot. average of un/re phase plots
MPP = MPP / c 
MPP = numpy.reshape(MPP,(540,720))


#what else would be good to include
STD=numpy.std(PM_avg) #I do not know how to include this in the data/images. I will record this in my notebook
print('STD of average phase map: ' + str(STD))

STD=numpy.std(MPP) #I do not know how to include this in the data/images. I will record this in my notebook
print('STD of Mega Phase Plot: ' + str(STD))

#showing and saving final PM
plt.ion()						
plt.imshow(PM_avg, cmap = 'jet')
cbar = plt.colorbar()#
plt.clim(vmin=-numpy.pi*1,vmax=numpy.pi*1)#
cbar.set_label("Phase Shift (rad)")#
plt.xlabel("Pixels(x)")
plt.ylabel("Pixels(y)")
plt.xlim([0,720])
plt.ylim([540,0])
plt.pause(0.00001)
name = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/phase_maps/' + Folder_Name + '_PM_avg.png' 
plt.savefig(name)
plt.show()
plt.clf()

#Saving MPP
plt.ion()						
plt.imshow(MPP, cmap = 'jet')
cbar = plt.colorbar()#
plt.clim(vmin=-numpy.pi*1,vmax=numpy.pi*1)#
cbar.set_label("Phase Shift (rad)")#
plt.xlabel("Pixels(x)")
plt.ylabel("Pixels(y)")
plt.xlim([0,720])
plt.ylim([540,0])
plt.pause(0.00001)
name = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/phase_maps/' + Folder_Name + '_MPP.png' 
plt.savefig(name)
plt.show()
plt.clf()