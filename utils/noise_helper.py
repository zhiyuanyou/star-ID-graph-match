# -*- coding: utf-8 -*-
"""
This code is used to generate the simulation star image in the noise of pixel. 
The pixel of the pixel noise satisfies guassian distribution, with the 
average 0 & the standard deviation sigma_pn, which is a hyper parameter.

This code is used to generate the simulation star image in the noise of lost 
star. Each star has the possibility to be lost except the main star. In practice, 
if the main star is lost, there is a large possibility of failure. 

This code is used to generate the simulation star image in the noise of spike. 
A spike is the noise that looks the same with the star. The noise is randomly 
added into the image according to randoly generated pixel coordinates. 

Written in 2020.01.26, revised in 2022.12.06
By Zhiyuan You
"""


import numpy as np
import random


# CN: CatalogNumber
# VM: VisualMagnitude
# RA: RightAscension
# Dec:  Declination
# vx,vy,vz: unit vector generated by RA & Dec or pixel coordinate
# x,y: the project coordinate
# AD: angular distance
# R: radius
# _ms: main star
# _ns: neighbor star
# _thre: threshold
# _pn: pixel noise


def add_noise(lines, args, para):
    if args.std_position:
        add_position_noise(lines, args.std_position)
    if args.num_lost:
        add_lost_noise(lines, args.num_lost)
    if args.num_false:
        add_false_noise(lines, args.num_false, para)
    return lines


# assume pn(pixel noise)'s distributes according to gaussian nosie. The average
# of the pn is 0, the std(standard deviation) is sigma_pn.
def add_position_noise(lines, sigma_pn):
    lines_pn = []
    for i_ns in range(len(lines)):
        data_ns = lines[i_ns].strip().split()
        assert len(data_ns) == 6
        CN_ns, _, x_ns, y_ns, _, _ = data_ns
        CN_ns, x_ns, y_ns = int(CN_ns), float(x_ns), float(y_ns)

        # add pixel noise to neighbor star
        x_pn = np.clip(sigma_pn * np.random.randn(1)[0], -3 * sigma_pn, 3 * sigma_pn)
        y_pn = np.clip(sigma_pn * np.random.randn(1)[0], -3 * sigma_pn, 3 * sigma_pn)
        x_ns_pn = x_ns + x_pn
        y_ns_pn = y_ns + y_pn

        line_ns = f"{CN_ns} {None} {x_ns_pn} {y_ns_pn} {None} {None}"
        lines_pn.append(line_ns)

    return lines_pn


def add_lost_noise(lines, num_lost):
    # randomly choose num_lost neighbor stars to be lost
    i_lost = random.sample(list(range(1, len(lines))), num_lost)
    i_lost = sorted(i_lost, reverse=True)
    for i in i_lost:
        lines.pop(i)
    return lines


def add_false_noise(lines, num_false, para):
    # randomly add num_false neighbor stars
    # CN: 0, VM: None, RA: None, Dec: None, they are all impossible to occur.
    for _ in range(num_false):
        x_sn = (-1 + 2 * random.random()) * para.N_x // 2
        y_sn = (-1 + 2 * random.random()) * para.N_y // 2
        line_false = f"0 {None} {x_sn} {y_sn} {None} {None}"
        lines.append(line_false)
    return lines
