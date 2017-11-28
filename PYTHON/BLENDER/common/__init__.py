bl_info = {
    "name": "Scene Setup",
    "category": "Scene",
}

import os
import bpy

from bpy.props import StringProperty
from bpy.props import BoolProperty

from . import parser
from . import semver
from . import linker
from . import mover
from . import pather
from . import sizer

from . import err
from . import log

class Starter(bpy.types.Operator):

    bl_idname = "common.start"
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Start {}'.format(bl_info['name'])

    blend = StringProperty()

    def execute(self, context): 
        def remove_mesh(k, v):
            scene = context.scene
            obj = scene.objects[k]
            scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)
            bpy.data.meshes.remove(v)

        # Open if blend given
        if self.blend and os.path.exists(self.blend):
            log.yaml('Loading blend file', self.blend)
            bpy.ops.wm.open_mainfile(filepath=self.blend)

        # Remove the default cube mesh
        for k,v in bpy.data.meshes.items():
            if k in ['Cube']:
                remove_mesh(k, v)
                log.yaml('Removed', k)

        # Create the sun
        if 'Sun' not in bpy.data.lamps:
            sun = bpy.data.lamps.new(name='Sun', type='SUN')
            sun_obj = bpy.data.objects.new(name='Sun', object_data=sun)
            context.scene.objects.link(sun_obj)

        # Set up the lamp
        if 'Lamp' in bpy.data.lamps:
            lamp = bpy.data.lamps['Lamp']
            lamp.energy = 5

        # Set up the sun
        sun = bpy.data.lamps['Sun']
        sun.energy = 0.5

        return {'FINISHED'}


class Stopper(bpy.types.Operator):

    bl_idname = "common.stop"
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Stop {}'.format(bl_info['name'])

    blend = StringProperty()
    output = StringProperty()
    movie = BoolProperty()

    def render(self, context):
        scene = context.scene
        render = scene.render
        # All frames in scene
        frames = scene.frame_start, scene.frame_end
        outdir = os.path.dirname(self.output)
        pather.make(outdir)
        # Path as the output of the scene
        render.filepath = self.output
        log.yaml('Rendering', self.output)
        # Render images to the output files
        if self.movie:
            pather.make(self.output)
            for i_fr in range(*frames):
                file_fr = '{:010d}'.format(i_fr)
                path_fr = self.output, file_fr
                out_fr = os.path.join(*path_fr)
                render.filepath = out_fr
                # Set current frame and write
                scene.frame_set(i_fr)
                bpy.ops.render.render(**{
                    'write_still': True
                })
            return
        bpy.ops.render.render(**{
            'write_still': True
        })
    def execute(self, context): 
        # Render if file given
        if self.output:
            self.render(context)

        # Save if blend given
        if self.blend:
            outdir = os.path.dirname(self.blend)
            pather.make(outdir)
            log.yaml('Saving blend file', self.blend)
            
            bpy.ops.wm.save_mainfile(**{
                'filepath': self.blend,
            })

        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
