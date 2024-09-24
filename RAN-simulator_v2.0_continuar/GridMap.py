import sys
from random import randrange
from Component import Component


class GridMap:

    def __init__(self, config):

        self.mode = config["mode"]
        self.components = config["components"]

        if self.mode == "auto":
            self.coord_x = config["coord_x"]
            self.coord_y = config["coord_y"]
            self.components_list = config["components_list"]
        else:
            self.height = config["height"]
            self.width = config["width"]
            self.resolution = config["resolution[m]"]

        self.grid = {}
        if self.mode == "plan":
            self.buildMode_plan()
        elif self.mode == "random":
            self.buildMode_random()
        elif self.mode == "auto":
            self.buildMode_auto()
        else:
            sys.exit("[GridMap] Unknown build mode")

    def buildMode_plan(self):
        k = -1
        for i in range(self.height):
            for j in range(self.width):
                k += 1
                self.grid[k] = {}
                self.grid[k]["coord"] = (i*self.resolution, j*self.resolution)
                self.grid[k]["traffic"] = Component(self.components[str(k)])

    def buildMode_random(self):
        k = -1
        ncomp = len(self.components)
        for i in range(self.height):
            for j in range(self.width):
                w = randrange(ncomp)
                k += 1
                self.grid[k] = {}
                self.grid[k]["coord"] = (i*self.resolution, j*self.resolution)
                self.grid[k]["traffic"] = Component(self.components[w])

    def buildMode_auto(self):
        k = -1
        for i in range(len(self.components)):
            k += 1
            self.grid[k] = {}
            self.grid[k]["coord"] = (self.coord_x[i], self.coord_y[i])
            self.grid[k]["traffic"] = Component(self.components_list[self.components[i]])

    def forward(self):
        data = {}
        for key, val in self.grid.items():
            data[key] = {}
            data[key]["traffic"] = val["traffic"].forward()
        return data

    def getItems(self):
        return self.grid.items()
