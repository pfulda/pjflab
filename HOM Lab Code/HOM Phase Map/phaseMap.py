from math import factorial
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.special import eval_hermite as hermite
from PIL import Image
import sys
from HOMlab import *

plt.style.use('seaborn-paper')
plt.rcParams["image.cmap"] = 'viridis'
plt.rcParams["font.family"] = "Arial"

lx = 9.2e-6
ly = 9.2e-6
beamsize  = 0.00258/2
def phaseValue(x, y, x1, x2, y1, y2, sign):
    xrange = x2-x1
    xcenter = (x2+x1)/2
    yrange = y2 - y1
    ycenter = (y2 + y1)/2
    circle = ((((x-xcenter)/xrange)**2 + ((y-ycenter)/yrange)**2)*2)
    deviation = 0
    # deviation = np.exp(-circle*50)/20
    if sign == 0:
        return 0 + deviation
    elif sign == 1:
        return 1 - deviation

def phaseBMP(wphase, mode="33"):
    # wphase2 = wphase*0.00258/2
    # wphase1 = wphase*0.00258/2

    if mode=="11":
        phaseHG = phaseHG11(wphase)
    elif mode=="22":
        phaseHG = phaseHG22(wphase)
    elif mode=="33":
        phaseHG = phaseHG33(wphase)
    elif mode=="44":
        phaseHG = phaseHG44(wphase)
    elif mode=="55":
        phaseHG = phaseHG55(wphase) 

    data = phaseHG*127.5
    im = Image.fromarray(data)
    im.convert(mode='L').save(f'./HG{mode}_{wphase:.3f}.bmp')

def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

if __name__ == "__main__":
 #   wsize = safe_list_get(sys.argv, 1, 0.683)
 #  for size in np.linspace(0.27, 0.33, 6):
  #     phaseBMP(size)

 #   sizes = np.arange(0.33, 0.36, 0.003)
    sizes = np.arange(0.27, 0.31, 0.01)
    for idx, size in enumerate(sizes):
        phaseBMP(size, mode="33")
        print(f"Size-{size} success! {idx}/{len(sizes)}")