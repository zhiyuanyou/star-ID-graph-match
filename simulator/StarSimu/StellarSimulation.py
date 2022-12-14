# -*- coding: utf-8 -*-
"""
This code is used to generate simulation star images through RightAscension & 
Declination of the stars in FOV of CCD.

Revised in 3/25/2020
By YouZhiyuan
"""

import cv2
import math
import numpy as np
import os

from PyQt5 import QtGui, QtCore


# CN: CatalogNumber
# VM: VisualMagnitude
# RA: RightAscension
# Dec:  Declination
# Roll: RollAngle
# oa: optical axis
# AD: angular distance
# vx,vy,vz: unit vector generated by RA & Dec or pixel coordinate
# x,y: the project coordinate
# _rot: rotation
# _simu: simulation
# _thre: threshold
# _s: star
# 为使得代码简练易读，对部分同类参数进行了合并，如下：
# RDR: RA_oa,Dec_oa,Roll_oa
# FOV: FOV_x,FOV_y
# N: N_x,N_y
# R: R_max,R_min
# Color: Color_back,Color_star


# simulation parameter
deg2rad = math.pi / 180
rad2deg = 180 / math.pi
RA_range = [0, 2 * math.pi]
Dec_range = [-math.pi / 2, math.pi / 2]
Roll_range = [0, 2 * math.pi]


# the project model of one star
def project_1s(Dec, RA, Roll, Dec_i, RA_i, N_x, N_y, FOV_x, FOV_y):
    # input:
    # Dec,RA，Roll: the Dec & RA & Roll of the optical axis
    # Dec_i,RA_i: the Dec & RA of the ith star
    # N_x,N_y: the resolution of the picture
    # FOV_x,FOV_y: the FOV of the CCD
    # calculate the rotate matrix Rx by theta_x
    # output:
    # x_s_rot, y_s_rot: the pixel coordinate of the image
    theta_x = -(math.pi / 2 - Dec)
    Rx = [
        [1, 0, 0],
        [0, np.cos(theta_x), np.sin(theta_x)],
        [0, -np.sin(theta_x), np.cos(theta_x)],
    ]
    # calculate the rotate matrix Rz by theta_z
    theta_z = -(math.pi / 2 - RA)
    Rz = [
        [np.cos(theta_z), np.sin(theta_z), 0],
        [-np.sin(theta_z), np.cos(theta_z), 0],
        [0, 0, 1],
    ]
    R = np.matmul(Rx, Rz)
    # calculate the inertial vector in inertial space
    v_inertial = [
        np.cos(RA_i) * np.cos(Dec_i),
        np.sin(RA_i) * np.cos(Dec_i),
        np.sin(Dec_i),
    ]
    # transfer the inertial vector to body vector in CCD space
    v_body = np.matmul(R, v_inertial)
    # project to the pixel coordinate (the space origin is the center of the image)
    Xr = -v_body[0] / v_body[2] * N_x / 2 / np.tan(FOV_x / 2 * deg2rad)
    Yr = -v_body[1] / v_body[2] * N_y / 2 / np.tan(FOV_y / 2 * deg2rad)
    # rotate the stars
    R_rotate = np.array([[np.cos(Roll), np.sin(Roll)], [-np.sin(Roll), np.cos(Roll)]])
    xy_s_rot = np.matmul(R_rotate, np.array([[Xr], [Yr]]))
    x_s_rot = xy_s_rot[0][0]
    y_s_rot = xy_s_rot[1][0]
    return x_s_rot, y_s_rot


# simulate the stellar image
def img_simu_lines(lines, RDR, FOV, N, VM_thre, R, Color):
    # input:
    # RDR: RA_oa,Dec_oa,Roll_oa
    # FOV: FOV_x,FOV_y
    # N: N_x,N_y
    # R: R_max,R_min
    # Color: Color_back,Color_star
    # output:
    # stellar image: img
    # stellar data: txt_list
    num_star = len(lines)
    RA_oa, Dec_oa, Roll_oa = RDR
    FOV_x, FOV_y = FOV
    N_x, N_y = N
    R_max, R_min = R
    Color_back, Color_star = Color
    # calculate the maximum FOV
    FOV_max = (
        np.arctan(
            np.sqrt(np.tan(FOV_x / 2 * deg2rad) ** 2 + np.tan(FOV_y / 2 * deg2rad) ** 2)
        )
        * rad2deg
    )
    # generate unit vector for calculating angular distance
    vx_oa = np.cos(RA_oa) * np.cos(Dec_oa)
    vy_oa = np.sin(RA_oa) * np.cos(Dec_oa)
    vz_oa = np.sin(Dec_oa)
    # save txt file and image
    txt_list = []
    img = np.zeros((N_y, N_x, 3), np.uint8)  # in numpy:(height,width), so:(N_y,N_x)
    img[:, :, 0] += Color_back[0]
    img[:, :, 1] += Color_back[1]
    img[:, :, 2] += Color_back[2]
    for i_s in range(num_star):
        data_s = lines[i_s].strip().split()
        assert len(data_s) == 4
        # generate unit vector for calculating angular distance
        CN_s, VM_s, RA_s, Dec_s = data_s
        CN_s, VM_s, RA_s, Dec_s = int(CN_s), float(VM_s), float(RA_s), float(Dec_s)
        vx_s = np.cos(RA_s) * np.cos(Dec_s)
        vy_s = np.sin(RA_s) * np.cos(Dec_s)
        vz_s = np.sin(Dec_s)
        # AD_oa_s: the angular distance between optical axis & star
        cos = vx_oa * vx_s + vy_oa * vy_s + vz_oa * vz_s
        AD_oa_s = np.arccos(np.clip(cos, -1, 1)) * rad2deg
        # x_s, y_s: the project coordinate of neighbor star
        x_s, y_s = project_1s(
            Dec_oa, RA_oa, Roll_oa, Dec_s, RA_s, N_x, N_y, FOV_x, FOV_y
        )
        if AD_oa_s <= FOV_max:
            if abs(x_s) > N_x / 2 or abs(y_s) > N_y / 2:
                # print('Some stars fall out of the image! ')
                pass
            else:
                # save txt file
                txt_list.append(f"{CN_s} {VM_s} {x_s} {y_s} {RA_s} {Dec_s}")
                # save image
                x_pixel = int(x_s + N_x / 2)  # in cv2: (x,y)
                y_pixel = int(y_s + N_y / 2)
                R = min(
                    int((VM_thre - VM_s) / VM_thre * R_max) + 1, R_max
                )  # the darkest is 1, the brightest is R_max
                cv2.circle(img, (x_pixel, y_pixel), R, Color_star, -1)
    return img, txt_list


# 随机仿真多张星图的线程类
# 由于随机仿真的星图数量过多会堵塞线程，需要另开线程用于随机仿真多张星图
class RandomSimuThread(QtCore.QThread):
    #  通过类成员对象定义信号对象
    signal_view = QtCore.pyqtSignal(list)

    def __init__(
        self,
        num_simu,
        if_cam_view,
        if_cam_save,
        view_result,
        f_star_path,
        FOV,
        N,
        VM_thre,
        R,
        Color,
        Save_dir,
    ):
        super(RandomSimuThread, self).__init__()
        self.num_simu = num_simu
        self.if_cam_view = if_cam_view
        self.if_cam_save = if_cam_save
        self.view_result = view_result
        # read the SAO database
        f_star = open(f_star_path, "r+")
        self.lines = f_star.readlines()
        f_star.close()
        self.num_star = len(self.lines)
        self.FOV = FOV
        self.N = N
        self.R = R
        self.VM_thre = VM_thre
        self.Color = Color
        self.pic_save_dir, self.txt_save_dir = Save_dir = Save_dir

    # 为线程定义一个函数
    def run(self):
        for i in range(self.num_simu):
            # 随机选择镜头的方位
            RA_oa = np.random.random() * (RA_range[1] - RA_range[0]) + RA_range[0]
            Dec_oa = np.random.random() * (Dec_range[1] - Dec_range[0]) + Dec_range[0]
            Roll_oa = (
                np.random.random() * (Roll_range[1] - Roll_range[0]) + Roll_range[0]
            )
            RDR = [RA_oa, Dec_oa, Roll_oa]
            # 进行星图仿真
            img, txt_list = img_simu_lines(
                self.lines, RDR, self.FOV, self.N, self.VM_thre, self.R, self.Color
            )
            # 通过信号槽显示图片
            if self.if_cam_view.checkState():
                self.signal_view.emit(list(img))
            # 保存星图图片和星图数据
            if self.if_cam_save.checkState():
                # save txt file
                txt_path = os.path.join(
                    self.txt_save_dir, f"RA{RA_oa}-Dec{Dec_oa}-Roll{Roll_oa}.txt"
                )
                txt_file = open(txt_path, "w+")
                txt_file.write("\n".join(txt_list))
                txt_file.close()
                # save generated image
                img_path = os.path.join(
                    self.pic_save_dir, f"RA{RA_oa}-Dec{Dec_oa}-Roll{Roll_oa}.jpg"
                )
                cv2.imwrite(img_path, img)
        self.view_result.append(str(self.num_simu) + "张随机星图仿真完成!")


# 星图仿真的主大类
class StellarSimulation:
    def __init__(self, view_result, view_cam, check_cam_save, check_cam_view):
        self.view_result = view_result
        self.view_cam = view_cam
        self.if_cam_save = check_cam_save
        self.if_cam_view = check_cam_view

    # 进行单张星图仿真的函数
    def img_simu_file(self, f_star_path, RDR, FOV, N, VM_thre, R, Color, Save_dir):
        # 读取星表数据
        f_star = open(f_star_path, "r+")
        lines = f_star.readlines()
        f_star.close()
        # 进行星图仿真
        img, txt_list = img_simu_lines(lines, RDR, FOV, N, VM_thre, R, Color)
        # 展示星图
        if self.if_cam_view.checkState():
            height, width, _ = img.shape
            # 将图像缩放为窗口的0.9以进行自适应显示，进行自适应显示的时候，图片的尺寸必须小于label的尺寸，否则会撑大label，出现溢出现象
            cam_height = self.view_cam.height()
            cam_width = self.view_cam.width()
            cam_ratio = min(cam_height * 0.9 / height, cam_width * 0.9 / width)
            cam_size = (int(cam_ratio * width), int(cam_ratio * height))
            img_view = cv2.resize(img, cam_size, interpolation=cv2.INTER_CUBIC)
            QtImg_cam = QtGui.QImage(
                img_view[:],
                img_view.shape[1],
                img_view.shape[0],
                img_view.shape[1] * 3,
                QtGui.QImage.Format_RGB888,
            )
            self.view_cam.setPixmap(QtGui.QPixmap.fromImage(QtImg_cam))
        # 保存星图图片和星图数据
        RA_oa, Dec_oa, Roll_oa = RDR
        pic_save_dir, txt_save_dir = Save_dir
        if self.if_cam_save.checkState():
            # save txt file
            txt_path = os.path.join(
                txt_save_dir, f"RA{RA_oa}-Dec{Dec_oa}-Roll{Roll_oa}.txt"
            )
            txt_file = open(txt_path, "w+")
            txt_file.write("\n".join(txt_list))
            txt_file.close()
            # save generated image
            img_path = os.path.join(
                pic_save_dir, f"RA{RA_oa}-Dec{Dec_oa}-Roll{Roll_oa}.jpg"
            )
            cv2.imwrite(img_path, img)

    # 根据亮度阈值进行恒星筛选的函数
    def select_VM(self, f_all_star_path, f_star_path, VM_thre):
        f_all_star = open(f_all_star_path)
        lines = f_all_star.readlines()
        f_all_star.close()
        f_star = open(f_star_path, "w+")
        # select the stars whose VM is less than VM_thre
        CN_list = []
        VM_list = []
        RA_list = []
        Dec_list = []
        for line in lines:
            # line: len(line) = 205, line[204] = '\n'
            CN = line[0:6]
            VM = line[80:84]
            RA = line[183:193]
            Dec = line[193:204]
            if float(VM) < VM_thre:
                f_star.write(f"{CN} {VM} {RA} {Dec}\n")
                CN_list.append(CN)
                VM_list.append(VM)
                RA_list.append(RA)
                Dec_list.append(Dec)
        f_star.close()

    # 进行随机仿真多张星图的函数
    def random_simu(self, f_star_path, num_simu, FOV, N, VM_thre, R, Color, Save_dir):
        # 创建随机仿真多张星图的线程
        self.hThreadHandle = RandomSimuThread(
            num_simu,
            self.if_cam_view,
            self.if_cam_save,
            self.view_result,
            f_star_path,
            FOV,
            N,
            VM_thre,
            R,
            Color,
            Save_dir,
        )
        self.hThreadHandle.signal_view.connect(self.call_back_cam)
        self.hThreadHandle.start()

    # 在界面上展示图像的回调函数
    def call_back_cam(self, img):
        img = np.array(img)
        height, width, _ = img.shape
        # 将图像缩放为窗口的0.9以进行自适应显示，进行自适应显示的时候，图片的尺寸必须小于label的尺寸，否则会撑大label，出现溢出现象
        cam_height = self.view_cam.height()
        cam_width = self.view_cam.width()
        cam_ratio = min(cam_height * 0.9 / height, cam_width * 0.9 / width)
        cam_size = (int(cam_ratio * width), int(cam_ratio * height))
        img_view = cv2.resize(img, cam_size, interpolation=cv2.INTER_CUBIC)
        QtImg_cam = QtGui.QImage(
            img_view.data,
            img_view.shape[1],
            img_view.shape[0],
            img_view.shape[1] * 3,
            QtGui.QImage.Format_RGB888,
        )
        self.view_cam.setPixmap(QtGui.QPixmap.fromImage(QtImg_cam))
