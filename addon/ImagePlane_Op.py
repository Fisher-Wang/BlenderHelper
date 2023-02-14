import bpy
from bpy.types import Operator
import os
from .utils import *

def import_image_plane(context):
    path = bpy.path.abspath(context.scene.image_path)
    bpy.ops.import_image.to_plane(
        files=[{"name": os.path.basename(path)}], 
        directory=os.path.dirname(path)
    )
    
    mesh = find_all(context, 'MESH')[0]
    length = max(mesh.measure.lenX, mesh.measure.lenY)
    bpy.ops.transform.resize(value=(length, length, length))
    
    ## Move plane below mesh
    # height = mesh.measure.maxZ - mesh.measure.minZ
    # bpy.ops.transform.translate(value=(0, 0, -height))

class SCENE_OT_IMPORT_IMAGE_PLANE(Operator):
    bl_label = 'Import Image as Plane'
    bl_idname = 'scene.import_image_plane'
    def execute(self, context):
        import_image_plane(context)
        return {'FINISHED'}

class SCENE_OT_SWITCH_VISIBILITY(Operator):
    bl_label = 'Switch Visibility'
    bl_idname = 'scene.switch_visibility'
    def execute(self, context):
        obj1 = context.scene.obj1
        obj2 = context.scene.obj2
        if not (obj1 and obj2):
            print('[WARN] Objects are not specified, auto selecting...')
            meshes = find_all(context, 'MESH')
            if len(meshes) != 2:
                print('[ERROR] There are %d meshes!' % len(meshes))
                return {'CANCELLED'}
            obj1 = meshes[0]
            obj2 = meshes[1]
        
        if obj1.hide_get() == True:
            obj1.hide_set(False)
            obj2.hide_set(True)
        else:
            obj1.hide_set(True)
            obj2.hide_set(False)
        
        return {'FINISHED'}