import glob
import h5py
import mahotas as mh
import math
import numpy as np
import os
from stl import mesh
import scipy
from skimage import measure
import sys
from xml.etree import ElementTree


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
  def create_stl(vol, filename, X=0, Y=0, tilewidth=1024):

    verts, faces = measure.marching_cubes(vol, 0, gradient_direction='ascent')
    applied_verts = verts[faces]
    vert_count = applied_verts.shape[0]

    mesh_data = np.zeros(vert_count, dtype=mesh.Mesh.dtype)

    # Z, Y and X offsets
    offset = np.array([0, Y*tilewidth, X*tilewidth])

    for i, v in enumerate(applied_verts):
        mesh_data[i][1] = v + offset

    m = mesh.Mesh(mesh_data)
    # with open(filename, 'w') as f:
    m.save(filename)

    return m    


  @staticmethod
  def run(datafile, X, Y, outdir, tilewidth=1024):

    # create output folder
    if not os.path.exists(outdir):
      os.makedirs(outdir)

    with h5py.File(datafile, 'r') as f:
      vol = f[f.keys()[0]][:,Y*tilewidth:Y*tilewidth+tilewidth,X*tilewidth:X*tilewidth+tilewidth]

    # grab all IDs
    all_ids = np.unique(vol)

    print 'Loaded data..'

    for id in all_ids:

      # skip 0
      outfile = str(id) + '_' + str(X) + '_' + str(Y) + '.stl'
      if id == 0 or os.path.exists(os.path.join(outdir, outfile)):
        continue

      try:

        # 1. thresholding
        thresholded = ThreeD.threshold(vol, id)
        for z in range(thresholded.shape[0]):
            thresholded[z] = mh.close_holes(thresholded[z])

        thresholded = np.repeat(thresholded, 10, axis=0)

        # 2. smoothing along Y
        thresholded_swapped = np.swapaxes(thresholded, 0, 1)
        thresholded_padded = np.pad(thresholded_swapped, 2, mode='constant')
        smoothed = ThreeD.smoothen(thresholded_padded)

        # 3. marching cubes
        smoothed = np.swapaxes(smoothed, 0, 1) # Z,Y,X
        outfile = str(id) + '_' + str(X) + '_' + str(Y) + '.stl'
        ThreeD.create_stl(smoothed, os.path.join(outdir, outfile), X=X, Y=Y, tilewidth=tilewidth)

        print 'Stored', outfile

      except:

        print 'Skipped', id
        continue

    print 'All done.'

  @staticmethod
  def create_website(stldir, outputfolder, ids=None):

    stl_files = None

    if ids == None:
      # grab all ids
      stl_files = sorted([os.path.basename(v) for v in glob.glob(os.path.join(stldir, '*.stl'))])

    else:

      # use the specified list
      stl_files = []
      stl_files = [os.path.basename(v) for id in ids for v in glob.glob(os.path.join(stldir, str(id)+'_*.stl'))]


    html_header = '''
<html>
<head>
  <script type='text/javascript' src='https://www.x3dom.org/x3dom/release/x3dom.js'></script>
  <script>

  window.onload = function() {

    document.getElementById('r').runtime.showAll();

  };

  </script>
</head>
<body style='padding:0px; margin:0px; overflow:hidden; background-color: #000'>
  <x3d id='r' width='100%' height='100%'>



    <scene>
      <viewpoint position='0 0 10' ></viewpoint>
    '''

    html_content = ''

    html_footer = '''
    </scene>
  </x3d>
</body>
</html>
    '''

    
    for f in stl_files:

      ID = int(f.split('_')[0])

      stl_file = os.path.join(stldir, f)
      x3d_file = os.path.join(outputfolder, f.replace('.stl', '.x3d'))
      mipmaps = f.replace('.stl', '_')
      html_file = os.path.join(outputfolder, f.replace('.stl', '.html'))

      x3d_cmd = 'aopt -i '+ stl_file +' -x '+ x3d_file
      r = os.system(x3d_cmd)
      mipmap_cmd = 'aopt -i '+ x3d_file + ' -K ' + mipmaps + ':pb -N '+ html_file
      r2 = os.system('cd ' + outputfolder + ' && ' + mipmap_cmd)

      if r == 0 and r2 == 0:
        print 'Generated X3D for', f
      else:
        print 'Error for', f
        continue

      # grab popGeometry HTML
      e = ElementTree.parse(os.path.join(outputfolder, f.replace('.stl', '.html'))).getroot()
      geometrynode = e.find('.//popGeometry')
      geometrytext = ElementTree.tostring(geometrynode)
      geometrytext = geometrytext.replace('primType="&quot;TRIANGLES&quot;"', "primType='\"TRIANGLES\"'")
      geometrytext = geometrytext.replace(' />', '></popGeometryLevel>')

      # create html
      color = np.mod(107*ID,700), np.mod(509*ID,700), np.mod(200*ID,700)

      mesh_html = '''
      <shape>
        <appearance>
          <material diffuseColor='$COLOR'></material>
        </appearance>
      '''.replace('$COLOR', str(color[0]/255.) + ' ' + str(color[1]/255.) + ' ' + str(color[2]/255.))

      mesh_html += '\n          ' + geometrytext
      mesh_html += '\n      ' + '</shape>'

      html_content += mesh_html + '\n'

      print 'Generated HTML for', f

    # return html_content

    with open(os.path.join(outputfolder, 'index.html'), 'w') as f:
      f.write(html_header + html_content + html_footer)

    print 'Stored index.html.'      



#
#
# EXAMPLE USAGE FROM PYTHON (FOR THE TOP 750x400x400 VOXELS)
#
# from threed import ThreeD
#
# DATA = '/home/d/data/toufiq/segmentation.h5'
# STLFOLDER = '/tmp/threeDNEW/'
# X3DFOLDER = '/tmp/x3dNEW/'
#
# ThreeD.run(DATA, 0, 0, STLFOLDER, tilewidth=200)
# ThreeD.run(DATA, 0, 1, STLFOLDER, tilewidth=200)
# ThreeD.run(DATA, 1, 0, STLFOLDER, tilewidth=200)
# ThreeD.run(DATA, 1, 1, STLFOLDER, tilewidth=200)
#
# ThreeD.create_website(STLFOLDER, X3DFOLDER, None) # <-- None means all IDs
#

#
# Now we will run the ThreeD.run with a tilewidth=1024 on the cluster and
# then ThreeD.create_website on Viper after all STLs were created.
#

if __name__ == "__main__":

  # we need the following parameters
  datapath = sys.argv[1]
  y = sys.argv[2]
  x = sys.argv[3]
  outputpath = sys.argv[4]

  if not os.path.exists(outputpath):
    os.makedirs(outputpath)

  # now run donkey run
  ThreeD.run(datapath, int(y), int(x), outputpath)




































