import bpy
from bpy.types import Panel

class HELPER_PT_CAMERA(Panel):
    bl_label = 'Camera'
    bl_idname = 'HELPER_PT_CAMERA'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('camera.add_orthographic')
        row = layout.row()
        row.prop(context.scene, 'camera_phi')
        row = layout.row()
        row.prop(context.scene, 'camera_theta')
        row = layout.row()
        row.operator('camera.set_position')