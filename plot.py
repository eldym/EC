import matplotlib.pyplot as plt
import numpy as np
from data import *

def difficulties_plot(difficulties):
    plt.plot(difficulties)
    plt.ylabel('Difficulty')
    plt.xlabel('Block #')
    plt.show()

def getPlot():
    allBlocks = ecDataGet.getAllBlocks()
    difficulties = []

    if len(allBlocks) > 100:
        i = len(allBlocks) - 100
    while i < len(allBlocks):
        difficulties.append(allBlocks[i][2])
        i += 1

    return difficulties_plot(difficulties)