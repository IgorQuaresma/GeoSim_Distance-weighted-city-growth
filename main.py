from pcraster import *
from pcraster.framework import *

print('BEEP BEEP BOOP loading . . . ')

# Rybski et al use gridsize 630 x 630
GRID = 100 #630

class CityGrowthModel(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    setclone(GRID,GRID,1,0,0)
    setglobaloption("unitcell")
    #setclone('clone.map')

  def initial(self):
    # parameter values:
    self.gamma = 2.5
    # instantiate empty map (all cells unoccupied)
    self.initialMap = boolean(1)

    # set single central cell to occupied
    self.uniqueMap = uniqueid(self.initialMap)
    self.totalCells = GRID**2
    #mapmaximum(self.uniqueMap)
    self.occupied = ifthenelse(self.uniqueMap == (GRID**2 / 2 - GRID/2), boolean(1), boolean(0))
    self.report(self.occupied, 'initial')

    # create distance maps for each cell
    for cell in range(1, self.totalCells+1):
      self.report(spread(self.uniqueMap == cell, scalar(1), scalar(1)), f'dist/{cell}')

  def dynamic(self):
    '''
    already occupied cells don't change
    unoccupied cells become occupied when Rybski et al Eq(1) evaluates to 1:
    '''
    # need to consider all cells where k=/= j:

    # for each cell calculate Eq1 considering every other occupied cell

    # assign ID to occupied cells?
    occCells = uniqueid(self.occupied)

    # create prob map
    probMap = spatial(scalar(0))
    self.report(probMap, 'output/probTest')

    # k is occupied
    for cell_j in range(1, self.totalCells+1):
      is_cell_j = self.uniqueMap == cell_j
      distMap = readmap(f'dist/{cell_j}')

      sum1map = ifthenelse(self.occupied, distMap ** (-self.gamma), 0)
      sum2map = distMap ** (-self.gamma)

      qj_c = maptotal(sum1map) / maptotal(sum2map)

      prob = ifthenelse(is_cell_j, qj_c, 0)
      probMap = probMap + prob

      #for cell in range(1, self.totalCells+1):
      #  is_cell_k = self.uniqueMap == cell
      #  sum1, sum2 = 0, 0
      #  for c in distMap:
      #    if c == self.occupied:
      #      sum1 += distMap(self.uniqueMap == cell_j) ** (-self.gamma)
#
      #    sum2 += distMap(self.uniqueMap == cell_j) ** (-self.gamma)
    #
#
      #qj_c = sum1 / sum2
      #probMap[self.uniqueMap == cell_j] = qj_c

    

    c = 1 / mapmaximum(probMap)
    probMap = c * probMap

    self.report(probMap, 'output/probMap')
    
    uniformMap = uniform(1)
    new_occupied = probMap >= uniformMap

    self.occupied = pcror(self.occupied, new_occupied)
    self.report(self.occupied, 'output/occ')

nrOfTimeSteps=10#100
CGModel = CityGrowthModel()
dynamicModel = DynamicFramework(CGModel,nrOfTimeSteps)
dynamicModel.run()

print()

