import numpy
import matplotlib.pyplot as plt

def PixelPoints (picList, NUM): #picList will be unraveled numpy array of intensity values

	#create certain pixels to iterate through
	pix1 = 720*260+260 #pixel in middle, will add more later, maybe randomize?
	y=[0]*400
	x=[0]*400

	#do we want average or time series of the pixel value?
	for i in range(NUM):
		arr = numpy.ravel(numpy.array(picList[i],dtype='int'))
		y[i]=arr[pix1] #proper way to say pixel pix1 of image i?
		x[i]=i

	#creating plot of pixels value
	plt.plot(x,y)
	plt.xlabel('Image number')
	plt.ylabel('Pixel Value')
	plt.title('Dark Measurment Test')
	name = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/noise_stuff/quicktest.png'
	plt.savefig(name)
	plt.show()
	
	#average value
	#average all pixels together?
	pix1AVG = numpy.mean(y)
	
	
	return (pix1AVG)

picList = []
#open image arrays
for i in range(400):
	imgName = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/Data/dark_test_1/dark_test_1' + '_%d.npy' % i
	IMG = numpy.load(imgName)
	picList.append(IMG)

x = PixelPoints(picList, 400)
print(x)