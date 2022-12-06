# -*- coding: utf-8 -*-
"""
This code is used to generated the k-vector of AD sum in mst for a rough search.

The generated k_vector & [q,m] are saved for future search.

Note that in order to fully understand the variable names & algorithms in this 
code, please readthe paper of k-vector 'k-Vector Range Searching Techniques' by 
Mortari in 2014.

This code also provide an example of how to use k-vector for a rough search.

Written in 2020.01.26, revised in 2022.12.06
by Zhiyuan You
"""


import numpy as np


# find proposed match graphs through the rough search of the AD sum in mst
# input:
# the AD sum which is for the rough search
# output:
# the start index & end index of the proposed match graphs
def search_k_vector(AD_mst_search, k_vector, q, m, epsilon_AD):
    k_length = len(k_vector)
    # search region: [y_down,y_up]
    y_down = AD_mst_search - epsilon_AD
    y_up = AD_mst_search + epsilon_AD
    # search start index & search end index
    # Because of the 'epsilon_AD', the 'int(np.floor((y_down-q)/m))' & int(np.ceil((y_up-q)/m)) may beyond the region [0,k_length-1],
    # so there is a clip function.
    i_start = k_vector[np.clip(int(np.floor((y_down - q) / m)), 0, k_length - 1)]
    i_end = k_vector[np.clip(int(np.ceil((y_up - q) / m)), 0, k_length - 1)] - 1
    return i_start, i_end
