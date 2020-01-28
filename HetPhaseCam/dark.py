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
def PixelPoints (picList, NUM): #picList will be unraveled numpy array of intensity values

	#create certain pixels to iterate through
	pix1 = 720*270+360 #pixel in middle, will add more later, maybe randomize? 
	y=[0]*100
	x=[0]*100

	#do we want average or time series of the pixel value? 
	for i in range(NUM): 
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


#method to change through seetings. 
#make sure to call the correct variables to set these values on the camera
def settings (nodemap, cam, M, N)
	result = true 

	#setting M th exposure time in us
	#4us is minimum. stops just before .01 seconds
	M = 4 + M*10
	result &= configure_exposure(cam, M)
	
	#setting gain value
	N = ???
    node_gain_auto = PySpin.CEnumerationPtr(nodemap.GetNode('GainAuto'))
    if not PySpin.IsAvailable(node_gain_auto) or not PySpin.IsReadable(node_gain_auto):
        print('Unable to disable auto gain (node retrieval). Aborting...')
        return False

    node_gain_auto_off = node_gain_auto.GetEntryByName('Off')
    if not PySpin.IsAvailable(node_gain_auto_off) or not PySpin.IsReadable(node_gain_auto_off):
        print('Unable to disable auto gain (enum entry retrieval). Aborting...')
        return False

    node_gain_auto.SetIntValue(node_gain_auto_off.GetValue())

    #do we need gain selector? checking blackfly 

    #set gain value (N) [potential do this the same way as the exposure method]
    node_gain = PySpin.CFloatPtr(nodemap.GetNode('Gain'))
    if not PySpin.IsAvailable(node_gain) or not PySpin.IsReadable(node_gain):
        print('Unable to set gain (node retrieval). Aborting...')
        return False



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

        #  Retrieve device serial number for filename
        #
        #  *** NOTES ***
        #  The device serial number is retrieved in order to keep cameras from
        #  overwriting one another. Grabbing image IDs could also accomplish
        #  this.
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)
			
			
		#From Novak (CP) okay so we dont need any PSA in this code
        print('')
        picList = []
        timelist = []
        picMatrix = []
        phaseList = []

        # Retrieve, convert, and save images
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

                    #  Print image information; height and width recorded in pixels
                    #
                    #  *** NOTES ***
                    #  Images have quite a bit of available metadata including
                    #  things such as CRC, image status, and offset values, to
                    #  name a few.
					#
					#Don't need this right now (CP)
                    ##width = image_result.GetWidth()
                    ##height = image_result.GetHeight()
                    ##print('Grabbed Image %d, width = %d, height = %d' % (i, width, height))

                    #  Convert image to mono 8
                    #
                    #  *** NOTES ***
                    #  Images can be converted between pixel formats by using
                    #  the appropriate enumeration value. Unlike the original
                    #  image, the converted one does not need to be released as
                    #  it does not affect the camera buffer.
                    #
                    #  When converting images, color processing algorithm is an
                    #  optional parameter.
                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
					
					#add to piclist
                    imgarray = image_converted.GetNDArray()
                    picList.append(imgarray)
                    picMatrix.append(imgarray)
                    # Create a unique filename
					#maybe later? (CP)
                    ##if device_serial_number:
                    ##    filename = 'Trigger-%s-%d.jpg' % (device_serial_number, i)
                    ##else:  # if serial number is empty
                    ##    filename = 'Trigger-%d.jpg' % i

                    # Save image (no thanks) Maybe get naming from save_aquire saving is desired on this code
                    #
                    #  *** NOTES ***
                    #  The standard practice of the examples is to use device
                    #  serial numbers to keep images of one device from
                    #  overwriting those of another.
                    ##image_converted.Save(filename)
                    ##print('Image saved at %s\n' % filename)
					
					#  Release image (from Novak, LivePhase_V3)
                    image_result.Release()
                    if i%4 == 0 and i > 0:
                        if i%8 == 0:
                            faze = fourpointphase(picList) #Novak_phase_no_mask #Novak_phase #carre_phase #fourpointphase
                            phaseList.append(faze)
                            #print(faze.dtype)
                            #print(numpy.shape(faze))                     
                            plt.ion()						
                            plt.imshow(faze, cmap = 'jet')
                            cbar = plt.colorbar()#
                            plt.clim(vmin=-numpy.pi,vmax=numpy.pi)#
                            cbar.set_label("Phase Shift (rad)")#
                            plt.xlabel("Pixels(x)")
                            plt.ylabel("Pixels(y)")
                            #plt.xlim([300,500])
                            #plt.ylim([200,400])
                            plt.pause(0.00001)
                            plt.show()
                            plt.clf()
							
                        
                        del picList[0:4] 
						
					

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False
        AVG=Avg(picMatrix, NUM_IMAGES)
        plt.ion()						
        plt.imshow(AVG, cmap = 'jet')	
        plt.show()
        plt.clf()
        name = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/MyFirstMEGAPHASEPLOT'
        plt.savefig(name)
		
		
		#attempt to combine saved phase map plots into one (400 intensity images)
        avg = [(540,720)]	#getting dimensional error... 	
        
        for i in range(10):
            avg += phaseList[i]	

        avg = avg / 10
        plt.ion()						
        plt.imshow(avg, cmap = 'jet')	
        plt.show()
        plt.clf()
        name = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/MEGAPHASEPLOT'
        plt.savefig(name)		

		
		
		#some more stuff from V3	
        timelist = numpy.asarray(timelist)
        timediffs = timelist[1:NUM_IMAGES]-timelist[0:NUM_IMAGES-1]
        print("Average time between image captures: ", numpy.mean(timediffs)," seconds")
        print("Standard deviation: ", numpy.std(timediffs)," seconds")
        print(timediffs[0:100])
        plt.ion()
        plt.plot(timediffs)
        plt.show()
		
		
        # End acquisition
        #
        #  *** NOTES ***
        #  Ending acquisition appropriately helps ensure that devices clean up
        #  properly and do not need to be power-cycled to maintain integrity.
        cam.EndAcquisition()

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
        	for N in range(TBD): #gain (is a log scale)
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