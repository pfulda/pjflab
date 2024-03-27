from math import factorial
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.special import eval_hermite as hermite
from PIL import Image
import sys
import argparse

# parser = argparse.ArgumentParser(description="Order of arguments: d (blazed grating size), size (the size of the attenuated area), twoD (if the attenuated area two D or one D), amp (the amplitude of the attenuated area)")
# args = parser.parse_args()
plt.style.use('seaborn-paper')
plt.rcParams["image.cmap"] = 'viridis'
plt.rcParams["font.family"] = "Arial"


lx = 9.2e-6
ly = 9.2e-6

def phaseHG33(wphase):
    wphase1 = wphase*0.00173636280612265462
    wphase2 = wphase*0.001467636280612265462
#     wphase1 = wphase*0.0016015
#     wphase2 = wphase*0.0016015
    zero = np.sqrt(1.5)
    x0 = np.array([-zero, 0, zero])*wphase1/np.sqrt(2)
    y0 = np.array([-zero, 0, zero])*wphase2/np.sqrt(2)
    
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

def blazedGratingGenerator(d):
    blazedGrating = np.ones((1152, 1920))
    darray1 = np.arange(d)/d*2
    wphase = 0.683
    wphase1 = wphase*0.00173636280612265462
    wphase2 = wphase*0.001467636280612265462


    for i in np.arange(0, 1920, d):
        for j in np.arange(1152):
            x = (i -1920/2)*lx
            y = (j -1152/2)*ly
            blazedGrating[j, i:i+d] = darray1
    return blazedGrating


def main(d):
    data = phaseHG33(0.683).astype(np.float32)
    data += blazedGratingGenerator(d)
    data = (data*127.5) % 255

    im = Image.fromarray(data)
    im.convert(mode='L').save(f'HG33_maxPur_blazed{d}.bmp')

def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

if __name__ == "__main__":
    d = int(safe_list_get(sys.argv, 1, 128))
    main(d)
