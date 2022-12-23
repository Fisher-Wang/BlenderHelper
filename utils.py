import bpy
import os
import math
from mathutils import Vector

def mkdir(dir_path, exist_ok=True):
    os.makedirs(dir_path, exist_ok=exist_ok)
    return dir_path

def get_node_tree(mesh):
    return [material.node_tree for material in mesh.data.materials if material != None][0]

def delete_all(context, types: list):
    for o in context.scene.objects:
        if o.type in types:
            o.select_set(True)
        else:
            o.select_set(False)
    bpy.ops.object.delete()

def find_all(context, type):
    rst = []
    for o in context.scene.objects:
        if o.type == type:
            rst.append(o)
    return rst

def select_one(context, object, active=True):
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    if active:
        context.view_layer.objects.active = object

def set_direction_to(object, focus_point=Vector((0.0, 0.0, 0.0)), distance=10.0):
    ## source: https://blender.stackexchange.com/a/100442
    '''
    #### Parameters
    - `object`: can be camera or light
    '''
    looking_direction = object.location - focus_point
    rot_quat = looking_direction.to_track_quat('Z', 'Y')
    object.rotation_euler = rot_quat.to_euler()
    object.location = rot_quat @ Vector((0.0, 0.0, distance))

def get_frame_range_obj(obj):
    if obj.animation_data:
        frame_start, frame_end = map(int, obj.animation_data.action.frame_range)
    else:
        frame_start, frame_end = 0, 0
    return frame_start, frame_end

def get_frame_range_scene(scene):
    min_frame_start, max_frame_end = math.inf, 0
    for obj in scene.objects:
        frame_start, frame_end = get_frame_range_obj(obj)
        min_frame_start = min(min_frame_start, frame_start)
        max_frame_end = max(max_frame_end, frame_end)
    return min_frame_start, max_frame_end