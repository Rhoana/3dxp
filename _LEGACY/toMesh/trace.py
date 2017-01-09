import math
import scipy
import numpy as np
import mahotas as mh
from skimage import measure

class Trace:
    spline_resolution = 1/16.
    def __init__(self,spots):

        # Generate edge_image output and edges input 
        self.edge_image = np.zeros(spots.shape,dtype=np.bool)
        self.max_shape = np.array(self.edge_image.shape)-1
        self.edges = measure.find_contours(spots, 0)
        self.edges.sort(self.sortAll)

    def run(self, edgen):
        if len(edgen) <= 4:
            return []
        y,x = zip(*edgen)
        # get the cumulative distance along the contour
        dist = np.sqrt((np.diff(x))**2 + (np.diff(y))**2).cumsum()[-1]
        # build a spline representation of the contour
        spline, u = scipy.interpolate.splprep([x, y])
        res =  int(math.ceil(self.spline_resolution*dist))
        sampler = np.linspace(0, u[-1], res)

        # resample it at smaller distance intervals
        interp_x, interp_y = scipy.interpolate.splev(sampler, spline)
        iy,ix = [[int(math.floor(ii)) for ii in i] for i in [interp_x,interp_y]]
        interp = [np.clip(point,[0,0],self.max_shape) for point in zip(ix,iy)]

        mh.polygon.fill_polygon(interp,self.edge_image)

    def sortAll(self,a,b):
        xylists = [zip(*a),zip(*b)]
        da,db = [np.array([max(v)-min(v) for v in l]) for l in xylists]
        return 2*int((da-db < 0).all())-1

    def runAll(self):
        if len(self.edges):
            self.run(self.edges[0])
        return self.edge_image

def tracefill(volume):
    traced = Trace(volume)
    return traced.runAll()
