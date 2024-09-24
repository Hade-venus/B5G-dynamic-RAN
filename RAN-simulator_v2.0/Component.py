import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from scipy import interpolate
import matplotlib.pyplot as plt
import copy, sys, os


class Component(object):

    def __init__(self, params):
        self.UE_mean = params["UE_norm_mean"]
        self.UE_var = params["UE_norm_var"]
        self.UE_min = params["UE_abs_min"]
        self.UE_max = params["UE_abs_max"]
        self.UE_noise = params["UE_abs_noise"]
        self.UE_shiftmax = params["UE_shift_max"]
        self.UE_shift = int(np.random.uniform(low=0,high=self.UE_shiftmax,size=1))
        self.interpl = params["interpl"]
        self.service = params["service"]

        self.UE_profile = self.generateUEProfile(starting=None)
        self.period = float(params["period"])

        self.t = 0
        self.i = 0
        self.hist = []

    def generateUEProfile(self, starting=None):
        df = pd.read_csv(os.getcwd()+self.UE_mean)

        X = np.array(df.time)
        X = (X-min(X))/float(max(X)-min(X))

        Y = np.array(df.val)
        Y = (Y-min(Y))/float(max(Y)-min(Y))
        Y = self.UE_min+np.multiply(Y, self.UE_max-self.UE_min)


        aux = np.where(Y <= 0)
        Y += np.random.uniform(low=-self.UE_var, high=self.UE_var, size=(len(Y),))

        if len(aux) > 0 : Y[aux] = 0
        w = np.where(Y > self.UE_max)
        if len(w) > 0 : Y[w] = self.UE_max
        w=np.where(Y<self.UE_min)
        if len(w)>0: Y[w]=self.UE_min
        if starting is not None: Y[0] = starting
        time = np.array(X)
        val = np.array(Y)
        if self.interpl == "spline":
            P = interpolate.InterpolatedUnivariateSpline(time, val)
        if self.interpl=="linear":
            P = interp1d(time, val)

        profile={"time":time,"val":val,"func":P}
        
        return profile

    def forward(self):
        self.t+=1
        if self.t>=self.period:
            self.t=0
            starting = self.UE_profile["func"](1)
            self.UE_profile = self.generateUEProfile(starting=starting)
            self.UE_shift = int(np.random.uniform(low=0,high=self.UE_shiftmax,size=1))
        tp=(self.t+self.UE_shift)%self.period
        rel_t=tp/self.period

        this_UE=self.UE_profile["func"](rel_t)
        if this_UE>0:
            noise=(this_UE*self.UE_noise)
            this_UE+=np.random.uniform(low=-noise,high=noise)
        if this_UE<self.UE_min: this_UE = self.UE_min
        if this_UE>self.UE_max: this_UE = self.UE_max

        traffic = {}
        traffic["type"] = self.service["type"]
        traffic["UL[Gb/s]"] = this_UE * self.service["UL[Mb/s]"] / 1000.0
        traffic["DL[Gb/s]"] = this_UE * self.service["DL[Mb/s]"] / 1000.0
        self.hist.append(traffic)
        return traffic