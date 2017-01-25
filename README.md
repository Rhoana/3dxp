# 3dxp
3D Experiments for Connectomics

## Installing and running on MacOS

- Clone the repo
- Update pip and install all requirements (coming soon)
- Download  and install [Instant Reality Player for X3DOM](http://doc.instantreality.org/media/uploads/downloads/2.8.0/InstantPlayer-MacOS-10.10-x64-2.8.0.38619.dmg)
- `echo "alias aopt='/Applications/Instant\ Player.app/Contents/MacOS/aopt'" >> ~/.bash_profile`
- make local changes to [simple3d.py](https://github.com/Rhoana/3dxp/blob/master/simple3d.py)
  - `DATA = '/full/path/to/your/BIGSEGMENTATIONFILE.h5'`
  - `ROOTDIR = '/full/path/to/your/OutputServerDirectory'`
  - `ALL_IDS = [ 1000, 1337, 99999]`
  - `INDEX = 'index.html'`
- `python simple3d.py`
- `cd /full/path/to/your/OutputServerDirectory`
- Make sure the header of `index.html` looks like this:
```
<head>
  <script type='text/javascript' src='https://www.x3dom.org/x3dom/release/x3dom.js'></script>
  <script type='text/javascript' src='javascript/frames.js'></script>
  <script type='text/javascript' src='javascript/main.js'></script>
  <link rel="stylesheet" href="css/main.css" type="text/css">
</head>
```
- Copy this just below the `<scene>` tag in `index.html`
```
      <viewpoint id="view" bind="true" position="3929.3813885733343 -2071.8817790267294 -1912.3739230587557" orientation="0.6159574590769997 0.7844869949019639 -0.07194833866803957 2.17017692095808" description="camera"></viewpoint>
            <transform bboxCenter='0,0,0' rotation='0 1 0 -1.5708'>
            <transform id='move0' bboxCenter='0,0,0' translation='1000 1000 -1773'>
            <transform bboxCenter='0,0,0' scale='1 -1 1'>
            <shape>
              <appearance>
                  <Texture>
                    <img style="display: none" src='images/1773.png'></img>
                  </Texture>
              </appearance>
              <plane primType='TRIANGLES' size='2000 2000' solid='false'></plane>
            </shape>
            </transform>
            </transform>
            </transform>
            <transform bboxCenter='0,0,0' rotation='0 1 0 -1.5708'>
            <transform id='move1' bboxCenter='0,0,0' translation='1000 1000 -1773'>
            <transform bboxCenter='0,0,0' scale='1 -1 1'>
            <shape>
              <appearance>
                  <Texture>
                    <img style="display: none" src='images/1773.png'></img>
                  </Texture>
              </appearance>
              <plane primType='TRIANGLES' size='2000 2000' solid='false'></plane>
            </shape>
            </transform>
            </transform>
            </transform> 


        <!-- SHOULD BE IN X -->
        <transform id='clipScopeX'>
        <transform bboxCenter='0,0,0' rotation='0 0 1 -1.5708'>
        <!-- <transform bboxCenter='0,0,0' rotation='0 0 1 -1.5708'> -->
        <transform id='move_slice' bboxCenter='0,0,0' translation='-1000 887 0'>
        <transform bboxCenter='0,0,0' scale='-1 -1 1'>
            <shape>
              <appearance>
                <texture>
                   <img style="display:none" src="images/0_in_x.png"> 
                </texture>
              </appearance>
              <plane primType='TRIANGLES' size='2000 1774' solid='false'></plane>
            </shape>
        </transform> 
        <!-- </transform>  -->
        </transform> 
        </transform> 
        </transform> 


        <!-- SHOULD BE IN Y -->
        <transform id='clipScopeY'>
        <transform bboxCenter='0,0,0' rotation='0 0 1 -1.5708'>
        <transform bboxCenter='0,0,0' rotation='0 1 0 -1.5708'>
        <transform id='move_slice' bboxCenter='0,0,0' translation='1000 887 0'>
        <transform bboxCenter='0,0,0' scale='1 -1 1'>
            <shape>
              <appearance>
                <texture>
                   <img style="display:none" src="images/0_in_y.png"> 
                </texture>
              </appearance>
              <plane primType='TRIANGLES' size='2000 1774' solid='false'></plane>
            </shape>
        </transform> 
        </transform> 
        </transform> 
        </transform> 
        </transform> 
```
- `python -m SimpleHTTPServer`
