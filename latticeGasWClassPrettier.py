#!/usr/bin/python
# -*- coding: utf-8 -*-
# spot for modifiable variables:

# let's stick to "square"s right now, enter the width of the top layer:

containerSize = 10
particleNumber = 50

import matplotlib.pyplot as plt
import math
import numpy as np
import random

# ----------------------------------------------------------------------------#

class Lattice:
    """Class used to work with the lattice."""
    def __init__(self,array):
        self.array = array
        
    def request_string(self, column, row):
        """Takes the target position in terms of a row and "column" and
        returns a string made from the paths around the node"""

        stringOutput = ''

        for i in range(0, 6):
            stringOutput = stringOutput + str(self.array[row][column][i])
        
        return stringOutput
    
    def spots_remaining(self, column, row):
        """Takes the target position in terms of a row and "column" and
        returns the number of spots, followed by their positions as a
        tuple."""

        countOfSpots = 0
        listOfSpots = []

        for i in range(0,6):
            if self.array[row][column][i] == 0:
                countOfSpots += 1
                listOfSpots.append(i)
        
        return countOfSpots, listOfSpots
    
    def request_pretty_list(self):

        for i in range(0, containerSize):
            for x in range(0, containerSize):
                print(self.request_string(i,x), end = ' ')
            print('\n')

    def particle_counter(self):
        particleDensityList = np.zeros((containerSize,containerSize), np.int8)

        for i in range(0,containerSize):
            for x in range(0, containerSize):
                particleDensityList[i][x] = np.count_nonzero(self.array[i][x] == 1)



        return particleDensityList

# ----------------------------------------------------------------------------#

def cell_number(containerSize):

    # Finds number of cells based on containerSize, and tells user (for debugging).

    cellNumber = containerSize * containerSize - int(containerSize / 2)

    return cellNumber

# ----------------------------------------------------------------------------#

def auto_square_edges(containerSize):
    """Categorizes the edges based on the size of the container. Takes containerSize
    and returns a tuple of topEdge, bottomEdge, leftEdge, rightEdge; each as a list.""" 

    # initializing/reseting all the lists
    
    leftEdge = []
    rightEdge = []
    topEdge = []
    bottomEdge = []

    # the following for loop defines the edges (without corners) as lists of
    # tuples denoting their (columnID, rowID)

    for i in range(1,containerSize-1):
        
        topEdge.append((i, 0))
        
        bottomEdge.append((i, containerSize-1))
        
        leftEdge.append((0, i))

        rightEdge.append((containerSize - i % 2 - 1, i))
        
        
    return topEdge, bottomEdge, leftEdge, rightEdge

# ----------------------------------------------------------------------------#  
    
def lattice_builder(edges):
    """this creates the initial lattice array with walls
     0 - corresponds to a path without a particle
     1 - corresponds to a path with a particle
     2 - corresponds to a wall"""


    topEdge, bottomEdge, leftEdge, rightEdge = edges  
    # initializes the lattice
    latticeList = Lattice(np.zeros((containerSize, containerSize, 6), np.int8))

    # top left corner and top right corner positions are set, they won't vary
    # if the container size is odd or even.
    latticeList.array[0][0] = (0, 2, 2, 2, 2, 0)  # topLeft
    latticeList.array[containerSize-1][0] = (2, 2, 2, 0, 0, 2) # topRight


    # the following if/else statement sets the walls for the bottom corners, which vary
    # based on whether the container size is odd or even. If even, the final row is short,
    # if odd, the final row is the same as the top row.
    if containerSize % 2 == 0: 
        latticeList.array[containerSize-2][containerSize-1] = (2, 0, 0, 0, 2, 2) # bottomRight
        latticeList.array[0][containerSize-1] = (0, 0, 0, 2, 2, 2) # bottomLeft
                        
    else:
        latticeList.array[containerSize-1][containerSize-1] = (2, 2, 0, 0, 2, 2) # bottomRight                 
        latticeList.array[0][containerSize-1] = (0, 0, 2, 2, 2, 2) # bottomLeft


    # the following for loops declare the edges based on either the lists provided by the
    # user, or automatically produced by auto_square_edges().
    for i in range(0,len(topEdge)):
        column, row = topEdge[i]
        latticeList.array[column][row] = (0, 2, 2, 0, 0, 0)
    
    
    for i in range(0,len(bottomEdge)):
        column, row = bottomEdge[i]
        latticeList.array[column][row] = (0, 0, 0, 0, 2, 2)  
    
    
    for i in range(0,len(leftEdge)):
        column, row = leftEdge[i]
        
        if i % 2 == 1:
            latticeList.array[column][row] = (0, 0, 2, 2, 2, 0)
        else:
            latticeList.array[column][row] = (0, 0, 0, 2, 0, 0)
    
    
    for i in range(0,len(rightEdge)):
        column, row = rightEdge[i]
        
        if i % 2 == 1:
            latticeList.array[column][row] = (2, 2, 0, 0, 0, 2)
        else:
            latticeList.array[column][row] = (2, 0, 0, 0, 0, 0)
            latticeList.array[column+1][row] = (2, 2, 2, 2, 2, 2)


    return latticeList

# ----------------------------------------------------------------------------#

def particleDistribution(latticeList):
    """places particles randomly, if a particle is in a position at first, it is
    assumed to be moving away from the center of the parent node."""


    particlesRemaining = particleNumber
    
    # the following while loop attempts to place a particle each iteration, if the spot
    # picked is full, it finds a new random spot on the next iteration. It consumes
    # particles as it goes, until it runs out. If a spot is full, nothing is consumed.

    while particlesRemaining != 0:
        
        # these randomly select a row and column
        randomColumn = random.randint(0, containerSize-1)
        randomRow = random.randint(0, containerSize-1)

        # this statement finds the number of spots left in the target, and which index
        # values they have
        spotsRemaining, openSpots = latticeList.spots_remaining(randomColumn, randomRow)
        

        # this if statement ensures that the only time a particle is added is when there
        # are spots remaining.
        if spotsRemaining > 0:
            positionChosen = random.choice(openSpots)

            latticeList.array[randomRow][randomColumn][positionChosen] = 1

            particlesRemaining -= 1

    return latticeList

# ----------------------------------------------------------------------------#

def display(particleCountList):
    """this displays the "container" and the particle density inside of it"""

    fig, ax = plt.subplots()
    im = ax.imshow(particleCountList, cmap='Blues')

    ax.set_title("Particle Distribution")
    fig.tight_layout()
    
    plt.show()

# ----------------------------------------------------------------------------#


latticeList = particleDistribution(lattice_builder(auto_square_edges(containerSize)))
latticeList.request_pretty_list()
#display(latticeList.particle_counter())