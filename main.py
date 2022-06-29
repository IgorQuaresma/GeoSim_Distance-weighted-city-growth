from pcraster import *
from pcraster.framework import *
import os

print('BEEP BEEP BOOP loading . . . ')

# Rybski et al use gridsize 630 x 630 and gamma between 2.0 and 3.0
GRID = 100 #630
GAMMA = 2.5

class CityGrowthModel(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    setclone(GRID,GRID,1,0,0)
    setglobaloption("unitcell")

    # check whether output directories exist. If not, make them:
    for folder in ['dist', 'output']:
      if not os.path.exists(folder):
        os.mkdir(folder)

  def initial(self):
    # model attributes:
    self.gamma = GAMMA # parameter value
    self.totalCells = GRID**2
    
    # instantiate empty map (all cells unoccupied) and assign ID for every cell:
    self.uniqueMap = uniqueid(boolean(1))

    # set single central cell to occupied
    self.occupied = ifthenelse(self.uniqueMap == (GRID**2 / 2 - GRID/2), boolean(1), boolean(0))
    self.report(self.occupied, 'initial')

    # create distance maps for each cell
    # first, check if distance maps for this gridsize already exist:
    if len(os.listdir('dist/')) == self.totalCells:
      print('Distance maps already exist')
    else:
      # this can take ages so we track it:
      print(f'Model initialised\nCreating spreads for {self.totalCells} cells')
      ten_pct = int(self.totalCells / 10)
      one_pct = int(self.totalCells / 100)
      for cell in range(1, self.totalCells+1):
        self.report(spread(self.uniqueMap == cell, scalar(1), scalar(1)), f'dist/{cell}')
        if self.totalCells % ten_pct == 0:
          print(f'{self.totalCells % ten_pct}%')
        elif self.totalCells % one_pct == 0:
          print('+')
        


  def dynamic(self):
    '''
    already occupied cells don't change
    unoccupied cells become occupied when Rybski et al Eq(1) evaluates to 1:
    '''
    # need to consider all cells where k=/= j:

    # for each cell calculate Eq1 considering every other occupied cell
    # create prob map
    probMap = spatial(scalar(0))

    # k is occupied, j is being considered
    for cell_j in range(1, self.totalCells+1):
      is_cell_j = self.uniqueMap == cell_j
      is_occupied = pcrand(is_cell_j, self.occupied)
      # ignore cell if it's already occupied:
      if not getCellValueAtBooleanLocation(is_cell_j, self.occupied):
        distMap = readmap(f'dist/{cell_j}')

        sum1map = ifthenelse(self.occupied, distMap ** (-self.gamma), 0)
        sum2map = distMap ** (-self.gamma)

        qj_c = maptotal(sum1map) / maptotal(sum2map)

        prob = ifthenelse(is_cell_j, qj_c, 0)
        probMap = probMap + prob

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

