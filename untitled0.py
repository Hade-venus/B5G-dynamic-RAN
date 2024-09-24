# -*- coding: utf-8 -*-
"""
Created on Fri May  3 13:11:31 2024

@author: Shaoxuan
"""

# 模拟虚拟传感器数据
sensor_data = [28.5, 29.0, 27.8, 30.2, 31.5]

# 边缘计算任务：计算传感器数据的平均值
def calculate_average(data):
    total = sum(data)
    average = total / len(data)
    return average

# 在边缘设备上执行数据处理任务
average_value = calculate_average(sensor_data)

# 输出结果
print("传感器数据的平均值为:", average_value)


import numpy as np

# 0维张量（标量）
scalar = np.array(5)

# 1维张量（向量）
vector = np.array([1, 2, 3, 4])

# 2维张量（矩阵）
matrix = np.array([[1, 2, 3], [4, 5, 6]])

# 3维张量
tensor_3d = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

print("0D Tensor:", scalar)
print("1D Tensor:", vector)
print("2D Tensor:", matrix)
print("3D Tensor:", tensor_3d)
