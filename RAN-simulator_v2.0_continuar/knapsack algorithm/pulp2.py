# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 12:36:46 2023

@author: Shaoxuan
"""

from pulp import *

class Sender:
    def __init__(self, name):
        self.name = name

class Receiver:
    def __init__(self, name):
        self.name = name

class DataTransferSystem:
    def __init__(self):
        self.senders = []
        self.receivers = []
        self.costs = {}

    def add_sender(self, sender):
        self.senders.append(sender)

    def add_receiver(self, receiver):
        self.receivers.append(receiver)

    def set_cost(self, sender, receiver, cost):
        self.costs[(sender, receiver)] = cost

    def transmit_data(self):
        prob = LpProblem("DataTransferProblem", LpMinimize)

        # 创建发送者和接收者的变量
        senders_vars = LpVariable.dicts("Sender", self.senders, 0, 1, LpInteger)
        receivers_vars = LpVariable.dicts("Receiver", self.receivers, 0, 1, LpInteger)

        # 创建数据传输变量
        transmit_vars = LpVariable.dicts("Transmit", (self.senders, self.receivers), 0, 1, LpInteger)

        # 定义目标函数，即最小化总成本
        prob += lpSum([self.costs[(sender, receiver)] * transmit_vars[sender][receiver]
                       for sender in self.senders
                       for receiver in self.receivers]), "Total_Cost"

        # 添加约束条件，每个发送者只能发送给一个接收者
        for sender in self.senders:
            prob += lpSum([transmit_vars[sender][receiver]
                           for receiver in self.receivers]) == senders_vars[sender]

        # 添加约束条件，每个接收者只能接收来自一个发送者的数据
        for receiver in self.receivers:
            prob += lpSum([transmit_vars[sender][receiver]
                           for sender in self.senders]) == receivers_vars[receiver]

        # 添加约束条件，每个发送者和接收者的变量之和为1（选择与否）
        for sender in self.senders:
            prob += senders_vars[sender] + lpSum([transmit_vars[sender][receiver]
                                                  for receiver in self.receivers]) == 1
        for receiver in self.receivers:
            prob += receivers_vars[receiver] + lpSum([transmit_vars[sender][receiver]
                                                      for sender in self.senders]) == 1

        # 求解整数线性规划问题
        prob.solve()

        # 打印结果
        print("Status:", LpStatus[prob.status])
        for sender in self.senders:
            for receiver in self.receivers:
                if transmit_vars[sender][receiver].varValue == 1:
                    print(f"{sender.name} is sending data to {receiver.name}")

# 创建发送者和接收者对象
sender1 = Sender("Sender1")
sender2 = Sender("Sender2")
receiver1 = Receiver("Receiver1")
receiver2 = Receiver("Receiver2")

# 创建数据传输系统对象
data_transfer_system = DataTransferSystem()

# 将发送者和接收者添加到数据传输系统中
data_transfer_system.add_sender(sender1)
data_transfer_system
