# Python module for doing various useful lab-related things in python

#check

import pylab as pl
import scipy.optimize
import numpy as np
import re
import gc

# Create a class of object to hold data and metadata from HP network analyzers

class NAdata_struct:
    def __init__(self):
        self.data = []
        self.filename = []
        self.analyzer_type = []
        self.data = []
        self.ncols = []
        self.IFBW = []
        self.source_pow = []
        self.sweep_type = []
        self.npoints = []
        self.ydata_units = []
        self.measure_type = []
        self.sweep_time = []
        self.col_headings = []
        self.freq = []
        self.channel = []
        self.name = self

# Function to read in data from a HP network analyzer ascii file

def read_HPNA_ascii(filename):
    """
    A function to read in data from a HP network analyzer ascii file.
    The only input is the filename. The output will be an instance of the NAdata_struct class, 
    or a list of such instances if the file contains data from two channels.
    """
    # initialize the list containing data and metadate that will be returned from the function 
    all_data = []

    print("Reading data from HPNA ascii file "+filename+"\n")

    # open the ascii file
    f = open(filename,'r')

    # read top level headers
    analyzer_type = f.readline()
    print("Instrument model: "+analyzer_type[1:len(analyzer_type)-3])
    date = f.readline()
    print("Data was taken on"+date[6:len(date)-3]+"\n")

    # chug through some blank lines
    for m in range(0,3):
        f.readline()
    
    # call fill_NAdata_struct sub-function to read in data from channel 1

    NAdata1 = fill_NAdata_struct(f)

    # chug through some more blank lines

    for i in range(0,2):
        f.readline()

    # check whether there is another channel. If not finish here and return the first channel data and metadata
    if not f.readline():
        nchannels=1
        all_data.append(NAdata1)
        print('End of file \n')

    # if there is another channel, read this and return both channels' data and metadata in a list
    else:
        nchannels=2
        NAdata2 = fill_NAdata_struct(f)
        all_data.append(NAdata1)
        all_data.append(NAdata2)
        
    results_str="Returning a list of %d data objects corresponding to %d channels in file %s\n" % (nchannels, nchannels, filename)
    print(results_str)
    return all_data

# A subfunction of readHPNAascii which actually does the reading from the file for each of up to 2 channels in a file

def fill_NAdata_struct(f):
    """
    A subfunction of readHPNAascii which actually does the reading from the file for 
    each of up to 2 channels in a file
    """

    # create an instance of the NAdata_struct class
    NAdata = NAdata_struct()

    NAdata.filename = f.name
    
    # read through segment of text file, setting metadata properties of NAdata_struc instance
    NAdata.channel = f.readline()
    print("Channel number = "+NAdata.channel)
    
    meastype_str = f.readline()
    NAdata.measure_type = "\""+meastype_str[15:len(meastype_str)-1]
    print('\tMeasurement type = '+NAdata.measure_type)

    ydataunits_str = f.readline()
    NAdata.ydata_units = "\""+ydataunits_str[14:len(ydataunits_str)-1]
    print('\tData units are '+NAdata.ydata_units)

    npoints_str = f.readline()
    NAdata.npoints = int(npoints_str[19:len(npoints_str)-3])
    print("\tNumber of yaxis points = "+str(NAdata.npoints))

    sweep_time_str = f.readline()
    NAdata.sweep_time = float(sweep_time_str[13:len(sweep_time_str)-5])
    print('\tSweep time is '+str(NAdata.sweep_time))

    sweep_type_str = f.readline()
    NAdata.sweep_type = "\""+sweep_type_str[13:len(sweep_type_str)-1]
    print('\tSweep type is '+NAdata.sweep_type)
    
    source_pow_str = f.readline()
    NAdata.source_pow = "\""+source_pow_str[16:len(source_pow_str)-1]
    print('\tSource power is '+NAdata.source_pow)

    IFBW_str = f.readline()
    IFBWwords = [w for w in re.split('\W', IFBW_str) if w]
    IFBWnum = int(IFBWwords[2])
    IFBWunits = IFBWwords[3]
    if IFBWunits == 'Hz':
        NAdata.IFBW = IFBWnum
    elif IFBWunits == 'kHz':
        NAdata.IFBW = IFBWnum*1000
    elif IFBWunits == 'MHz':
        NAdata.IFBW = IFBWnum*1e6
    print("\tIF BW is "+str(NAdata.IFBW)+"Hz\n")
    f.readline()

    # Find column headers of all columns present
    NAdata.col_headings = re.findall('\"(.*?)\"', f.readline())

    # Get number of columns
    NAdata.ncols = len(NAdata.col_headings)

    # Initialize the data object of the NAdata_struct instance as a numpy array
    NAdata.data = np.zeros((NAdata.npoints, NAdata.ncols))

    # Read the data from the text file into the data object
    for i in range(0,NAdata.npoints):
        floats = [float(x) for x in f.readline().split()]
        NAdata.data[i,:] = floats
    return NAdata

# A function to fit beam radius data to the Gaussian propagation function. 

def fit_beam_profile(z_data, w_data, w0guess, z0guess, lam=1064e-9, show_plot=1, plotpts=100, title='Beam scan fit', w2zero=True, saveplot=False, filename='beamfit.pdf'):
    """
    A function to fit beam radius data to the Gaussian propagation function.
    All data and fit guess inputs should be in meters. Beam sizes must be radii, not diameter.
    """
    
    # defining the sub-function that describes the theoretical propagation of a Gaussian beam
    def zw0z02w(z, w0, z0, lam):
        z_R = np.pi*w0**2/lam
        w = w0*np.sqrt(1+((z-z0)/z_R)**2)
        return w
    
    # run optimization procedure, fitting the waist size and location to give best match between data and theory
    popt,pcov = scipy.optimize.curve_fit(lambda z_data, w0, z0: zw0z02w(z_data, w0, z0, lam), z_data, w_data, p0=[w0guess,z0guess])

    # set function outputs equal to the results of the fit
    w0out=popt[0]
    z0out=popt[1]
    
    # if plot is requested, plot it with defaults or options as requested in function inputs.
    if show_plot == 1:
        import pylab as pl
        z_fit = np.linspace(min(z_data),max(z_data),plotpts)
        w_fit = zw0z02w(z_fit, w0out, z0out, lam)

        um=1e6
        pl.figure()
        pl.plot(z_data,w_data*um,'bo', label = 'Data')
        pl.plot(z_fit,w_fit*um,'b', label = 'Fit')
        pl.tight_layout
        pl.grid()
        pl.xlabel('Position [m]')
        pl.ylabel('Beam size [$\mu$m]')
        pl.xlim((min(z_data),max(z_data)))
        if w2zero:
            pl.ylim((0,max(w_data)*um))
        pl.legend(loc=0)
        pl.title(title)
        if saveplot:
            pl.savefig(filename)
     
    # return fit results       
    return w0out, z0out        
