import bpy
from bpy.types import Panel

class HELPER_PT_PIPELINE(Panel):
    bl_label = 'Pipeline'
    bl_idname = 'HELPER_PT_PIPELINE'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MVPSRenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('render.pipeline')