# 3dxp
3D Experiments for Connectomics

Designed to work with the [Butterfly Image Server](https://github.com/rhoana/butterfly)

Documented in [Scalable Interactive Visualization for Connectomics](http://www.mdpi.com/2227-9709/4/3/29/pdf)

### Installation
```
pip install -r ./PYTHON/requirements.txt
```

### Configuration

Find many working examples using the [Sly Markup Language](TASKS/readme.md)

![visual result](https://github.com/thejohnhoffer/img/raw/master/bfly/100um_20ids.gif)

### Detailed Usage

To go from [a boss index](https://github.com/microns-ariadne/pipeline_engine#output) to an image stack, use `./PYTHON/conversion/boss2stack.py`
```
usage: boss2stack.py [-h] [--trial TRIAL] [--runs RUNS] [--scale SCALE]
                     [--delta DELTA] [--out OUT] [--fmt FMT] [-l LIST] [-z Z]
                     [-y Y] [-x X]
                     files

Rescale a grid of tiff files to an image stack

positional arguments:
  files                 The path to a json file listing all tiff files

optional arguments:
  -h, --help            show this help message and exit
  --trial TRIAL, -t TRIAL
                        The trial number for this run (0)
  --runs RUNS, -r RUNS  The number of runs for all slices (1)
  --scale SCALE, -s SCALE
                        Downsampling times in Z,Y,X (0:0:0)
  --delta DELTA, -d DELTA
                        Define full voxel 0,0,0 in data Z,Y,X (0:0:0)
  --out OUT, -o OUT     The directory to save the output images (./out)
  --fmt FMT, -f FMT     The output format as jpg, tif, or png (png)
  -l LIST, --list LIST  Mask for : separated list of values
  -z Z                  The start and end Z slices to use
  -y Y                  The start and end Y slices to use
  -x X                  The start and end X slices to use
```

To go from an image stack to an [HDF5 File](https://en.wikipedia.org/wiki/Hierarchical_Data_Format), use `./PYTHON/conversion/***2hd.py`

```
usage: jpg2hd.py [-h] [-t string] [-o string] [-c] [-z Z] [-y Y] [-x X]
                 [jpgs] [out]

Stack all jpgs into a hdf5 file!

positional arguments:
  jpgs        input folder with all jpgs (default jpgs)
  out         output file (default out.h5)

optional arguments:
  -h, --help  show this help message and exit
  -t string   datatype for output file (default uint8)
  -o string   Little Endian channel order as rgba,bgr (default none)
  -c          -c enables -t uint32 (and default -o bgr)
  -z Z        The start:stop subregion to crop in Z (default full)
  -y Y        The start:stop subregion to crop in Y (default full)
  -x X        The start:stop Subregion to crop in X (default full)
```

To count the values in an [HDF5 File](https://en.wikipedia.org/wiki/Hierarchical_Data_Format) with the broadest distribution, use `./PYTHON/all_counts.py`
```
usage: all_counts.py [-h] [-b BLOCK] [-d DEEP] ids out

Save the deepest or the biggest cells

positional arguments:
  ids                   input hd5 id volume (default in.h5)
  out                   output text list directory (default .)

optional arguments:
  -h, --help            show this help message and exit
  -b BLOCK, --block BLOCK
                        Number of blocks in each dimension (default 10)
  -d DEEP, --deep DEEP  save top ids by depth (default 0)

``` 

To go from an [HDF5 File](https://en.wikipedia.org/wiki/Hierarchical_Data_Format) to an [STL File](https://en.wikipedia.org/wiki/STL_(file_format)), use `./PYTHON/all_stl.py`

```
Try installing and then changing to another directory before importing mahotas.
usage: all_stl.py [-h] [--xyz] [-f FOLDER] [-p] [-d DEEP] [-t TRIAL]
                  [-b BLOCK] [-n NUMBER] [-l LIST]
                  ids out

Make an hdf5 file into stl meshes!

positional arguments:
  ids                   input hd5 id volume (default in.h5)
  out                   output web directory (default .)

optional arguments:
  -h, --help            show this help message and exit
  --xyz                 Store meshes with xyz coordinates (default zyx)!
  -f FOLDER, --folder FOLDER
                        folder format for meshes of id %d (default %d)
  -p, --pre             Use NG prerendered format instead (default stl)
  -d DEEP, --deep DEEP  rank top ids by depth (default 0)
  -t TRIAL, --trial TRIAL
                        Which of the b*b*b tiles to generate (default 0)
  -b BLOCK, --block BLOCK
                        Number of blocks in each dimension (default 10)
  -n NUMBER, --number NUMBER
                        make meshes for the top n ids (default 1)
  -l LIST, --list LIST  make meshes for : separated list of ids
```

To go from [STL Files](https://en.wikipedia.org/wiki/STL_(file_format)) to [X3Dom POP HTML files](https://x3dom.org/pop/) that include image planes from a corresponding image stack and [HDF5](https://en.wikipedia.org/wiki/Hierarchical_Data_Format) file, install [aopt](https://doc.x3dom.org/tutorials/models/aopt/index.html) and use `./PYTHON/all_x3d.py`
```
usage: all_x3d.py [-h] [-n NUMBER] [-l LIST] [-t TRIAL] [--runs RUNS]
                  [-d DEEP] [-w WWW] [-V VRATIO] [-R RRATIO] [-I IRATIO]
                  raw img [out]

Make an hdf5 file into html meshes!

positional arguments:
  raw                   input raw h5 volume (default raw.h5)
  img                   input raw img folder (default imgs)
  out                   output web directory (default .)

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        make meshes for the top n ids (default 1)
  -l LIST, --list LIST  make meshes for : separated list of ids
  -t TRIAL, --trial TRIAL
                        The trial number for this run (0)
  --runs RUNS, -r RUNS  The number of runs for all the ids (1)
  -d DEEP, --deep DEEP  rank top ids by depth (default 0)
  -w WWW, --www WWW     folder containing js/css (default www)
  -V VRATIO, --Vratio VRATIO
                        Original voxel physical z size over xy size (default
                        10.0)
  -R RRATIO, --Rratio RRATIO
                        Number of downsamplings in z:xy of raw img data
                        (default 0:3)
  -I IRATIO, --Iratio IRATIO
                        Number of downsamplings in z:xy of ID mesh data
                        (default 0:3)
```

To combine multiple [X3Dom POP HTML files](https://x3dom.org/pop/) into one index, use `./PYTHON/all_index.py`
```
usage: all_index.py [-h] [-f INDEX] [-l LIST] [out]

Make an hdf5 file into html meshes!

positional arguments:
  out                   output web directory (default .)

optional arguments:
  -h, --help            show this help message and exit
  -f INDEX, --index INDEX
                        output filename (default index.html)
  -l LIST, --list LIST  make meshes for : separated list of ids
```
If you made it here, enjoy a [comic](https://xkcd.com/1742/)

![XKCD Will it Work with Minimal Configuration](https://imgs.xkcd.com/comics/will_it_work.png)
