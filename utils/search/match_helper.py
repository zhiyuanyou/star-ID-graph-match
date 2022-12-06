# -*- coding: utf-8 -*-
"""
This code is used to search the best match between the test graph & the databse 
graph. The graph match algorithm is relatively slow so far. However, it is very 
important that it is not a single star match or a pattern match, when the graph 
match is done, every star in the graph is matched with the database. 

Written in 2020.01.26, revised in 2022.12.06
by Zhiyuan You
"""


import copy
import numpy as np


# match 2 graphs & calculate the error after match
# input:
# 2 adjacency matrix of 2 graphs for match
# output:
# the match error of 2 graphs
def match_graph(M_adj_g1, M_adj_g2, para):
    # the number of vertex in 2 graph
    num_g1, _ = M_adj_g1.shape
    num_g2, _ = M_adj_g2.shape

    # construct all possible vertex pairs for match.
    # In the affinity matrix, the vertex pairs are in the diagnal, this is where
    # the variable name 'i_diag' comes from.
    i_diag = []
    for i_g1 in range(num_g1):
        for i_g2 in range(num_g2):
            i_diag.append((i_g1, i_g2))

    # construct the affinity matrix
    M_affi = np.zeros((num_g1 * num_g2, num_g1 * num_g2))
    for i in range(num_g1 * num_g2):
        for j in range(i, num_g1 * num_g2):
            # if there is a vertex, the element of the M_affi should be 0.
            if i_diag[i][0] == i_diag[j][0] or i_diag[i][1] == i_diag[j][1]:
                pass
            # if there are 2 edges, the none-diagnal of M_affi should be calculated.
            else:
                i_g1_s1 = i_diag[i][0]
                i_g1_s2 = i_diag[j][0]
                i_g2_s1 = i_diag[i][1]
                i_g2_s2 = i_diag[j][1]
                edge_g1 = M_adj_g1[i_g1_s1][i_g1_s2]
                edge_g2 = M_adj_g2[i_g2_s1][i_g2_s2]
                affi_value = 1 / np.exp(para.times_sub_AD * abs(edge_g1 - edge_g2))
                M_affi[i][j] = affi_value
                M_affi[j][i] = affi_value

    # find the eigenvalue & eigenvector
    eigenvalue, eigenvector = np.linalg.eig(M_affi)
    # find the maximum eigenvalue
    max_eigenvalue = np.max(eigenvalue)
    i_max_eigenvalue = np.argmax(eigenvalue)
    # find the principal eigenvector
    prin_eigenvector = copy.deepcopy(eigenvector[:, i_max_eigenvalue])
    # make sure all the elements of the prin_eigenvector have the same plus-minus
    assert (
        sum(prin_eigenvector >= 0) == num_g1 * num_g2
        or sum(prin_eigenvector <= 0) == num_g1 * num_g2
    )
    # make sure all the elements of the prin_eigenvector are positive
    if sum(prin_eigenvector <= 0) == num_g1 * num_g2:
        prin_eigenvector = -prin_eigenvector

    # construct the 0-1 vector which indicates the match result
    vector_judge = np.array([None] * (num_g1 * num_g2))
    sum_1_0 = sum(vector_judge == 0) + sum(vector_judge == 1)
    # only if all values in vector_judge are 0 or 1, terminate.
    while not sum_1_0 == num_g1 * num_g2:
        max_elem = np.max(prin_eigenvector)
        i_max_elem = np.argmax(prin_eigenvector)
        vector_judge[i_max_elem] = 1
        prin_eigenvector[i_max_elem] = -float("inf")
        i_g1_max = i_diag[i_max_elem][0]
        i_g2_max = i_diag[i_max_elem][1]
        for i in range(num_g1 * num_g2):
            i_g1, i_g2 = i_diag[i]
            if not (i_g1 == i_g1_max and i_g2 == i_g2_max):
                if i_g1 == i_g1_max or i_g2 == i_g2_max:
                    vector_judge[i] = 0
                    prin_eigenvector[i] = -float("inf")
        sum_1_0 = sum(vector_judge == 0) + sum(vector_judge == 1)

    # construct 2 vertex list represent the match result
    i_g1_list = []
    i_g2_list = []
    for i in range(num_g1 * num_g2):
        if vector_judge[i] == 1:
            i_g1 = i_diag[i][0]
            i_g2 = i_diag[i][1]
            i_g1_list.append(i_g1)
            i_g2_list.append(i_g2)

    # construct 2 adjancency matrix that could calculate the error
    assert len(i_g1_list) == len(i_g2_list)
    num_match = len(i_g1_list)
    M_adj_g1_match = np.zeros((num_match, num_match))
    M_adj_g2_match = np.zeros((num_match, num_match))
    for i in range(num_match):
        i_g1_s1 = i_g1_list[i]
        i_g2_s1 = i_g2_list[i]
        for j in range(i + 1, num_match):
            i_g1_s2 = i_g1_list[j]
            i_g2_s2 = i_g2_list[j]
            M_adj_g1_match[i][j] = M_adj_g1[i_g1_s1][i_g1_s2]
            M_adj_g1_match[j][i] = M_adj_g1_match[i][j]
            M_adj_g2_match[i][j] = M_adj_g2[i_g2_s1][i_g2_s2]
            M_adj_g2_match[j][i] = M_adj_g2_match[i][j]

    # use the default norm(F norm) to represent the error
    error = np.linalg.norm(M_adj_g1_match - M_adj_g2_match) / num_match
    return error
