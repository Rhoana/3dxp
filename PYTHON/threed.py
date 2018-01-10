import os
import sys
import time
import json
import glob
import h5py
import random
import numpy as np
from stl import mesh
from skimage import measure
from xml.etree import ElementTree


class ThreeD:

    pattern = '<!-- {MESHES} -->'
    html_header = '''
<html>
<head>
  <script type='text/javascript' src='https://www.x3dom.org/x3dom/release/x3dom.js'></script>
  <script type='text/javascript' src='javascript/gl-matrix-min.js'></script>
  <script type='text/javascript' src='javascript/main.js'></script>
  <link rel="stylesheet" href="css/main.css" type="text/css"/>
</head>
<body onload="startup({DIMZ})">
  <x3d id='r' width='100%' height='100%'>

    <scene id='scene'>
      <viewpoint id="view" bind="true" position="-3907.452893023825 3412.645607228069 1698.6871532265088" orientation="-0.38641924151512014 0.5710252704568496 0.7242998759399042 4.044510548789248" description="camera"></viewpoint>

            <transform bboxCenter='0 0 0' scale='{R_SCALE}'>
            <transform bboxCenter='0,0,0' rotation='0 1 0 -1.5708'>
            <transform id='move0' bboxCenter='0,0,0' translation='{HALFDIMX} {HALFDIMY} -{DIMZ}'>
            <transform bboxCenter='0,0,0' scale='1 -1 1'>
            <shape>
              <appearance>
                  <Texture>
                    <img style="display: none" src='images/{LASTIMAGE}.jpg'></img>
                  </Texture>
              </appearance>
              <plane primType='TRIANGLES' size='{DIMX} {DIMY}' solid='false'></plane>
            </shape>
            </transform>
            </transform>
            </transform>
            </transform>

            <transform bboxCenter='0 0 0' scale='{R_SCALE}'>
            <transform bboxCenter='0,0,0' rotation='0 1 0 -1.5708'>
            <transform id='move1' bboxCenter='0,0,0' translation='{HALFDIMX} {HALFDIMY} -{DIMZ}'>
            <transform bboxCenter='0,0,0' scale='1 -1 1'>
            <shape>
              <appearance>
                  <Texture>
                    <img style="display: none" src='images/{LASTIMAGE}.jpg'></img>
                  </Texture>
              </appearance>
              <plane primType='TRIANGLES' size='{DIMX} {DIMY}' solid='false'></plane>
            </shape>
            </transform>
            </transform>
            </transform>
            </transform>


        <!-- SHOULD BE IN X -->
        <transform bboxCenter='0 0 0' scale='{R_SCALE}'>
        <transform id='clipScopeX'>
        <transform bboxCenter='0,0,0' rotation='0 0 1 -1.5708'>
        <transform id='move_slice' bboxCenter='0,0,0' translation='-{HALFDIMY} {HALFDIMZ} 0'>
        <transform bboxCenter='0,0,0' scale='-1 -1 1'>
            <shape>
              <appearance>
                <texture>
                   <img style="display:none" src="0_in_x.png"></img>
                </texture>
              </appearance>
              <plane primType='TRIANGLES' size='{DIMY} {DIMZ}' solid='false'></plane>
            </shape>
        </transform>
        </transform>
        </transform>
        </transform>
        </transform>


        <!-- SHOULD BE IN Y -->
        <transform bboxCenter='0 0 0' scale='{R_SCALE}'>
        <transform id='clipScopeY'>
        <transform bboxCenter='0,0,0' rotation='0 0 1 -1.5708'>
        <transform bboxCenter='0,0,0' rotation='0 1 0 -1.5708'>
        <transform id='move_slice' bboxCenter='0,0,0' translation='{HALFDIMX} {HALFDIMZ} 0'>
        <transform bboxCenter='0,0,0' scale='1 -1 1'>
            <shape>
              <appearance>
                <texture>
                   <img style="display:none" src="0_in_y.png"></img>
                </texture>
              </appearance>
              <plane primType='TRIANGLES' size='{DIMX} {DIMZ}' solid='false'></plane>
            </shape>
        </transform>
        </transform>
        </transform>
        </transform>
        </transform>
        </transform>

    <group>
    <transform bboxCenter='0 0 0' scale='{I_SCALE}'>
    '''
    
    html_footer = '''
    </transform>
    </group>
    </scene>
  </x3d>
</body>
</html>
    '''

    @staticmethod
    def threshold(arr, val):

        out = np.zeros(arr.shape, dtype=np.bool)
        out[arr == val] = 1

        return out

    @staticmethod
    def create_stl(vol, filename, blockshape, Z=0, Y=0, X=0):

        verts, faces = measure.marching_cubes(vol, 0, gradient_direction='ascent')[:2]
        applied_verts = verts[faces]
        vert_count = applied_verts.shape[0]

        mesh_data = np.zeros(vert_count, dtype=mesh.Mesh.dtype)

        # Z, Y and X offsets
        offset = [Z, Y, X] * blockshape

        for i, v in enumerate(applied_verts):
            mesh_data[i][1] = v + offset

        m = mesh.Mesh(mesh_data)
        m.save(filename)

    @staticmethod
    def create_pre(vol, filename, blockshape, Z=0, Y=0, X=0):

        verts, faces = measure.marching_cubes(vol, 0, gradient_direction='ascent')[:2]
        all_verts = verts[faces].reshape(-1, 3) + [Z, Y, X] * blockshape
        n_verts = len(all_verts)

        mesh_data = np.float32([n_verts] + all_verts.flatten())

        with open(filename, 'w') as wf:
            wf.write(mesh_data.tobytes())
 
    @staticmethod
    def run(datafile, Z, Y, X, outdir, blockshape=200, idlist=[], order='zyx', is_pre=False):

        # Validate axis order
        if set('zyx') != set(order):
            order = 'zyx'
        # Get axis order as numbers
        axis_ids = dict(zip('zyx', [0,1,2]))
        axis_order = list(map(axis_ids.get, order))

        # Get blockshape for all dimensions
        if not hasattr(blockshape, '__len__'):
            blockshape = [blockshape]*3
        blockshape = np.uint32(blockshape)

        # create output folder
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        with h5py.File(datafile, 'r') as f:
            zo,ze = np.array([Z,Z+1])*blockshape[0]
            yo,ye = np.array([Y,Y+1])*blockshape[1]
            xo,xe = np.array([X,X+1])*blockshape[2]
            vol = f[f.keys()[0]][zo:ze, yo:ye, xo:xe]

        # grab all IDs
        # TODO: This returns `np.float64` for `np.uint32`
        # This causes big problems and should be fixed.
        all_ids = np.unique(vol)
        if len(idlist) == 0:
            idlist = all_ids

        # Check for ids not in data 
        missing_ids = np.setdiff1d(idlist, all_ids)
        if len(missing_ids):
            print 'Cannot find {}'.format(missing_ids)

        # Check for ids in data
        using_ids = np.intersect1d(idlist, all_ids)
        print 'Using Loaded IDs: {}'.format(using_ids)

        MESH_EXT = 'stl'
        if is_pre:
            MESH_EXT = 'pre'

        for id in using_ids:

            # Get the output name and folder
            outfolder = os.path.join(outdir, str(id))
            name_fmt = '{{}}_{{}}_{{}}'.format(*axis_order)
            name_fmt = '{}_{}'.format(order, name_fmt)
            # Simple name for old assumptions
            if axis_order == [0,1,2]:
                name_fmt = '{0}_{1}_{2}'
            outname = name_fmt.format(Z,Y,X)
            outname += '.{}'.format(MESH_EXT)
            # Make outfolder if doesn't yet exist
            if not os.path.exists(outfolder):
                os.makedirs(outfolder)

            # Combine to get the full output path
            outpath = os.path.join(outfolder, outname)
            # Continue if output path doesn't exist
            if id == 0 or os.path.exists(outpath):
                continue

            try:

                # 1. thresholding
                thresholded = ThreeD.threshold(vol, id)

                # 2. padding and swapping along Y
                thresholded_swapped = np.swapaxes(thresholded, 0, 1)
                thresh_padded = np.pad(thresholded_swapped, 2, mode='constant')

                # 3. marching cubes
                thresh_padded = np.swapaxes(thresh_padded, 0, 1) # Z,Y,X
                final_padded = np.transpose(thresh_padded, axis_order)
                # Create mesh with given axis order
                if is_pre:
                    ThreeD.create_pre(final_padded, outpath, blockshape, Z=Z, Y=Y, X=X)
                else:
                    ThreeD.create_stl(final_padded, outpath, blockshape, Z=Z, Y=Y, X=X)

                print 'Stored {}/{}'.format(id, outname)

            except:

                print 'Skipped', id
                continue

    @staticmethod
    def start_website(stldir, ids=[]):

        if not len(ids):
            # grab all ids
            return [v for v in glob.glob(os.path.join(stldir, '*', '*.stl'))]
        else:
            # use the specified list
            return [v for id in ids for v in glob.glob(os.path.join(stldir, str(id), '*.stl'))]

    @staticmethod
    def create_website(stldir, outputfolder, ids=[], dimz=1024, dimy=1024, dimx=1024,**keywords):

        # Get all stl_files
        stl_files = ThreeD.start_website(stldir, ids)

        print stldir
        print stl_files

        html_content = {}
        html_new_files = {}

        html_string = lambda s: ElementTree.tostring(s, method='html')

        # create output folder
        if not os.path.exists(outputfolder):
            os.makedirs(outputfolder)

        # Make a time folder
        time_dir = os.path.join(outputfolder, 'time')
        if not os.path.exists(time_dir):
            os.makedirs(time_dir)

        # Make empty time object
        time_out = {
            "N": 0,
            "TOTAL": 0,
            "LIST": [], 
            "ID_LIST": [],
        }

        for stl_file in stl_files:

            # Start timing
            t0 = time.time()

            # Convert to old format
            path, basename = os.path.split(stl_file) 
            f = '{}_{}'.format(os.path.basename(path), basename)         

            STRID = f.split('_')[0]
            mipfile = '_'.join(f.split('_')[1:])
            mipmaps = mipfile.replace('.stl', '_')
            mipdir = os.path.join(outputfolder,STRID)
            ID = int(STRID)

            x3d_file = os.path.join(mipdir, f.replace('.stl', '.x3d'))
            html_tmp_file = os.path.join(outputfolder, f.replace('.stl', '.html'))
            html_id_file = os.path.join(outputfolder, STRID+'.html')

            if not os.path.exists(mipdir):
                os.makedirs(mipdir)

            id_saved = os.path.exists(html_id_file)
            id_x3d_done = os.path.exists(x3d_file)
            id_read = STRID in html_content

            if id_saved:
                if not id_read:
                    shapes = ElementTree.parse(html_id_file).getroot().findall('.//group/transform/*')
                    grouptext = [html_string(shape) for shape in shapes]
                    html_content[STRID] = ''.join(grouptext)
                print 'X3D exists for', f
                continue

            result = [0,0]
            format_cmd = 'aopt -i '+ stl_file +' -x '+ x3d_file
            mipmap_cmd = 'aopt -i '+ x3d_file + ' -K ' + STRID+'/'+mipmaps + ':pb -N '+ html_tmp_file
            if not id_x3d_done:
                result[0] = os.system(format_cmd)
            result[1] = os.system('cd ' + outputfolder + ' && ' + mipmap_cmd)

            if not id_read:
                html_content[STRID] = ''
            if not any(result):
                print 'Generated HTML for', mipmaps
            else:
                print 'Error making', mipmaps
                print format_cmd
                print mipmap_cmd
                continue

            # grab popGeometry HTML
            e = ElementTree.parse(html_tmp_file).getroot()
            geometrynode = e.find('.//popGeometry')
            geometrytext = html_string(geometrynode)

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

            html_content[STRID] += mesh_html + '\n'
            html_new_files[STRID] = html_id_file

            print 'Generated HTML ', html_tmp_file
            os.remove(html_tmp_file)

            # Stop timing
            t1 = time.time()
            # Store time info
            one_time = t1 - t0

            # Write to output
            time_out["N"] += 1
            time_out["TOTAL"] += one_time
            time_out["LIST"].append(one_time)
            time_out["ID_LIST"].append(ID)

        # Make a time file with random name
        t_count = len(os.listdir(time_dir))
        t_noise = random.randint(0, 10**8 - 1)
        time_name = '{}_{:08d}.json'.format(t_count, t_noise)
        time_file = os.path.join(time_dir, time_name)

        # Write all time info to a file
        with open(time_file, 'w') as tf:
            print "Writing times to {}".format(time_file)
            json.dump(time_out, tf)

        string_pad = 5
        html_header = ThreeD.html_header
        html_header = html_header.replace('{DIMX}', str(dimx))
        html_header = html_header.replace('{DIMY}', str(dimy))
        html_header = html_header.replace('{DIMZ}', str(dimz))
        html_header = html_header.replace('{HALFDIMX}', str(int(dimx/2.)))
        html_header = html_header.replace('{HALFDIMY}', str(int(dimy/2.)))
        html_header = html_header.replace('{HALFDIMZ}', str(int(dimz/2.)))
        html_header = html_header.replace('{LASTIMAGE}', str(int(dimz-1)).zfill(string_pad))
        # Get scales for raw images and id meshes
        r_scale = keywords.get('r_scale', '10 1 1')
        i_scale = keywords.get('i_scale', '10 1 1')
        # replace both raw and id scale in the header
        html_header = html_header.replace('{R_SCALE}', r_scale)
        html_header = html_header.replace('{I_SCALE}', i_scale)


        html_footer = ThreeD.html_footer

        # return html_content
        all_html = ''
        for pop_key in html_content:
            pop_html = html_content[pop_key]
            all_html += pop_html

            if pop_key in html_new_files:
                new_file = html_new_files[pop_key]
                # OUTPUT the HTML for the given ID
                with open(new_file, 'w') as f:
                    f.write(html_header + pop_html + html_footer)

                print 'Stored {}'.format(new_file)

        with open(os.path.join(outputfolder, 'null.html'), 'w') as f:
            f.write(html_header + ThreeD.pattern + html_footer)

        # Link scripts
        WWW_IN = keywords.get('www','www')

        if os.path.exists(WWW_IN):
            for lang in ['css', 'javascript']:
                in_link = os.path.join(WWW_IN, lang)
                out_link = os.path.join(outputfolder, lang)
                if os.path.exists(in_link) and not os.path.exists(out_link):
                    os.symlink(in_link, out_link)

    @staticmethod
    def merge_website(out_root, outfile='index.html', only_ids=[]):

        # Get format for valid file names
        index_format = '{}.html'
        # Format all the file paths
        input_format = os.path.join(out_root, index_format)
        null_path = os.path.join(out_root, 'null.html')
        out_path = os.path.join(out_root, outfile)
        # List all input file paths matching the format
        files = glob.glob(input_format.format('*'))

        # Stringify html elements
        html_string = lambda s: ElementTree.tostring(s, method='html')

        # Open the null file with the replaceable comment
        with open(null_path,'r') as nf:
            null = nf.read()

        shapes = []

        # Load all files if empty list
        if not len(only_ids):
            shape_ids = files
        else:
            # Load only files in list that exist
            file_ids = map(input_format.format, only_ids)
            shape_ids = list(set(files) & set(file_ids))

        print """
Merging all files:
{}
        """.format('\n'.join(shape_ids))
        # Load requested ids that exist
        for f in shape_ids:
            shapes += ElementTree.parse(f).getroot().findall('.//group/transform/*')
        
        # Convert all the shapes to strings 
        grouptext = [html_string(shape) for shape in shapes]
        null = null.replace(ThreeD.pattern, ''.join(grouptext))

        # Write all the shapes to an output
        with open(out_path, 'w') as nf:
            nf.write(null)
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
# ThreeD.run(DATA, 0, 0, STLFOLDER, blockshape=200)
# ThreeD.run(DATA, 0, 1, STLFOLDER, blockshape=200)
# ThreeD.run(DATA, 1, 0, STLFOLDER, blockshape=200)
# ThreeD.run(DATA, 1, 1, STLFOLDER, blockshape=200)
#
# ThreeD.create_website(STLFOLDER, X3DFOLDER, None) # <-- None means all IDs
#

#
# Now we will run the ThreeD.run with a blockshape=1024 on the cluster and
# then ThreeD.create_website on Viper after all STLs were created.
#

if __name__ == "__main__":

    # we need the following parameters
    datapath = sys.argv[1]
    z = sys.argv[2]
    y = sys.argv[3]
    x = sys.argv[4]
    outputpath = sys.argv[5]
    blockshape = sys.argv[6]
    id_list = sys.argv[7]

    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    # now run donkey run
    ThreeD.run(datapath, int(z), int(y), int(x), outputpath, int(blockshape), id_list.split(' '))

