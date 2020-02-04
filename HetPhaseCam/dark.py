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

#user input variables 
NUM_IMAGES = int(input("Please enter the number of images you would like: "))  # number of images to grab
M = int(input("Enter the size of the exposure settings you would like: ")) #number of exposure settings
m = int(input("Enter the slope or step increment of the exposure you would like: "))
N = int(input("Enter the numer of gain settings you would like: ")) #number of gain settings
n = int(input("Enter the slope or step size of gain settings you would like (it is a log base): "))
Folder_Name = input("Enter the name of the folder you wish to save the images too\nthis will also be the beginning of the file name\n(Be careful to not overwrite another folder within\nthe Data directory by using the same name): ")

Data_dir = 'C:/Users/localadmin/Desktop/Phase_Camera_Images/Data'
data_path = os.path.join(Data_dir,Folder_Name)
os.mkdir(data_path)
print('Directory created:', Folder_Name)

#rather than making 3D matrix with (M,N,I), instead one dependent var array
#and have the M and N arrays so that we are plotting in 3D two ind vs one dep
#array of size M*N=(#ofexposuresettings)*(#ofgainsettings)
DarkNoise = numpy.empty((M,N))
#KL: see https://stackoverflow.com/questions/6667201/how-to-define-a-two-dimensional-array-in-python

#global indices for interrogated pixel grid (coming from pjflab file 'Generation_of_Pixel_Array.ipynb')
Array_PixID = [ 21640,  21720,  21800,  21880,  21960,  22040,  22120,  22200,
        22280,  64840,  64920,  65000,  65080,  65160,  65240,  65320,
        65400,  65480, 108040, 108120, 108200, 108280, 108360, 108440,
       108520, 108600, 108680, 151240, 151320, 151400, 151480, 151560,
       151640, 151720, 151800, 151880, 194440, 194520, 194600, 194680,
       194760, 194840, 194920, 195000, 195080, 237640, 237720, 237800,
       237880, 237960, 238040, 238120, 238200, 238280, 280840, 280920,
       281000, 281080, 281160, 281240, 281320, 281400, 281480, 324040,
       324120, 324200, 324280, 324360, 324440, 324520, 324600, 324680,
       367240, 367320, 367400, 367480, 367560, 367640, 367720, 367800,
       367880]


#method for checking the pixel value of images
#Power Spectral Desnsity !!!! 
def PixelPoints (picList,j,k): #picList will be list of unraveled numpy array of intensity values. j and k are paramater space


    #empty array which will hold avg intensity value over NUM_IMAGES per PIXID
    Avg_Array = numpy.empty(numpy.size(Array_PixID))

    #figure out proper way to use time series for Power Spectral Density 
    for j in range(numpy.size(Array_PixID)):
        PixID = Array_PixID[j]  #single pixel per iteration on Array_PixID elements
        IVal = [0]*NUM_IMAGES #creates new IVal array for each pixel probed
        for i in range(NUM_IMAGES):
            arr=numpy.ravel(numpy.array(picList[i])) #each iteration chooses different intensity image
            IVal[i] = arr[PixID] #each element of IVal will get intensity values from same pixel per Array_PixID iteration
        Avg_IV = numpy.mean(IVal) #averages all NUM_IMAGES elements in IVal to a single value
        Avg_Array[j] = Avg_IV #new avgd intensity added to Avg_Array per PixID iterated through

    Tot_Avg = numpy.mean(Avg_Array) #Averages all 81 elements of Avg_Array (i.e. 81 pixels) for avg intensity over sensor of a given (M,N)

    DarkNoise[M][N] = Tot_Avg #assigns to element (M,N) or DarkNoise the Tot_Avg for the same (M,N) settings

def configure_exposure(cam, exp): #exp is expusre time defined by loop iteration and user settigns
    """
     This function configures a custom exposure time. Automatic exposure is turned
     off in order to allow for the customization, and then the custom setting is
     applied.
     :param cam: Camera to configure exposure for.
     :type cam: CameraPtr
     :return: True if successful, False otherwise.
     :rtype: bool
    """

    #print ('*** CONFIGURING EXPOSURE ***\n')

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
            print ('Unable to disable automatic exposure. Aborting...')
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        #print ('Automatic exposure disabled...')

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
            print ('Unable to set exposure time. Aborting...')
            return False

        # Ensure desired exposure time does not exceed the maximum
        exposure_time_to_set = exp
        exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
        cam.ExposureTime.SetValue(exposure_time_to_set)
        #print ('Shutter time set to ' + str(exposure_time_to_set) + 's us...\n') 

    except PySpin.SpinnakerException as ex:
        print ('Error: %s') % ex
        result = False

    return result

def configure_gain(nodemap,cam,gain):
    try:
        result = True

        #must turn auto gain off before changing gaoin settings
        if cam.GainAuto.GetAccessMode() != PySpin.RW:
            print ('Unable to disable automatic Gain. Aborting...')
            return False

        cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        print ('Automatic exposure disabled...')


        if cam.Gain.GetAccessMode() != PySpin.RW:
            print ('Unable to set exposure time. Aborting...')
            return False

        # Ensure desired gain does not exceed the maximum
        gain_to_set = gain
        gain_to_set = min(cam.Gain.GetMax(), gain_to_set)
        cam.Gain.SetValue(gain_to_set)
        print ('Gain set to ' + str(gain_to_set) + ' dB...\n') 

    except PySpin.SpinnakerException as ex:
        print ('Error: ') % ex
        result = False

    return result


#method to change through seetings. 
#make sure to call the correct variables to set these values on the camera
def settings (nodemap, cam, j, k):
    result = True 

	#setting exp the exposure time in us
	#4us is minimum. stops just before .01 seconds
    exp = 4 + j*m
    result &= configure_exposure(cam, exp)
	
	#setting gain value
    gain = k * n #(0-30)
    result &= configure_gain(nodemap,cam,gain)

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
        print('Error GNIBT: %s' % ex)
        return False

    return result

def acquire_images(cam, nodemap, nodemap_tldevice, j, k): #j is exposure number, k is gain level 
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

    #print('*** IMAGE ACQUISITION ***\n')
    try:
        result = True

        #  Begin acquiring images
        cam.BeginAcquisition()

        #print('Acquiring images...')
						
		#matrix to collect images 
        print('')
        picList = [] #picList is local so it should have to be cleared every time running acquire images
        
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
                print('Error image acq: %s' % ex)
                return False

        #now that picList is populated with NUM_Images we send it to 
        #pixel points where n pixels will be averaged throughput all images
        #then average of pixel n will be compared to make sure all n pixels are behaving 
        #the same at which point all averages of n pixels will be averaged to give the dark noise 
        #value for the M/N Exposure/Gain settings configureation
        cam.EndAcquisition()  #KL_758 :)
        PixelPoints(picList,j,k)    

    except PySpin.SpinnakerException as ex:
        print('Error imgAcq: %s' % ex)
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

def run_single_camera(cam,j,k):
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

        #result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        #configure settings
        if settings(nodemap, cam, j, k) is False: 
            return False

        # Configure trigger
        if configure_trigger(cam) is False:
            return False

        # Acquire images 
        #every time this is called take 100 images with M and N settings (how many pixels)
        result &= acquire_images(cam, nodemap, nodemap_tldevice, j, k) 
		
        # Reset trigger
        result &= reset_trigger(nodemap)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error run_single_cam: %s' % ex)
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
        for j in range(M):
            for k in range(N):
                result &= run_single_camera(cam,j,k) #this loops through all M and N, for each combination saving data from NUM_Images number of intensity images
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
    
    #save 2D array
    name = data_path + '.npy'
    numpy.save(name,DarkNoise)      
    print('DarkNoise is saved, booo-yaaaaaaaaa')

    input('Done! Press Enter to exit...')
    return result

if __name__ == '__main__':
    main()