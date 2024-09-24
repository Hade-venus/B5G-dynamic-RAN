# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 15:12:30 2023

@author: Shaoxuan
"""
import matplotlib.pyplot as plt
def createGrid(n, m, l, radius_macro,radius_micro):
    
    sol={}
    sol["grid"]={}
    sol["antennas"]={}
    sol["stats"]={}
    
    h = l / float(n+1)

    sol["grid"]["coord_x"]=[]
    sol["grid"]["coord_y"]=[]
    
    for j in range(n):
        for i in range(n):
            sol["grid"]["coord_x"].append(i*h+h)
            sol["grid"]["coord_y"].append(j*h+h)
            
    h = l / float(m+1)     
    sol["antennas"]["coord_x"]=[]
    sol["antennas"]["coord_y"]=[]
    
    # MBS
    sol["antennas"]["coord_x"].append(l/2.0)
    sol["antennas"]["coord_y"].append(l/2.0)
    
    #muBS
    for j in range(m):
        for i in range(m):
            sol["antennas"]["coord_x"].append(i*h+h)
            sol["antennas"]["coord_y"].append(j*h+h)
            
    
    #plt.plot(sol["grid"]["coord_x"],sol["grid"]["coord_y"],'bo',sol["antennas"]["coord_x"],sol["antennas"]["coord_y"],"rx")
    
    
    
   
    
    fig, axes = plt.subplots()
    axes.set_xlim((0-h, l+h))
    axes.set_ylim((0-h, l+h))
    plt.plot(sol["grid"]["coord_x"],sol["grid"]["coord_y"],'bo',sol["antennas"]["coord_x"],sol["antennas"]["coord_y"],"rx")
    plt.plot(sol["antennas"]["coord_x"][0],sol["antennas"]["coord_y"][0],"go")
    
    for i in range(len(sol["antennas"]["coord_x"])):
        x=sol["antennas"]["coord_x"][i]
        y=sol["antennas"]["coord_y"][i]
        if i==0:
            cc = plt.Circle((x, y), radius_macro , color='g', fill=False)
        else:
            cc = plt.Circle((x, y), radius_micro , color='r', fill=False)
        axes.add_artist(cc)
    #axes.set_aspect( 1 ) 
    
    fig.savefig('plotcircles.png')
    
    return sol
S=createGrid(8,4,450,300,100)