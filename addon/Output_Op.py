import bpy
from bpy.types import Operator
import subprocess
import sys
from os.path import join as pjoin
import numpy as np
import cv2

from .utils import *
from .world2camera import get_3x4_RT_matrix_from_blender

# VIEW_LAYER_NAME = 'View Layer' if bpy.app.version_string.startswith('2.') and sys.platform == "win32" else 'ViewLayer'
VIEW_LAYER_NAME = 'ViewLayer'

def get_normal_map(context, output_path):
    old_color = context.scene.world.color
    old_engine = context.scene.render.engine
    
    context.scene.view_layers[VIEW_LAYER_NAME].use_pass_z = True
    context.scene.view_layers[VIEW_LAYER_NAME].use_pass_normal = True
    context.scene.render.engine = 'CYCLES'
    context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    context.scene.render.image_settings.color_depth = '32'
    context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still = True)
    
    context.scene.world.color = old_color
    context.scene.render.engine = old_engine

def convert_normal_map(output_dir):
    ## Choice 1: System Python with OpenEXR
    # subprocess.run([
    #     'python', 
    #     pjoin(os.path.dirname(__file__), 'exr2png.py'),
    #     '-d', output_dir
    # ])
    
    ## Choice 2: Blender Python with OpenEXR
    from .exr2png import main as convert
    convert(output_dir, output_dir)

def get_camera(camera, output_path):
    RT = get_3x4_RT_matrix_from_blender(camera)
    RT = np.asarray(RT)
    np.savetxt(output_path, RT)

class SCENE_OT_EXPORT_NORMAL(Operator):
    bl_label = 'Normal & Depth'
    bl_idname = 'scene.export_normal'
    def execute(self, context):
        output_dir = bpy.path.abspath(context.scene.output_dir)
        get_normal_map(context, pjoin(output_dir, 'result_normal_depth.exr'))
        convert_normal_map(output_dir)
        get_camera(context.scene.camera, pjoin(output_dir, 'camera_RT.txt'))
        return {'FINISHED'}

def get_image(context, output_dir):
    context.scene.view_layers[VIEW_LAYER_NAME].use_pass_z = False
    context.scene.view_layers[VIEW_LAYER_NAME].use_pass_normal = False
    
    ## WARN: Do not use PNG/TIFF if you want linear image!!!
    ## Choice 1: PNG
    # context.scene.render.image_settings.file_format = 'PNG'
    # context.scene.render.image_settings.color_depth = '16'
    # context.scene.render.image_settings.compression = 100
    ## Choice 2: TIFF, nothing different
    # context.scene.render.image_settings.file_format = 'TIFF'
    # context.scene.render.image_settings.color_depth = '16'
    ## Choice 3: Multi-Layer EXR, recommand
    context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    context.scene.render.image_settings.color_depth = '32'
    
    context.scene.render.filepath = pjoin(output_dir, 'result_image.exr')
    bpy.ops.render.render(write_still=True)

def convert_image(output_dir):
    from .exr2png import handle_single_image
    img = handle_single_image(pjoin(output_dir, 'result_image.exr'))
    img = img[..., ::-1]  # RGB to BGR
    img = img / img.max()  # XXX: just for preview
    cv2.imwrite(pjoin(output_dir, 'image.png'), (img*65535).astype('uint16'), [cv2.IMWRITE_PNG_COMPRESSION, 9])

class SCENE_OT_EXPORT_IMAGE(Operator):
    bl_label = 'Image'
    bl_idname = 'scene.export_image'
    def execute(self, context):
        output_dir = bpy.path.abspath(context.scene.output_dir)
        get_image(context, output_dir)
        convert_image(output_dir)
        return {'FINISHED'}