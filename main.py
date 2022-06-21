from pcraster import *
from pcraster.framework import *

print('BEEP BEEP BOOP loading . . . ')

class CityGrowthModel(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    # Rybski et al use gridsize 630 x 630
    setclone('clone.map')

  def initial(self):
    # instantiate empty map (all cells unoccupied)
    self.initialMap = boolean(1)
    # set single central cell to occupied
    self.initialMap = ifthenelse(pcrand(ycoordinate(self.initialMap) == 200, xcoordinate(self.initialMap) == 200), scalar(1), scalar(0))
    self.report(self.initialMap, 'initial')

  def dynamic(self):
    pass

nrOfTimeSteps=100
CGModel = CityGrowthModel()
dynamicModel = DynamicFramework(CGModel,nrOfTimeSteps)
dynamicModel.run()

print()




