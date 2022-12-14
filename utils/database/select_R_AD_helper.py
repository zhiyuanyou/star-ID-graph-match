# -*- coding: utf-8 -*-
"""
This code is used to select the star in R_AD and generate new txt file & image.

Note that R_AD<min(FOV_x,FOV_y), & R_AD is a hyper parameter. 

Written in 2020.01.26, revised in 2022.12.06
By Zhiyuan You
"""

import math
import numpy as np


# CN: CatalogNumber
# VM: VisualMagnitude
# RA: RightAscension
# Dec:  Declination
# vx,vy,vz: unit vector generated by RA & Dec or pixel coordinate
# x,y: the project coordinate
# AD: angular distance
# _ms: main star
# _ns: neighbor star
# _thre: threshold


deg2rad = math.pi / 180
rad2deg = 180 / math.pi


def select_R_AD(lines, para):
    data_ms = lines[0].strip().split()
    assert len(data_ms) == 6

    # generate unit vector for calculating angular distance
    CN_ms, _, _, _, RA_ms, Dec_ms = data_ms
    CN_ms, RA_ms, Dec_ms = int(CN_ms), float(RA_ms), float(Dec_ms)
    vz_ms = np.sin(Dec_ms)
    vx_ms = np.cos(RA_ms) * np.cos(Dec_ms)
    vy_ms = np.sin(RA_ms) * np.cos(Dec_ms)

    for i_ns in range(len(lines) - 1, 0, -1):
        data_ns = lines[i_ns].strip().split()
        assert len(data_ns) == 6
        CN_ns, _, _, _, RA_ns, Dec_ns = data_ns
        CN_ns, RA_ns, Dec_ns = int(CN_ns), float(RA_ns), float(Dec_ns)

        # generate unit vector for calculating angular distance
        vz_ns = np.sin(Dec_ns)
        vx_ns = np.cos(RA_ns) * np.cos(Dec_ns)
        vy_ns = np.sin(RA_ns) * np.cos(Dec_ns)

        # if there are some numerous errors, |cos| may slightly > 1
        cos = vx_ns * vx_ms + vy_ns * vy_ms + vz_ns * vz_ms
        AD_ms_ns = np.arccos(np.clip(cos, -1, 1)) * rad2deg
        if AD_ms_ns > para.R_AD:
            lines.pop(i_ns)

    return lines
