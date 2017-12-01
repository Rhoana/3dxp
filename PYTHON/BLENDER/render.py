import bpy
from mathutils import Vector

import math
import sys
import os

DIRNAME = os.path.dirname(__file__)
if not DIRNAME in sys.path:
    sys.path.append(DIRNAME)

COMMON = os.path.join(DIRNAME, 'common', '__init__.py')
bpy.ops.wm.addon_install(filepath=COMMON)
bpy.ops.wm.addon_enable(module='common')
bpy.ops.wm.save_userpref()

from common import parser
from common import semver
from common import err
from common import log

def main(arg, versions):
    context = bpy.context
    scene = context.scene
    render = scene.render
    # Open the scene
    bpy.ops.common.start(blend=arg.blend)
    # All frames in scene
    frames = scene.frame_start, scene.frame_end
    n_frames = int(frames[0] - frames[1])
    # Frames for this task
    task_frames = n_frames / arg.runs
    task_start = task_frames * arg.task
    task_end = task_start + task_frames
    # Set scene frames
    scene.frame_start = task_start
    scene.frame_end = task_end
    # Add task to path
    task_file = '{:010d}'.format(task)
    task_out = os.path.join(arg.output, task_file)

    print(task_out, task_start, task_end)
    return
    # Stop the scene
    bpy.ops.common.stop(**{
        'output': arg.output,
        'movie': True,
    })

if __name__ == "__main__":
    describe = 'Set up the scene.'
    filename = os.path.basename(__file__)
    # Get argument parser
    items = [
        'blend', 'output',
    ]
    cmd = parser.setup(filename, describe, items)
    parser.add_argument(cmd, 'task')
    parser.add_argument(cmd, 'runs')
    # Get most recent version
    versions = semver.all()
    semver.setup(versions)
    # Run everything safely
    err.wrap(cmd, main, versions)
