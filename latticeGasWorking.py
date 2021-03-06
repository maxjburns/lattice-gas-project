#!/usr/bin/python
# -*- coding: utf-8 -*-
# spot for modifiable variables:

import matplotlib.pyplot as plt
import numpy as np
from numpy import random
import pytest
from scipy.optimize import leastsq

# ----------------------------------------------------------------------------#

class Lattice:
    """
    Class used to create and display the lattice.
    
    For Initialization:
    containerSize refers to the length of one side of the square container.
    particleNumber refers to the number of particles added during random distribution
    distribution refers to the type of particle distribution.
        
    Currently there are four parameters for distribution:
        
        'random', which creates a random assortment of particles based on particleNumber

        'controlledRandom', which creates a random assortment of particles in defined
        x and y bounds.
        
        'tripleCollisionDemo', which places six particles in the two possible orientations
        that could produce a three-direction collision
        
        'doubleCollisionDemo', which places six particles in the three possible orientations
        that could produce a two-direction collision.
        """
    #================================================================================#
    
    def __init__(self, containerSize=100, particleNumber=5000, distribution='random', yBounds=(0,0), xBounds=(0,0)):
        
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

        elif distribution == 'controlledRandom':
            self.controlled_random_particles(yBounds, xBounds)
        
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

    def controlled_random_particles(self, yBounds, xBounds):
        """
        places particles randomly, if a particle is in a position at first, it is
        assumed to be moving away from the center of the parent node. Takes yBounds
        and xBounds as arguments, both are tuples.
        """
        
        xMin, xMax = xBounds
        yMin, yMax = yBounds
        
        assert yMin != yMax and xMin != xMax 
        assert yMin > 1 and xMin > 1  
        assert yMax < self.containerSize-1 and xMax < self.containerSize-1
        assert self.particleNumber <= (yMax - yMin) * (xMax - xMin) * 6

        self.counter = 0
        self.coordList = []
        particlesRemaining = self.particleNumber
        
        # the following while loop attempts to place a particle each iteration, if the spot
        # picked is full, it finds a new random spot on the next iteration. It consumes
        # particles as it goes, until it runs out. If a spot is full, nothing is consumed.

        while particlesRemaining != 0:
            
            # these randomly select a row and column
            randomColumn = random.randint(xMin, xMax)
            randomRow = random.randint(yMin, yMax)
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
        im = ax.imshow(particleCountList, cmap='Blues', interpolation='bilinear')
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
        """
        propagate process the first part of each "turn", where move from their parent
        node to another node, based on their index position. at the beginning of
        propagate, particles are moving away from the central node, at the end,
        they are moved and considered to be moving away.
        """
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
        """
        collide processes the second part of each "turn", where particles bounce off edges
        and other particles. On entering collide, particles have an index which denotes the
        direction that they are approaching the center of the node from. During collide, the
        particles move from their original index, to another index, across the node if there
        is no collision.
        """
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
        """
        Graphs the rT values produced by the simulation.
        
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
        -prints information about each iteration to the terminal, once finished, the intended graph is displayed.
        """

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
        
        print("\n\nbetaFit Value:")
        print(betaFit)
        print("\n\nrFit Value:")
        print(rFit)

        #-----setting up graph:-----#
        yList = avgRTValues
        curveList = np.linspace(minValue, maxValue, 1000)
        plt.errorbar(xList, yList, yerr=stdRTValues, fmt='o', ecolor='red')
        plt.plot(curveList, betaFit * np.power(curveList, rFit))

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
        """
        Takes the index value of coordList and the target coordinate. Replaces the value of
        coord and adds a particle to the new board.
        """
        newy, newx, newz = newCoord

        self.coordList[index] = newCoord
        self.newBoard[newy][newx][newz] = 1

    #================================================================================#

    def display_advanced_data(self, displayType, title, timeStep=50, pauseBetweenSteps=.05, arrayResolution=20):
        """
        Method to display more advanced data, including a lower resolution particle map, and vector field diagram.

        INPUT:
        *timeStep- the total number of movement steps to process
        *pauseBetweenSteps- the amount of time between each movement step, must be greater than zero.
        *arrayResolution- the dimensions of the displayed array.
        *display- takes a function which returns one or more lists. One list will create a heatmap,
        two lists will create a vector map, three lists will create a vector map with a heatmap
        in the background.

        OUPUT:
        displays a visualization, based on the value of display:
        'particleBoxes' creates a heatmap of particle distribution with dimensions based on array resolution. 
        Effectively, it is a lower resolution version of the standard display_heatmap().
        'momentumVectors' uses the simulation to create a vector field of arrows, based on total momentum at each point.
        """
        resolutionStep = self.containerSize / arrayResolution
        if resolutionStep - int(resolutionStep) != 0:
            raise AssertionError()

        self.timeStep = timeStep
        countVar = self.timeStep
        fig, ax = plt.subplots()
        fig.tight_layout()
        ax.set_title(str(title))
        
        data = displayType(resolutionStep)
        theType = type(np.zeros((2,2,2)))
        arraysOnly = [val for val in data if type(val)==theType]
        del(theType)
        if np.shape(arraysOnly) == (1, arrayResolution, arrayResolution):
            arraysOnly = arraysOnly[0]

        for countVar in range(self.timeStep, 0, -1):
            if np.shape(arraysOnly) == (arrayResolution, arrayResolution):
                if np.shape(data) != (arrayResolution, arrayResolution):
                    numberList = []
                    for i in range(1, len(data)):
                        numberList.append(data[i])
                    data = data[0]

                if countVar == self.timeStep:
                    im = ax.imshow(data, cmap='Blues', interpolation='bilinear')
                    im.set_clim(vmin=0, vmax=np.max(data)/2)
                    fig.colorbar(im, ax=ax)

                if np.max(data) > 5:
                    im.set_clim(vmin=0, vmax=np.max(data)/2)
                
                im.set_data(data)
                
            elif len(arraysOnly) == 2:
                if countVar % resolutionStep == 0:
                    plt.clf()
                    ax.set_title(str(title))
                    plt.quiver(data[0], data[1], scale=int(arrayResolution / 3), scale_units='inches')

            elif len(arraysOnly) == 3:
                ax.cla()
                ax.set_title(str(title))
                ax.quiver(data[0], data[1], scale = int(arrayResolution / 3), scale_units='inches', color='w', lw=.5, ec='black')
                im = ax.imshow(data[2], cmap='plasma', interpolation='bilinear')

                if countVar == self.timeStep:
                    im.set_clim(vmin=0, vmax=np.max(data[2])/2)
                    fig.colorbar(im, ax=ax)

                if np.max(data[2]) > 5:
                    im.set_clim(vmin=0, vmax=np.max(data[2])/2)

            self.propagate()
            self.collide()
                
            plt.pause(pauseBetweenSteps)
            data = displayType(resolutionStep)
            
        plt.show()         

    #================================================================================#

    def find_particle_boxes(self, resStep):
        """
        Used with the method display_advanced_data().
        INPUT:
        resStep- each "pixel" in the lattice has dimensions resStep x resStep,
        therefore is equal to containerSize / arrayResolution.
        
        OUTPUT:
        modifies self.heatmapList, replacing old values with the sum of all
        particles in a "pixel" of the lattice. a "pixel" is a square of dimensions
        resStep x resStep, and there are arrayResolution * arrayResolution "pixels".
        """
        arrayResolution = int(self.containerSize / resStep)
        heatmapList = np.zeros((arrayResolution, arrayResolution), dtype=int)
        resStep = int(resStep)
        
        for y in range(arrayResolution):
            for x in range(arrayResolution):
                yStart = y * resStep
                yEnd = (y + 1) * resStep
                xStart = x * resStep
                xEnd = (x + 1) * resStep
                
                heatmapList[y][x] = np.sum(self.lattice[yStart:yEnd, xStart:xEnd])

        return heatmapList

    #================================================================================#

    def find_momentum_vectors(self, resStep):
        """
        Used with the method display_advanced_data(), to create two lists of vector totals.
        INPUT:
        resStep- each "pixel" in the lattice has dimensions resStep x resStep,
        therefore is equal to containerSize / arrayResolution.
        
        OUTPUT:
        returns yVectorArray, xVectorArray in a tuple. both arrays are 2D, of dimensions
        arrayResolution x arrayResolution, and contain the seperated x and y components of
        total particle vectors.
        """
        arrayResolution = int(self.containerSize / resStep)
        resStep = int(resStep)
        yVectorArray = np.zeros((arrayResolution, arrayResolution))
        xVectorArray = np.zeros((arrayResolution, arrayResolution))
        countArray = np.zeros((arrayResolution, arrayResolution))
        totalMomentum = 0
        xyVectors = ((0.0, 1.0), (np.sqrt(3)/-2, 0.5), (np.sqrt(3)/-2, -0.5), (0.0, -1.0), (np.sqrt(3)/2, -0.5), (np.sqrt(3)/2, 0.5))

        for coord in self.coordList:
            y, x, z = coord
            xVector, yVector = xyVectors[z]

            yVectorArray[int(y // resStep)][int(x // resStep)] += yVector
            xVectorArray[int(y // resStep)][int(x // resStep)] += xVector

            countArray[int(y // resStep)][int(x // resStep)] += 1

            totalMomentum += (xVector**2 + yVector**2)

        yVectorArray = np.true_divide(yVectorArray, countArray)
        xVectorArray = np.true_divide(xVectorArray, countArray)
        
        return yVectorArray, xVectorArray, totalMomentum

    #================================================================================#

    def find_energy(self, resStep):
        """
        Used with the method display_advanced_data().
        INPUT:
        resStep- each "pixel" in the lattice has dimensions resStep x resStep,
        therefore is equal to containerSize / arrayResolution.
        
        OUTPUT:
        modifies self.heatmapList, replacing old values with the sum of all
        particles in a "pixel" of the lattice. a "pixel" is a square of dimensions
        resStep x resStep, and there are arrayResolution * arrayResolution "pixels".
        """
        arrayResolution = int(self.containerSize / resStep)
        heatmapList = np.zeros((arrayResolution, arrayResolution), dtype=int)
        resStep = int(resStep)
        xyVectors = ((0.0, 1.0), (np.sqrt(3)/2, 0.5), (np.sqrt(3)/2, -0.5), (0.0, -1.0), (np.sqrt(3)/-2, -0.5), (np.sqrt(3)/-2, 0.5))
        yVectorArray = np.zeros((arrayResolution, arrayResolution))
        xVectorArray = np.zeros((arrayResolution, arrayResolution))

        for coord in self.coordList:
            y, x, z = coord
            xVector, yVector = xyVectors[z]

            yVectorArray[int(y // resStep)][int(x // resStep)] += yVector
            xVectorArray[int(y // resStep)][int(x // resStep)] += xVector

            heatmapList[int(y // resStep)][x // resStep] += 1

        yVectorArray = np.true_divide(yVectorArray, heatmapList)
        xVectorArray = np.true_divide(xVectorArray, heatmapList)

        return yVectorArray, xVectorArray, heatmapList



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
        latticeList = Lattice(containerSize=100, particleNumber=500, distribution='random')
        latticeList.no_display_run(timeStep=300, numberOfRuns=5)
        latticeList.particle_counter()
        assert np.sum(latticeList.particle_counter()) == 500

    #================================================================================#

    def test_conserveMomentum(self):
        latticeList = Lattice(containerSize=50, particleNumber=5000, distribution='random')
        
        y0, x0, momentum0 = latticeList.find_momentum_vectors(resStep=10)
        del(y0)
        del(x0)

        latticeList.propagate()
        latticeList.collide()

        y1, x1, momentum1 = latticeList.find_momentum_vectors(resStep=10)
        del(y1)
        del(x1)

        assert momentum0 == momentum1

if __name__ == '__main__':

    latticeList = Lattice(containerSize=100, particleNumber=600, distribution='controlledRandom', yBounds=(2,20), xBounds=(2,20))

    #latticeList.plot_rT(testValue='particleNumber', minValue=50, maxValue=10000, pointNumber=8, n=6, style="logarithmic", tStep=40)
    #latticeList.no_display_run(timeStep=30, numberOfRuns=1)

    #latticeList.display_heatmap(timeStep=100, pauseBetweenSteps=.05)
    latticeList.display_advanced_data(latticeList.find_energy, title='energy flow', timeStep=5000, pauseBetweenSteps=0.01, arrayResolution=10)
    #
    # display can be either particleBoxes or momentumVectors
    #