#!/usr/bin/python
# -*- coding: utf-8 -*-
# spot for modifiable variables:


import matplotlib.pyplot as plt
import numpy as np
from numpy import random
import time


# ----------------------------------------------------------------------------#

class Lattice:
    """Class used to create and display the lattice.
    
    For Initialization:
    containerSize refers to the length of one side of the square container.
    particleNumber refers to the number of particles added during random distribution
    distribution refers to the type of particle distribution.
        
    Currently there are three parameters for distribution:
        
        'random', which creates a random assortment of particles based on particleNumber
        
        'tripleCollisionDemo', which places six particles in the two possible orientations
        that could produce a three-direction collision
        
        'doubleCollisionDemo', which places six particles in the three possible orientations
        that could produce a two-direction collision."""
    #================================================================================#
    
    def __init__(self, containerSize=100, particleNumber=5000, distribution='random'):
        
        self.lattice = np.zeros((containerSize, containerSize, 6), np.int8)
        self.containerSize = containerSize
        self.particleNumber = particleNumber


        if distribution == 'tripleCollisionDemo':
            self.manual_particles([(3, 3, 5), (5, 3, 1), (4, 5, 3), (8, 6, 0), (7, 7, 4), (9, 7, 2)])
        
        elif distribution == 'doubleCollisionDemo':    
            self.manual_particles([(1, 1, 5), (3, 2, 2), (5, 5, 0), (5, 7, 3), (8, 2, 1), (6, 3, 4)])
        
        elif distribution == 'random':
            self.random_particles()
        
        else:
            self.random_particles()

    #================================================================================#   
     
    def request_string(self, column, row):
        """Takes the target position in terms of a row and "column" and
        returns a string made from the paths around the node"""

        stringOutput = ''

        for i in range(0, 6):
            stringOutput = stringOutput + str(self.lattice[row][column][i])
        
        return stringOutput

    #================================================================================#

    def spots_remaining(self, column, row):
        """Takes the target position in terms of a row and "column" and
        returns the number of spots, followed by their positions as a
        tuple."""

        listOfSpots = []

        for i in range(0,6):
            if self.lattice[column][row][i] == 0:
                listOfSpots.append(i)
        
        return listOfSpots

    #================================================================================#

    def request_pretty_list(self):
        """Creates a string version of the array, 0s denote open spots, 1s denote
        particles"""
        for i in range(0, self.containerSize):
            for x in range(0, self.containerSize):
                print(self.request_string(i,x), end = ' ')
            print('\n')

    #================================================================================#
    
    def cell_number(self):

        """Finds number of cells based on containerSize"""

        cellNumber = self.containerSize * self.containerSize - int(self.containerSize / 2)

        return cellNumber   

    #================================================================================#

    def random_particles(self):
        """places particles randomly, if a particle is in a position at first, it is
        assumed to be moving away from the center of the parent node."""

        assert self.particleNumber <= self.cell_number() * 6

        particlesRemaining = self.particleNumber
        
        # the following while loop attempts to place a particle each iteration, if the spot
        # picked is full, it finds a new random spot on the next iteration. It consumes
        # particles as it goes, until it runs out. If a spot is full, nothing is consumed.

        while particlesRemaining != 0:
            
            # these randomly select a row and column
            randomColumn = random.randint(1, self.containerSize-2)
            randomRow = random.randint(1, self.containerSize-2)
            openSpots = self.spots_remaining(randomColumn, randomRow)

            
            # this if statement ensures that the only time a particle is added is when there
            # are spots remaining.
            if len(openSpots) > 0:
                positionChosen = random.choice(openSpots)
                self.lattice[randomRow][randomColumn][positionChosen] = 1

                particlesRemaining -= 1

    #================================================================================#

    def manual_particles(self, manualParticleList):
        
        for i in range(0, len(manualParticleList)):
            x, y, z = manualParticleList[i]

            self.lattice[x][y][z] = 1

    #================================================================================#

    def particle_counter(self):
        """creates a array of how many particles are around the nodes in each spot."""
        particleCountTime.recordTime()
        particleCountList = np.zeros((self.containerSize, self.containerSize), np.int8)

        for i in range(0, self.containerSize):
            for x in range(0, self.containerSize):
                particleCountList[i][x] = np.count_nonzero(self.lattice[i][x] == 1)


        self.particleCountList = particleCountList
        particleCountTime.recordTime()
  
    #================================================================================#

    def display_heatmap(self, timeStep=50, pauseBetweenSteps=.05):
        """this displays the "container" and the particle density inside of it. runs
        propagate, then collision, and then recounts particle density."""
        countVar = timeStep
        fig, ax = plt.subplots()
        

        ax.set_title("Particle Distribution")
        fig.tight_layout()
        self.particle_counter()
        im = ax.imshow(self.particleCountList, cmap='Blues')

        while countVar != 0:
            displayTime.recordTime()
            overallTime.recordTime()
            self.particle_counter()
            
            im.set_data(self.particleCountList)
            self.propagate()
            self.collide()
            
            plt.pause(pauseBetweenSteps)
            countVar -=1
            if(countVar == 0):
                print('overall:')
                overallTime.requestTotalTime()

                overallTime.requestTimeList()
                
                print('propagate:')
                propoTime.requestTotalTime()

                propoTime.requestHalfList()
                
                print('collision:')
                collisionTime.requestTotalTime()

                collisionTime.requestHalfList()

                print('display:')
                displayTime.requestTotalTime()

                displayTime.requestHalfList()

                print('particle counter:')
                particleCountTime.requestTotalTime()

                particleCountTime.requestHalfList()

            displayTime.recordTime()


        plt.show()

    #================================================================================#

    def propagate(self):
        """propagate process the first part of each "turn", where move from their parent
        node to another node, based on their index position. at the beginning of
        propagate, particles are moving away from the central node, at the end,
        they are moved and considered to be moving away."""
        newBoard = np.zeros((self.containerSize, self.containerSize, 6), np.int8)


        vectorsOnEvenRow = [(1, 0, 3), (0, -1, 3), (-1, -1, 3), (-1, 0, -3), (-1, 1, -3), (0, 1, -3)]
        vectorsOnOddRow = [(1, 0, 3), (1, -1, 3), (0, -1, 3), (-1, 0, -3), (0, 1, -3), (1, 1, -3)]
        propoTime.recordTime()
        for y in range(0, self.containerSize):
            for x in range(0, self.containerSize):
                # that if statement actually helps! (marginally)
                if self.particleCountList[y][x] > 0: # just for efficiency, many spaces have no particles, so no need to check all their spaces
                    for z in range(0, 6):
                        
                        if y % 2 == 0:
                            xChange, yChange, zChange = vectorsOnEvenRow[z]
                        else:
                            xChange, yChange, zChange = vectorsOnOddRow[z]
                        if self.lattice[y][x][z] == 1:
                            newBoard[y + yChange][x + xChange][z + zChange] = 1


        self.lattice = newBoard
        propoTime.recordTime()
        
    #================================================================================#

    def collide(self):
        """collide processes the second part of each "turn", where particles bounce off edges
        and other particles. On entering collide, particles have an index which denotes the
        direction that they are approaching the center of the node from. During collide, the
        particles move from their original index, to another index, across the node if there
        is no collision."""
        collisionTime.recordTime()
        newBoard = np.zeros((self.containerSize, self.containerSize, 6), np.int8)
        standardVectors = [3, 3, 3, -3, -3, -3]
        leftBounceVectors = [0, 4, 3, -3, -3, -4]
        rightBounceVectors = [3, 3, 2, 0, -2, -3]
        topBounceVectors = [3, 3, 3, -3, 1, -1]
        bottomBounceVectors = [3, 1, -1, -3, -3, -3]
        


        for y in range(0, self.containerSize):
            for x in range(0, self.containerSize):
                for z in range(0, 6):
                   
                    if self.lattice[y][x][z] == 1:

                        if x != self.containerSize - 1 and y != self.containerSize - 1 and x != 0 and y != 0:
                            
                            zChange = standardVectors[z]
                            if self.lattice[y][x][z + zChange] == 1:                               

                                if z == 0 or z == 3:
                                    scatterPattern = random.choice([1, 2])

                                elif z == 1 or z == 4:
                                    scatterPattern = random.choice([-1, 1])
                
                                elif z == 2 or z == 5:
                                    scatterPattern = random.choice([-1, -2])


                                newBoard[y][x][z + scatterPattern] = 1
                                newBoard[y][x][z + zChange + scatterPattern] = 1
                                self.lattice[y][x][z] = 0
                                self.lattice[y][x][z + zChange] = 0

                            elif z < 3 and self.lattice[y][x][z + 2] == 1 and self.lattice[y][x][z + 6*(z % 2) - 2] == 1:
                                
                                self.lattice[y][x][z] = 0
                                self.lattice[y][x][z + 2] = 0
                                self.lattice[y][x][z + 6*(z % 2) - 2] = 0
                                newBoard[y][x][z] = 1
                                newBoard[y][x][z + 2] = 1
                                newBoard[y][x][z + 6*(z % 2) - 2] = 1

                            else:
                                newBoard[y][x][z + zChange] = 1
                        
                        else:
                            if x == self.containerSize - 1:
                                zChange = rightBounceVectors[z]

                            elif y == self.containerSize - 1:
                                zChange = bottomBounceVectors[z]
                            
                            elif x == 0:
                                zChange = leftBounceVectors[z]
                            
                            elif y == 0:
                                zChange = topBounceVectors[z]

                                
                            newBoard[y][x][z + zChange] = 1
                    

        self.lattice = newBoard
        collisionTime.recordTime()
        
    #================================================================================#


class Timer:
    """Used for debugging purposes, has a few utilities which measure the time it takes for a
    block of code to run"""

    def __init__(self):
        self.startingTime = 0
        self.timesRecorder = [0]
        self.timesSinceLastCheck = []

    def startTimer(self):
        """Starts the initial timer, used to determine total time a program takes to run"""
        self.startingTime = time.perf_counter()

    def recordTime(self):
        """Records the time state, and appends it to timesRecorder. Then appends the difference
        in the recorded time, and the time before it, in timesSinceLastCheck."""
        
        timeElapsed = time.perf_counter() - self.startingTime 
        
        self.timesRecorder.append(timeElapsed)
        self.timesSinceLastCheck.append(np.round(self.timesRecorder[-1] - self.timesRecorder[-2], decimals=3))

    def requestTotalTime(self):
        """Simple function which prints the last time recorded"""
        print(self.timesRecorder[-1])

    def requestTimeList(self):
        """displays the recorded list of time differences, only suitable when only one recordTime function
        is triggered in a test run.""" 
        for i in range(len(self.timesSinceLastCheck)//10):
            for x in range(10):
                print(self.timesSinceLastCheck[i*10 + x], end=', ')

            print('\n')

    def requestHalfList(self):
        """displays the recorded list of time differences when running one recordTime at the beginning of a
        function, and another at the end. Skips every other value in order to only see the space between the
        two calls of RecordTime."""
        for i in range(len(self.timesSinceLastCheck)//10):
            for x in range(1, 10, 2):
                
                print(self.timesSinceLastCheck[i*10 + x], end=', ')

            print('\n')
                
latticeList = Lattice(containerSize=100, particleNumber=10000, distribution='random')

overallTime = Timer()
propoTime = Timer()
collisionTime = Timer()
displayTime = Timer()
particleCountTime = Timer()


overallTime.startTimer()
propoTime.startTimer()
collisionTime.startTimer()
displayTime.startTimer()
particleCountTime.startTimer()

latticeList.display_heatmap(timeStep=100, pauseBetweenSteps=.05)




