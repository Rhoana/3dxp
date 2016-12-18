import mahotas as mh
import math
from stl import mesh
import numpy as np
import scipy
from skimage import measure

class ThreeD:

  @staticmethod
  def threshold(arr, val):

    out = np.zeros(arr.shape, dtype=np.bool)
    out[arr == val] = 1

    return out

  @staticmethod
  def smoothen(vol, spline_resolution=1/16.):

    out = np.zeros(vol.shape, dtype=np.bool)

    for z in range(vol.shape[0]):

      slice = vol[z]
      out_slice = np.zeros(slice.shape, dtype=np.bool)

      contours = measure.find_contours(slice, 0)

      if len(contours) < 1:
        continue

      y,x = zip(*contours[0])
      # get the cumulative distance along the contour
      dist = np.sqrt((np.diff(x))**2 + (np.diff(y))**2).cumsum()[-1]
      # build a spline representation of the contour
      spline, u = scipy.interpolate.splprep([x, y])
      res =  int(math.ceil(spline_resolution*dist))
      sampler = np.linspace(0, u[-1], res)

      # resample it at smaller distance intervals
      interp_x, interp_y = scipy.interpolate.splev(sampler, spline)
      iy,ix = [[int(math.floor(ii)) for ii in i] for i in [interp_x,interp_y]]

      interp = [np.clip(point,[0,0], np.array(slice.shape)-1) for point in zip(ix,iy)]

      mh.polygon.fill_polygon(interp, out_slice)

      out[z] = out_slice

    return out

  @staticmethod
  def create_mesh(vol, filename):

    verts, faces = measure.marching_cubes(vol, 0, gradient_direction='ascent')
    applied_verts = verts[faces]
    vert_count = applied_verts.shape[0]

    mesh_data = np.zeros(vert_count, dtype=mesh.Mesh.dtype)

    for i, v in enumerate(applied_verts):
        mesh_data[i][1] = v# + bboff

    m = mesh.Mesh(mesh_data)
    with open(filename, 'w') as f:
        m.save(filename, f)
    return m    
