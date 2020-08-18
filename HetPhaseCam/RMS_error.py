#using numpy arrays
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
from scipy import ndimage



#User input of which Data folder they desire
Folder_Name = input("Enter the name of the file you wish to retrieve the images from: ") #Folder_Name in some previous save_aquire (versions newer than 191216)
pha_bool = input("is the data intensity or phase data? Enter 0 for phase, 1 for intensity: ") #is this working rn??
#Find number of numpy array files within 'Folder_Name'
if pha_bool == '0':
	Data_dir = 'C:/Users/localadmin/Documents/pjflab/HetPhaseCam/Phase_Maps/'
elif pha_bool == '1':
	Data_dir = 'C:/Users/localadmin/Documents/pjflab/HetPhaseCam/Data/'
else:
	print('please enter a 0 or 1')
	sys.exit()

data_path = os.path.join(Data_dir,Folder_Name)
NUM_IMAGES_list = os.listdir(data_path) #Num(instensity images)=Num(numpy arrays), not the number of phase maps
NUM_IMAGES = len(NUM_IMAGES_list)
print("Number of intensity image numpy arrays present in " + Folder_Name + " is: ", NUM_IMAGES)

picList = []
NOVAK_PHA_PLT =[]

imgName = data_path +"/" + Folder_Name + '_0.npy'
IMG = np.load(imgName)

cord = np.where(IMG==np.amax((IMG)))
x = int(np.average(cord[1]))
y = int(np.average(cord[0]))

y1 = y - 50
y2 = y + 50
x1 = x - 50
x2 = x + 50

IMG = IMG[y1:y2,x1:x2]
picList.append(IMG)
#open image arrays
for i in range(NUM_IMAGES-1):
	i+=1
	imgName = data_path +"/" + Folder_Name + '_%d.npy' % i
	IMG = np.load(imgName)
	IMG = IMG[y1:y2,x1:x2]
	#print(numpy.max(IMG))
	picList.append(IMG)


#average carre phase map
FPP_avg = np.empty(10000)
phase_list = []
#carre_no_Mask = p.empty(388800) #maybe later. compare to mask
c = 0

if pha_bool == '1':
	print("running PSA")
	for i in range(NUM_IMAGES):
		if i % 8 == 0 and i > 0:  #MAKE SURE OVERLAP IS RIGHT... (%8 FOR NOVAK, %4 FOR 4P AND CARRE)
			c += 1
			#phase of each pixel, assuming: list of five images read in, equally centered and sized
			arr1 = np.ravel(np.array(picList[i+0],dtype='int'))
			arr2 = np.ravel(np.array(picList[i+1],dtype='int')) #converts to numpy arrays for faster operation
			arr3 = np.ravel(np.array(picList[i+2],dtype='int'))
			arr4 = np.ravel(np.array(picList[i+3],dtype='int'))
			arr5 = np.ravel(np.array(picList[i+4],dtype='int'))
			phase = np.empty(10000)

			mask = np.ones(10000,dtype=bool)

			cuts = np.where(arr1 < 10) #only masked if it is zero, dark noise value of around one or two...

			mask[cuts] = False

			p1 = arr1[mask]
			p2 = arr2[mask]
			p3 = arr3[mask]
			p4 = arr4[mask]
			p5 = arr5[mask]

			den = 2*p3-p1-p5

			A = p2-p4

			B = p1-p5

			num = np.sqrt(abs(4*A**2-B**2))

			pm = np.sign(A)

			pha = np.arctan2(pm*num,den)

			phase[~mask] = 0
			phase[mask] = pha

			phase_list.append(phase)
			FPP_avg += phase
	FPP_avg = FPP_avg / c

else:
	sum = np.zeros(10000)
	for i in range(len(picList)):
		phase_list.append(np.ravel(np.array(picList[i],dtype='int')))
		sum += phase_list[i]
	FPP_avg = sum/len(phase_list)




#RMS error
pha_error = np.zeros(10000)
num = np.zeros(10000)
for i in range(len(phase_list)):
	num += (FPP_avg - phase_list[i])**2
pha_error = np.sqrt(num/len(phase_list))

def error(phase_map):
	mean = np.average(phase_map)
	num = 0
	for i in range(10000):
		num += (mean - phase_map[i])**2
	error = np.sqrt(num/10000)
	return error

error_avg = error(FPP_avg)
error_single = error(phase_list[0])
mean_avg = np.mean(FPP_avg)
mean_single = np.mean(phase_list[0])
mean_error = np.mean(pha_error)


print('error of averaged phase maps:',error_avg,'error of single PM:',error_single)
print("mean error from error per pixel:",mean_error)
print('mean of averaged phase maps:',mean_avg,'mean of single PM:',mean_single)

pha_error = np.reshape(pha_error,(100,100))
FPP_avg = np.reshape(FPP_avg,(100,100))

plt.ion()
plt.imshow(pha_error, cmap = 'jet')
cbar = plt.colorbar()#
cbar.set_label("RMS phase error (rad)")#
plt.xlabel("Pixels(x)")
plt.ylabel("Pixels(y)")
plt.title("RMS error " + str(Folder_Name))
#plt.xlim([200,500])
#plt.ylim([400,125])
plt.pause(0.00001)

today=date.today()
d1 = today.strftime("%Y%m%d")

phase_error_name = 'C:/Users/localadmin/Documents/pjflab/HetPhaseCam/Phase_Maps/' + Folder_Name + '_' + 'RMSerror_max.png'
plt.savefig(phase_error_name)
plt.show()
plt.clf()

print("phase map saved at:", phase_error_name)

name = 'C:/Users/localadmin/Documents/pjflab/HetPhaseCam/Phase_Maps/' + Folder_Name + '_' + 'RMSerror_max'
np.save(name, pha_error)
