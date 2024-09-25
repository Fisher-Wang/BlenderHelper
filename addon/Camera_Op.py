import bpy
import math
import numpy as np
from .utils import *
from .utils_debug import *
from mathutils import Vector

def add_orthographic_camera(context):
    debug_print('[INFO] Calling add_orthographic_camera')
    delete_all(context, 'CAMERA')
    
    mesh = find_all(context, 'MESH')[0]
    maxLen = max(mesh.measure.lenX, mesh.measure.lenY)
    print(maxLen)
    
    bpy.ops.object.camera_add(location=(0, 0, 10), rotation=(0, 0, -1))
    context.scene.camera = context.object
    camera = context.scene.camera
    set_direction_to(camera, distance=10)
    # This sentence fails on blender 2.93.11, but work well on blender 2.83.20 and 3.3.1
    bpy.ops.transform.rotate(value=math.pi, orient_axis='Z')

    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = maxLen
    camera.data.clip_end = 10000  # XXX: increase this value when rendered result is blank!
    return camera

class CAMERA_OT_ADD_ORTHOGRAPHIC(bpy.types.Operator):
    bl_label = 'Add Otrho Camera'
    bl_idname = 'camera.add_orthographic'
    def execute(self, context):
        add_orthographic_camera(context)
        return {'FINISHED'}

def set_camera_pos(cam, phi, theta):
    dis = np.linalg.norm(np.asarray(cam.location))
    cam.location = phi_theta_to_xyz(phi, theta)
    set_direction_to(cam, Vector((0, 0, 0)), distance=dis)

class CAMERA_OT_SET_POSITION(bpy.types.Operator):
    bl_label = 'Set Position'
    bl_idname = 'camera.set_position'
    def execute(self, context):
        set_camera_pos(context.scene.camera, context.scene.camera_phi, context.scene.camera_theta)
        return {'FINISHED'}