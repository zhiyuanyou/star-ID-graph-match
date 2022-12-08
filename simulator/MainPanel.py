# -*- coding: utf-8 -*-
"""
星图仿真界面的主函数。

By You Zhiyuan 2020.3.25
"""

import sys

from PyQt5 import QtWidgets

from PanelLogic import PanelLogic


if __name__ == "__main__":
    # 实例化QApplication类，作为GUI主程序入口
    app = QtWidgets.QApplication(sys.argv)
    # 实例化界面并展示
    DetectPanel = PanelLogic()
    DetectPanel.show()
    # 当需要结束主循环过程释放内存时，使用sys.exit()。又exec是python关键字，为了以示区别，写成exec_。
    sys.exit(app.exec_())
