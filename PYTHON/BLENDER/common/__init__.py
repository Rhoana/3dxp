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
from . import cycler
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
        # Cycles
        context.scene.render.engine = 'CYCLES' 

        def remove_object(o):
            iters = {
                'MESH': bpy.data.meshes,
                'LAMP': bpy.data.lamps,
            }
            o_data = o.data
            o_iter = iters.get(o.type, None)
            scene = context.scene
            scene.objects.unlink(o)
            bpy.data.objects.remove(o)
            if o_iter:
                o_iter.remove(o_data)

        # Open if blend given
        if self.blend and os.path.exists(self.blend):
            log.yaml('Loading blend file', self.blend)
            bpy.ops.wm.open_mainfile(filepath=self.blend)
        bad_mesh = {'Cube'}
        bad_lamp = {'Lamp'}
        bad = bad_mesh | bad_lamp
        # Remove the default cube mesh
        for o in bpy.data.objects:
            names = {o.name, o.data.name}
            if names & bad:
                log.yaml('Removed', o.name)
                remove_object(o)

        # Create the sun
        if 'Sun' not in bpy.data.lamps:
            bpy.ops.object.lamp_add(**{
                'type': 'SUN',
            })
            sun = bpy.context.active_object
            sun.data.name = 'Sun'
            sun.name = 'Sun'

        area_locs = {
            'Area': (2.0, 2.0, 10.0),
            'Over': (0.0, 0.0, 1.0),
            'Under': (0.0, 0.0, -1.0),
        }
        area_size = {
            'Area': 0.5,
            'Over': 0.5,
            'Under': 0.5,
        }
        area_bright = {
            'Area': 10000,
            'Over': 100,
            'Under': 100,
        }

        # Create an area lamp
        def make_area(_name, _location):
            if _name in bpy.data.lamps:
                return
            bpy.ops.object.lamp_add(**{
                'location': _location,
                'type': 'AREA',
            })
            area = bpy.context.active_object
            area.data.name = _name
            area.name = _name

        # Set up some area lamps
        for name,loc in area_locs.items():
            make_area(name, loc)
            area = bpy.data.lamps[name]
            area.shadow_buffer_soft = 100
            area.size = area_size[name]
            a_bright = area_bright[name]
            a_pow = a_bright * (loc[-1] ** 2)
            area.energy = a_pow * (area.size ** 2)

        # Set up the sun
        sun = bpy.data.lamps['Sun']
        sun.cycles.cast_shadow = False
        sun.energy = 2

        #remove_lamp('Area')
        #remove_lamp('Sun')

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
            log.yaml('Frames', frames)
            pather.make(self.output)
            # Set frame to first frame
            scene.frame_set(frames[0])
            render.ffmpeg.codec = 'H264'
            render.ffmpeg.format = 'MPEG4'
            render.fps_base = render.fps / 24
            render.resolution_x = 900 * 2
            render.resolution_y = 500 * 2
            render.image_settings.file_format = 'FFMPEG'
            # Animate movie
            bpy.ops.render.render(**{
                'animation': True
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
