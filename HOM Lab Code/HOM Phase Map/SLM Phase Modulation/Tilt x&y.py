from math import factorial
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.special import eval_hermite as hermite
from PIL import Image
import sys

plt.style.use('seaborn-paper')
plt.rcParams["image.cmap"] = 'viridis'
plt.rcParams["font.family"] = "Arial"

l = 9.2e-6
cx = int(1920/2)
cy = int(1152/2)
wx0 = 1310e-6
wy0 = 1150e-6
lamb = 1064e-9

def defocus(alpha, index):
    x = np.arange(-960, 960)*l
    y = np.arange(-576, 576)*l
    xx, yy = np.meshgrid(x, y)
    rs = xx
    # rs = yy

    k = 255/lamb # 2 pi is 255 in the SLM language  # lens phase: k/(2f)*(x^2+y^2)
    defocus_map = rs*k*alpha
    data = (defocus_map)%255

    im = Image.fromarray(data)
    if index < 10:
        label = f"0{index}"
    else:
        label = f"{index}"
    im.convert(mode='L').save(f'./{label}.bmp') 


if __name__ == "__main__":

    dwell = 0.02

    powers = 200*np.sin(2*np.pi*np.arange(0, 1, dwell)) + 60
    powers *= 1e-6

    for idx, power in enumerate(powers):
        defocus(power, index=idx)
        print(f"Power-{power} success! {idx}/{len(powers)}")