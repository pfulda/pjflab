#MCMC for table top

#%matplotlib inline
#imports needed for plotting and animation
import matplotlib.pyplot as plt
import autograd.numpy as np
#import hpc do not need with this code
#import pykat as pk nor do we need this
import skimage
import scipy
from scipy import fft
from scipy import ndimage

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LogNorm
from matplotlib import animation
from IPython.display import HTML


from autograd import elementwise_grad, value_and_grad
from scipy.optimize import minimize
from collections import defaultdict
from itertools import zip_longest
from functools import partial

from IPython.display import HTML

import os
import PySpin

#initial variables
#boundaries of parameter space
#Double check what sort od bounds should be used
exp_bounds = np.arange(40, 6000, 1) #lower bound, upper bound, step size in units of us
gain_bounds = np.arange(0,5,0.05)

#deminsions of parameters
ParamSpcDims=2

#these are the choices allowed for new MCMC steps
StepSet_exp = [-10, 0, 10]
StepSet_gain = [-0.2,0,0.1]


#Adding code from Kaden's simulation MCMC. Will be 2D as camera powers must be changed manually
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

#this will take the place of f in the toy model
def AvgSNR2(images): #change to just the recorded images
    #finding the bright spot on the images
    #print("called SNR")
    cords = ndimage.measurements.center_of_mass(images[0])
    x = int(cords[1])
    y = int(cords[0])
    x_array=np.linspace(x-4,x+5,10)
    y_array=np.linspace(y-4,y+5,10)
    """
    neg_Avg_SNR2: return negative value of the squared avg SNR amongst the calculated pixels
    x_array: numpy array generated from defining sensor
    y_array: numpy array generated from defining sensor
    beam1_amp: numpy array generated by specifying beam power
    beam2_curved_amp: numpy array generated by specifying curvature and beam power
    """
    SNRs = []
    t = np.linspace(0.025,10,400)
    #Change this, we dont need to make any pixels
    for i in range(len(x_array)): #still want to be on the center of the camera (what if beams arent aligned??)
        for j in range(len(y_array)):
            pixel_data = PullPixelData(rowi=int(y_array[i]), coli=int(x_array[j]), n_beatnote=images)
            SNRi = SNR(t=t, pixel_data=pixel_data)
            SNRs.append(SNRi)
    neg_Avg_SNR2 = -1*(sum(SNRs)/len(SNRs))**2
    #print("This is the value of SNR" , neg_Avg_SNR2)
    #so as to ensure saturated (-<SNR>^2) do not dominate the results....just set equal to 0
    #just be careful with the camera
    SatBool = 0
    for i in range(4):
        if np.max(images[i]) > 65510: #this value for 12 bit
            SatBool = 1
    if SatBool == 1:
        neg_Avg_SNR2 = 0

    return neg_Avg_SNR2

class TriggerType:
    HARDWARE = 2

CHOSEN_TRIGGER = TriggerType.HARDWARE
# Camera Code... need to set parameters of camera and record images
def camera_code(exp, gain,NUM_IMAGES):
#set variables and send out images (can I return the images before the method ends?)
#number of images, what else?? some sort of time array(could just make up based on capture frequency)
    images=[]
    snr = 0

    def configure_exp_gain(cam,exp,gain):
        try:
            result = True
            nodemap = cam.GetNodeMap()


        #exposure (need to reset?)
            if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False

            cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            #print('Automatic exposure disabled...')

            if cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False

            exposure_time_to_set = exp #measured in us
            exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
            cam.ExposureTime.SetValue(exposure_time_to_set)
            print('Shutter time set to %s us...\n' % exposure_time_to_set)


            #gain
            if cam.GainAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic Gain. Aborting...')
                return False

            cam.GainAuto.SetValue(PySpin.GainAuto_Off)

            if cam.Gain.GetAccessMode() != PySpin.RW:
                print('Unable to set gain. Aborting...')
                return False

            gain_to_set = gain #measured in dB
            gain_to_set = min(cam.Gain.GetMax(), gain_to_set)
            cam.Gain.SetValue(gain_to_set)
            print('Gain set to %s dB...\n' % gain_to_set)


            #setting the pixel format
            node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode('PixelFormat'))
            if PySpin.IsAvailable(node_pixel_format) and PySpin.IsWritable(node_pixel_format):

                # Retrieve the desired entry node from the enumeration node
                node_pixel_format_mono8 = PySpin.CEnumEntryPtr(node_pixel_format.GetEntryByName('Mono12p'))
                if PySpin.IsAvailable(node_pixel_format_mono8) and PySpin.IsReadable(node_pixel_format_mono8):

                    # Retrieve the integer value from the entry node
                    pixel_format_mono8 = node_pixel_format_mono8.GetValue()

                    # Set integer as new value for enumeration node
                    node_pixel_format.SetIntValue(pixel_format_mono8)

                    print('Pixel format set to %s...' % node_pixel_format.GetCurrentEntry().GetSymbolic())

                    #check bits per pixel
                    ##if PySpin.IsAvailable(node_pixel_size) and PySpin.IsReadable(node_pixel_size):
                        #print(node_pixel_size)

                else:
                    print('Pixel format mono 12 not available...')

            else:
                print('Pixel format not available...')


            #set ADC to 12 bit
            node_ADC = PySpin.CEnumerationPtr(nodemap.GetNode('AdcBitDepth'))
            if not PySpin.IsAvailable(node_ADC) or not PySpin.IsWritable(node_ADC):
                print('Unable to get ADC (node retrieval). Aborting...')
                return False

            node_ADC_setting = node_ADC.GetEntryByName('Bit12')
            if not PySpin.IsAvailable(node_ADC_setting) or not PySpin.IsReadable(
                    node_ADC_setting):
                print('Unable to set ADC (enum entry retrieval). Aborting...')
                return False
            node_ADC.SetIntValue(node_ADC_setting.GetValue())

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result



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

        #print('*** CONFIGURING TRIGGER ***\n')



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

            #print('Trigger mode disabled...')

            # Select trigger source
            # The trigger source must be set to hardware or software while trigger
            # mode is off.
            node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
            if not PySpin.IsAvailable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
                print('Unable to get trigger source (node retrieval). Aborting...')
                return False

            if CHOSEN_TRIGGER == TriggerType.HARDWARE:
                node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line3') #40Hz from CG
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
            #print('Trigger mode turned back on...')


        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return result



    def grab_next_image_by_trigger(nodemap, cam):  # not sure what this does, but its working so it will be left
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
                     # don't need to see this every image
                    ## print('Use the hardware to trigger image acquisition.')
                a = 2

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return result


    def acquire_images(cam, nodemap, nodemap_tldevice):
        """
            This function acquires and saves 10 images from a device.
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

            #print('Acquisition mode set to continuous...')

            #  Begin acquiring images
            cam.BeginAcquisition()

            #print('Acquiring images...')


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
                #print('Device serial number retrieved as %s...' % device_serial_number)


            print('')
            #picList = []

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

                        #change to 12 bit
                        #(self,format,algorithm)
                        #Image_Result = image_result.ResetImage(720,540,0,0,PySpin.PixelFormat_Mono12p)
                        #print(image_result.GetPixelFormatName())
                        image_converted = image_result.Convert(PySpin.PixelFormat_Mono16, PySpin.HQ_LINEAR)

                        image_result.Release()

                        #add to piclist
                        imgarray = image_converted.GetNDArray()
                        images.append(imgarray)

                except PySpin.SpinnakerException as ex:
                    print('Error: %s' % ex)
                    return False


            # End acquisition
            #
            #  *** NOTES ***
            #  Ending acquisition appropriately helps ensure that devices clean up
            #  properly and do not need to be power-cycled to maintain integrity.
            cam.EndAcquisition()
            snr = AvgSNR2(images) #try with picList
            #print("this is SNR in acquire images",SNR) #this is not the value being returne

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return snr


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

            #print('Trigger mode disabled...')

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

        #print('*** DEVICE INFORMATION ***\n')

        try:
            result = True
            node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

            if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
                features = node_device_information.GetFeatures()
                #for feature in features:
                    #node_feature = PySpin.CValuePtr(feature)
                    #print('%s: %s' % (node_feature.GetName(),
                                      #node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

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

            #result &= print_device_info(nodemap_tldevice)
            #dont need to print all of that

            # Initialize camera
            cam.Init()

            # Retrieve GenICam nodemap
            nodemap = cam.GetNodeMap()

            #configure settings
            if configure_exp_gain(cam,exp,gain) is False:
                return False

            # Configure trigger
            if configure_trigger(cam) is False:
                return False

            # Acquire images
            snr = acquire_images(cam, nodemap, nodemap_tldevice)
            #print("SNR after acquire_images: ", snr)

            # Reset trigger
            result &= reset_trigger(nodemap)

            # Deinitialize camera
            cam.DeInit()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return snr


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
        #print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

        # Retrieve list of cameras from the system
        cam_list = system.GetCameras()

        num_cameras = cam_list.GetSize()

        #print('Number of cameras detected: %d' % num_cameras)

        # Finish if there are no cameras
        if num_cameras == 0:
            # Clear camera list before releasing system
            cam_list.Clear()

            # Release system instance
            system.ReleaseInstance()

            print('Not enough cameras!')
            input('Done! Press Enter to exit...')
            return False

        # Run example on each camera
        for i, cam in enumerate(cam_list):

            #print('Running example for camera %d...' % i)

            snr = run_single_camera(cam)
            #print("SNR after run_single_cam: ", snr)
            #print('Camera %d example complete... \n' % i)

        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        del cam

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        #input('Done! Press Enter to exit...')
        #print("SNR before last nested method: ", snr)
        return snr


    #if __name__ == '__main__':
        #main()

    snr = main()
    #SNR = AvgSNR2(images) #is this running?
    #print("SNR before end of method: ", snr)
    return snr 

def CreatePathNames(NumPaths):
    #set up path names
    path_iter = []
    path_base = "path"
    for i in range(0,NumPaths):
        path_name = path_base + "_" + str(i)
        path_iter.append(path_name)
    return path_iter


def AppendPathStart(path_iter, x0s):
    #add random (x,y) starting points to individual paths which are initially held as lists in a dict
    paths_ = defaultdict(list)
    iii=0
    for path in path_iter:
        paths_[path].append(x0s[:,iii]) #how do list in dictonaries work, should it be x0s[iii] ??
        iii+=1
    return paths_


#create random initial coords for each of your N number of paths
def SnakePath_Start(NumPaths, ParamSpcDims, exp_bounds, gain_bounds):
    #create random (x,y) starting points:
    #initialize empty list to place random (x,y) starting points
    x0s=[]
    #run for loop to append random (x,y,q) to list as numpy arrays, these coords are called x0i
    for i in range(NumPaths):
        x0i = np.array([np.random.choice(exp_bounds), np.random.choice(gain_bounds)])
        #print("this is x0" + str(i) + ": " + str(x0i))
        x0s.append(x0i)
    #print("this is x0s:" +str(x0s))
    #print("shape:"+str(np.shape(x0s)))
    x0s = np.array(x0s).T
    print("this is x0s (post T):" +str(x0s))
    print("shape:"+str(np.shape(x0s))+'\n')
    path_iter = CreatePathNames(NumPaths)
    paths_ = AppendPathStart(path_iter, x0s)

    return x0s, paths_, path_iter


#This is the Markov Chain portion of the MCMC, you are effectively only moving to a new coord
#if it will decrease the z value
#try three small increment comparisons, if neither, take kamikazi leap for new position in parameter space
#StepSet should be list of possible steps, one set for each of the camera parameters
#X0i should be 2X1 coords
#ParamSpcDims should be 2
#AvgSNR2 should be function to be minimized
def SnakeChoice(paths_, StepSet_exp, StepSet_gain, ParamSpcDims, path_i, index_i,Zvec):
#why is ParamChoices_SNR a var, well it isn't anymore
    CoordsPostChoice = np.zeros((1,ParamSpcDims))

    x0 = paths_['path_'+str(path_i)][index_i][0]
    #print("this is x0:" +str(x0) + "\n")
    y0 = paths_['path_'+str(path_i)][index_i][1]
    #print("this is y0:" +str(y0) + "\n")
    #q0 = paths_['path_'+str(path_i)][index_i][2] ONLY USING TWO PARAMETERS
    print("Initial (x,y)= (" + str(x0) + "," + str(y0) + ")")
    #initial Z value at beginning of step choice sequence
    Zvalue0 = Zvec #NEW METHOD FOR SETTING CAMERA PARAMETERS x0 is exp, y0 is gain (need to send images to the SNR)
    print("Initial Z value:" + str(Zvalue0))
    #random addition to x0, y0
    Plusx0 = np.random.choice(a=StepSet_exp)
    Plusy0 = np.random.choice(a=StepSet_gain)
    #ensures no (0,0) additions to (x,y)
    if Plusx0==0 and Plusy0==0:
        Plusx0 = np.random.choice(a=[StepSet_exp[0], StepSet_exp[2]])
    print("Plusx0: " + str(Plusx0))
    print("Plusy0: " + str(Plusy0))
    #potential new coords
    xn0 = x0+Plusx0
    yn0 = y0+Plusy0
    #check on boundary conditions (i.e. keep snakes on bounded space)
    if xn0 > exp_bounds[-1]:
        xn0 = xn0 - 2*Plusx0
    if xn0 < exp_bounds[0]:
        xn0 = xn0 - 2*Plusx0
    if yn0 > gain_bounds[-1]:
        yn0 = yn0 - 2*Plusy0
    if yn0 < gain_bounds[0]:
        yn0 = yn0 - 2*Plusy0
    #comparison Z value
    Zvalue_n0 = camera_code(xn0,yn0,400)
    print("Z value from step attempt 1: " + str(Zvalue_n0) + ", with (x,y): (" + str(xn0) + "," + str(yn0) +")")
    #round-off delta, will artificially increase Zvalue0 so that comparison has a better chance
    delta = 1e-2
    #test: Y: try another random step; N: new coords accepted bc new Z is less than original Z+delta
    if (Zvalue0 + delta) < Zvalue_n0:
        Plusx1 = np.random.choice(a=StepSet_exp)
        Plusy1 = np.random.choice(a=StepSet_gain)
        #ensures no (0,0) additions to (x,y)
        if Plusx1==0 and Plusy1==0:
            Plusx1 = np.random.choice(a=[StepSet_exp[0], StepSet_exp[2]])
        print("Plusx1: " + str(Plusx1))
        print("Plusy1: " + str(Plusy1))
        xn1 = x0 + Plusx1
        yn1 = y0 + Plusy1
        #ensures coords stay within bounds
        if xn1 > exp_bounds[-1]:
            xn1 = xn1 - 2*Plusx1
        if xn1 < exp_bounds[0]:
            xn1 = xn1 - 2*Plusx1
        if yn1 > gain_bounds[-1]:
            yn1 = yn1 - 2*Plusy1
        if yn1 < gain_bounds[0]:
            yn1 = yn1 - 2*Plusy1

        Zvalue_n1 = camera_code(xn1,yn1,400)
        print("Z value from step attempt 2: " + str(Zvalue_n1) + ", with (x,y): (" + str(xn1) + "," + str(yn1) +  ")")
        #test: Y: try another random step; N: return xn1, yn1
        if Zvalue0 + delta < Zvalue_n1:
            Plusx2 = np.random.choice(a=StepSet_exp)
            Plusy2 = np.random.choice(a=StepSet_gain)
            #ensures no (0,0) additions to (x,y)
            if Plusx2==0 and Plusy2==0:
                Plusx2 = np.random.choice(a=[StepSet_exp[0], StepSet_exp[2]])
            print(Plusx2)
            print(Plusy2)
            xn2 = x0 + Plusx2
            yn2 = y0 + Plusy2
            #arbitrary choice to send x back by 2*random x step if exceeds bounds
            if xn2 > exp_bounds[-1]:
                xn2 = xn2 - 2*Plusx2
            if xn2 < exp_bounds[0]:
                xn2 = xn2 - 2*Plusx2
            if yn2 > gain_bounds[-1]:
                yn2 = yn2 - 2*Plusy2
            if yn2 < gain_bounds[0]:
                yn2 = yn2 - 2*Plusy2

            Zvalue_n2 = camera_code(xn2,yn2,400)
            print("Z value from step attempt 3: " + str(Zvalue_n2) + ", with (x,y): (" + str(xn2) + "," + str(yn2) + ")")
            #test: Y: no big jump attempt, N: return xn2, yn2
            if Zvalue0 + delta < Zvalue_n2:
                PlusBIGx = 10*np.random.choice(a=StepSet_exp)
                PlusBIGy = 10*np.random.choice(a=StepSet_gain)
                if PlusBIGx==0 and PlusBIGy==0:
                    PlusBIGx = 5*np.random.choice(a=[StepSet_exp[0], StepSet_exp[2]])
                print(PlusBIGx)
                print(PlusBIGy)
                xnBIG = x0 + PlusBIGx
                ynBIG = y0 + PlusBIGy
                #arbitrary choice to send x back by 2*random x step
                if xnBIG > exp_bounds[-1]:
                    xnBIG = xnBIG - 2*PlusBIGx
                if xnBIG < exp_bounds[0]:
                    xnBIG = xnBIG - 2*PlusBIGx
                if ynBIG > gain_bounds[-1]:
                    ynBIG = ynBIG - 2*PlusBIGy
                if ynBIG < gain_bounds[0]:
                    ynBIG = ynBIG - 2*PlusBIGy

                Zvalue_nBIG = camera_code(xnBIG, ynBIG,400)
                print("Z value from BIG JUMP final attempt: " + str(Zvalue_nBIG) + ", with (x,y): (" + str(xnBIG) + "," + str(ynBIG) + ")")
                if Zvalue0 + delta < Zvalue_nBIG:
                    CoordsPostChoice[:,0]=x0
                    CoordsPostChoice[:,1]=y0
                    #print("shape of coords: "+ str(np.shape(CoordsPostChoice)))
                    Zexit = np.asarray(Zvalue0).reshape((1,1))
                    paths_['path_'+str(path_i)]=np.vstack([paths_['path_'+str(path_i)],CoordsPostChoice])
                else:
                    CoordsPostChoice[:,0]=xnBIG
                    CoordsPostChoice[:,1]=ynBIG
                    #print("shape of coords: "+str(np.shape(CoordsPostChoice)))
                    Zexit = np.asarray(Zvalue_nBIG).reshape((1,1))
                    paths_['path_'+str(path_i)]=np.vstack([paths_['path_'+str(path_i)],CoordsPostChoice])
            else:
                CoordsPostChoice[:,0]=xn2
                CoordsPostChoice[:,1]=yn2
                #print("shape of coords: "+str(np.shape(CoordsPostChoice)))
                Zexit = np.asarray(Zvalue_n2).reshape((1,1))
                paths_['path_'+str(path_i)]=np.vstack([paths_['path_'+str(path_i)],CoordsPostChoice])
        else:
            CoordsPostChoice[:,0]=xn1
            CoordsPostChoice[:,1]=yn1
            #print("shape of coords: "+str(np.shape(CoordsPostChoice)))
            Zexit = np.asarray(Zvalue_n1).reshape((1,1))
            paths_['path_'+str(path_i)]=np.vstack([paths_['path_'+str(path_i)],CoordsPostChoice])

    else:
        CoordsPostChoice[:,0]=xn0
        CoordsPostChoice[:,1]=yn0
        #print("shape of coords: "+str(np.shape(CoordsPostChoice)))
        Zexit = np.asarray(Zvalue_n0).reshape((1,1))
        paths_['path_'+str(path_i)]=np.vstack([paths_['path_'+str(path_i)],CoordsPostChoice])
    #decided I wanted something more like 2X1 than 1X2 for CoordsPostChoice
    return CoordsPostChoice, Zexit, paths_['path_'+str(path_i)];


#current_coords should be one of the 2X1 entries of 'paths_'; for ex. paths_['path_i']
def CreateFullPath_i(Numberiterations, paths_, path_i, StepSet_exp, StepSet_gain):
    index_i=0
    BreakFlag=0
    c=0
    Zvec = np.asarray(camera_code(paths_['path_'+str(path_i)][index_i][0],paths_['path_'+str(path_i)][index_i][1],400 )).reshape((1,1))
    current_coords = paths_['path_'+str(path_i)]
    while (BreakFlag==0) and (index_i<Numberiterations):
        compare_coords = current_coords
        current_coords, Zexit, paths_['path_'+str(path_i)] = SnakeChoice(paths_,StepSet_exp, StepSet_gain, ParamSpcDims,path_i, index_i,Zvec[index_i])
        Zvec=np.vstack([Zvec,Zexit])
        print("this is Zvec: " + str(Zvec))
        if (-0.1 < (Zvec[index_i]-Zvec[index_i+1]) < 0.1):
            c+=.5
            if c == 1:
                BreakFlag = 1
                print("Break condition met, negligible difference between consecutive Z values\n")
                print("Current Coords: "+ str(current_coords)+", Zexit: " + str(Zexit) + ", iterations performed: " +str(index_i) + "\n")
                if np.array_equal(compare_coords,current_coords) == 1:
                    print("\n Break condition tripped by unchanged coords!")
        if (index_i+1 == Numberiterations):
            BreakFlag = 1
            print("\n Break condition met by reaching iteration limit!")
        print("Difference in consecutive Z vals: " + str(Zvec[index_i]-Zvec[index_i+1]))
        index_i += 1

    return paths_['path_'+str(path_i)], Zvec


#function to create all i paths
def CreateAllPaths(NumPaths, StepSet_exp, StepSet_gain, ParamSpcDims, Numberiterations):
    #set up initial random path coordinates
    x0s, paths_, path_iter = SnakePath_Start(NumPaths, ParamSpcDims=ParamSpcDims, exp_bounds=exp_bounds, gain_bounds=gain_bounds)
    ZvecTotal = []
    for path_i in range(0,NumPaths):
        paths_['path_'+str(path_i)], Zvec = CreateFullPath_i(Numberiterations=Numberiterations, paths_=paths_, path_i=path_i, StepSet_exp=StepSet_exp, StepSet_gain=StepSet_gain)
        ZvecTotal.append(Zvec)
    return paths_, ZvecTotal, path_iter, Numberiterations


def SNR_Analysis(mins,mins_params,ZvecTotal, paths_, exp_bounds, gain_bounds):
   #count number of saturated paths
    NumSatPaths = 0
    #which paths saturated
    SatPaths = []
    #find min in a path, append value to mins, append indx where the min occurred from the path
    for i in range(0,len(ZvecTotal)):
        min_i = np.min(ZvecTotal[i])
        for j in range(10):
            if min_i < mins[j]:
                k=9-j
                for ii in range(k):
                    mins[9-ii] = mins[8-ii]
                mins[j] = min_i
                mins_params[j] = paths_['path_'+str(i)][-1]
                minidx = np.where(ZvecTotal[i]==mins[0])
                break

        #minidx = minidx[0]
        #mins.append(min_i)
        mins_params.append(paths_['path_'+str(i)][-1])
        if ZvecTotal[i][-1] ==0:
            NumSatPaths += 1
            SatPaths.append(i)


    #SNR-type val
    AbsMin = min(mins)
    #integer index from mins, this is essentially telling us which ZvecTotal[i]
    WhichZvec = 0
    #pull out the parameters which resulted in the minimum val
    AbsMinParams = mins_params[WhichZvec]
    print("\n Results from running MCMC minimization of -(SNR^2) for 2D paramter space...")
    print("\n subject to the following boundaries:")
    print("\n exposure times: [" +str(exp_bounds[0]) + ", " +str(exp_bounds[-1]) +"]" )
    print("\n gain values: [" + str(gain_bounds[0]) + ", " + str(gain_bounds[-1]) + "]")
    print("\n with " + str(len(ZvecTotal)) + " paths and " + str(Numberiterations) + " iterations allowed per path")
    print("\n The most negative value of -(SNR^2) = " + str(AbsMin))
    print("\n The path which contained the minimum -(SNR^2): " + str(WhichZvec))
    print("\n The parameters which resulted in the minimum -(SNR^2): (exposure time, gain) = " +str(AbsMinParams))
    print("\n Number of paths which saturated: " + str(NumSatPaths))

    print("\n The ten lowest SNR values with repective parameters: \n")
    for i in range(10):
        print("-<SNR^2>: " + str(mins[i]) + " Parameters (Exp, Gain): " + str(mins_params[i]))

    return mins, mins_params


ZvecTotal = []
paths_, ZvecTotal, path_iter, Numberiterations = CreateAllPaths(NumPaths=100, StepSet_exp=StepSet_exp, StepSet_gain=StepSet_gain, ParamSpcDims=ParamSpcDims, Numberiterations=30)

#used to store the minimum -SNR^2 value from each seed
mins=[0,0,0,0,0,0,0,0,0,0]
#used to store the indices of the minimum -SNR^2 from each path
mins_params = [0,0,0,0,0,0,0,0,0,0]

mins, mins_params = SNR_Analysis(mins,mins_params,ZvecTotal=ZvecTotal, paths_=paths_, exp_bounds=exp_bounds, gain_bounds=gain_bounds)
