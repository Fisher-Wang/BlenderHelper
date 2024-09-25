import bpy
from bpy.types import Panel

class HELPER_PT_RENDER_SETTING(Panel):
    bl_label = 'Setting'
    bl_idname = 'HELPER_PT_RENDER_SETTING'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene.render, 'resolution_x', text='Width')
        row = layout.row()
        row.prop(context.scene.render, 'resolution_y', text='Height')