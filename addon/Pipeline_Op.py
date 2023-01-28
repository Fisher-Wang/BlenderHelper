import bpy
import numpy as np
import yaml
from bpy.types import Operator
from os.path import join as pjoin
from .utils import *
from .Camera_Op import *
from .Light_Op import *
from .Output_Op import *

def pipeline(obj_dir, output_base_dir, obj_names):
    context = bpy.context
    for obj_name in obj_names:
        output_dir = mkdir(pjoin(output_base_dir, obj_name))
        
        ## Add Camera
        delete_all(context, 'CAMERA')
        # bpy.ops.object.camera_add(location=(0, 0, 8), rotation=(0, 0, -1))  # duck
        bpy.ops.object.camera_add(location=(0, 0, 2500), rotation=(0, 0, -1))  # whale
        camera = context.scene.camera = context.object
        camera.data.clip_end = 10000  # XXX: increase this value when rendered result is blank!
        
        ## Set Camera
        set_camera_pos(camera, 45, 0)
        
        ## Add Light
        ls = multi_light(context, 3)
        write_json(pjoin(output_dir, 'light_information.json'), ls)
        
        ## Set Light
        # TODO
        
        ## Animation
        frame_start, frame_end = get_frame_range_scene(context.scene)
        for frame in range(frame_start, frame_end+1):
            if frame > 10: break
            od = mkdir(pjoin(output_dir, f'frame_{frame:03d}'))
            context.scene.frame_set(frame)
            get_camera(camera, od)
            
            switch_cast_shadow(context, enable=True)
            get_all(context, od, normal=True, depth=True, albedo=True)
            convert_all(od, od)
            os.rename(pjoin(od, 'image.png'), pjoin(od, 'image_shadow.png'))
            os.rename(pjoin(od, 'image.npy'), pjoin(od, 'image_shadow.npy'))
            
            switch_cast_shadow(context, enable=False)
            get_all(context, od, normal=False, depth=False, albedo=False)
            convert_all(od, od)

class RENDER_OT_PIPELINE(Operator):
    bl_idname = 'render.pipeline'
    bl_label = 'Pipeline'
    
    def execute(self, context):
        output_base_dir = bpy.path.abspath(context.scene.output_dir)
        pipeline('', output_base_dir, ['whale'])  # TODO: temp
        return {'FINISHED'}
        