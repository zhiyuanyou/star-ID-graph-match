# -*- coding: utf-8 -*-
"""
This code is used to select the best parameter epsilon_mst. 

Written in 2020.02.17, revised in 2022.12.08
by Zhiyuan You
"""

import copy
import glob
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import random

from easydict import EasyDict

from utils.search.select_R_AD_helper import select_R_AD
from utils.search.graph_helper import gen_graph
from utils.common.mst_helper import gen_mst
from utils.noise_helper import add_noise


deg2rad = math.pi / 180
rad2deg = 180 / math.pi


def simulate_one(file_names, para):
    error_AD_sum_mst_list = []
    for f_read_name in file_names:
        with open(f_read_name) as fr:
            lines = fr.readlines()

        # generate mst
        lines = select_R_AD(lines, para)
        graph = gen_graph(lines, para)
        graph, _ = gen_mst(graph)
        AD_sum_mst = graph["AD_sum_mst"]

        # generate noise AS_sum_mst
        lines_noise = add_one_noise(lines, args, para)
        lines_noise = select_R_AD(lines_noise, para)
        graph_noise = gen_graph(lines_noise, para)
        graph_noise, _ = gen_mst(graph_noise)
        AD_sum_mst_noise = graph_noise["AD_sum_mst"]

        # calculate the error
        error_AD_sum_mst = abs(AD_sum_mst - AD_sum_mst_noise)
        error_AD_sum_mst_list.append(error_AD_sum_mst)

    return error_AD_sum_mst_list


def add_one_noise(lines, args, para):
    args_one = copy.deepcopy(args)
    noise_type = random.choice([0, 1, 2])
    if noise_type == 0:
        args_one.num_lost = 0
        args_one.num_false = 0
    elif noise_type == 1:
        args_one.std_position = 0
        args_one.num_false = 0
    elif noise_type == 2:
        args.std_position = 0
        args.num_lost = 0
    else:
        raise ValueError
    lines_noise = add_noise(lines, args, para)
    return lines_noise


if __name__ == "__main__":
    # simulation parameter
    para = EasyDict({})
    # Radius of AD that generate a graph
    para.R_AD = 6
    para.FOV_x = 20  # FOV
    para.FOV_y = 20
    para.N_x = 1024  # resolution
    para.N_y = 1024
    para.num_simu = 3

    # noise
    args = EasyDict({})
    args.std_position = 1
    args.num_lost = 1
    args.num_false = 1

    # ergodic every navigation star
    database_txt_dir = "./database/txt_star_image"
    file_names = glob.glob(os.path.join(database_txt_dir, "*.txt"))

    error_AD_sum_mst_list = []
    for i_simu in range(para.num_simu):
        print(f"Simulating: {i_simu + 1}")
        error_AD_sum_mst_list += simulate_one(file_names, para)

    error_max = max(error_AD_sum_mst_list)
    num_total = len(error_AD_sum_mst_list)

    # draw the results
    x_list = np.linspace(0, error_max, 500)
    y_list = []
    for epsilon_x in x_list:
        y_pro_epsilon = sum(error_AD_sum_mst_list <= epsilon_x) / num_total * 100
        y_list.append(y_pro_epsilon)

    plt.plot(x_list, y_list)
    plt.grid()
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylim(-3, 103)
    plt.xlabel("$\Delta^x$/°", fontsize=14)
    plt.ylabel("$Proportion$/%", fontsize=14)
    plt.title(
        "Proportion of simulations satisfying $\Delta$ < $\Delta^x$ with various $\Delta^x$",
    )
    plt.show()
