#making a plot of the noise at various Exposure and Gain settings
#

#make sure proper things have been imported
import os
import PySpin
import numpy
import matplotlib.pyplot as plt
import time
from PIL import Image
from numpy import array, empty, ravel, where, ones, reshape, arctan2
from matplotlib.pyplot import plot, draw, show, ion

#2D arrray for exposure,gain,and 'dark noise measurement'
DarkNoise = [0][0] #how big? which axis is which?  


NUM_IMAGES = 100 #100 images for each exposure/gain configuration

#not sure where these need to go
#method for checking the pixel value of images
def PixelPoints (picList): #picList will be unraveled numpy array of intensity values
    #what do we need to save? Dont need to show each plot
    
	#create certain pixels to iterate through
	pix1 = 720*270+360 #pixel in middle, will add more later, maybe randomize? 
	y=[0]*100
	x=[0]*100

	#do we want average or time series of the pixel value? 
	for i in range(NUM_IMAGES): 
		arr=numpy.ravel(numpy.array(picList[i]))
		y[i]=arr[pix1] #proper way to say pixel pix1 of image i? 
		x[i]=i

<<<<<<< HEAD
	#maybe dont do this with all of these? 
	#compare various pixels for any settings configuration. 
=======
>>>>>>> 3d7ae6a3243b3c859c35ff348e5fa6c42da1962e
	#creating plot of pixels value 
	plt.plot(x,y)
	plt.xlabel('Image number')
	plt.ylabel('Pixel Value')
	plt.title('Dark Measurment Test')
	plt.show()	

	#average value
	#average all pixels together? 
	pix1AVG = numpy.mean(x)

def configure_exposure(cam, M): #set M to proper us value
    """
     This function configures a custom exposure time. Automatic exposure is turned
     off in order to allow for the customization, and then the custom setting is
     applied.

     :param cam: Camera to configure exposure for.
     :type cam: CameraPtr
     :return: True if successful, False otherwise.
     :rtype: bool
    """

    print '*** CONFIGURING EXPOSURE ***\n'

    try:
        result = True

        # Turn off automatic exposure mode
        #
        # *** NOTES ***
        # Automatic exposure prevents the manual configuration of exposure
        # times and needs to be turned off for this example. Enumerations
        # representing entry nodes have been added to QuickSpin. This allows
        # for the much easier setting of enumeration nodes to new values.
        #
        # The naming convention of QuickSpin enums is the name of the
        # enumeration node followed by an underscore and the symbolic of
        # the entry node. Selecting "Off" on the "ExposureAuto" node is
        # thus named "ExposureAuto_Off".
        #
        # *** LATER ***
        # Exposure time can be set automatically or manually as needed. This
        # example turns automatic exposure off to set it manually and back
        # on to return the camera to its default state.

        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print 'Unable to disable automatic exposure. Aborting...'
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        print 'Automatic exposure disabled...'

        # Set exposure time manually; exposure time recorded in microseconds
        #
        # *** NOTES ***
        # Notice that the node is checked for availability and writability
        # prior to the setting of the node. In QuickSpin, availability and
        # writability are ensured by checking the access mode.
        #
        # Further, it is ensured that the desired exposure time does not exceed
        # the maximum. Exposure time is counted in microseconds - this can be
        # found out either by retrieving the unit with the GetUnit() method or
        # by checking SpinView.

        if cam.ExposureTime.GetAccessMode() != PySpin.RW:
            print 'Unable to set exposure time. Aborting...'
            return False

        # Ensure desired exposure time does not exceed the maximum
        exposure_time_to_set = M
        exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
        cam.ExposureTime.SetValue(exposure_time_to_set)
        print 'Shutter time set to %s us...\n' % exposure_time_to_set

    except PySpin.SpinnakerException as ex:
        print 'Error: %s' % ex
        result = False

    return result

def configure_gain(nodemap, N):
    try:
        result = true
    
        # Create float node
        node_gain = PySpin.CFloatPtr(nodemap.GetNode('Gain'))

        #set value
        node_gain.SetValue(N)

                # Retrieve float value
        value = node_gain.GetValue()

                # Print value
        #print_with_indent(level, '%s: %s' % (display_name, value))

    except PySpin.SpinnakerException as ex:
        print ('Error: %s') % ex
        return False

    return result


#method to change through seetings. 
#make sure to call the correct variables to set these values on the camera
def settings (nodemap, cam, M, N)
	result = true 

	#setting M th exposure time in us
	#4us is minimum. stops just before .01 seconds
	M = 4 + M*10
	result &= configure_exposure(cam, M)
	
	#setting gain value
	N = N * .1 #(0-30)
    result &= configure_gain(nodemap, N)

	return result


#Hardware trigger... 
class TriggerType:
    HARDWARE = 2 

CHOSEN_TRIGGER = TriggerType.HARDWARE    

#method to configure hardware trigger to apropriate source
def configure_trigger(cam):
    """
    This function configures the camera to use a trigger. First, trigger mode is
    set to off in order to select the trigger source. Once the trigger source
    has been selected, trigger mode is then enabled, which has the camera
    capture only a single image upon the execution of the chosen trigger.

     :param cam: Camera to configure trigger for.
     :type cam: CameraPtr
     :return: True if successful, False otherwise.
     :rtype: bool
    """
    result = True

    print('*** CONFIGURING TRIGGER ***\n')

    

    try:
        # Ensure trigger mode off
        # The trigger must be disabled in order to configure whether the source
        # is software or hardware.
        nodemap = cam.GetNodeMap()
        node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
        if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
            print('Unable to disable trigger mode (node retrieval). Aborting...')
            return False

        node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
        if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
            print('Unable to disable trigger mode (enum entry retrieval). Aborting...')
            return False

        node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

        print('Trigger mode disabled...')

        # Select trigger source
        # The trigger source must be set to hardware or software while trigger
        # mode is off.
        node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
        if not PySpin.IsAvailable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
            print('Unable to get trigger source (node retrieval). Aborting...')
            return False

        if CHOSEN_TRIGGER == TriggerType.HARDWARE: #Should alays be true
            node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line3') 
            if not PySpin.IsAvailable(node_trigger_source_hardware) or not PySpin.IsReadable(
                    node_trigger_source_hardware):
                print('Unable to set trigger source (enum entry retrieval). Aborting...')
                return False
            node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())

        # Turn trigger mode on
        # Once the appropriate trigger source has been set, turn trigger mode
        # on in order to retrieve images using the trigger.
        node_trigger_mode_on = node_trigger_mode.GetEntryByName('On')
        if not PySpin.IsAvailable(node_trigger_mode_on) or not PySpin.IsReadable(node_trigger_mode_on):
            print('Unable to enable trigger mode (enum entry retrieval). Aborting...')
            return False

        node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())
        print('Trigger mode turned back on...')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def grab_next_image_by_trigger(nodemap, cam):
    """
    This function acquires an image by executing the trigger node.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        # Use trigger to capture image
        # The software trigger only feigns being executed by the Enter key;
        # what might not be immediately apparent is that there is not a
        # continuous stream of images being captured; in other examples that
        # acquire images, the camera captures a continuous stream of images.
        # When an image is retrieved, it is plucked from the stream.

        if CHOSEN_TRIGGER == TriggerType.HARDWARE:
            a = 2 #will this make it happy? (CP) update still dont get this but it works 
			
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def acquire_images(cam, nodemap, nodemap_tldevice, M, N): #M is exposure number, N is gain level 
    """
    This function acquires saves images from a device.
    Please see Acquisition example for more in-depth comments on acquiring images.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***\n')
    try:
        result = True

        #set exposure and gain 
        result &= settings(nodemap, cam, M, N)

        # Set acquisition mode to continuous
        # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print('Acquisition mode set to continuous...')

        #  Begin acquiring images
        cam.BeginAcquisition()

        print('Acquiring images...')
						
		#matrix to collect images 
        print('')
        picList = []
        
        # Retrieve, convert, and save images
        # image number specified and iterated through for each exposure/gain configuration
        for i in range(NUM_IMAGES):
            try:

                #  Retrieve the next image from the trigger
                result &= grab_next_image_by_trigger(nodemap, cam)

                #  Retrieve next received image
                image_result = cam.GetNextImage()

                #  Ensure image completion
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:
                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
					
					#add to piclist
                    imgarray = image_converted.GetNDArray()
                    picList.append(imgarray) #array of the pixel values of each individual image 
					
					#  Release image 
                    image_result.Release() 	

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

        #now that picList is populated with NUM_Images we send it to 
        #pixel points where n pixels will be averaged throughput all images
        #then average of pixel n will be compared to make sure all n pixels are behaving 
        #the same at wich point all averages of n pixels will be averaged to give the dark noise 
        #value for the M/N Exposure/Gain settings configureation
        PixelPoints(picList)    #result &= (?)

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def reset_trigger(nodemap):
    """
    This function returns the camera to a normal state by turning off trigger mode.
  
    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
        if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
            print('Unable to disable trigger mode (node retrieval). Aborting...')
            return False

        node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
        if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
            print('Unable to disable trigger mode (enum entry retrieval). Aborting...')
            return False

        node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

        print('Trigger mode disabled...')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** DEVICE INFORMATION ***\n')

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not available.')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def run_single_camera(cam):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        err = False

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Configure trigger
        if configure_trigger(cam) is False:
            return False

        # Acquire images 
        #double loop, acquire images will call method(s?) to set the proper settings 
        for M in range(999): #exposure (4us to just under .01s)
        #[.01 is probably too close to the capture frequancy]) maybe more iterations through smaller range??
        	for N in range(300): #gain (is a log scale) (0-30 dB)
        		#everytime this is called take 100 images with M and N settings (how many pixels)
        		result &= acquire_images(cam, nodemap, nodemap_tldevice, M, N) 

        # Reset trigger
        result &= reset_trigger(nodemap)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """

    # Since this application saves images in the current folder
    # we must ensure that we have permission to write to this folder.
    # If we do not have permission, fail right away.
    try:
        test_file = open('test.txt', 'w+')
    except IOError:
        print('Unable to write to current directory. Please check permissions.')
        input('Press Enter to exit...')
        return False

    test_file.close()
    os.remove(test_file.name)

    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:
        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera, should only be one...
    #should loop go around run signle cam a=with variables passed for the settings? 
    for i, cam in enumerate(cam_list):

        print('Running example for camera %d...' % i)

        result &= run_single_camera(cam)
        print('Camera %d example complete... \n' % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()
	
	# averaging method 
    #avg = Avg(picList, 160) ### 160 NUMBER OF IMAGES TO USE, SHOULD BE CONFIDENT NO BEAM stepping
	
    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')
    return result


if __name__ == '__main__':
    main()