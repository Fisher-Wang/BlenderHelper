import bpy
from bpy.types import Panel

class HELPER_PT_LIGHT(Panel):
    bl_label = 'Light'
    bl_idname = 'HELPER_PT_LIGHT'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'phi')
        row = layout.row()
        row.prop(context.scene, 'theta')
        row = layout.row()
        row.operator('render.set_light_direction', icon='SNAP_NORMAL')
        row = layout.row()
        row.operator('render.multi_light')
        