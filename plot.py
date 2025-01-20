import matplotlib.pyplot as plt
import numpy as np
from data import *

def difficulties_plot(difficulties, beginIndex):
    pos = list(range(len(difficulties)))
    newTickers = list(range(beginIndex, beginIndex+len(difficulties)))

    plt.plot(difficulties)
    plt.xticks(pos, newTickers, rotation=90)
    plt.ylabel('Difficulty')
    plt.xlabel('Block #')
    plt.savefig('chart.png', bbox_inches='tight')

def makePlot():
    allBlocks = ecDataGet.getAllBlocks()
    difficulties = []

    if len(allBlocks) > 30:
        i = len(allBlocks) - 30
    else: i = 0

    beginIndex = i
    
    while i < len(allBlocks):
        difficulties.append(allBlocks[i][2])
        i += 1

    return difficulties_plot(difficulties, beginIndex)

makePlot()