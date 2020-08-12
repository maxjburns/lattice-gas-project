#!/usr/bin/python
# -*- coding: utf-8 -*-
# spot for modifiable variables:


import matplotlib.pyplot as plt
import numpy as np
from numpy import random
import pytest
from scipy.optimize import leastsq
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
        self.multiRun = False
        


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
            if self.lattice[row][column][i] == 0:
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
        self.counter = 0
        self.coordList = []
        particlesRemaining = self.particleNumber
        
        # the following while loop attempts to place a particle each iteration, if the spot
        # picked is full, it finds a new random spot on the next iteration. It consumes
        # particles as it goes, until it runs out. If a spot is full, nothing is consumed.

        while particlesRemaining != 0:
            
            # these randomly select a row and column
            randomColumn = random.randint(1, self.containerSize-1)
            randomRow = random.randint(1, self.containerSize-1)
            openSpots = self.spots_remaining(randomColumn, randomRow)

            
            # this if statement ensures that the only time a particle is added is when there
            # are spots remaining.
            if len(openSpots) > 0:
                positionChosen = random.choice(openSpots)
                self.lattice[randomRow][randomColumn][positionChosen] = 1
                
                self.coordList.append([randomRow, randomColumn, positionChosen])
                self.counter += 1
                
                particlesRemaining -= 1

    #================================================================================#

    def manual_particles(self, manualParticleList):
        
        for i in range(0, len(manualParticleList)):
            x, y, z = manualParticleList[i]

            self.lattice[x][y][z] = 1

    #================================================================================#

    def particle_counter(self, yStart=0, yEnd=-1, xStart=0, xEnd=-1):
        """creates a array of how many particles are around the nodes in each spot."""
        
        if yEnd == -1:
            yEnd = self.containerSize
            xEnd = self.containerSize
        
        particleCountList = np.zeros((yEnd - yStart, xEnd - xStart), np.int8)
        xIndex = 0
        yIndex = 0
        yEnd-=1
        xEnd-=1

        for y in range(yStart, yEnd):
            xIndex = 0
            for x in range(xStart, xEnd):
                
                particleCountList[yIndex][xIndex] = np.count_nonzero(self.lattice[y][x] == 1)

                xIndex+=1
            yIndex+=1

        return particleCountList
  
    #================================================================================#

    def display_heatmap(self, timeStep=50, pauseBetweenSteps=.05):
        """this displays the "container" and the particle density inside of it. runs
        propagate, then collision, and then recounts particle density."""
        
        fig, ax = plt.subplots()
        
        self.timeStep = timeStep
        
        countVar = self.timeStep
        ax.set_title("Particle Distribution")
        fig.tight_layout()
        particleCountList = self.particle_counter()
        im = ax.imshow(particleCountList, cmap='plasma')
        fig.colorbar(im, ax=ax)

        while countVar > 0:
            
            particleCountList = self.particle_counter()
            
            im.set_data(particleCountList)
            
            self.propagate()
            
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
        self.newBoard = np.zeros((self.containerSize, self.containerSize, 6), np.int8)
        
        vectorsOnEvenRow = [(1, 0, 3), (0, -1, 3), (-1, -1, 3), (-1, 0, -3), (-1, 1, -3), (0, 1, -3)]
        vectorsOnOddRow = [(1, 0, 3), (1, -1, 3), (0, -1, 3), (-1, 0, -3), (0, 1, -3), (1, 1, -3)]
        
        for (i, coord) in enumerate(self.coordList): 
            y, x, z = coord
            
            if y % 2 == 0:
                xChange, yChange, zChange = vectorsOnEvenRow[z]
            else:
                xChange, yChange, zChange = vectorsOnOddRow[z]

            self.point_change(i, [y + yChange, x + xChange, z + zChange])
        
        self.lattice = self.newBoard.copy()
        self.newBoard = []
        
    #================================================================================#

    def collide(self):
        """collide processes the second part of each "turn", where particles bounce off edges
        and other particles. On entering collide, particles have an index which denotes the
        direction that they are approaching the center of the node from. During collide, the
        particles move from their original index, to another index, across the node if there
        is no collision."""
        self.newBoard = np.zeros((self.containerSize, self.containerSize, 6), np.int8)
        standardVectors = [3, 3, 3, -3, -3, -3]
        topBounceVectors = [0, 4, 3, -3, -3, -4]
        bottomBounceVectors = [3, 3, 2, 0, -2, -3]
        leftBounceVectors = [3, 3, 3, -3, 1, -1]
        rightBounceVectors = [3, 1, -1, -3, -3, -3]
        scatterList = [(1,2), (-1,1), (-1,-2), (1,2), (-1,1), (-1,-2)]
        tripleIndexes = [(2, 4), (3, 5), (4, 0), (5, 1), (0, 2), (1,3)]
        scatteredVals = []
        self.scatterCounter = 0

        for (i, coord) in enumerate(self.coordList):
            
            y, x, z = coord  
            
            if x != self.containerSize - 1 and y != self.containerSize - 1 and x != 0 and y != 0:
                                
                zChange = standardVectors[z]
                tripOne, tripTwo = tripleIndexes[z]
                
                if self.lattice[y][x][z + zChange] == 1 and np.sum(self.lattice[y][x])==2:                               
                    
                    if not [y, x, z] in scatteredVals:
                        scatteredVals.append([y, x, z + zChange])
                        scatteredVals.append([y, x, z])
                        scatterPattern = scatterList[z][self.scatterCounter]
                        self.scatterCounter = -1 * self.scatterCounter + 1

                        self.point_change(i, [y, x, z + scatterPattern])
                        self.point_change(i, [y, x, z + zChange + scatterPattern])

                elif self.lattice[y][x][tripOne] == 1 and self.lattice[y][x][tripTwo] == 1:
                    self.point_change(i, coord)

                else:
                    self.point_change(i, [y, x, z + zChange])
                        
            else:
                cornerCheck = 0               
                tempBounces = self.bounces

                if x == self.containerSize - 1: # bottom
                    zChange = bottomBounceVectors[z]
                    self.bounces += np.sqrt(3) / 2
                    cornerCheck += 1

                if y == self.containerSize - 1: # right side
                    zChange = rightBounceVectors[z]
                    if z == 0:
                        self.bounces += 1.0
                    else:
                        self.bounces += 0.5
                    cornerCheck += 1
                                
                if x == 0: # top
                    zChange = topBounceVectors[z]
                    self.bounces += np.sqrt(3) / 2
                    cornerCheck += 1
                                
                if y == 0: # left side
                    zChange = leftBounceVectors[z]
                    if z == 3:
                        self.bounces += 1.0
                    else:
                        self.bounces += 0.5
                    cornerCheck += 1

                if cornerCheck > 1:
                    self.bounces = tempBounces + 1.0
                    zChange = 0

                self.point_change(i, [y, x, z + zChange])

        
        self.lattice = self.newBoard.copy()
       
        self.newBoard = []

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
            
            while countVar > 0:
                
                self.propagate()
                self.collide()

                countVar -=1
                
                if(countVar == 0):
                    
                    self.simulation_stats()
                    
                    print("\nTrial " + str(i+1) + ":\nrT = " + str(self.rValues[i]))
                    print("Pressure: " + str(self.pressure))
                    print("Volume: 1")
                    print("Number of Particles: " + str(self.particleNumber))
                    print("Bounces: " + str(self.bounces))
                    print("Time Steps: " + str(self.timeStep))
                    print("containerSize: " + str(self.containerSize))

            self.finalBounces = self.bounces
            if numberOfRuns > 1:
                self.reset_simulation()

        
        print("\nAverage rT value: " + str(sum(self.rValues)/len(self.rValues)))
        print("Average Pressure value: " + str(sum(self.pValues)/len(self.pValues)))
        print("Average Number of Bounces: " + str(sum(self.bValues)/len(self.bValues)))
        
    #================================================================================#

    def reset_simulation(self, includeLists=False):
        """Wipes the board and resets bounces, then redistributes the correct number of particles."""
        if includeLists:
            self.rValues = []
            self.pValues = []
            self.bValues = []

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

    def plot_rT(self, testValue='tStep', minValue=100, maxValue=500, pointNumber=12, n=5, style="linear", tStep=30):
        """Graphs the rT values produced by the simulation.
        
        INPUT:
        -testValue is the value that will correspond to the x axis, and be varied. Expects a string 'tStep', 
        'containerSize', or 'particleNumber'.
        -minValue and maxValue expect ints, and correspond to the first mapped x value, and the final x value.
        -pointNumber expects an int, and designates how many points will be graphed.
        -n expects an int, and designates how many times a simulation is run with identical conditions, before the 
        results are averaged.
        -style expects a string, either "linear" or "logarithmic", and refers to the y axis scaling
        -tStep is only used when timeStep is not the value being tested, it determines the number of time steps each
        iteration, when testing containerSize or particleNumber.

        OUTPUT:
        -prints information about each iteration to the terminal, once finished, the intended graph is displayed."""

        stdRTValues = []
        avgRTValues = []
        self.multiRun = True

        fig = plt.figure()
        ax = fig.add_subplot()
        xList = np.linspace(minValue, maxValue, pointNumber)
        xList = [round(x) for x in xList]
        for i in range(len(xList)):
            xList[i] += xList[i] % 2
    

        #-----running simulations:-----#
        if testValue == 'tstep':
            for x in xList:

                self.reset_simulation(includeLists=True)
                latticeList.no_display_run(timeStep=x, numberOfRuns=n)
                
                stdRTValues.append(np.std(self.rValues))
                avgRTValues.append(np.average(self.rValues))
                
        else:
            for x in xList: 
                if testValue == 'containerSize':
                    self.containerSize = x
                elif testValue == 'particleNumber':
                    self.particleNumber = x
                
                self.reset_simulation(includeLists=True)
                latticeList.no_display_run(timeStep=tStep, numberOfRuns=n)
                
                stdRTValues.append(np.std(self.rValues))
                avgRTValues.append(np.average(self.rValues))
        
        
        #-----least square:-----#
        
        def model(x, b, r):
            return b * np.power(x, r)

        def residuals(p, rT, x, rTerr):
            err = (rT - model(x, p[0], p[1]))/rTerr
            return err

        print("\nStandard Deviation of RT averages:")
        print(stdRTValues)

        plsq = leastsq(residuals, x0=[1.0, -2.0], args=(avgRTValues, xList, stdRTValues))
        betaFit = plsq[0][0]
        rFit = plsq[0][1]
        print(plsq)
        
        print("\n\nbetaFit Value:")
        print(betaFit)
        print("\n\nrFit Value:")
        print(rFit)

        #-----setting up graph:-----#
        yList = avgRTValues
        curveList = np.linspace(minValue, maxValue, 1000)
        plt.errorbar(xList, yList, yerr=stdRTValues, fmt='o', ecolor='red')
        print(np.shape(curveList))
        print(np.shape(betaFit * np.power(curveList, rFit)))
        plt.plot(curveList, betaFit * np.power(curveList, rFit))
        print(betaFit / np.power(xList, rFit))

        ax.legend([testValue + "vs rT"])
        ax.set_ylabel("rT")
        ax.set_xlabel(testValue)
        plt.legend(loc='upper left')
        if style == 'logarithmic':
            ax.set_yscale('log')
            ax.set_xscale('log')

        plt.show()

    #================================================================================#

    def point_change(self, index, newCoord):
        """Takes the index value of coordList and the target coordinate. Replaces the value of
        coord and adds a particle to the new board."""
        newy, newx, newz = newCoord

        self.coordList[index] = newCoord
        self.newBoard[newy][newx][newz] = 1

    #================================================================================#

    def find_particle_boxes(self, resStep):
        arrayResolution = int(self.containerSize / resStep)
        resStep = int(resStep)
        
        
        for y in range(arrayResolution):
            for x in range(arrayResolution):
                yStart = y * resStep
                yEnd = (y + 1) * resStep
                xStart = x * resStep
                xEnd = (x + 1) * resStep
                
                self.heatmapList[y][x] = np.sum(self.lattice[yStart:yEnd, xStart:xEnd])

    #================================================================================#

    def display_advanced_data(self, timeStep=50, pauseBetweenSteps=.05, display='particleBoxes', arrayResolution=20):
        self.heatmapList = np.zeros((arrayResolution, arrayResolution), dtype=int)
        self.heatmapList[4][5] = 4 * self.particleNumber / arrayResolution**2 # why in the world does this work?

        if display == 'particleBoxes':
            resolutionStep = self.containerSize / arrayResolution

            if resolutionStep - int(resolutionStep) != 0:
                raise AssertionError()

            fig, ax = plt.subplots()
        
            self.timeStep = timeStep
            
            countVar = self.timeStep
            ax.set_title("Particle Distribution")
            fig.tight_layout()
            
            
            im = ax.imshow(self.heatmapList, cmap='plasma')
            fig.colorbar(im, ax=ax)
            
            while countVar > 0:

                self.find_particle_boxes(resStep=resolutionStep)
                
                im.set_data(self.heatmapList)
                
                self.propagate()
                
                self.collide()
                
                plt.pause(pauseBetweenSteps)
                countVar -=1
                if(countVar == 1):
                    
                    print('wall bounces: ' + str(self.bounces))
            
            plt.show()


class TesterClass:
    
    def test_bounceCount(self):
        latticeList = Lattice(containerSize=150, particleNumber=5000, distribution='random')
        latticeList.no_display_run(timeStep=30, numberOfRuns=1)
        assert latticeList.finalBounces > 800 and latticeList.finalBounces < 1100

    #================================================================================#

    def test_particlePlacer(self):
        latticeList = Lattice(containerSize=150, particleNumber=5000, distribution='random')
        latticeList.particle_counter()
        assert latticeList.particleNumber == 5000 and np.sum(latticeList.particle_counter()) == 5000   

    #================================================================================#

    def test_particlesDisappear(self):
        latticeList = Lattice(containerSize=15, particleNumber=10, distribution='random')
        latticeList.no_display_run(timeStep=300, numberOfRuns=1)
        latticeList.particle_counter()
        assert np.sum(latticeList.particle_counter()) == 10

    #================================================================================#


if __name__ == '__main__':

    latticeList = Lattice(containerSize=500, particleNumber=8000, distribution='random')

    #latticeList.plot_rT(testValue='particleNumber', minValue=100, maxValue=6000, pointNumber=6, n=6, style="logarithmic", tStep=40)
    #latticeList.no_display_run(timeStep=30, numberOfRuns=1)

    #latticeList.display_heatmap(timeStep=100, pauseBetweenSteps=.05)
    latticeList.display_advanced_data(timeStep=50, pauseBetweenSteps=.05, display='particleBoxes', arrayResolution=50)

