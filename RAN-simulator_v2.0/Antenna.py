import sys
import numpy as np

class Antenna(object):

    def __init__(self, id_a, config, options):
        self.id = id_a
        self.type = config["type"]
        self.allowableOptions = options
        self.option = config["option"]
        
        self.split_FH = None
        self.split_MH = None
        self.CU=None
        self.DU=None
        
        self.selectOption()
        
        self.coord = (config["coord"]["x"], config["coord"]["y"])
        self.params = config["params"]
        self.active = True if config["active"] == 1 else False

        self.capacity = self.params["capacity[Gb/s]"]
        self.PR=self.params["peakRate[Gb/s]"]
        self.BW=self.params["bandwidth[MHz]"]              #bandwidth of the NR and the unit is MHz
        self.BWR=self.params["refBandwidth[MHz]"]          # reference bandwidth of NR and the unit is MHz
        self.NL=self.params["nLayers"]                     #number of layers 
        self.NLR=self.params["nRefLayers"]                 # number of reference layers
        self.M=self.params["ModulationOrder"]              # modulation order
        self.ML=self.params["refModulationOrder"]          #refernce modulation order 
        self.NSC=self.params["nSubcarrers"]                #the number of subcarrers in the bandwidth
        self.NS=self.params["nSymbols"]                    #number of symbols in 1ms
        self.W=self.params["nIQbits"]                      #number of IQ bits
        #self.NAP=self.paras["nAtennaPorts"]                #number of antenna ports
        self.MAC=self.params["MACinformation[Gb/s]"]        # MAC information i.e. split7.2 is 120Mb/s
        self.S=self.params["signalingBitrate[Gb/s]"]        # signalling bit rate 16Mb/s
        self.C=self.params["constant"]                      # this is a constant of value of 1000
        #self.frequency = config["frequnecy"]
        self.supportedSplitFH = [7.2, 2, 4]
        self.supportedSplitMH = [2, 4]

        self.neighbor = config["neighbor"]

    def selectOption(self):
        if self.option not in self.allowableOptions:
            sys.exit("[selectOption] Not allowable option")
        self.split_FH = self.allowableOptions[self.option]["split_FH"]
        self.split_MH = self.allowableOptions[self.option]["split_MH"]
        self.CU=self.allowableOptions[self.option]["CU"]
        self.DU=self.allowableOptions[self.option]["DU"]

    def propagate(self, x):
        loss = 0
        if x > self.capacity:
            loss = x-self.capacity
            x = self.capacity
        fh = self.computeFH(x)
        mh = self.computeMH()
        bh = self.computeBH(x)
        
        if self.DU >= 1:
            traffic_access = fh
        elif self.CU >= 1:
            traffic_access = mh
        else:
            traffic_access = bh

        if self.DU == 2:
            traffic_metro = fh
        elif self.CU == 2:
            traffic_metro = mh
        else:
            traffic_metro = bh

        return loss, fh, mh, bh, traffic_access, traffic_metro

    def computeFH(self, x):
        if self.split_FH == 7.2:
            load = x/float(self.params["capacity[Gb/s]"])
            #fh = load*self.params["FH[Gb/s]"]
            fh=(load*self.NSC*self.NS*self.NL*self.W*self.C+self.MAC*(1e6))/float(1e9)
        elif self.split_FH == 2:
            fh = self.PR*self.BW/self.BWR*self.NL/self.NLR*self.M/self.ML+self.S
        elif self.split_FH == 4:
            fh = self.PR*self.BW/self.BWR*self.NL/self.NLR*self.M/self.ML
            #fh = self.params["FH[Gb/s]"]
        elif self.split_FH == 0:
            return 0
        else:
            sys.exit("[computeFH] Unknown split")
        return fh

    def computeMH(self):
        if self.split_MH==2:
            mh=self.PR*self.BW/self.BWR*self.NL/self.NLR*self.M/self.ML+self.S
        elif self.split_MH==4:
            mh=self.PR*self.BW/self.BWR*self.NL/self.NLR*self.M/self.ML
        elif self.split_MH == 0:
            return 0
        else:
            sys.exit("[computeMH] Unknown split")
        return mh
    
    def computeBH(self, x):
        return x

    def changeAntennaStatus(self, status):
        if self.active is status:
           sys.exit("[changeAntennaStatus] The antenna has the same status")
        self.active = status

    def changeOption(self, new_option, check_equal=True):
        if check_equal and self.option == new_option:
            sys.exit("[changeOption] The antenna has the same option")
        self.option = new_option
        self.selectOption()
        
    def distanceToCenter(self, coord):
        return np.sqrt(np.square(self.coord[0]-coord[0])+np.square(self.coord[1]-coord[1]))

    def isReachable(self, coord):
        dist = self.distanceToCenter(coord)
        if dist <= self.params["radius[m]"]:
            return True
        else:
            return False

    def computePower(self, coord): # TODO: Shaoxuan: review and implement according to real formulas
        dist = self.distanceToCenter(coord)
        # frequency=2600MHz
        
        factor = 1-np.sqrt(dist / float(self.params["radius[m]"]))
        power = np.max(factor*self.params["powerMax[dBm]"], 0)
        return power

