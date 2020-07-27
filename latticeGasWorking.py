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
        self.distribution = distribution
        self.bounces = 0
        self.rValues = []
        self.pValues = []
        self.bValues = []


        if distribution == 'tripleCollisionDemo':
            self.manual_particles([(3, 3, 5), (5, 3, 1), (4, 5, 3), (8, 6, 0), (7, 7, 4), (9, 7, 2)])
        
        elif distribution == 'doubleCollisionDemo':    
            self.manual_particles([(1, 1, 5), (3, 2, 2), (5, 5, 0), (5, 7, 3), (8, 2, 1), (6, 3, 4)])
        
        elif distribution == 'random':
            self.random_particles()
        
        else:
            self.random_particles()

    #================================================================================#   
     
    def __repr__(self):
        """Creates a string version of the array, 0s denote open spots, 1s denote
        particles"""
        listOutput = ''
        
        for i in range(0, self.containerSize):
            for x in range(0, self.containerSize):
                listOutput += self.request_string(i,x)
                listOutput += ' '
            listOutput += '\n'

        return listOutput

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
        particleCountList = np.zeros((self.containerSize, self.containerSize), np.int8)

        for i in range(0, self.containerSize):
            for x in range(0, self.containerSize):
                particleCountList[i][x] = np.count_nonzero(self.lattice[i][x] == 1)


        self.particleCountList = particleCountList
  
    #================================================================================#

    def display_heatmap(self, timeStep=50, pauseBetweenSteps=.05):
        """this displays the "container" and the particle density inside of it. runs
        propagate, then collision, and then recounts particle density."""
        
        fig, ax = plt.subplots()
        
        self.timeStep = timeStep
        
        countVar = self.timeStep
        ax.set_title("Particle Distribution")
        fig.tight_layout()
        self.particle_counter()
        im = ax.imshow(self.particleCountList, cmap='Blues')

        while countVar != 0:
            
            self.particle_counter()
            
            im.set_data(self.particleCountList)
            self.find_particles()
            self.propagate()
            self.find_particles()
            self.collide()
            
            plt.pause(pauseBetweenSteps)
            countVar -=1
            if(countVar == 1):
                
                print('wall bounces: ' + str(self.bounces))


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
        
        for y in self.yList:
            
            for x in self.xList:
                # that if statement actually helps! (marginally)
                #if self.particleCountList[y][x] > 0: # just for efficiency, many spaces have no particles, so no need to check all their spaces
                for z in range(0, 6):
                        
                    if y % 2 == 0:
                        xChange, yChange, zChange = vectorsOnEvenRow[z]
                    else:
                        xChange, yChange, zChange = vectorsOnOddRow[z]
                    if self.lattice[y][x][z] == 1:
                        newBoard[y + yChange][x + xChange][z + zChange] = 1


        self.lattice = newBoard
        
    #================================================================================#

    def collide(self):
        """collide processes the second part of each "turn", where particles bounce off edges
        and other particles. On entering collide, particles have an index which denotes the
        direction that they are approaching the center of the node from. During collide, the
        particles move from their original index, to another index, across the node if there
        is no collision."""
        newBoard = np.zeros((self.containerSize, self.containerSize, 6), np.int8)
        standardVectors = [3, 3, 3, -3, -3, -3]
        topBounceVectors = [0, 4, 3, -3, -3, -4]
        bottomBounceVectors = [3, 3, 2, 0, -2, -3]
        leftBounceVectors = [3, 3, 3, -3, 1, -1]
        rightBounceVectors = [3, 1, -1, -3, -3, -3]
        scatterList = [(1,2), (-1,1), (-1,-2)]

        
        for y in self.yList:
            for x in self.xList:
                for z in range(0, 6):
                   
                    if self.lattice[y][x][z] == 1:

                        if x != self.containerSize - 1 and y != self.containerSize - 1 and x != 0 and y != 0:
                            
                            zChange = standardVectors[z]
                            if self.lattice[y][x][z + zChange] == 1:                               

                                
                                scatterPattern = random.choice(scatterList[z])

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
                            
                            if x == self.containerSize - 1: # bottom
                                zChange = bottomBounceVectors[z]
                                self.bounces += np.sqrt(3) / 2
                                

                            elif y == self.containerSize - 1: # right side
                                zChange = rightBounceVectors[z]
                                if z == 0:
                                    self.bounces += 1.0
                                else:
                                    self.bounces += 0.5
                            
                            elif x == 0: # top
                                zChange = topBounceVectors[z]
                                self.bounces += np.sqrt(3) / 2
                            
                            elif y == 0: # left side
                                zChange = leftBounceVectors[z]
                                if z == 3:
                                    self.bounces += 1.0
                                else:
                                    self.bounces += 0.5

                               
                            newBoard[y][x][z + zChange] = 1
                    

        self.lattice = newBoard

    #================================================================================#    
    
    def simulation_stats(self):
        """Records the r value when called."""
        
        self.avgParticleVelocity = self.timeStep / (self.containerSize - 1)
        self.pressure = (self.bounces * (self.avgParticleVelocity)**2) / 8
        
        self.rT = self.pressure / self.particleNumber

        self.rValues.append(self.rT)
        
        self.pValues.append(self.pressure)
        self.bValues.append(self.bounces)

    #================================================================================#

    def no_display_run(self, timeStep=20, numberOfRuns=1):
        """this runs a simulation of the particle physics without displaying anything.
        Runs a number of times as indicated by numberOfRuns, and displays r values."""
        
        
        
        self.timeStep = timeStep

        for i in range(0, numberOfRuns):
            countVar = self.timeStep
            while countVar != 0:

                self.find_particles()
                self.propagate()

                self.find_particles()
                self.collide()
                
                countVar -=1

                if(countVar == 0):
                    
                    self.simulation_stats()
                    print("\nTrial " + str(i+1) + ":\nrT = " + str(self.rValues[i]))
                    print("Pressure: " + str(self.pressure))
                    print("Volume: 1")
                    print("Number of Particles: " + str(self.particleNumber))
                    #print("Temperature: " + str(self.temperature))
                    print("Bounces: " + str(self.bounces))
                    print("Time Steps: " + str(self.timeStep))

            self.reset_simulation()

        
        print("\nAverage rT value: " + str(sum(self.rValues)/len(self.rValues)))
        print("Average Pressure value: " + str(sum(self.pValues)/len(self.pValues)))
        print("Average Number of Bounces: " + str(sum(self.bValues)/len(self.bValues)))

    #================================================================================#

    def reset_simulation(self):
        """Wipes the board and resets bounces, then redistributes the correct number of particles."""
        self.lattice = np.zeros((self.containerSize, self.containerSize, 6), np.int8)
        self.bounces = 0
        

        if self.distribution == 'tripleCollisionDemo':
            self.manual_particles([(3, 3, 5), (5, 3, 1), (4, 5, 3), (8, 6, 0), (7, 7, 4), (9, 7, 2)])
        
        elif self.distribution == 'doubleCollisionDemo':    
            self.manual_particles([(1, 1, 5), (3, 2, 2), (5, 5, 0), (5, 7, 3), (8, 2, 1), (6, 3, 4)])
        
        elif self.distribution == 'random':
            self.random_particles()
        
        else:
            self.random_particles()

    #================================================================================#

    def find_particles(self):
        self.xList = []
        fullSpotList = np.any(self.lattice, axis=2)

        tfyList = np.any(fullSpotList, axis=1)
        indexList = np.where(tfyList == 1)
        self.yList = indexList[0]

        for y in self.yList:      
            xIndexList = np.where(fullSpotList[y] == 1)
            self.xList.append(xIndexList[0][0])

    #================================================================================#


latticeList = Lattice(containerSize=500, particleNumber=100, distribution='random')

latticeList.no_display_run(timeStep=500, numberOfRuns=10)

#latticeList.display_heatmap(timeStep=20, pauseBetweenSteps=.05)

