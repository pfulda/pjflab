from math import factorial
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.special import eval_hermite as hermite
from PIL import Image
import sys
import argparse
from HOMlab import *

# parser = argparse.ArgumentParser(description="Order of arguments: d (blazed grating size), size (the size of the attenuated area), twoD (if the attenuated area two D or one D), amp (the amplitude of the attenuated area)")
# args = parser.parse_args()
plt.style.use('seaborn-paper')
plt.rcParams["image.cmap"] = 'viridis'
plt.rcParams["font.family"] = "Arial"


lx = 9.2e-6
ly = 9.2e-6

def blazedGratingGenerator(d, size, twoD, amp, xshift, yshift):
    blazedGrating = np.ones((1152, 1920))
    darray1 = np.arange(d)/d*amp
    darray2 = np.arange(d)/d*amp/2
    wphase = 0.4
    wphase1 = wphase*0.00173636280612265462
    wphase2 = wphase*0.001467636280612265462

    zero = np.sqrt(size)
    x0 = np.array([-zero+xshift, 0+xshift, zero+xshift])*wphase1/np.sqrt(2)
    x0index = x0//lx + 960
    x0index = x0index.astype(int)

    y0 = np.array([-zero+yshift, 0+yshift, zero+yshift])*wphase2/np.sqrt(2)
    y0index = y0//ly + 576
    y0index = y0index.astype(int)

    for i in np.arange(0, 1920, d):
        for j in np.arange(1152):
            x = (i -1920/2)*lx
            y = (j -1152/2)*ly
            blazedGrating[j, i:i+d] = darray1
            if twoD==2:
                if x0[0] < x and (x + d*lx)< x0[2] and y0[0] < y < y0[2]:
                    blazedGrating[j, i:i+d] = darray1
                elif x < x0[2] and (x + d*lx) > x0[2] and y0[0] < y < y0[2]:
                    blazedGrating[j, i:x0index[2]] = darray1[:x0index[2]-i]
                elif x0[0] > x and (x + d*lx) > x0[0] and y0[0] < y < y0[2]:
                    blazedGrating[j, x0index[0]:i+d] = darray1[-(i+d-x0index[0]):]
            else:
                if x0[0] < x and (x + d*lx)< x0[2]:
                    blazedGrating[j, i:i+d] = darray2
                elif x < x0[2] and (x + d*lx) > x0[2]:
                    blazedGrating[j, i:x0index[2]] = darray1[:x0index[2]-i]
                elif x0[0] > x and (x + d*lx) > x0[0]:
                    blazedGrating[j, x0index[0]:i+d] = darray1[-(i+d-x0index[0]):]
    return blazedGrating


def main(d, size, twoD, amp, xshift, yshift):
    data = phaseHG33(0.4).astype(np.float32)
    data += blazedGratingGenerator(d, size, twoD, amp, xshift, yshift)
    data = (data*127.5) % 255

    im = Image.fromarray(data)
    im.convert(mode='L').save(f'HG33_maxPur_blazed_{d}{size}{twoD}{amp}{xshift}{yshift}_Fri.bmp')

def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

if __name__ == "__main__":
    d = int(safe_list_get(sys.argv, 1, 64))
    size = float(safe_list_get(sys.argv, 2, 1.5))
    twoD = int(safe_list_get(sys.argv, 3, 2))
    amp = int(safe_list_get(sys.argv, 4, 2))
    xshift = float(safe_list_get(sys.argv, 5, 0))
    yshift = float(safe_list_get(sys.argv, 6, 0))
    main(d, size, twoD, amp, xshift, yshift)
