import bpy
from bpy.types import Operator
import subprocess
from os.path import join as pjoin
from .utils import *

VIEW_LAYER_NAME = 'View Layer' if bpy.app.version_string.startswith('2.') else 'ViewLayer'

def get_normal_map(context, output_path):
    old_color = context.scene.world.color
    old_engine = context.scene.render.engine
    
    context.scene.view_layers[VIEW_LAYER_NAME].use_pass_z = True
    context.scene.view_layers[VIEW_LAYER_NAME].use_pass_normal = True
    context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    context.scene.render.image_settings.color_depth = '32'
    context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still = True)
    
    context.scene.world.color = old_color
    context.scene.render.engine = old_engine

class SCENE_OT_EXPORT_NORMAL(Operator):
    bl_label = 'Export Normal'
    bl_idname = 'scene.export_normal'
    def execute(self, context):
        ## TODO: 为什么会闪退？？？
        get_normal_map(context, pjoin(context.scene.output_dir, 'Normal_gt.exr'))
        # subprocess.run([
        #     'python', 
        #     'exr2png.py',
        #     '-d', context.scene.output_dir
        # ])
        return {'FINISHED'}