#using numpy arrays
#Will compute RMS error over single PM, average PM, and MPP, RMS error per pixel, SNR^2 per pixel,
#average SNR^2, contrast per pixel, contrast over array

import os
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
from PIL import Image
from numpy import array, empty, ravel, where, ones, reshape, arctan2
from matplotlib.pyplot import plot, draw, show, ion
from datetime import date
import sys
import scipy
from scipy import fft

picList = []
phaseList = []
error_per_pix = np.array((540,720))
SNR_per_pix =np.array((540,720))
con_map_1 = np.empty(388800)
con_map_2 = np.empty(388800)
dif_con_map = np.array((540,720))

PM_avg = np.empty(388800)
MPP = np.empty(388800) #Mega phase plot, un/re averaged

#User input of which Data folder they desire
Folder_Name = input("Enter the name of the file you wish to retrieve the images from: ") #Folder_Name in some previous save_aquire (versions newer than 191216)

#Find number of numpy array files within 'Folder_Name'
Data_dir = 'C:/Users/physics-svc-fulda/Desktop/HetPhaseCam/Data'
data_path = os.path.join(Data_dir,Folder_Name)
NUM_IMAGES_list = os.listdir(data_path) #Num(instensity images)=Num(numpy arrays), not the number of phase maps
NUM_IMAGES = len(NUM_IMAGES_list)
print("Number of intensity image numpy arrays present in " + Folder_Name + " is: ", NUM_IMAGES)

folder ='C:/Users/physics-svc-fulda/Desktop/HetPhaseCam/Phase_Maps/'
folder_path = os.path.join(folder,Folder_Name)
os.mkdir(folder_path)

#open image arrays
for i in range(NUM_IMAGES):
	#imgName = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/Data/' + File_Name + '-%d.npy' % i
	imgName = data_path +"/" + Folder_Name + '_%d.npy' % i
	IMG = np.load(imgName)
	picList.append(IMG)

#early saturation check
#for i in range(4):
#	if np.max(picList[i]) > 65510: #this value for 12 bit
#		sys.exit("An image is saturated. Aborting")


def PullPixelData(rowi, coli, n_beatnote):
	#pulls out value at pixel [rowi][coli] of image i
	pixel_data = [i[rowi][coli] for i in n_beatnote]
	return pixel_data

def SNR(t,pixel_data):
	N = len(t)
	fs = 40
	ft = 2*scipy.fft.fft(pixel_data)/N
	h = ft[0:N//2]
	signal = np.abs(h[100])
	#print(signal)
	noise = np.sum(np.abs(h[1:99])) + np.sum(np.abs(h[101:200]))
	#print(noise)
	SNR = signal/noise

	return SNR

def time_per_pixel(images): #change to just the recorded images
	SNRs = []
	t = np.linspace(0.025,10,400)
	#Change this, we dont need to make any pixels
	for i in range(540): #still want to be on the center of the camera (what if beams arent aligned??)
		for j in range(720):
			pixel_data = PullPixelData(rowi=i, coli=j, n_beatnote=images)
			SNRi = SNR(t=t, pixel_data=pixel_data)
			SNRs.append(SNRi)

	Avg_SNR2 = (sum(SNRs)/len(SNRs))**2
	SNR_map = np.reshape(np.array(SNRs),(540,720))

	return Avg_SNR2, SNR_map

AVG_SNR2, SNR_per_pix = time_per_pixel(picList)
plt.ion()
plt.imshow(SNR_per_pix)
cbar = plt.colorbar()#
cbar.set_label("SNR^2")#
plt.xlabel("Pixels(x)")
plt.ylabel("Pixels(y)")
plt.title("SNR^2 per pixel. Average SNR^2: "+str(AVG_SNR2))
plt.xlim([0,720])
plt.ylim([540,0])
plt.pause(0.00001)
name = folder_path + "/" + Folder_Name + '_SNR_per_pixel.png'
plt.savefig(name)
plt.show()
plt.clf()

def contrast (arr1, arr2, arr3, arr4): #this is from Guzman paper. we are using novak insteasd of 4point, however these contrast values should still be valid
	Con_map = np.empty(388800)
	C = 0
	a = 0
	b = 0
	d = 0
	for i in range (388800):
		A_i = arr1[i] - arr3[i]
		B_i = arr4[i] - arr2[i]
		D_i = arr1[i] + arr3[i] + arr4[i] + arr2[i]
		Con_map[i] = 2*np.sqrt((A_i**2+B_i**2)/D_i)
		a += A_i
		b += B_i
		d += D_i
	C = 2 * np.sqrt(a**2 + b**2) / d
	return C,Con_map

#converting to phase maps
c = 0
for i in range(NUM_IMAGES):
	if i % 4 == 0 and i > 4 and i < NUM_IMAGES - 4:  #MAKE SURE OVERLAP IS RIGHT... (%8 FOR NOVAK, %4 FOR 4P AND CARRE)
		c += 1
		#phase of each pixel, assuming: list of five images read in, equally centered and sized
		p1 = np.ravel(picList[i-4]) #add i to take appropriate image for each phase plot
		p2 = np.ravel(picList[i-3]) #converts to numpy arrays for faster operation
		p3 = np.ravel(picList[i-2])
		p4 = np.ravel(picList[i-1])
		p5 = np.ravel(picList[i])
		phase=np.empty(388800)

		#Novak PSA arithmetic
		den = 2*p3-p1-p5
		A = p2-p4
		B = p1-p5
		num = np.sqrt(abs(4*A**2-B**2))
		pm = np.sign(A)
		phase = np.arctan2(pm*num,den)

		#adding 1D PM values to average PM
		PM_avg += phase
		phaseList.append(phase)

		#contrast of first phase map\
		if c == 1:
			C1, con_map_1 = contrast(p1,p2,p3,p4)
			con_map_1 = np.reshape(con_map_1,(540,720))
			plt.ion()
			plt.imshow(con_map_1)
			cbar = plt.colorbar()#
			cbar.set_label("Contrast")#
			plt.xlabel("Pixels(x)")
			plt.ylabel("Pixels(y)")
			plt.title("Contrast per pixel. Average contrast: "+str(C1))
			plt.xlim([0,720])
			plt.ylim([540,0])
			plt.pause(0.00001)
			name = folder_path + "/" + Folder_Name + '_Contrast_per_pixel.png'
			plt.savefig(name)
			plt.show()
			plt.clf()
		if c == 90:
			C2, con_map_2 = contrast(p1,p2,p3,p4)
			con_map_2 = np.reshape(con_map_2,(540,720))
			dif_con_map = con_map_1 - con_map_2
			DC = C1-C2
			plt.ion()
			plt.imshow(dif_con_map)
			cbar = plt.colorbar()#
			cbar.set_label("Change in contrast")#
			plt.xlabel("Pixels(x)")
			plt.ylabel("Pixels(y)")
			plt.title("CHange in contrast per pixel. Change of average contrast: "+str(DC))
			plt.xlim([0,720])
			plt.ylim([540,0])
			plt.pause(0.00001)
			name = folder_path + "/" + Folder_Name + '_change_contrast_per_pixel.png'
			plt.savefig(name)
			plt.show()
			plt.clf()


			#mask to avoid trailing unwrapping,
			#hoping this isn't needed
			#arr1 = numpy.ravel(numpy.array(picList[i],dtype='int'))	#would it be better to use the first image of the whole set or of the PM set
			#mask = numpy.ones(388800,dtype=bool)
			#cuts = numpy.where(arr1 < 300)
			#mask[cuts] = False

			pha_un = np.zeros(388800)
			phase=np.ravel(phase)

			for i in range(540):
				for j in range(719):
					k = 0
					a = phase[720*i+j+1]
					b = phase[i*720+j]
					if (a + np.pi*1.5 < b): #and (mask[720*i+j+1+k] == False): #what happens if only one of a or b is unmasked (both are, phase is not boolean)
						for k in range(719-j):
							phase[720*i+j+1+k] += 2*np.pi
					elif (a > 1.5*np.pi + b): #and (mask[720*i+j+1+k] == False):
						for k in range (719-j):
							phase[720*i+j+1+k] -= 2*np.pi
			#pha_un[~mask] = 0
			#pha_un[mask] = phase[mask]
			pha_un = phase

			#subtract out mean of unwrapped phase map.
			x = np.mean(pha_un)
			pha_un = pha_un - x

			#rewrap
			pha_re = np.empty(388800)
			pha_re = np.ravel(pha_un) #turns back into 1D array, rewrapping can be done on pixel by pixel basis
			for i in range(388800):
				while pha_re[i] < -np.pi:
					pha_re[i] += 2*np.pi
				while pha_re[i] > np.pi:
					pha_re[i] -= 2*np.pi

			MPP += pha_re

#average of all phase maps
PM_avg = PM_avg / c
PM_avg = np.reshape(PM_avg,(540,720))


#Mega Phase Plot. average of un/re phase plots
MPP = MPP / c
MPP = np.reshape(MPP,(540,720))

STD_PM=np.std(PM_avg) #I do not know how to include this in the data/images. I will record this in my notebook
print('STD of average phase map: ' + str(STD_PM))

STD_MPP=np.std(MPP) #I do not know how to include this in the data/images. I will record this in my notebook
print('STD of Mega Phase Plot: ' + str(STD_MPP))

#showing and saving final PM
plt.ion()
plt.imshow(PM_avg, cmap = 'jet')
cbar = plt.colorbar()#
plt.clim(vmin=-np.pi*1,vmax=np.pi*1)#
cbar.set_label("Phase Shift (rad)")#
plt.title("Avergae Phase. Standard Deviation: "+str(STD_PM))
plt.xlabel("Pixels(x)")
plt.ylabel("Pixels(y)")
plt.xlim([0,720])
plt.ylim([540,0])
plt.pause(0.00001)
name = folder_path + "/" + Folder_Name + '_PM_avg.png'
plt.savefig(name)
plt.show()
plt.clf()

name = folder_path + "/" + Folder_Name + '_PM_avg'
np.save(name, PM_avg)


#Saving MPP
plt.ion()
plt.imshow(MPP, cmap = 'jet')
cbar = plt.colorbar()#
plt.clim(vmin=-np.pi*1,vmax=np.pi*1)#
cbar.set_label("Phase Shift (rad)")#
plt.title("Mega Phase Plot. Standard Deviation: "+str(STD_MPP))
plt.xlabel("Pixels(x)")
plt.ylabel("Pixels(y)")
plt.xlim([0,720])
plt.ylim([540,0])
plt.pause(0.00001)
name = folder_path + "/" + Folder_Name + '_MPP.png'
plt.savefig(name)
plt.show()
plt.clf()

name = folder_path + "/" + Folder_Name + '_MPP'
np.save(name, MPP)

#RMS error
PM_avg=np.ravel(PM_avg)
num = np.empty(388800)
for i in range(len(phaseList)):
	num += (PM_avg - phaseList[i])**2
error_per_pix = np.sqrt(num/len(phaseList))
error_per_pix=np.reshape(error_per_pix,(540,720))
PM_avg=np.reshape(PM_avg,(540,720))


def error(phase_map):
	mean = np.average(np.ravel(phase_map))
	num = 0
	for i in range(len(phase_map)):
		num += (mean - phase_map[i])**2
	error = np.sqrt(num/388800)
	return error

error_avg = error(PM_avg)
error_MPP = error(MPP)
error_single = error(phaseList[0])
mean_avg = np.mean(PM_avg)
mean_single = np.mean(phaseList[0])
mean_error = np.mean(error_per_pix)


print('error of averaged phase maps:'+str(STD_PM)+'error of single PM:'+str(error_single))
print('error of Mega Phase Plot:'+str(STD_MPP))
print("mean error from error per pixel:"+str(mean_error))
print('mean of averaged phase maps:'+str(mean_avg)+'mean of single PM:'+str(mean_single))
print('average SNR over array:'+str(AVG_SNR2))

plt.ion()
plt.imshow(error_per_pix, cmap = 'jet')
cbar = plt.colorbar()#
cbar.set_label("RMS phase error (rad)")#
plt.title('Error per pixel. Average error:'+str(mean_avg))
plt.xlabel("Pixels(x)")
plt.ylabel("Pixels(y)")
plt.title("RMS error " + str(Folder_Name))
#plt.xlim([200,500])
#plt.ylim([400,125])
plt.pause(0.00001)

today=date.today()
d1 = today.strftime("%Y%m%d")
phase_error_name= folder_path + "/" + Folder_Name + '_RMSerror_max.png'
plt.savefig(phase_error_name)
plt.show()
plt.clf()

print("phase map saved at:"+str(phase_error_name))

name= folder_path + "/" + Folder_Name + '_RMSerror_max'
np.save(name, error_per_pix)
