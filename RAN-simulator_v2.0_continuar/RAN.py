import sys, copy
from Antenna import Antenna
from GridMap import GridMap
import numpy as np

class RAN:
    def __init__(self, config, slicing = False):
        
        print("Initializing...")
        self.config_general = config["general"]
        self.options = config["options"]
        self.slicing = config["slicing"] if slicing else None
        self.resolution= self.config_general["resolution[s]"]
        self.T = self.config_general["num_steps"]
        self.skip = self.config_general["skip"]
        self.config_antennas = config["antennas"]
        self.config_grid = config["grid"]

        self.grid = GridMap(self.config_grid)
        self.antennas = {}
        for antenna_id, antenna_params in self.config_antennas.items():
            self.antennas[antenna_id] = Antenna(antenna_id, antenna_params, self.options)
            if self.slicing:
                self.antennas[antenna_id].slices = copy.deepcopy(self.slicing)
        self.assignment = {}
        self.buildAssignment()
        self.activeAntennas = 0
        self.computeNumberActiveAntennas()

    def computeNumberActiveAntennas(self):
        self.activeAntennas = 0
        for key_antenna, antenna in self.antennas.items():
            if antenna.active:
                self.activeAntennas += 1

    def buildAssignment(self): # Shaoxuan: to implement considering true constraints
        self.assignment = {}
        for key_grid, dict_grid in self.grid.getItems():
            self.assignment[key_grid] = {}
            coord_grid = dict_grid["coord"]
            best_power=-1
            best_antenna=None
            for key_antenna, antenna in self.antennas.items():
                if not antenna.active:
                    continue
                if not antenna.isReachable(coord_grid):
                    continue
                this_power = antenna.computePower(coord_grid)
                if this_power > best_power:
                    best_antenna = key_antenna
                    best_power = this_power
            self.assignment[key_grid][best_antenna] = 1

    def stepForward(self):

        stats = {"general":{}, "total":{"UL":{},"DL":{}},"antenna":{}}
        stats["general"]["active antennas"] = self.activeAntennas
        stats["general"]["min_load_id"] = 0
        stats["general"]["min_load_val"] = 0
        stats["general"]["max_load_id"] = 0
        stats["general"]["max_load_val"] = 0
        for k in ["UL","DL"]:
            stats["total"][k]["loss"] = 0
            stats["total"][k]["input traffic"] = 0
            stats["total"][k]["traffic access"] = 0 
            stats["total"][k]["traffic metro"] = 0
            stats["total"][k]["traffic eMBB"] = 0
            stats["total"][k]["traffic URLLC"] = 0
            stats["total"][k]["traffic mIoT"] = 0
        data = self.grid.forward()

        input_traffic = {}
        for key_grid, dict_grid in data.items():
            traffic = dict_grid["traffic"]
            for key_antenna, factor in self.assignment[key_grid].items():
                if key_antenna not in input_traffic:
                    input_traffic[key_antenna]= {"total":{"UL":0,"DL":0},"type":{"eMBB":{"UL":0,"DL":0},"URLLC":{"UL":0,"DL":0},"mIoT":{"UL":0,"DL":0}}}
                if traffic["type"] not in input_traffic[key_antenna]["type"]:
                    input_traffic[key_antenna]["type"][traffic["type"]] = {"UL":0, "DL":0}
                #input_traffic[key_antenna]["type"][traffic["type"]["UL"]] += traffic["UL[Gb/s]"]
                #input_traffic[key_antenna]["type"][traffic["eMBB"]["UL"]] += traffic["eMBB"]["UL[Gb/s]"]
                #input_traffic[key_antenna]["type"][traffic["URLLC"]["UL"]] += traffic["URLLC"]["UL[Gb/s]"]
                #input_traffic[key_antenna]["type"][traffic["mIoT"]["UL"]] += traffic["mIoT"]["UL[Gb/s]"]
                #input_traffic[key_antenna]["total"]["UL"] += traffic["UL[Gb/s]"]
                #input_traffic[key_antenna]["type"][traffic["eMBB"]]["DL"] += traffic["eMBB"]["DL[Gb/s]"]
                #input_traffic[key_antenna]["type"][traffic["URLLC"]]["DL"] += traffic["URLLC"]["DL[Gb/s]"]
                #input_traffic[key_antenna]["type"][traffic["mIoT"]["DL"]] += traffic["mIoT"]["DL[Gb/s]"]
                #input_traffic[key_antenna]["type"][traffic["type"]]["DL"] += traffic["DL[Gb/s]"]
                #input_traffic[key_antenna]["total"]["DL"] += traffic["DL[Gb/s]"]
                input_traffic[key_antenna]["type"][traffic["type"]]["UL"] += traffic["UL[Gb/s]"]
                #input_traffic[key_antenna]["type"]["eMBB"]["UL"] += traffic["eMBB"]["UL[Gb/s]"]
                #input_traffic[key_antenna]["type"]["URLLC"]["UL"] += traffic["URLLC"]["UL[Gb/s]"]
                #input_traffic[key_antenna]["type"]["mIoT"]["UL"] += traffic["mIoT"]["UL[Gb/s]"]
                input_traffic[key_antenna]["total"]["UL"] += traffic["UL[Gb/s]"]
                #input_traffic[key_antenna]["type"]["eMBB"]["DL"] += traffic["eMBB"]["DL[Gb/s]"]
                #input_traffic[key_antenna]["type"]["URLLC"]["DL"] += traffic["URLLC"]["DL[Gb/s]"]
                #input_traffic[key_antenna]["type"]["mIoT"]["DL"] += traffic["mIoT"]["DL[Gb/s]"]
                input_traffic[key_antenna]["type"][traffic["type"]]["DL"] += traffic["DL[Gb/s]"]
                input_traffic[key_antenna]["total"]["DL"] += traffic["DL[Gb/s]"]

        min_load_val = None
        min_load_id = None
        max_load_val = None
        max_load_id = None

        for key_antenna, antenna in self.antennas.items():
            if key_antenna not in input_traffic: continue
            this_load_UL = input_traffic[key_antenna]["total"]["UL"] / antenna.capacity
            this_load_DL = input_traffic[key_antenna]["total"]["DL"] / antenna.capacity
            this_load = max(this_load_UL, this_load_DL)

            if min_load_val is None or this_load < min_load_val:
                min_load_val = this_load
                min_load_id = key_antenna

            if max_load_val is None or this_load > max_load_val:
                max_load_val = this_load
                max_load_id = key_antenna

            stats["general"]["min_load_id"] = min_load_id
            stats["general"]["min_load_val"] = min_load_val
            stats["general"]["max_load_id"] = max_load_id
            stats["general"]["max_load_val"] = max_load_val

            if self.slicing is None:
                traffic_UL = input_traffic[key_antenna]["total"]["UL"]
                traffic_DL = input_traffic[key_antenna]["total"]["DL"]
                loss_UL, fh_UL, mh_UL, bh_UL, traffic_access_UL, traffic_metro_UL = antenna.propagate(traffic_UL, slice=None)
                loss_DL, fh_DL, mh_DL, bh_DL, traffic_access_DL, traffic_metro_DL = antenna.propagate(traffic_DL, slice=None)
            else:
                loss_UL = fh_UL= mh_UL = bh_UL = traffic_UL = traffic_access_UL = traffic_metro_UL = 0
                loss_DL = fh_DL = mh_DL = bh_DL = traffic_DL = traffic_access_DL = traffic_metro_DL = 0

                slice_aux={}
                for type_id, type_dict in input_traffic[key_antenna]["type"].items():
                    sl_id = antenna.slices["services"][type_id] if type_id in antenna.slices["services"] else antenna.slices["services"]["mIoT"]
                    sl = {"id":sl_id, "service":type_id, "option":antenna.slices["options"][sl_id], "size":antenna.slices["size"][sl_id]}

                    if sl_id not in slice_aux: slice_aux[sl_id]={"traffic":0, "capacity":antenna.capacity*sl["size"]}

                    traffic_UL_aux = type_dict["UL"]
                    traffic_DL_aux = type_dict["DL"]
                    slice_aux[sl_id]["traffic"]+=float(max(traffic_UL_aux,traffic_DL_aux))
                    loss_UL_aux, fh_UL_aux, mh_UL_aux, bh_UL_aux, traffic_access_UL_aux, traffic_metro_UL_aux = antenna.propagate(traffic_UL_aux, slice=sl)
                    loss_DL_aux, fh_DL_aux, mh_DL_aux, bh_DL_aux, traffic_access_DL_aux, traffic_metro_DL_aux = antenna.propagate(traffic_DL_aux, slice=sl)

                    traffic_UL += traffic_UL_aux
                    loss_UL += loss_UL_aux
                    fh_UL += fh_UL_aux
                    mh_UL += mh_UL_aux
                    bh_UL += bh_UL_aux
                    traffic_access_UL += traffic_access_UL_aux
                    traffic_metro_UL += traffic_metro_UL_aux

                    traffic_DL += traffic_DL_aux
                    loss_DL += loss_DL_aux
                    fh_DL += fh_DL_aux
                    mh_DL += mh_DL_aux
                    bh_DL += bh_DL_aux
                    traffic_access_DL += traffic_access_DL_aux
                    traffic_metro_DL += traffic_metro_DL_aux

            stats["total"]["UL"]["loss"] += loss_UL
            stats["total"]["UL"]["input traffic"] += traffic_UL
            stats["total"]["UL"]["traffic access"] += traffic_access_UL
            stats["total"]["UL"]["traffic metro"] += traffic_metro_UL
            stats["total"]["UL"]["traffic eMBB"] += traffic_metro_UL
            stats["total"]["UL"]["traffic URLLC"] += traffic_metro_UL
            stats["total"]["UL"]["traffic mIoT"] += traffic_metro_UL
            stats["total"]["DL"]["loss"] += loss_DL
            stats["total"]["DL"]["input traffic"] += traffic_DL
            stats["total"]["DL"]["traffic access"] += traffic_access_DL
            stats["total"]["DL"]["traffic metro"] += traffic_metro_DL
            stats["total"]["DL"]["traffic eMBB"] += traffic_metro_DL
            stats["total"]["DL"]["traffic URLLC"] += traffic_metro_DL
            stats["total"]["DL"]["traffic mIoT"] += traffic_metro_DL

            stats["antenna"][key_antenna]={"UL":{},"DL":{}}
            stats["antenna"][key_antenna]["UL"] = {"loss": loss_UL, "F-H traffic": fh_UL, "M-H traffic": mh_UL,
                                                   "B-H traffic": bh_UL}
            stats["antenna"][key_antenna]["DL"] = {"loss": loss_DL, "F-H traffic": fh_DL, "M-H traffic": mh_DL,
                                                   "B-H traffic": bh_DL}
            if self.slicing:
                stats["antenna"][key_antenna]["slices"] = slice_aux

        return stats

    def changeAntennaStatus(self,changes):
        for antenna_id, status in changes.items():
            if antenna_id not in self.antennas:
                sys.exit("[changeAntennaStatus] Incorrect antenna id")
            self.antennas[antenna_id].changeAntennaStatus(status)


    def activeNeighbor(self, ref_id):
        neighbor = copy.copy(self.antennas[ref_id].neighbor)
        while len(neighbor) > 0:
            neigh_id = neighbor.pop(0)
            if not self.antennas[neigh_id].active:
                self.antennas[neigh_id].changeAntennaStatus(True)
                self.buildAssignment()
                self.computeNumberActiveAntennas()
                break

    def deactiveAntenna(self, ref_id):
        if self.antennas[ref_id].fixed: 
            return
        if  self.activeAntennas == 1:
            return
        self.antennas[ref_id].changeAntennaStatus(False)
        self.buildAssignment()
        self.computeNumberActiveAntennas()


    def changeSplit(self, flexMode, flexParams, stats):
        if flexMode=="random":
            self.setRandomSplit(flexParams["options"], p_change=flexParams["p_change"], sync=flexParams["sync"])
        elif flexMode=="policy":
            self.setPolicySplit(flexParams,stats)
        else:
            sys.exit("[RAN] Unknown flexible mode")

    def setRandomSplit(self, options, p_change=None, sync=False):
        if sync:
            new_option = options[int(np.floor(len(options) * np.random.rand(1)))]
        for key_antenna, antenna in self.antennas.items():
            if p_change is not None and np.random.rand(1)>p_change: continue
            if not sync:
                new_option=options[int(np.floor(len(options)*np.random.rand(1)))]
            antenna.changeOption(new_option, check_equal=False)



    def resizeSlices(self, antenna_id, slices_surplus, slices_slack):
        slices_subs, slices_add = self.sliceReassignment(slices_surplus, slices_slack)
        for slice_id in slices_surplus.keys():
            before = slices_surplus[slice_id]
            after = slices_subs[slice_id]
            diff = before-after
            newsize = (self.antennas[antenna_id].slices["size"][slice_id]*self.antennas[antenna_id].capacity-diff)/self.antennas[antenna_id].capacity
            self.antennas[antenna_id].slices["size"][slice_id] = newsize

        for slice_id in slices_slack.keys():
            before=slices_slack[slice_id]
            after=slices_add[slice_id]
            diff=before-after
            newsize=(self.antennas[antenna_id].slices["size"][slice_id]*self.antennas[antenna_id].capacity+diff)/self.antennas[antenna_id].capacity
            self.antennas[antenna_id].slices["size"][slice_id] = newsize

    def sliceReassignment(self ,SA, SB):

            S1 = copy.copy(SA)
            S2 = copy.copy(SB)
            total_s1 = 0
            total_s2 = 0
            for key, val in S1.items():
                total_s1 += val
            for key, val in S2.items():
                total_s2 += val
            if total_s1 >= total_s2:
                ratio = total_s2 / total_s1
                for k, v in S1.items():
                    S1[k] = v * (1 - ratio)
                for k, v in S2.items():
                    S2[k] = 0
            else:
                S2_copy = copy.copy(S2)
                n = float(len(S2.keys()))

                while (total_s1 > 0):
                    min_id = min(S2_copy, key=S2_copy.get)
                    min_val = S2_copy[min_id]
                    aux = total_s1 / n
                    if aux > min_val:
                        subs = min_val
                    else:
                        subs = aux
                    total_s1 -= subs * n
                    delkeys = []
                    for k in S2_copy.keys():
                        S2_copy[k] -= subs
                        if S2_copy[k] <= 0:
                            delkeys.append(k)
                            n -= 1
                    if len(delkeys) > 0:
                        for k in delkeys:
                            del S2_copy[k]
                for k, v in S1.items():
                    S1[k] = 0
                for k, v in S2.items():
                    if k in S2_copy:
                        S2[k] = S2_copy[k]
                    else:
                        S2[k] = 0
            return (S1, S2)


    def setPolicySplit(self,params,stats):
        # TODO: Shaouxuan to design and implement
        pass


