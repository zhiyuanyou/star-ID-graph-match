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


def gen_k_vertor(graph_list, para):
    # create the 2 points: (0,AD_mst_min-kexi),(star_num-1,AD_mst_max+kexi)
    star_num = len(graph_list)
    AD_mst_min = graph_list[0]["AD_sum_mst"]
    AD_mst_max = graph_list[-1]["AD_sum_mst"]
    # the uncertainty caused by the machine error.
    kexi_machine = para.epsilon_machine * max(abs(AD_mst_min), abs(AD_mst_max))

    # Note that since python's index begin at 0, but the k-vector paper's index begin at 1, so there are some small differences.
    # the linear equation: z = mx + q, 2 points: (0,AD_mst_min-kexi),(star_num-1,AD_mst_max+kexi).
    m = (AD_mst_max - AD_mst_min + 2 * kexi_machine) / (star_num - 1)
    q = AD_mst_min - kexi_machine

    # generate the k-vector
    k_vector = []
    for i in range(star_num):
        z = m * i + q
        k_temp = 0
        for graph in graph_list:
            if graph["AD_sum_mst"] <= z:
                k_temp += 1
            else:
                break
        k_vector.append(k_temp)
    return k_vector, q, m


"""
Following is an example of how to use k-vector to search a known AD_mst_search. 
input: 
    the sum of angular distance in minimum spanning tree: AD_mst_search
output:
    the search start index & search end index: i_start & i_end
hyper parameter: 
    the uncertainty of AD_mst_search: epsilon_AD


import numpy as np

AD_mst_search = 30.35  # the sum AD in mst for search
epsilon_AD = 0.3  # this is a hyper parameter, which need to be adjust
# search region: [y_down,y_up]
y_down = AD_mst_search - epsilon_AD
y_up = AD_mst_search + epsilon_AD
# search start index & search end index
i_start = k_vector[int(np.floor((y_down - q) / m))]
i_end = k_vector[int(np.ceil((y_up - q) / m))] - 1

print("The start index: " + str(i_start) + ", the AD left bound: " + str(y_down))
print("The end index: " + str(i_end) + ", the AD right bound: " + str(y_up))
"""
