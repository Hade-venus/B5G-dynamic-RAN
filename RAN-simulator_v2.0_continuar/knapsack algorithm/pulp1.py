# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 14:10:14 2023

@author: Shaoxuan
"""

import pulp as pl 
from pulp import *
import pandas as pd
import numpy as np


def Link_reassignment(inputData):

    # Get data from inputData dict

    F=inputData["F"] #set of tarffic flows
    D=inputData["D"] #set of edge d
    S=inputData["S"] # set of of spectrum for the request
    W=inputData["W"] #set of nodes
    T=inputData["T"] # request's target nodes
    k_d=inputData["k_d"] #capacity of link edge d
    q_f=inputData["q_f"] #amount of capacity in the edge d
    c_m=inputData["c_m"] #cost of optical node
    #h_fs=inputData["h_fs"] # if flow f belongs to the service type s
    delta_fd= inputData["delta_fd"] # if flow f can be assigned to link edge d
    M=inputData["M"]
    #E_in=inputData["E_in"] # if flow or link e leaves from node n
    #E_on=inputData["E_on"] # if flow or link e arrives at node n
    print(F)
    print(D)
    print(S)
    print(W)
    print(T)
    nF = len(F)
    nD = len(D)
    nS = len(S)
    nW = len(W)
    nT=  len(T)


    # Create the problem
    my_lp_problem = pl.LpProblem('Link_reassignment', pl.LpMinimize)
   # Create the decision varibles

    x_fd =[pulp.LpVariable("x{0}{1}".format(f, d), cat="Binary") for f in range(nF) for d in range(nD)] # x=1 if flow i is routed through edge d
    y_sd=[pulp.LpVariable("y{0}{1}".format(s, d), cat="Continuous") for s in range(nS) for d in range(nD)] # amount of traffic in edge d
    z_d=[pulp.LpVariable("z{0}".format(d), cat="Binary") for d in range(nD)] # z=1 if edge d is used
    w_m=[pulp.LpVariable("w{0}".format(m), cat="Binary") for m in range(nW)] # w=1 if node m is used
    print(x_fd)
    print(y_sd)
    print(z_d)
    print(w_m)

    print(delta_fd)

    # add objective function
    objFunc = sum(c_m[m]*w_m[m] for m in range(nW))
    my_lp_problem.setObjective(objFunc)

    # add constraint 1: node-link formulation Xfe
    for t in range(nT):
        my_lp_problem += (sum(delta_fd[f][d]*x_fd[f*nD+d] for f in range(nF) for d in range(len(D)))-T*w_m[m] for m in range(nW)) == 0 

    # add constraint 2: aggregation node-link formualtion
    for f in range(nF):
            my_lp_problem += (x_fd[f*nD+d] - M*z_d[d] for d in range(len(D))) <= 0

    # add constraint 3:link capcaity fromulation
    for d in range(len(D)):
        my_lp_problem += (sum(y_sd[s*nD+d] for s in range(len(S))) - k_d[d]) <= 0
    # add constraint 4: edge e less or equal to 1 
    for w in range(nW):
        my_lp_problem +=(sum(z_d[d] for m in range(len(W))))<=1  
    # add constraint 5: edge e less or equal to M*Wm   
    for w in range(nW):
        for d in range(nD):
         my_lp_problem +=(sum(z_d[d]-M*w_m[m] for m in range(len(W))))<=0 
   
    
    my_lp_problem.solve()

    for variable in my_lp_problem.variables():
        print ("{} = {}".format(variable.name, variable.varValue))

    print (pulp.value(my_lp_problem.objective))

if __name__ == '__main__':
    F=[0,1,2,3,4,5,6]
    D=[0,1,2]
    S=[0,1] #0:eMBB / 1:URLLC
    W=[0,1]
    T=[0,1]
    M=100
    k_d=[100,100,100]
    q_f=[10,20,30,30,30,40,10]
    c_m=[1000,1000,1500]
    cf_d=[1000,1000,1500]
    cv_d=[1,1,1]
    h_fs=[[1,0],
          [1,0],
          [0,1],
          [0,1],
          [1,0],
          [1,0],
          [0,1]]
    delta_fd=[
        [1, 1 ,0],
        [1, 1, 0],
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
        [0, 1, 1],
        [0, 1, 1]
    ]

    inputData={"F":F,"D":D,"S":S,"W":W,"T":T,"k_d":k_d,"q_f":q_f,"c_m":c_m,"delta_fd":delta_fd,"M":M}
    Link_reassignment(inputData)