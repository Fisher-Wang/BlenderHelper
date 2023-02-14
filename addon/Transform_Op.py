import bpy
from bpy.types import Operator
import mathutils
import math

def trans_set_origin(object):
    object.matrix_world_origin = object.matrix_world

def trans_reset(object):
    object.matrix_world = object.matrix_world_origin

def trans_rotate(object, angle):
    M = mathutils.Matrix.Rotation(math.radians(angle), 4, 'Z')
    object.matrix_world = M @ object.matrix_world

def trans_scale_z(object, scale):
    M = mathutils.Matrix.Scale(scale, 4, (0, 0, 1))
    object.matrix_world = M @ object.matrix_world

class MESH_OT_SET_ORIGIN(Operator):
    bl_label = 'Set as Origin'
    bl_idname = 'object.trans_set_origin'
    def execute(self, context):
        trans_set_origin(context.object)
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return context.object is not None

class MESH_OT_RESET(Operator):
    bl_label = 'Reset'
    bl_idname = 'object.trans_reset'
    def execute(self, context):
        trans_reset(context.object)
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return context.object is not None

class MESH_OT_SET(Operator):
    bl_label = 'Set'
    bl_idname = 'object.trans_set'
    def execute(self, context):
        trans_rotate(context.object, context.object.rotation)
        trans_scale_z(context.object, context.object.scale_z)
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return context.object is not None
        