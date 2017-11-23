bl_info = {
    "name": "Scene Setup",
    "category": "Scene",
}

import os
import bpy

from bpy.props import StringProperty

from . import parser
from . import semver
from . import linker
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

        # Set up the sun
        if 'Sun' not in bpy.data.lamps:
            sun = bpy.data.lamps.new(name='Sun', type='SUN')
            sun_obj = bpy.data.objects.new(name='Sun', object_data=sun)
            context.scene.objects.link(sun_obj)
            sun.energy = 0.1
            log.att(sun)

        # Set up the lamp
        if 'Lamp' in bpy.data.lamps:
            lamp = bpy.data.lamps['Lamp']
            lamp.energy = 1

        return {'FINISHED'}


class Stopper(bpy.types.Operator):

    bl_idname = "common.stop"
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Stop {}'.format(bl_info['name'])

    blend = StringProperty()
    output = StringProperty()

    def execute(self, context): 
        # Render if file given
        if self.output:
            outdir = os.path.dirname(self.output)
            pather.make(outdir)
            # Path as the output of the scene
            context.scene.render.engine = 'CYCLES'
            context.scene.render.filepath = self.output
            log.yaml('Rendering', self.output)
            # Write a single image to the output
            bpy.ops.render.render(write_still=True)

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
