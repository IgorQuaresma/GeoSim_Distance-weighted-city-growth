from pcraster import *
from pcraster.framework import *

print('BEEP BEEP BOOP loading . . . ')

GRID = 630

class CityGrowthModel(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    # Rybski et al use gridsize 630 x 630
    setclone(GRID,GRID,1,0,0)
    #setclone('clone.map')

  def initial(self):
    # parameter values:
    self.gamma = 2.5
    # instantiate empty map (all cells unoccupied)
    self.initialMap = boolean(1)

    # set single central cell to occupied
    self.uniqueMap = uniqueid(self.initialMap)
    self.report(self.uniqueMap, 'unique')
    self.initialMap = ifthenelse(self.uniqueMap == (GRID**2 - GRID/2), scalar(1), scalar(0))

    self.report(self.initialMap, 'initial')

  def dynamic(self):
    pass

nrOfTimeSteps=100
CGModel = CityGrowthModel()
dynamicModel = DynamicFramework(CGModel,nrOfTimeSteps)
dynamicModel.run()

print()




#self.initialMap = ifthenelse(pcrand(pcrgt(ycoordinate(self.initialMap), 5), pcrgt(xcoordinate(self.initialMap), 5)), scalar(1), scalar(0))
#self.initialMap = ifthenelse(pcrand(pcrand(
#  ycoordinate(self.initialMap) >= 5, 
#  ycoordinate(self.initialMap) <= 6), pcrand( 
#  xcoordinate(self.initialMap) >= 5,
#  xcoordinate(self.initialMap) <= 6), 
#  ), scalar(1), scalar(0))