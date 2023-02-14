import bpy
from bpy.types import Operator
import subprocess
import sys
from os.path import join as pjoin
import numpy as np
import cv2

from .utils import *
from .world2camera import get_3x4_P_matrix_from_blender
from .exr2png import convert_all

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

def get_camera(camera, output_dir):
    P, K, RT = get_3x4_P_matrix_from_blender(camera)
    focal_length = camera.data.lens
    P = np.asarray(P).tolist()
    K = np.asarray(K).tolist()
    RT = np.asarray(RT).tolist()
    data = {
        'focal_length': focal_length,
        'P': P,
        'K': K,
        'RT': RT,
    }
    write_json(pjoin(output_dir, 'camera.json'), data)

class SCENE_OT_EXPORT_NORMAL(Operator):
    bl_label = 'Normal & Depth'
    bl_idname = 'scene.export_normal'
    def execute(self, context):
        output_dir = bpy.path.abspath(context.scene.output_dir)
        get_normal_map(context, pjoin(output_dir, 'result.exr'))
        get_camera(context.scene.camera, output_dir)
        convert_all(output_dir, output_dir)
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

def get_albedo(context, output_dir):
    context.scene.view_layers["ViewLayer"].use_pass_diffuse_color = True
    
    context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    context.scene.render.image_settings.color_depth = '32'
    context.scene.render.filepath = pjoin(output_dir, 'result_albedo.exr')
    bpy.ops.render.render(write_still=True)
    
    context.scene.view_layers["ViewLayer"].use_pass_diffuse_color = False

def convert_albedo(output_dir):
    from .exr2png import handle_albedo
    img = handle_albedo(pjoin(output_dir, 'result_albedo.exr'))
    np.save(pjoin(output_dir, 'albedo.npy'), img)
    img = img[..., ::-1]  # RGB to BGR
    img = img / img.max()  # XXX: just for preview
    cv2.imwrite(pjoin(output_dir, 'preview_albedo.png'), (img*65535).astype('uint16'), [cv2.IMWRITE_PNG_COMPRESSION, 9])

class SCENE_OT_EXPORT_ALBEDO(Operator):
    bl_label = 'Albedo'
    bl_idname = 'scene.export_albedo'
    def execute(self, context):
        output_dir = bpy.path.abspath(context.scene.output_dir)
        get_albedo(context, output_dir)
        convert_albedo(output_dir)
        return {'FINISHED'}

def get_all(context, output_dir, normal=True, depth=True, albedo=True):
    context.scene.render.engine = 'CYCLES'
    
    context.scene.view_layers[VIEW_LAYER_NAME].use_pass_z = depth
    context.scene.view_layers[VIEW_LAYER_NAME].use_pass_normal = normal
    context.scene.view_layers[VIEW_LAYER_NAME].use_pass_diffuse_color = albedo
    
    context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    context.scene.render.image_settings.color_depth = '32'
    context.scene.render.filepath = pjoin(output_dir, 'result.exr')
    bpy.ops.render.render(write_still=True)

class RENDER_OT_HIDE_OTHERS(Operator):
    bl_label = 'Hide Others'
    bl_idname = 'render.hide_others'
    def execute(self, context):
        for mesh in find_all(context, 'MESH'):
            if mesh.select_get():
                mesh.hide_render = False
            else:
                mesh.hide_render = True
                
        return {'FINISHED'}