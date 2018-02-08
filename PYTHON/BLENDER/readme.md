### 3DXP Blender usage

This is a set of command line tools to render images like this:

![Render](https://github.com/thejohnhoffer/img/raw/master/port/0.gif)

### Harvard-specific preparation
```
source new-modules.sh
module load blender/2.69-fasrc01
export PYTHONDONTWRITEBYTECODE=1
```

### General usage

To pass any `$args` to a `$py` file this directory:

```
blender -noaudio -b -P $py -- $args
```

To set up lighting with `py=lights.py`, here is the man page:

```
usage: blender -P lights.py -- [-h] [-b BLEND] [-o OUTPUT]

Set up the scene.

optional arguments:
  -h, --help            show this help message and exit
  -b BLEND, --blend BLEND
                        Blender file to save output
  -o OUTPUT, --output OUTPUT
                        Output folder to render scene images
```

To import stl or obj files with `py=import.py` here is the man page:

```
usage: blender -P import.py -- [-h] [-f FILE] [-l LIST] [-b BLEND] [-o OUTPUT]
                               [--XYZ XYZ] [--VOL VOL] [--xyz XYZ] [--vol VOL]
                               [--vox VOX] [--nm NM] [--tmp TMP]
                               folder

Import mesh files.

positional arguments:
  folder                /folder/ or /id_%d/folder/

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  *_segmentation_%d.stl (default *.*)
  -l LIST, --list LIST  %d:%d:%d... list for %d in folder and file
  -b BLEND, --blend BLEND
                        Blender file to save output
  -o OUTPUT, --output OUTPUT
                        Output folder to render scene images
  --XYZ XYZ             Set X:Y:Z origin of full volume in microns (default 0:0:0)
  --VOL VOL             Set D:H:W size of volume measured in um (default 50:50:50)
  --xyz XYZ             Xi:Yi:Zi # subvolumes offset from origin (default 0:0:0)
  --vol VOL             Xn:Yn:Zn subvolumes in full volume (default 1:1:1)
  --vox VOX             w:h:d of voxels per mesh unit (default 1:1:1)
  --nm NM               w:h:d of nm per voxel (default 4:4:30)
  --tmp TMP             Temporary folder (default tmp)
```

To import images as textuered planes with `py=slices.py`, here is the man page:

```
usage: blender -P slices.py -- [-h] [-f FILE] [-l LIST] [-b BLEND] [-o OUTPUT]
                               [--XYZ XYZ] [--VOL VOL] [--xyz XYZ] [--vol VOL]
                               [--vox VOX] [--nm NM]
                               folder

Import slice images.

positional arguments:
  folder                /folder/ or /id_%d/folder/

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  *_segmentation_%d.stl (default *.*)
  -l LIST, --list LIST  %d:%d:%d... list for %d in folder and file
  -b BLEND, --blend BLEND
                        Blender file to save output
  -o OUTPUT, --output OUTPUT
                        Output folder to render scene images
  --XYZ XYZ             Set X:Y:Z origin of full volume in microns (default 0:0:0)
  --VOL VOL             Set D:H:W size of volume measured in um (default 50:50:50)
  --xyz XYZ             Xi:Yi:Zi # subvolumes offset from origin (default 0:0:0)
  --vol VOL             Xn:Yn:Zn subvolumes in full volume (default 1:1:1)
  --vox VOX             w:h:d of voxels per mesh unit (default 1:1:1)
  --nm NM               w:h:d of nm per voxel (default 4:4:30)
```

To animate through all image planes with `py=scrolll.py`, here is the man page:

```
usage: blender -P scroll.py -- [-h] [-b BLEND] [-o OUTPUT] [--VOL VOL]
                               [--XYZ XYZ] [--zspan ZSPAN] [--zps ZPS]
                               [--fps {...}]

Set up the scene.

optional arguments:
  -h, --help            show this help message and exit
  -b BLEND, --blend BLEND
                        Blender file to save output
  -o OUTPUT, --output OUTPUT
                        Output folder to render scene images
  --VOL VOL             Set D:H:W size of volume measured in um (default 50:50:50)
  --XYZ XYZ             Set X:Y:Z origin of full volume in microns (default 0:0:0)
  --zspan ZSPAN         start:stop slices (default all)
  --zps ZPS             z slices per second (default 4)
  --fps {4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63}
                        frames per second (default 1)
```


