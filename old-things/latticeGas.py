#!/usr/bin/python
# -*- coding: utf-8 -*-
# spot for modifiable variables:

# let's stick to "square"s right now, enter the width of the top layer:

containerSize = 15
particleNumber = 100

import matplotlib.pyplot as plt
import math
import numpy as np
import random

# ----------------------------------------------------------------------------#

class Nodes:
    """Class used to represent all the Nodes of the lattice."""
    def __init__(self,latticePosition,right,upRight,upLeft,left,downLeft,downRight):
        self.latticePosition = latticePosition
        self.right = right
        self.upRight = upRight
        self.upLeft = upLeft
        self.left = left
        self.downLeft = downLeft
        self.downRight = downRight
        
    def request_string(self):
        """Returns a string made from the position data of the Node"""
        stringOutput = f'{self.right}{self.upRight}{self.upLeft}{self.left}{self.downLeft}{self.downRight}'
        return stringOutput
    
    def spots_remaining(self):
        countOfSpots = 0
        listOfSpots = []

        if self.right == 0:
            countOfSpots += 1
            listOfSpots.append(0)

        if self.upRight == 0:
            countOfSpots+=1
            listOfSpots.append(1)

        if self.upLeft == 0:
            countOfSpots+=1
            listOfSpots.append(2)

        if self.left == 0:
            countOfSpots+=1
            listOfSpots.append(3)

        if self.downLeft == 0:
            countOfSpots+=1
            listOfSpots.append(4)

        if self.downRight == 0:
            countOfSpots+=1
            listOfSpots.append(5)

        
        return countOfSpots, listOfSpots
    
    def replace_value(self, posToReplace, newValue):
       
        if posToReplace == 0:
            self.right = newValue

        elif posToReplace == 1:
            self.upRight = newValue

        elif posToReplace == 2:
            self.upLeft = newValue

        elif posToReplace == 3:
            self.left = newValue

        elif posToReplace == 4:
            self.downLeft = newValue

        elif posToReplace == 5:
            self.downRight = newValue  


# ----------------------------------------------------------------------------#

def cell_number(containerSize, particleNumber):

    # Finds number of cells based on containerSize, and tells user (for debugging).

    cellNumber = containerSize * containerSize - int(containerSize / 2)
    #print('Total Number of cells in Matrix: ' + str(cellNumber) + '\n')
    return cellNumber


# ----------------------------------------------------------------------------#

def the_categorizer(containerSize, particleNumber):

    # i like having a quick reference to whether the originial size is odd or even

    containerEven = containerSize % 2

    cellNumber = cell_number(containerSize, particleNumber)

    # initializing/reseting all the lists
    latticeList = []
    for x in range(0,cellNumber):
        latticeList.append(Nodes(-1,-1,-1,-1,-1,-1,-1))
        
    
    shorterLineMiddles = []
    shorterLineLEdges = []
    shorterLineREdges = []
    longerLineMiddles = []
    longerLineLEdges = []
    longerLineREdges = []

    # the following for loop modfiies six lists, in order to categorise
    # the index values into what part of the lattice they are

    for i in range(0, (containerSize - 2) // 2 + containerSize % 2):

        # basePoint is the left edge of the shorter part of the lattice,
        # so i use it as a reference point. as the index value increases,
        # basePoint is updated. the abstraction makes it easier for me to read it.

        basePoint = i * (2 * containerSize - 1) + containerSize

        # this for loop fills the lists that correspond to the shorter
        # lines of the lattice

        for x in range(0, containerSize - 3):

            if x == 0:
                shorterLineLEdges.append(basePoint)

            shorterLineMiddles.append(basePoint + x + 1)

            if x == containerSize - 4:
                shorterLineREdges.append(basePoint + containerSize - 2)

        # this if loop is here because if there are an even number of rows,
        # then the bottom row is short, which means there is one fewer iteration
        # needed of the longer line list appending.

        if containerEven or i != (containerSize - 2) // 2 - 1 + containerSize % 2:

            # this for loop fills the lists that correspond to the longer
            # lines of the lattice

            for x in range(0, containerSize - 2):

                if x == 0:
                    longerLineLEdges.append(basePoint + containerSize - 1)

                longerLineMiddles.append(basePoint + containerSize + x)

                if x == containerSize - 3:
                    longerLineREdges.append(basePoint + 2 * containerSize - 2)

    # these print statements are for debugging, to make sure that everything is
    # categorized correctly

    #print("\nshorterLineMiddles: " + ' '.join(map(str, shorterLineMiddles)))
    #print("\nshorterLineLEdges: " + ' '.join(map(str, shorterLineLEdges)))
    #print("\nshorterLineREdges: " + ' '.join(map(str, shorterLineREdges)))
    
    #print("\nlongerLineMiddles: " + ' '.join(map(str, longerLineMiddles)))
    #print("\nlongerLineLEdges: " + ' '.join(map(str, longerLineLEdges)))
    #print("\nlongerLineREdges: " + ' '.join(map(str, longerLineREdges)))

    # this fills the initial lattice array
    # 0 - corresponds to a path without a particle
    # 1 - corresponds to a path with a particle
    # 2 - corresponds to a wall

    for i in range(0, cellNumber):

        # these define the top row

        if i == 0:
            latticeList[i] = Nodes(i, 0, 2, 2, 2, 2, 0)  # topLeft

        elif i < containerSize - 1:
            latticeList[i] = Nodes(i, 0, 2, 2, 0, 0, 0) # topMid
               
        elif i == containerSize - 1:
            latticeList[i] = Nodes(i, 2, 2, 2, 0, 0, 2) # topRight
        
        
        # these define the shorter middle rows
        
        elif i in shorterLineMiddles:
            latticeList[i] = Nodes(i, 0, 0, 0, 0, 0, 0) # shorterMid
         
        elif i in shorterLineLEdges:
            latticeList[i] = Nodes(i, 0, 0, 0, 2, 0, 0) # shorterLeft

        elif i in shorterLineREdges:
            latticeList[i] = Nodes(i, 2, 0, 0, 0, 0, 0) # shorterRight
        
        
        # these define the longer middle rows

        elif i in longerLineMiddles:
            latticeList[i] = Nodes(i, 0, 0, 0, 0, 0, 0) # longerMid
             
        elif i in longerLineLEdges:
            latticeList[i] = Nodes(i, 0, 0, 2, 2, 2, 0) # longerLeft
            
        elif i in longerLineREdges:
            latticeList[i] = Nodes(i, 2, 2, 0, 0, 0, 2) # longerRight
            

        else:

        # this block is for the bottom row, the if statement is there because
        # the bottom row can be either long or short, which changes which areas
        # are walls or paths.

            if containerEven:

                if i == cellNumber - 1:
                    latticeList[i] = Nodes(i, 2, 0, 0, 0, 2, 2) # bottomRight

                elif i > cellNumber - containerSize + 1:
                    latticeList[i] = Nodes(i, 0, 0, 0, 0, 2, 2) # bottomMid

                elif i == cellNumber - containerSize + 1:
                    latticeList[i] = Nodes(i, 0, 0, 0, 2, 2, 2) # bottomLeft
                    
            elif not containerEven:

                if i == cellNumber - 1:
                    latticeList[i] = Nodes(i, 2, 2, 0, 0, 2, 2) # bottomRight

                elif i > cellNumber - containerSize:
                    latticeList[i] = Nodes(i, 0, 0, 0, 0, 2, 2) # bottomMid
                    
                elif i == cellNumber - containerSize:
                    latticeList[i] = Nodes(i, 0, 0, 2, 2, 2, 2) # bottomLeft
                    
            else:

            # I included this just in case something goes wrong

                latticeList.append('UND')

    # this displays the lattice in number form

    print("\n\nold latticeList: ")
    for i in range(0,len(latticeList)):
        print(latticeList[i].request_string(), end =' ')
    return latticeList


# ----------------------------------------------------------------------------#

# places particles randomly, if a particle is in a position at first, it is
# assumed to be moving away from the center of the parent node.

def particleDistribution(latticeList):
    particlesRemaining = particleNumber
    cellNumber = cell_number(containerSize, particleNumber)
    # places a particle each iteration

    while particlesRemaining != 0:
        
        
        site = random.randint(0, cellNumber-1)
        #nodeAtSite = latticeList[site].request_string()

        # print statements are for easy debugging

        #print('\nOriginal: ' + nodeAtSite + ' Pos: ' + str(site))
        spotsRemaining, openSpots = latticeList[site].spots_remaining()
        

        if spotsRemaining>0:
            positionChosen = random.choice(openSpots)

            latticeList[site].replace_value(positionChosen, 1)

            particlesRemaining-=1
            #print('\nNew: ' + nodeAtSite + ' Pos: ' + str(site))
        
            #print('son of a gun, node full')



        
    return latticeList


# ----------------------------------------------------------------------------#

latticeList = particleDistribution(the_categorizer(containerSize,particleNumber))
print("\n\nnew latticeList: ")
for i in range(0,len(latticeList)):
    print(latticeList[i].request_string(), end =' ')

# ----------------------------------------------------------------------------#
