import bpy
from bpy.types import Panel

class CAMERA_BASE:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MVPSRenderHelper'
    bl_options = {"DEFAULT_CLOSED"}

class HELPER_PT_CAMERA(CAMERA_BASE, Panel):
    bl_label = 'Camera'
    bl_idname = 'HELPER_PT_CAMERA'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('camera.add_orthographic')

class HELPER_PT_CAMERA_POSE(CAMERA_BASE, Panel):
    bl_label = 'Pose'
    bl_idname = 'HELPER_PT_CAMERA_POSE'
    bl_parent_id = 'HELPER_PT_CAMERA'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'camera_phi')
        row = layout.row()
        row.prop(context.scene, 'camera_theta')
        row = layout.row()
        row.operator('camera.set_position')