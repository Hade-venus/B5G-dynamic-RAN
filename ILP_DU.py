# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 12:41:25 2023

@author: Shaoxuan
"""


import pulp as pl 
from pulp import *
import pandas as pd
import numpy as np


def DU_reassignment(inputData):

    # Get data from inputData dict

    F=inputData["F"] #set of tarffic flows
    D=inputData["D"] #set of DU location
    S=inputData["S"] # set of service type
    k_d=inputData["k_d"] #capacity in DU units of location d
    q_f=inputData["q_f"] #amount of DU units that flow f requires
    cf_d=inputData["cf_d"] #cost of openning DU location d
    cv_d=inputData["cv_d"] # cost of DU units allocatted in DU location j
    h_fs=inputData["h_fs"] # if flow f belongs to the service type s
    delta_fd= inputData["delta_fd"] # if flow f can be assigned to DU location d
    print(F)
    print(D)
    print(S)
    nF = len(F)
    nD = len(D)
    nS = len(S)


    # Create the problem
    my_lp_problem = pl.LpProblem('DU_reassignment', pl.LpMinimize)
   # Create the decision varibles

    x_fd =[pulp.LpVariable("x{0}{1}".format(f, d), cat="Binary") for f in range(nF) for d in range(nD)] # x=1 if flow i is assigned to DU location d
    y_sd=[pulp.LpVariable("y{0}{1}".format(s, d), cat="Continuous") for s in range(nS) for d in range(nD)] # amount of DU units of service type i that are allocate in DU laoction
    z_d=[pulp.LpVariable("z{0}".format(d), cat="Binary") for d in range(nD)] # z=1 if DU location is open

    print(x_fd)
    print(y_sd)
    print(z_d)

    print(delta_fd)

    # add objective function
    objFunc = sum(cf_d[d]*z_d[d] for d in range(nD)) + sum(cv_d[d]*y_sd[s*nD+d] for s in range(nS) for d in range(nD))
    my_lp_problem.setObjective(objFunc)

    # add constraint 1
    for f in range(nF):
        my_lp_problem += (sum(delta_fd[f][d]*x_fd[f*nD+d] for d in range(len(D)))) == 1

    # add constraint 2
    for s in range(nS):
        for d in range(nD):
            my_lp_problem += (y_sd[s*nD+d] - sum(h_fs[f][s] * x_fd[f*nD + d]*q_f[f] for f in range(nF))) == 0

    # add constraint 3
    for d in range(len(D)):
        my_lp_problem += (sum(y_sd[s*nD+d] for s in range(len(S))) - k_d[d]*z_d[d]) <= 0

    my_lp_problem.solve()

    for variable in my_lp_problem.variables():
        print ("{} = {}".format(variable.name, variable.varValue))

    print (pulp.value(my_lp_problem.objective))

if __name__ == '__main__':
    F=[0,1,2,3,4,5,6]
    D=[0,1,2]
    S=[0,1] #0:eMBB / 1:URLLC
    k_d=[100,100,100]
    q_f=[10,20,30,30,30,40,10]
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

    inputData={"F":F,"D":D,"S":S,"k_d":k_d,"q_f":q_f,"cf_d":cf_d,"cv_d":cv_d,"h_fs":h_fs,"delta_fd":delta_fd}
    DU_reassignment(inputData)