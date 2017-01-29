import os, sys
from getmesh import *

if __name__ == "__main__":

  # we need the following parameters
  datapath = sys.argv[1]
  z = sys.argv[2]
  y = sys.argv[3]
  x = sys.argv[4]
  outputpath = sys.argv[5]
  tilewidth = sys.argv[6]
  id_list = sys.argv[7]

  if not os.path.exists(outputpath):
    os.makedirs(outputpath)

  # now run donkey run
  ThreeD.run(datapath, int(z), int(y), int(x), outputpath, int(tilewidth), id_list.split(' '))

