import bpy
from bpy.types import Panel

class HELPER_PT_ANIMATION_CONTROL(Panel):
    bl_label = 'Animation Control'
    bl_idname = 'HELPER_PT_ANIMATION_CONTROL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MVPSRenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'frame_custom')
