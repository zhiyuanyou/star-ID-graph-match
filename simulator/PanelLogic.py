# -*- coding: utf-8 -*-
"""
星图仿真界面的逻辑类。

By You Zhiyuan 2020.3.25
"""

import os

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QColorDialog

from PanelUI import Ui_Panel
from StarSimu.StellarSimulation import StellarSimulation


class PanelLogic(QWidget, Ui_Panel):
    def __init__(self, parent=None):
        super(PanelLogic, self).__init__(parent)
        self.setupUi(self)
        self.pic_save_dir = ""
        self.txt_save_dir = ""
        self.database_star_dir = "./database"
        self.btn_cam_savedir.clicked.connect(self.Click_set_savedir)
        self.btn_take_pic.clicked.connect(self.Click_take_img)
        self.btn_VM_select.clicked.connect(self.Click_select_VM)
        self.btn_color_back.clicked.connect(lambda: self.Click_change_color("back"))
        self.btn_color_star.clicked.connect(lambda: self.Click_change_color("star"))
        self.btn_random_simu.clicked.connect(self.Click_random_simu)
        self.check_cam_save.stateChanged.connect(self.Change_save)
        self.check_cam_view.stateChanged.connect(self.Change_view)
        # self.view_cam.setScaledContents(True)  # 进行自适应图片显示
        self.obj_Stellar_Simulation = StellarSimulation(
            self.view_result, self.view_cam, self.check_cam_save, self.check_cam_view
        )
        self.Color_back = (0, 0, 0)
        self.Color_star = (255, 255, 255)

    def Click_set_savedir(self):
        tempdir = QtWidgets.QFileDialog.getExistingDirectory(self, "选取文件夹", "./")
        if len(tempdir):
            self.view_result.append("已设置储存路径: " + tempdir + "！")
            self.savedir_cam = tempdir
            # self.pic_save_dir 用于储存仿真星图
            self.pic_save_dir = os.path.join(self.savedir_cam, "pic")
            if not os.path.exists(self.pic_save_dir):
                os.makedirs(self.pic_save_dir)
            # self.txt_save_dir 用于储存星图数据
            self.txt_save_dir = os.path.join(self.savedir_cam, "txt")
            if not os.path.exists(self.txt_save_dir):
                os.makedirs(self.txt_save_dir)
            self.view_result.moveCursor(QtGui.QTextCursor.End)
        else:
            self.view_result.append("未成功设置储存路径！")

    def Click_take_img(self):
        RA_oa = self.SpinBox_RA_oa.value()
        Dec_oa = self.SpinBox_Dec_oa.value()
        Roll_oa = self.SpinBox_Roll_oa.value()
        FOV_x = self.SpinBox_FOV_x.value()
        FOV_y = self.SpinBox_FOV_y.value()
        N_x = self.SpinBox_res_x.value()
        N_y = self.SpinBox_res_y.value()
        R_max = self.SpinBox_star_R_max.value()
        R_min = self.SpinBox_star_R_min.value()
        VM_thre = round(self.SpinBox_star_VM.value(), 1)  # 由于该参数涉及到文件名，故用round去除一些数据误差

        RDR = [RA_oa, Dec_oa, Roll_oa]
        FOV = [FOV_x, FOV_y]
        N = [N_x, N_y]
        R = [R_max, R_min]
        Color = [self.Color_back, self.Color_star]
        Save_dir = [self.pic_save_dir, self.txt_save_dir]

        # 判断此时是否已经进行了亮度筛选，能否星图仿真
        f_star_path = os.path.join(
            self.database_star_dir, "sao_VM_thre" + str(VM_thre) + ".txt"
        )
        if not os.path.exists(f_star_path):
            self.view_result.append("星图仿真失败，请先进行亮度阈值为" + str(VM_thre) + "时的亮度筛选！")
        else:
            self.obj_Stellar_Simulation.img_simu_file(
                f_star_path, RDR, FOV, N, VM_thre, R, Color, Save_dir
            )
            self.view_result.append("星图仿真完成!")
        self.view_result.moveCursor(QtGui.QTextCursor.End)

    def Click_select_VM(self):
        f_all_star_path = os.path.join(self.database_star_dir, "sao")
        VM_thre = round(self.SpinBox_star_VM.value(), 1)  # 由于该参数涉及到文件名，故用round去除一些数据误差
        f_star_path = os.path.join(
            self.database_star_dir, "sao_VM_thre" + str(VM_thre) + ".txt"
        )
        if not os.path.exists(f_star_path):
            self.obj_Stellar_Simulation.select_VM(f_all_star_path, f_star_path, VM_thre)
            self.view_result.append("亮度阈值为" + str(VM_thre) + "时的亮度筛选完成！")
        else:
            self.view_result.append("亮度阈值为" + str(VM_thre) + "时的亮度筛选已进行过，无需重复进行！")
        self.view_result.moveCursor(QtGui.QTextCursor.End)

    def Click_random_simu(self):
        num_simu = self.SpinBox_num.value()
        FOV_x = self.SpinBox_FOV_x.value()
        FOV_y = self.SpinBox_FOV_y.value()
        N_x = self.SpinBox_res_x.value()
        N_y = self.SpinBox_res_y.value()
        R_max = self.SpinBox_star_R_max.value()
        R_min = self.SpinBox_star_R_min.value()
        VM_thre = round(self.SpinBox_star_VM.value(), 1)  # 由于该参数涉及到文件名，故用round去除一些数据误差

        FOV = [FOV_x, FOV_y]
        N = [N_x, N_y]
        R = [R_max, R_min]
        Color = [self.Color_back, self.Color_star]
        Save_dir = [self.pic_save_dir, self.txt_save_dir]

        # 判断此时是否已经进行了亮度筛选，能否星图仿真
        f_star_path = os.path.join(
            self.database_star_dir, "sao_VM_thre" + str(VM_thre) + ".txt"
        )
        if not os.path.exists(f_star_path):
            self.view_result.append("星图仿真失败，请先进行亮度阈值为" + str(VM_thre) + "时的亮度筛选！")
        else:
            self.obj_Stellar_Simulation.random_simu(
                f_star_path, num_simu, FOV, N, VM_thre, R, Color, Save_dir
            )
        self.view_result.moveCursor(QtGui.QTextCursor.End)

    def Click_change_color(self, para):
        Color = QColorDialog.getColor()
        Color_rgb = Color.getRgb()
        Color_rgb = (Color_rgb[0], Color_rgb[1], Color_rgb[2])
        if Color.isValid():
            if para == "back":
                self.Color_back = Color_rgb
                self.label_color_back.setStyleSheet(
                    "QWidget {background-color:%s}" % Color.name()
                )
            elif para == "star":
                self.Color_star = Color_rgb
                self.label_color_star.setStyleSheet(
                    "QWidget {background-color:%s}" % Color.name()
                )
            else:
                raise ValueError("The value of para should be 'back' or 'star' ")
        else:
            self.view_result.append("未成功选择颜色！")

    def Change_save(self, para):
        check_save = self.check_cam_save
        if check_save.checkState():
            if not hasattr(self, "savedir_cam"):
                check_save.setCheckState(False)
                self.view_result.append("设置储存失败: 请先进行设置存储路径!")
        self.view_result.moveCursor(QtGui.QTextCursor.End)

    def Change_view(self):
        check_view = self.check_cam_view
        view = self.view_cam
        if not check_view.checkState():
            view.clear()
        self.view_result.moveCursor(QtGui.QTextCursor.End)
