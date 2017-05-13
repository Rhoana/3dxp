# Making an animation

## Preparation

Set the `slice` in `javascript/main.js` to the total number of slices.


## Recording keyframes

Open `index.html` as output by `example_*.sh`  
Use the down arrow key to move down the stack in even intervals.  
Along the way, press the right arrow key to record your current keyframes.  
When you have recorded many keyframes, export them with the shift key.  


## Interpolating the frames

Copy the `LAYERS` from the above json as the `keyframes` array in the `save_frames` function of `index_min.html`.  
Edit this array if necessary to be monotonically decreasing.  

From the root of this repo, open `getmesh/frames/format_frames.py`.  
Copy the `FRAMES` from the above json in this script and run it.  

Copy the resulting `interp.txt` text file to replace all `viewpoint` elements in the `scene` element in `index_min.html`.

Open `index_min.html`, and enter `save_frames()` in the developer console. Wait.  

Copy the resulting file to `javascript/frames.js`


## Done

Now, reopen `index.html` and hit space to view the animation.
