#!/usr/bin/python
# -*- coding: utf-8 -*-
# spot for modifiable variables:

# let's stick to "square"s right now, enter the width of the top layer:

containerSize = 100
particleNumber = 10000

import cProfile

import math
import matplotlib.pyplot as plt
import numpy as np
import random
import time

# ----------------------------------------------------------------------------#

class Lattice:
    """Class used to work with the lattice."""
    #================================================================================#
    
    def __init__(self, containerSize=100, particleNumber=5000):
        
        self.lattice = np.zeros((containerSize, containerSize, 6), np.int8)
        self.containerSize = containerSize
        self.particleNumber = particleNumber

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

        for i in range(0, containerSize):
            for x in range(0, containerSize):
                print(self.request_string(i,x), end = ' ')
            print('\n')

    #================================================================================#
    
    def cell_number(self):

        # Finds number of cells based on containerSize, and tells user (for debugging).

        cellNumber = self.containerSize * self.containerSize - int(self.containerSize / 2)

        return cellNumber   

    #================================================================================#

    def random_particles(self):
        """places particles randomly, if a particle is in a position at first, it is
        assumed to be moving away from the center of the parent node."""

        assert self.particleNumber <= self.cell_number() * 6

        particlesRemaining = particleNumber
        
        # the following while loop attempts to place a particle each iteration, if the spot
        # picked is full, it finds a new random spot on the next iteration. It consumes
        # particles as it goes, until it runs out. If a spot is full, nothing is consumed.

        while particlesRemaining != 0:
            
            # these randomly select a row and column
            randomColumn = random.randint(1, containerSize-2)
            randomRow = random.randint(1, containerSize-2)
            openSpots = self.spots_remaining(randomColumn, randomRow)

            
            # this if statement ensures that the only time a particle is added is when there
            # are spots remaining.
            if len(openSpots) > 0:
                positionChosen = random.choice(openSpots)
                self.lattice[randomRow][randomColumn][positionChosen] = 1

                particlesRemaining -= 1



    #================================================================================#

    def particle_counter(self):
        particleCountList = np.zeros((containerSize,containerSize), np.int8)

        for i in range(0,containerSize):
            for x in range(0, containerSize):
                particleCountList[i][x] = np.count_nonzero(self.lattice[i][x] == 1)


        self.particleCountList = particleCountList


        
    #================================================================================#

    def display_heatmap(self):
        """this displays the "container" and the particle density inside of it"""
        countVar = self.containerSize
        fig, ax = plt.subplots()
        

        ax.set_title("Particle Distribution")
        fig.tight_layout()

        while countVar != 0:
            if(countVar == 20):
                start = time.time()
            self.particle_counter()
            
            im = ax.imshow(self.particleCountList, cmap='Blues')
            self.propagate()
            self.collide()
            
            plt.pause(0.05)
            countVar -=1
            if(countVar == 1):
                end = time.time()
                print('total:')
                print(end - start)


        plt.show()

    #================================================================================#

    def propagate(self):
        
        newBoard = np.zeros((containerSize, containerSize, 6), np.int8)


        vectors = [(1, 0, 3), (0, -1, 3), (-1, -1, 3), (-1, 0, -3), (-1, 1, -3), (0, 1, -3)]
        
        
        for y in range(0, containerSize):
            for x in range(0, containerSize):
                # that if statement actually helps!
                if self.particleCountList[x][y] > 0: # just for efficiency, many spaces have no particles, so no need to check all their spaces
                    for z in range(0, 6):
                        xChange, yChange, zChange = vectors[z]
                        if self.lattice[x][y][z] == 1 and x < containerSize - 1 and y < containerSize - 1:
                            
                            newBoard[x + xChange][y + yChange][z + zChange] = 1
                        
        self.lattice = newBoard
        

    #================================================================================#

    def collide(self):

        newBoard = np.zeros((containerSize, containerSize, 6), np.int8)
        vectors = [3, 3, 3, -3, -3, -3]
        for y in range(0, containerSize):
            for x in range(0, containerSize):
                for z in range(0, 6):
                    zChange = vectors[z]
                    
                    if self.lattice[x][y][z] == 1 and x < containerSize - 1 and y < containerSize - 1:
                        newBoard[x][y][z + zChange] = 1
        
        self.lattice = newBoard
        
    #================================================================================#




latticeList = Lattice(100, 6000)
latticeList.random_particles()
latticeList.display_heatmap()

