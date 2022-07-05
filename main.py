import os

from pcraster import *
from pcraster.framework import *


# Rybski et al use gridsize 630 x 630 and gamma between 2.0 and 3.0
GRID = 64 #630 don't use odd numbers
GAMMA = 2.5
GAMMA_STANDARD_DEVIATION = 0.5

# Displaying results in /data
# aguila --scenarios="{1,2,3,4,5,6,7,8,9,10,11,12}" --timesteps=[1,10,1] --multi=3x4 gamma p_oc n_oc oc
# aguila --quantiles=[0.025,0.975,0.005] --timesteps=[1,10,1] p_oc n_oc oc


class CityGrowthModel(DynamicModel, MonteCarloModel):
  def __init__(self):
    DynamicModel.__init__(self)
    MonteCarloModel.__init__(self)
    setclone(GRID,GRID,1,0,0)
    #setglobaloption("unitcell")

    # check whether the directory for the distance maps exist. If not, make them:
    if not os.path.exists('dist'):
      os.mkdir('dist')

  def premcloop(self):
    # model attributes:
    self.totalCells = GRID**2
    
    # instantiate empty map (all cells unoccupied) and assign ID for every cell:
    self.uniqueMap = uniqueid(boolean(1))
    self.report(self.uniqueMap, 'uniqueid')

    # create distance maps for each cell
    # first, check if distance maps for this gridsize already exist:
    existing_maps = len(os.listdir('dist/'))
    if existing_maps == self.totalCells:
      print('Distance maps already exist\nModel initialised')
    else:
      if existing_maps > self.totalCells:
        for map in os.listdir('dist/'):
          os.remove(f'dist/{map}')
      # this can take ages so we track it:
      print(f'Model initialised\nCreating spreads for {self.totalCells} cells')
      ten_pct = int(self.totalCells / 10)
      one_pct = int(self.totalCells / 100)
      for cell in range(1, self.totalCells+1):
        self.report(spread(self.uniqueMap == cell, scalar(1), scalar(1)), f'dist/{cell}')
        if cell % one_pct == 0:
          print(f'\t{round(cell / self.totalCells * 100, 2)}%', end='\r')
        #elif cell % one_pct == 0:
        #  print('+')
      print('\t100.00%')

    self.initial_map = ifthenelse(self.uniqueMap == (GRID**2 / 2 - GRID/2), boolean(1), boolean(0))
    self.report(self.initial_map, 'initial')

  def initial(self):
    self.gamma = mapnormal() * GAMMA_STANDARD_DEVIATION + GAMMA # parameter value
    self.report(self.gamma, 'gamma')

    # set single central cell to occupied
    self.occupied = self.initial_map

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
      # ignore cell if it's already occupied:
      if not getCellValueAtBooleanLocation(is_cell_j, self.occupied):
        distMap = readmap(f'dist/{cell_j}')

        sum1map = ifthenelse(self.occupied, distMap ** (-self.gamma), 0)
        sum2map = distMap ** (-self.gamma)

        qj_c = maptotal(sum1map) / maptotal(sum2map)

        prob = ifthenelse(is_cell_j, qj_c, 0)
        probMap = probMap + prob

    # no divide by zero, use max
    c = 1 / max(mapmaximum(probMap),1e-10)
    probMap = c * probMap

    self.report(probMap, 'p_oc')
    
    uniformMap = uniform(1)
    new_occupied = probMap >= uniformMap

    self.occupied = pcror(self.occupied, new_occupied)
    self.report(self.occupied, 'oc')

    #total number of occupied cells
    self.number_occupied = maptotal(scalar(self.occupied))
    self.report(self.number_occupied, 'n_oc')

  def postmcloop(self):
    samples = self.sampleNumbers()
    time_steps = self.timeSteps()
    percentiles = [0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.975]
    mcpercentiles(['p_oc', 'n_oc', 'oc'], percentiles, samples, time_steps)
    # mcaveragevariance(['p_oc', 'n_oc'], samples, time_steps)


if __name__ == "__main__":
  # Run in /data subdirectory
  file_dir = sys.path[0]
  working_dir = os.path.join(file_dir, 'data')
  if not os.path.exists(working_dir):
    os.makedirs(working_dir)
  os.chdir(working_dir)

  time_steps = 10
  sample_number = 12
  city_growth_model = CityGrowthModel()
  dynamic_model = DynamicFramework(city_growth_model, time_steps)
  monte_carlo_model = MonteCarloFramework(dynamic_model, sample_number)
  monte_carlo_model.run()
