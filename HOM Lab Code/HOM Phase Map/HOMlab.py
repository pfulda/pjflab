from math import factorial
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.special import eval_hermite as hermite
import matplotlib.cm as cm
from scipy.optimize import fsolve
from scipy.optimize import newton_krylov
from scipy.optimize import curve_fit
from mpl_toolkits.axes_grid1 import make_axes_locatable

beamsize = 0.00258/2
lx = 9.2e-6
ly = 9.2e-6

def U_n(x, n, w0=1):
    w = w0*beamsize
    beam = ((2/np.pi)**0.25)*((1/(2**n*factorial(n)*w))**0.5)*hermite(n, np.sqrt(2)*x/w)*np.exp(-x**2/w**2)

    return beam

def phaseHG11(wphase):
    wphase *= beamsize
    zero = np.sqrt(1.5)
    x0 = np.array([0])*wphase/np.sqrt(2)
    y0 = np.array([0])*wphase/np.sqrt(2)
    
    phaseHG11 = np.ones((1920, 1152))

    for i in np.arange(1920):
        for j in np.arange(1152):
            x = (i-1920/2)*lx
            y = (j-1152/2)*ly
            
            if (x0[0] < x < 1920*lx/2 and -1152*ly/2 < y < y0[0]) or (-1920*lx/2 < x < x0[0] and y0[0] < y < 1152*ly/2):
                phaseHG11[i][j] = 0

    return np.rot90(phaseHG11)

def phaseHG22(wphase):
    wphase *= beamsize
    zero = np.sqrt(1.5)
    x0 = np.array([-0.707106781186548, 0.707106781186548])*wphase/np.sqrt(2)
    y0 = np.array([-0.707106781186548, 0.707106781186548])*wphase/np.sqrt(2)
    
    phaseHG22 = np.ones((1920, 1152))

    for i in np.arange(1920):
        for j in np.arange(1152):
            x = (i-1920/2)*lx
            y = (j-1152/2)*ly
            
            if (x0[0] < x < x0[1] and -1152*ly/2 < y < y0[0]) or \
            (-1920*lx/2 < x < x0[0] and y0[0] < y < y0[1]) or (x0[1] < x < 1920*lx/2 and y0[0] < y < y0[1]) \
            or (x0[0] < x < x0[1] and y0[1] < y < 1152*ly/2):
                phaseHG22[i][j] = 0

    return np.rot90(phaseHG22)

def phaseHG33(wphase):
    wphase *= beamsize
    zero = np.sqrt(1.5)
    x0 = np.array([-zero, 0, zero])*wphase/np.sqrt(2)
    y0 = np.array([-zero, 0, zero])*wphase/np.sqrt(2)
    
    phaseHG33 = np.ones((1920, 1152))

    for i in np.arange(1920):
        for j in np.arange(1152):
            x = (i-1920/2)*lx
            y = (j-1152/2)*ly
            
            if (x0[0] < x < x0[1] and -1152*ly/2 < y < y0[0]) or (x0[2] < x < 1920*lx/2 and -1152*ly/2 < y < y0[0]) or \
            (-1920*lx/2 < x < x0[0] and y0[0] < y < y0[1]) or (x0[1] < x < x0[2] and y0[0] < y < y0[1]) or \
            (x0[0] < x < x0[1] and y0[1] < y < y0[2]) or (x0[2] < x < 1920*lx/2 and y0[1] < y < y0[2]) or \
            (-1920*lx/2 < x < x0[0] and y0[2] < y < 1152*ly/2) or (x0[1] < x < x0[2] and y0[2] < y < 1152*ly/2):
                phaseHG33[i][j] = 0

    return np.rot90(phaseHG33)

def phaseHG44(wphase):
    wphase *= beamsize
    zero = np.sqrt(1.5)
    x0 = np.array([-1.65068012388578, -0.524647623275290, 0.524647623275290, 1.65068012388578])*wphase/np.sqrt(2)
    y0 = np.array([-1.65068012388578, -0.524647623275290, 0.524647623275290, 1.65068012388578])*wphase/np.sqrt(2)
    
    phaseHG44 = np.ones((1920, 1152))

    for i in np.arange(1920):
        for j in np.arange(1152):
            x = (i-1920/2)*lx
            y = (j-1152/2)*ly
            
            if (x0[0] < x < x0[1] and -1152*ly/2 < y < y0[0]) or (x0[2] < x < x0[3] and -1152*ly/2 < y < y0[0]) or \
            (-1920*lx/2 < x < x0[0] and y0[0] < y < y0[1]) or (x0[1] < x < x0[2] and y0[0] < y < y0[1]) or (x0[3] < x < 1920*lx/2 and y0[0] < y < y0[1]) or \
            (x0[0] < x < x0[1] and y0[1] < y < y0[2]) or (x0[2] < x < x0[3] and y0[1] < y < y0[2]) or \
            (-1920*lx/2 < x < x0[0] and y0[2] < y < y0[3]) or (x0[1] < x < x0[2] and y0[2] < y < y0[3]) or (x0[3] < x < 1920*lx/2 and y0[2] < y < y0[3]) or \
            (x0[0] < x < x0[1] and y0[3] < y < 1152*ly/2) or (x0[2] < x < x0[3] and y0[3] < y < 1152*ly/2):
                phaseHG44[i][j] = 0

    return np.rot90(phaseHG44)

def phaseHG55(wphase):
    wphase *= beamsize
    zero1 = np.sqrt((5+np.sqrt(10))/2)
    zero2 = np.sqrt((5-np.sqrt(10))/2)

    x0 = np.array([-zero1, -zero2, 0, zero2, zero1])*wphase/np.sqrt(2)
    y0 = np.array([-zero1, -zero2, 0, zero2, zero1])*wphase/np.sqrt(2)
    
    phaseHG55 = np.ones((1920, 1152))

    for i in np.arange(1920):
        for j in np.arange(1152):
            x = (i-1920/2)*lx
            y = (j-1152/2)*ly
            
            if (x0[0] < x < x0[1] and -1152*ly/2 < y < y0[0]) or (x0[2] < x < x0[3] and -1152*ly/2 < y < y0[0]) or \
            (x0[4] < x < 1920*lx/2 and -1152*ly/2 < y < y0[0]) or \
            (-1920*lx/2 < x < x0[0] and y0[0] < y < y0[1]) or (x0[1] < x < x0[2] and y0[0] < y < y0[1]) or \
            (x0[3] < x < x0[4] and y0[0] < y < y0[1]) or \
            (x0[0] < x < x0[1] and y0[1] < y < y0[2]) or (x0[2] < x < x0[3] and y0[1] < y < y0[2]) or \
            (x0[4] < x < 1920*lx/2 and y0[1] < y < y0[2]) or \
            (-1920*lx/2 < x < x0[0] and y0[2] < y < y0[3]) or (x0[1] < x < x0[2] and y0[2] < y < y0[3]) or \
            (x0[3] < x < x0[4] and y0[2] < y < y0[3]) or \
            (x0[0] < x < x0[1] and y0[3] < y < y0[4]) or (x0[2] < x < x0[3] and y0[3] < y < y0[4]) or \
            (x0[4] < x < 1920*lx/2 and y0[3] < y < y0[4]) or \
             (-1920*lx/2< x < x0[0] and y0[4] < y < 1152*ly/2) or (x0[1] < x < x0[2] and y0[4] < y < 1152*ly/2) or \
            (x0[3]< x < x0[4] and y0[4] < y < 1152*ly/2):
                phaseHG55[i][j] = 0

    return np.rot90(phaseHG55)

def phaseHG66(wphase):
    wphase *= beamsize
    zero = np.sqrt(1.5)
    x0 = np.array([-2.35060497367449, -1.33584907401370, -0.436077411927617,
                   0.436077411927617, 1.33584907401370, 2.35060497367449])*wphase/np.sqrt(2)
    y0 = np.array([-2.35060497367449, -1.33584907401370, -0.436077411927617,
                   0.436077411927617, 1.33584907401370, 2.35060497367449])*wphase/np.sqrt(2)
    
    phaseHG66 = np.ones((1920, 1152))

    for i in np.arange(1920):
        for j in np.arange(1152):
            x = (i-1920/2)*lx
            y = (j-1152/2)*ly
            
            if (x0[0] < x < x0[1] and -1152*ly/2 < y < y0[0]) or (x0[2] < x < x0[3] and -1152*ly/2 < y < y0[0]) or (x0[4] < x < x0[5] and -1152*ly/2 < y < y0[0]) or \
            (-1920*lx/2 < x < x0[0] and y0[0] < y < y0[1]) or (x0[1] < x < x0[2] and y0[0] < y < y0[1]) or (x0[3] < x < x0[4] and y0[0] < y < y0[1]) or (x0[5] < x < 1920*lx/2 and y0[0] < y < y0[1]) or \
            (x0[0] < x < x0[1] and y0[1] < y < y0[2]) or (x0[2] < x < x0[3] and y0[1] < y < y0[2]) or (x0[4] < x < x0[5] and y0[1] < y < y0[2]) or\
            (-1920*lx/2 < x < x0[0] and y0[2] < y < y0[3]) or (x0[1] < x < x0[2] and y0[2] < y < y0[3]) or (x0[3] < x < x0[4] and y0[2] < y < y0[3]) or (x0[5] < x < 1920*lx/2 and y0[2] < y < y0[3]) or\
            (x0[0] < x < x0[1] and y0[3] < y < y0[4]) or (x0[2] < x < x0[3] and y0[3] < y < y0[4]) or (x0[4] < x < x0[5] and y0[3] < y < y0[4]) or \
            (-1920*lx/2 < x < x0[0] and y0[4] < y < y0[5]) or (x0[1] < x < x0[2] and y0[4] < y < y0[5]) or (x0[3] < x < x0[4] and y0[4] < y < y0[5]) or (x0[5] < x < 1920*lx/2 and y0[4] < y < y0[5]) or\
            (x0[0] < x < x0[1] and y0[5] < y < 1152*ly/2) or (x0[2] < x < x0[3] and y0[5] < y < 1152*ly/2) or (x0[4] < x < x0[5] and y0[5] < y < 1152*ly/2):
                phaseHG66[i][j] = 0

    return np.rot90(phaseHG66)

def phaseHG77(wphase):
    wphase *= beamsize

    x0 = np.array([-2.65196135683523, -1.67355162876747, -0.816287882858965, 0, 
                   0.816287882858965, 1.67355162876747, 2.65196135683523])*wphase/np.sqrt(2)
    y0 = np.array([-2.65196135683523, -1.67355162876747, -0.816287882858965, 0, 
                   0.816287882858965, 1.67355162876747, 2.65196135683523])*wphase/np.sqrt(2)
    
    phaseHG77 = np.ones((1920, 1152))

    for i in np.arange(1920):
        for j in np.arange(1152):
            x = (i-1920/2)*lx
            y = (j-1152/2)*ly
            
            if (x0[0] < x < x0[1] and -1152*ly/2 < y < y0[0]) or (x0[2] < x < x0[3] and -1152*ly/2 < y < y0[0]) or \
            (x0[4] < x < x0[5] and -1152*ly/2 < y < y0[0]) or (x0[6] < x < 1920*lx/2 and -1152*ly/2 < y < y0[0]) or \
            (-1920*lx/2 < x < x0[0] and y0[0] < y < y0[1]) or (x0[1] < x < x0[2] and y0[0] < y < y0[1]) or \
            (x0[3] < x < x0[4] and y0[0] < y < y0[1]) or (x0[5] < x < x0[6] and y0[0] < y < y0[1]) or \
            (x0[0] < x < x0[1] and y0[1] < y < y0[2]) or (x0[2] < x < x0[3] and y0[1] < y < y0[2]) or \
            (x0[4] < x < x0[5] and y0[1] < y < y0[2]) or (x0[6] < x < 1920*lx/2 and y0[1] < y < y0[2]) or \
            (-1920*lx/2 < x < x0[0] and y0[2] < y < y0[3]) or (x0[1] < x < x0[2] and y0[2] < y < y0[3]) or \
            (x0[3] < x < x0[4] and y0[2] < y < y0[3]) or (x0[5] < x < x0[6] and y0[2] < y < y0[3]) or \
            (x0[0] < x < x0[1] and y0[3] < y < y0[4]) or (x0[2] < x < x0[3] and y0[3] < y < y0[4]) or \
            (x0[4] < x < x0[5] and y0[3] < y < y0[4]) or (x0[6] < x < 1920*lx/2 and y0[3] < y < y0[4]) or \
            (-1920*lx/2< x < x0[0] and y0[4] < y < y0[5]) or (x0[1] < x < x0[2] and y0[4] < y < y0[5]) or \
            (x0[3]< x < x0[4] and y0[4] < y < y0[5]) or (x0[5]< x < x0[6] and y0[4] < y < y0[5]) or \
            (x0[0] < x < x0[1] and y0[5] < y < y0[6]) or (x0[2] < x < x0[3] and y0[5] < y < y0[6]) or \
            (x0[4] < x < x0[5] and y0[5] < y < y0[6]) or (x0[6] < x < 1920*lx/2 and y0[5] < y < y0[6]) or \
            (-1920*lx/2< x < x0[0] and y0[6] < y < 1152*ly/2) or (x0[1] < x < x0[2] and y0[6] < y < 1152*ly/2) or \
            (x0[3]< x < x0[4] and y0[6] < y < 1152*ly/2) or (x0[5]< x < x0[6] and y0[6] < y < 1152*ly/2):
                phaseHG77[i][j] = 0

    return np.rot90(phaseHG77)

def phaseHG88(wphase):
    wphase *= beamsize
    zero = np.sqrt(1.5)
    x0 = np.array([-2.93063742025724, -1.98165675669584, -1.15719371244678, -0.381186990207322,
                   0.381186990207322, 1.15719371244678, 1.98165675669584, 2.93063742025724])*wphase/np.sqrt(2)
    y0 = np.array([-2.93063742025724, -1.98165675669584, -1.15719371244678, -0.381186990207322,
                   0.381186990207322, 1.15719371244678, 1.98165675669584, 2.93063742025724])*wphase/np.sqrt(2)
    
    phaseHG88 = np.ones((1920, 1152))

    for i in np.arange(1920):
        for j in np.arange(1152):
            x = (i-1920/2)*lx
            y = (j-1152/2)*ly
            
            if (x0[0] < x < x0[1] and -1152*ly/2 < y < y0[0]) or (x0[2] < x < x0[3] and -1152*ly/2 < y < y0[0]) or (x0[4] < x < x0[5] and -1152*ly/2 < y < y0[0]) or (x0[6] < x < x0[7] and -1152*ly/2 < y < y0[0]) or \
            (-1920*lx/2 < x < x0[0] and y0[0] < y < y0[1]) or (x0[1] < x < x0[2] and y0[0] < y < y0[1]) or (x0[3] < x < x0[4] and y0[0] < y < y0[1]) or (x0[5] < x < x0[6] and y0[0] < y < y0[1]) or (x0[7] < x < 1920*lx/2 and y0[0] < y < y0[1]) or \
            (x0[0] < x < x0[1] and y0[1] < y < y0[2]) or (x0[2] < x < x0[3] and y0[1] < y < y0[2]) or (x0[4] < x < x0[5] and y0[1] < y < y0[2]) or (x0[6] < x < x0[7] and y0[1] < y < y0[2]) or \
            (-1920*lx/2 < x < x0[0] and y0[2] < y < y0[3]) or (x0[1] < x < x0[2] and y0[2] < y < y0[3]) or (x0[3] < x < x0[4] and y0[2] < y < y0[3]) or (x0[5] < x < x0[6] and y0[2] < y < y0[3]) or (x0[7] < x < 1920*lx/2 and y0[2] < y < y0[3]) or \
            (x0[0] < x < x0[1] and y0[3] < y < y0[4]) or (x0[2] < x < x0[3] and y0[3] < y < y0[4]) or (x0[4] < x < x0[5] and y0[3] < y < y0[4]) or (x0[6] < x < x0[7] and y0[3] < y < y0[4]) or \
            (-1920*lx/2 < x < x0[0] and y0[4] < y < y0[5]) or (x0[1] < x < x0[2] and y0[4] < y < y0[5]) or (x0[3] < x < x0[4] and y0[4] < y < y0[5]) or (x0[5] < x < x0[6] and y0[4] < y < y0[5]) or (x0[7] < x < 1920*lx/2 and y0[4] < y < y0[5]) or \
            (x0[0] < x < x0[1] and y0[5] < y < y0[6]) or (x0[2] < x < x0[3] and y0[5] < y < y0[6]) or (x0[4] < x < x0[5] and y0[5] < y < y0[6]) or (x0[6] < x < x0[7] and y0[5] < y < y0[6]) or \
            (-1920*lx/2 < x < x0[0] and y0[6] < y < y0[7]) or (x0[1] < x < x0[2] and y0[6] < y < y0[7]) or (x0[3] < x < x0[4] and y0[6] < y < y0[7]) or (x0[5] < x < x0[6] and y0[6] < y < y0[7]) or (x0[7] < x < 1920*lx/2 and y0[6] < y < y0[7]) or \
            (x0[0] < x < x0[1] and y0[7] < y < 1152*ly/2) or (x0[2] < x < x0[3] and y0[7] < y < 1152*ly/2) or (x0[4] < x < x0[5] and y0[7] < y < 1152*ly/2) or (x0[6] < x < x0[7] and y0[7] < y < 1152*ly/2):
                phaseHG88[i][j] = 0

    return np.rot90(phaseHG88)

def phaseHG99(wphase):
    wphase *= beamsize

    x0 = np.array([-3.19099320178153, -2.26658058453184, -1.46855328921667, -0.723551018752838, 0, 
                   0.723551018752838, 1.46855328921667, 2.26658058453184, 3.19099320178153])*wphase/np.sqrt(2)
    y0 = np.array([-3.19099320178153, -2.26658058453184, -1.46855328921667, -0.723551018752838, 0, 
                   0.723551018752838, 1.46855328921667, 2.26658058453184, 3.19099320178153])*wphase/np.sqrt(2)
    
    phaseHG99 = np.ones((1920, 1152))

    for i in np.arange(1920):
        for j in np.arange(1152):
            x = (i-1920/2)*lx
            y = (j-1152/2)*ly
            
            if (x0[0] < x < x0[1] and -1152*ly/2 < y < y0[0]) or (x0[2] < x < x0[3] and -1152*ly/2 < y < y0[0]) or \
            (x0[4] < x < x0[5] and -1152*ly/2 < y < y0[0]) or (x0[6] < x < x0[7] and -1152*ly/2 < y < y0[0]) or \
            (x0[8] < x < 1920*lx/2 and -1152*ly/2 < y < y0[0]) or \
            (-1920*lx/2 < x < x0[0] and y0[0] < y < y0[1]) or (x0[1] < x < x0[2] and y0[0] < y < y0[1]) or \
            (x0[3] < x < x0[4] and y0[0] < y < y0[1]) or (x0[5] < x < x0[6] and y0[0] < y < y0[1]) or \
            (x0[7] < x < x0[8] and y0[0] < y < y0[1]) or \
            (x0[0] < x < x0[1] and y0[1] < y < y0[2]) or (x0[2] < x < x0[3] and y0[1] < y < y0[2]) or \
            (x0[4] < x < x0[5] and y0[1] < y < y0[2]) or (x0[6] < x < x0[7] and y0[1] < y < y0[2]) or \
            (x0[8] < x < 1920*lx/2 and y0[1] < y < y0[2]) or \
            (-1920*lx/2 < x < x0[0] and y0[2] < y < y0[3]) or (x0[1] < x < x0[2] and y0[2] < y < y0[3]) or \
            (x0[3] < x < x0[4] and y0[2] < y < y0[3]) or (x0[5] < x < x0[6] and y0[2] < y < y0[3]) or \
            (x0[7] < x < x0[8] and y0[2] < y < y0[3]) or \
            (x0[0] < x < x0[1] and y0[3] < y < y0[4]) or (x0[2] < x < x0[3] and y0[3] < y < y0[4]) or \
            (x0[4] < x < x0[5] and y0[3] < y < y0[4]) or (x0[6] < x < x0[7] and y0[3] < y < y0[4]) or \
            (x0[8] < x < 1920*lx/2 and y0[3] < y < y0[4]) or  \
            (-1920*lx/2< x < x0[0] and y0[4] < y < y0[5]) or (x0[1] < x < x0[2] and y0[4] < y < y0[5]) or \
            (x0[3]< x < x0[4] and y0[4] < y < y0[5]) or (x0[5]< x < x0[6] and y0[4] < y < y0[5]) or \
            (x0[7]< x < x0[8] and y0[4] < y < y0[5]) or \
            (x0[0] < x < x0[1] and y0[5] < y < y0[6]) or (x0[2] < x < x0[3] and y0[5] < y < y0[6]) or \
            (x0[4] < x < x0[5] and y0[5] < y < y0[6]) or (x0[6] < x < x0[7] and y0[5] < y < y0[6]) or \
            (x0[8] < x < 1920*lx/2 and y0[5] < y < y0[6]) or \
            (-1920*lx/2< x < x0[0] and y0[6] < y < y0[7]) or (x0[1] < x < x0[2] and y0[6] < y < y0[7]) or \
            (x0[3]< x < x0[4] and y0[6] < y < y0[7]) or (x0[5]< x < x0[6] and y0[6] < y < y0[7]) or \
            (x0[7]< x < x0[8] and y0[6] < y < y0[7]) or \
            (x0[0] < x < x0[1] and y0[7] < y < y0[8]) or (x0[2] < x < x0[3] and y0[7] < y < y0[8]) or \
            (x0[4] < x < x0[5] and y0[7] < y < y0[8]) or (x0[6] < x < x0[7] and y0[7] < y < y0[8]) or \
            (x0[8] < x < 1920*lx/2 and y0[7] < y < y0[8]) or \
            (-1920*lx/2< x < x0[0] and y0[8] < y < 1152*ly/2) or (x0[1] < x < x0[2] and y0[8] < y < 1152*ly/2) or \
            (x0[3]< x < x0[4] and y0[8] < y < 1152*ly/2) or (x0[5]< x < x0[6] and y0[8] < y < 1152*ly/2) or \
            (x0[7]< x < x0[8] and y0[8] < y < 1152*ly/2):
                phaseHG99[i][j] = 0

    return np.rot90(phaseHG99)



if __name__ == "__main__":
    lx = 6.5e-6
    ly = 6.5e-6
    x = (np.arange(0, 1000) - 1000/2)*lx
    y = (np.arange(0, 1000) - 1000/2)*ly
    xx, yy = np.meshgrid(x, y, sparse=True)

    for index in range(1, 10):
        print(f"#### HG{index}{index} is running ... ####")
        efficiencyAll = []
        i = 0

        for wphase in np.linspace(0.1, 0.7, 150):
            efficiencies = []
            phase = eval(f"phaseHG{index}{index}")(wphase)
            HG00 = U_n(xx, 0)*U_n(yy, 0)
            P0 = (HG00*np.conj(HG00)).sum()
            Field = HG00*np.exp(1j*phase*np.pi)

            for wBasis in np.linspace(0.1, 0.7, 150):
                HGnm = U_n(xx, index, wBasis)*U_n(yy, index, wBasis)
                summ = (HGnm*np.conj(HGnm)).sum()
                coeff = (Field*np.conj(HGnm)).sum()/summ
                power = abs(coeff)**2*summ/abs(P0)
                efficiencies.append(power)
               
            if i%10 == 0:
                print(f"HG{index}{index}: {i}/150 number of phase map size has been done...")
            i += 1
            efficiencyAll.append(efficiencies)

    with open( f"./efficienciesBasisWaist_HG{index}{index}.p", "wb" ) as p:
        pickle.dump(efficiencyAll, p)



