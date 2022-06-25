from pcraster import *
from pcraster.framework import *

print('BEEP BEEP BOOP loading . . . ')

# Rybski et al use gridsize 630 x 630
GRID = 630

class CityGrowthModel(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    setclone(GRID,GRID,1,0,0)
    #setclone('clone.map')

  def initial(self):
    # parameter values:
    self.gamma = 2.5
    # instantiate empty map (all cells unoccupied)
    self.initialMap = boolean(1)

    # set single central cell to occupied
    self.uniqueMap = uniqueid(self.initialMap)
    self.occupied = ifthenelse(self.uniqueMap == (GRID**2 / 2 - GRID/2), boolean(1), boolean(0))
    self.report(self.occupied, 'initial')

  def dynamic(self):
    '''
    already occupied cells don't change
    unoccupied cells become occupied when Rybski et al Eq(1) evaluates to 1:
    '''
    # need to consider all cells where k=/= j:
    # however, no need to exclude any cells as distance d will be 0
    j = self.occupied
    distances = spread(j, scalar(1), scalar(1))

    num = maptotal(scalar(self.occupied) * distances**self.gamma)
    denom = maptotal(distances**self.gamma)
    #new_occupied = self.occupied

    q = num / denom
    c = 1 / mapmaximum(q)
    qj = c * q
    self.report(qj, 'output/q')
    self.report(distances, 'output/distance')
    pass

nrOfTimeSteps=10#100
CGModel = CityGrowthModel()
dynamicModel = DynamicFramework(CGModel,nrOfTimeSteps)
dynamicModel.run()

print()

