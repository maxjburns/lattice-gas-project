# spot for modifiable variables:

#let's stick to "square"s right now, enter the width of the top layer:

containerSize = 10


particleNumber=30



import math
import random

#----------------------------------------------------------------------------#

def startup():
    #let's stick to "square"s right now, enter the width of the top layer:
    
    
    #i like having a quick reference to whether the originial size is odd or even
    containerEven = containerSize%2==0
    
    #initializing/reseting all the lists
    global latticeList
    latticeList = []
    shorterLineMiddles = []
    shorterLineLEdges = []
    shorterLineREdges = []
    longerLineMiddles = []
    longerLineLEdges = []
    longerLineREdges = []
    
    
    #Finds number of cells based on containerSize, and tells user (for debugging).
    global cellNumber
    cellNumber=(containerSize*containerSize)-int(containerSize/2)
    print("Total Number of cells in Matrix: " + str(cellNumber) + "\n")
    
    
    # the following for loop modfiies six lists, in order to categorise
    # the index values into what part of the lattice they are
    
    for i in range(0,int(math.ceil(float(containerSize-2)/2))):
        
        # basePoint is the left edge of the shorter part of the lattice,
        # so i use it as a reference point. as the index value increases,
        # basePoint is updated. the abstraction makes it easier for me to read it.
        basePoint= i*(2*containerSize-1) + containerSize
        
        
        # this for loop fills the lists that correspond to the shorter
        # lines of the lattice
        for x in range(0,containerSize-3):
            
            if(x==0):
                shorterLineLEdges.append(basePoint)
            
            shorterLineMiddles.append(basePoint+x+1)
            
            if(x==containerSize-4):
                shorterLineREdges.append(basePoint + (containerSize - 2))
             
          
            
        # this if loop is here because if there are an even number of rows,
        # then the bottom row is short, which means there is one fewer iteration
        # needed of the longer line list appending.
        if(containerEven or i!=int(math.ceil(float(containerSize-2)/2))-1):      
            
            # this for loop fills the lists that correspond to the longer
            # lines of the lattice
            for x in range(0,containerSize-2):
                
                if(x==0):
                    longerLineLEdges.append(basePoint + (containerSize - 1))    
                
                longerLineMiddles.append(basePoint + containerSize + x)
               
                if(x==containerSize-3):
                    longerLineREdges.append(basePoint + 2*containerSize-2) 
        
            
    #these print statements are for debugging, to make sure that everything is
    #categorized correctly
    print("\nshorterLineMiddles: " + ' '.join(map(str, shorterLineMiddles)))
    print("\nshorterLineLEdges: " + ' '.join(map(str, shorterLineLEdges)))
    print("\nshorterLineREdges: " + ' '.join(map(str, shorterLineREdges)))
    
    print("\nlongerLineMiddles: " + ' '.join(map(str, longerLineMiddles)))
    print("\nlongerLineLEdges: " + ' '.join(map(str, longerLineLEdges)))
    print("\nlongerLineREdges: " + ' '.join(map(str, longerLineREdges)))
    
    
    
    # this fills the initial lattice array
    # 0 - corresponds to a path without a particle
    # 1 - corresponds to a path with a particle
    # 2 - corresponds to a wall
    for i in range(0,(cellNumber)):
       
        # these define top row
        if(i==0):
           latticeList.append("022220") #topLeft
        
        elif(i<containerSize-1):
            latticeList.append("022000") #topMid
        
        elif(i==containerSize-1):
            latticeList.append("222002") #topRight
            
        # these define the shorter middle rows    
        elif(i in shorterLineMiddles):
            latticeList.append("000000") #shorterMid
        
        elif(i in shorterLineLEdges):
            latticeList.append("000200") #shorterLeft
        
        elif(i in shorterLineREdges):
            latticeList.append("200000") #shorterRight
            
        # these define the longer middle rows     
        elif(i in longerLineMiddles):
            latticeList.append("000000") #longerMid
        
        elif(i in longerLineLEdges):
            latticeList.append("002220") #longerLeft
        
        elif(i in longerLineREdges):
            latticeList.append("220002") #longerRight
            
        # this block is for the bottom row, the if statement is there because
        # the bottom row can be either long or short, which changes which areas
        # are walls or paths.
        else:
            
            if(containerEven==True): 
                
                if(i==cellNumber-1):
                    latticeList.append("200022") #bottomRight
                
                elif(i>cellNumber-containerSize + 1):
                    latticeList.append("000022") #bottomMid
                
                elif(i==cellNumber-containerSize + 1):
                    latticeList.append("000222") #bottomLeft
            
            
            elif(containerEven==False):
               
                if(i==cellNumber-1):
                    latticeList.append("220022") #bottomRight
                
                elif(i>cellNumber-containerSize):
                    latticeList.append("000022") #bottomMid
                
                elif(i==cellNumber-containerSize):
                    latticeList.append("002222") #bottomLeft
            
            # I included this just in case something goes wrong   
            else:
                latticeList.append("UND")
        
        
        
        
    # this displays the lattice in number form   
    print("\nlatticeList: "+ ' '.join(map(str, latticeList)))
    


#----------------------------------------------------------------------------#

# places particles randomly, if a particle is in a position at first, it is
# assumed to be moving away from the center of the parent node.
def particleDistribution():
    
    # places a particle each iteration
    for i in range(0,particleNumber):
        
        tempList = [] # used to store positions of zeroes (empty spots) around a node
        fullChecker = True # used to check if node is full
        
        # loop runs until it finds an unfilled node
        while fullChecker:
            # this block randomly picks a site to edit, and then sets entryAtSite 
            # to be equal to the string there.
            site=random.randint(0,cellNumber-1) 
            entryAtSite=latticeList[site]
            
            if entryAtSite.find('0') != -1:
                fullChecker = False
            else:
                print("son of a gun, node full")
        # print statements are for easy debugging
        print("\nOriginal: " + entryAtSite + " Pos: " + str(site))
        
        # checks each number in the target string, and saves the positions of
        # any zeroes to tempList to be referenced later
        for x in range(0,6):
            
            if entryAtSite.find('0',x,x+1)!=-1:
                tempList.append(x)
        
        chosenPosition = tempList[random.randint(0,len(tempList)-1)] # picks a random 0 to replace
        
        entryAtSite = entryAtSite[0:chosenPosition] + '1' + entryAtSite[chosenPosition+1:len(entryAtSite)] #cuts up the string to remove the target zero and add a one.
        latticeList[site]=entryAtSite # replaces the old entry with the updated one.
        
        
        print("Updated: " + entryAtSite)

#----------------------------------------------------------------------------# 
    
    
    
startup()
particleDistribution()
print("\n\nnew latticeList: "+ ' '.join(map(str, latticeList)))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#----------------------------------------------------------------------------#    
    
    
