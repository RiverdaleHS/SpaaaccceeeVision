"""
=================
An animated image
=================

This example demonstrates how to animate an image.
"""
import numpy as np
import cv2
import threading
from networktables import NetworkTables
import random
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import copy


fig = plt.figure()


def f(x, y):
    return np.sin(x) + np.cos(y)

x = np.linspace(0, 2 * np.pi, 120)
y = np.linspace(0, 2 * np.pi, 100).reshape(-1, 1)

im = plt.imshow(cv2.imread("2016_images/0.jpg"), animated=True)


def updatefig(*args):
    return cv2.imread("2016_images/0.jpg")

ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()