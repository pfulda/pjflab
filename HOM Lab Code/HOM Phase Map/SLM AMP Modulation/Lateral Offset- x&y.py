import numpy as np
from PIL import Image
from scipy import integrate

l = 9.2e-6
d = 16
cx = int(1920/2)
cy = int(1152/2)
wx0 = 1310e-6
wy0 = 1150e-6

def original_beam(): 
    x = (np.arange(0, 1920, d) - cx)/(wx0/l)
    y = (np.arange(0, 1152, d) - cy)/(wy0/l) 
    xx, yy = np.meshgrid(y, x)
    original = np.exp(-(xx**2+yy**2)/w**2)
    return original

def efficiency_norm(a, R=1):
    x = y = np.linspace(-R, R, 100)
    xx, yy = np.meshgrid(x, y)
    norm = gaussian_a(xx, yy, a).max()
    return norm

def gaussian_a(x, y, a=0):
    # return np.exp((-((x-a)**2+y**2) + x**2 + y**2)*(-1/w**2))
    return np.exp((-((y-a)**2+x**2) + x**2 + y**2)*(-1/w**2))

def contour_map_a(i, j, a=0, eff_norm=1):
    wx = wx0/l
    wy = wy0/l
    i = i-cx
    j = j-cy
    x = i/wx
    y = j/wy

    eff = gaussian_a(x, y, a)/eff_norm

    contour = eff*np.arange(d)/(d-1)*255
    return contour[::-1], eff

def power_cal(a, eff_norm=1):
    eff_map = []
    for i in np.arange(0, 1920, d):
        temp = []
        for j in np.arange(0, 1152, d):
            _, eff = contour_map_a(i, j, a=a, eff_norm=eff_norm)
            temp.append(eff)
        eff_map.append(temp)

    eff_map = np.array(eff_map)
    power = np.sum(eff_map*originalBeam)**2*(l*d)**2/originalBeamPower

    return power

def phase_image_a(a, index=0, eff_norm=1, power_norn=1):
    phase_d16 = np.zeros((1152, 1920))

    for i in np.arange(0, 1920, d):
        for j in np.arange(0, 1152, d):
            darray, _ = contour_map_a(i, j, a=a, eff_norm=eff_norm)
            phase_d16[j:j+d, i:i+d] = darray

    phase_d16 = phase_d16/power_norn

    im = Image.fromarray(phase_d16)
    if index < 10:
        label = f"0{index}"
    else:
        label = f"{index}"
    im.convert(mode='L').save(f'./{label}.bmp') 

R = 1
w = 1
originalBeam = original_beam()
originalBeamPower = np.sum(originalBeam)**2*(l*d)**2

if __name__ == "__main__":

    dwell = 0.02

    a_s = 0.1*np.sin(2*np.pi*np.arange(0, 1, dwell)) + 0.011

    # power_effs = []
    # for idx, a in enumerate(a_s):
    #     eff_norm = efficiency_norm(a, R=R)
    #     power_eff = power_cal(a, eff_norm=eff_norm,)
    #     power_effs.append(power_eff)

    A = 1
    c = 0
    power_effs = A*np.arange(1e-3, 1, dwell) + c
    power_effs = power_effs**0.5
    power_effs = power_effs/power_effs.min()

    for idx, a in enumerate(a_s):
        power_norn = power_effs[idx]
        # print(power_norn)
        power_norn = 1
        eff_norm = efficiency_norm(a, R=R)
        phase_image_a(a=a, index=idx, eff_norm=eff_norm, power_norn=power_norn)
        print(f"Lateral Offset-{a} success! {idx}/{len(a_s)}")

# alim = [-0.3, 0.3]. amp = 0.2, offset=-0.15
