# 一些编程过程中可能会用到的工具
import numpy as np


def box_inertia(shape, m):
    x, y, z = shape
    ixx = (y*y + z*z) * m / 12
    iyy = (x*x + z*z) * m / 12
    izz = (x*x + y*y) * m / 12
    return [ixx, iyy, izz]


box_inertia([0.12, 0.25, 0.4], 20)