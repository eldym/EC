import matplotlib.pyplot as plt
from data import *

def difficulties_plot(difficulties, beginIndex):
    # Creates x axis tickers
    pos = list(range(len(difficulties)))
    newTickers = list(range(beginIndex, beginIndex+len(difficulties)))

    # Plots the data of difficulties
    plt.plot(difficulties)

    # Creates custom tickers that properly display the block numbers
    plt.xticks(pos, newTickers, rotation=90)

    # Labels
    plt.ylabel('Difficulty')
    plt.xlabel('Block #')

    # Saves plotted chart as a png file
    plt.savefig('chart.png', bbox_inches='tight')
    plt.close() # Resets plt

def makePlot():
    # Gets block data to make a plot
    allBlocks = ecDataGet.getAllBlocks()
    difficulties = []

    # Get beginning index
    if len(allBlocks) > 31:
        i = len(allBlocks) - 31
    else: i = 0

    beginIndex = i
    
    # Appends appropriate data points
    while i < len(allBlocks):
        difficulties.append(allBlocks[i][2])
        i += 1

    # Sends data points to make chart image file
    difficulties_plot(difficulties, beginIndex)

makePlot() # For running in a dedicated terminal