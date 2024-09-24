import json, ast, os
from pathlib import Path
import sys
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

from RAN import RAN

def main():

    args = sys.argv[1:]
    if len(args) < 1:
        sys.exit("argument: grid config file name is missing")

    if len(args) < 2:
        sys.exit("argument: results path is missing")

    working_dir = os.getcwd() # current code path
    data_folder = Path(sys.path[0])
    configFileName = str(working_dir) + str(args[0])+".json"
    resultsFileName = str(working_dir) + str(args[1]) + ".csv"
    summaryFileName = str(working_dir) + str(args[1]) + "_summary.csv"
    

    configFile = open(Path(configFileName)).read()
    config = ast.literal_eval(json.dumps(json.loads(configFile)))

    mode = config["RANcontrol"]["mode"]
    

    slicing = False if mode == "static" or mode == "dynamic" or "slicing" not in config else True

    print(slicing)

    ran = RAN(config, slicing)

    load_thr_min = config["RANcontrol"]["ONOFFswitching"]["load_thr_min"]
    load_thr_max = config["RANcontrol"]["ONOFFswitching"]["load_thr_max"]
    load_slice_low = config["RANcontrol"]["dynamicSlicing"]["load_low"]
    load_slice_high = config["RANcontrol"]["dynamicSlicing"]["load_high"]
    #freq = config["RANcontrol"]["flexibleSplit"]["freq"]
    #flexMode = config["RANcontrol"]["flexibleSplit"]["mode"]
    #flexParams = config["RANcontrol"]["flexibleSplit"]["params"][flexMode]

    first = True

    for t in range(ran.T):
        print("Step " + str(t) + " out of " + str(ran.T))
        stats = ran.stepForward()
        if t > ran.skip:
            if first:
                results = pd.json_normalize(stats, sep='_')
                first = False
            else:
                aux = pd.json_normalize(stats, sep='_')
                results = pd.concat([results, aux])
                
        if mode == "static":
            continue

        if mode == "dynamic" or mode == "dynamic_slicing":
            if stats["general"]["max_load_val"] > load_thr_max:
                print("activate neighbor: ", stats["general"]["max_load_id"])
                ran.activeNeighbor(stats["general"]["max_load_id"])
            if stats["general"]["min_load_val"] < load_thr_min:
                print("deactivate: ", stats["general"]["min_load_id"])
                ran.deactiveAntenna(stats["general"]["min_load_id"])
        if mode == "slicing" or mode == "dynamic_slicing":
            for key_antenna, antenna_dict in stats["antenna"].items():
                slices_surplus = {}
                slices_slack = {}
                for slice_id, slice_dict in antenna_dict["slices"].items():
                    load = slice_dict["traffic"]/slice_dict["capacity"]
                    if load < load_slice_low:
                        slices_surplus[slice_id] = slice_dict["capacity"]-slice_dict["traffic"]/load_slice_low
                    elif load > load_slice_high:
                        slices_slack[slice_id] = slice_dict["traffic"]/load_slice_high-slice_dict["capacity"]
                if not bool(slices_surplus):
                    continue
                if not bool(slices_slack):
                    continue
                print(key_antenna)
                print("slices_surplus: ", slices_surplus)
                print("slices_slack: ", slices_slack)
                ran.resizeSlices(key_antenna, slices_surplus, slices_slack)

    results.to_csv(resultsFileName, sep=";", index=False)
    results_aux = results.loc[:,["total_UL_input traffic", "total_DL_input traffic", "total_UL_traffic access", "total_DL_traffic access", "total_UL_traffic metro", "total_DL_traffic metro", "total_UL_loss","total_DL_loss","general_active antennas","total_UL_traffic eMBB","total_DL_traffic eMBB","total_UL_traffic URLLC","total_DL_traffic URLLC","total_UL_traffic mIoT","total_DL_traffic mIoT"]]
    results_aux.to_csv(summaryFileName, sep=";", index=False)

if __name__ == "__main__":
    main()