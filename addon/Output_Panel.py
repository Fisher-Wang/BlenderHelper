import bpy
from bpy.types import Panel

class HELPER_PT_OUTPUT(Panel):
    bl_label = 'Output'
    bl_idname = 'HELPER_PT_OUTPUT'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('scene.export_normal')
        row = layout.row()
        row.operator('scene.export_image', text='Image')
        ## TODO: implement this
        row = layout.row()
        row.operator('scene.export_image', text='Image w/o Shadow')
        row = layout.row()
        row.operator('scene.export_albedo')
        ## TODO: implement this
        row = layout.row()
        row.operator('scene.export_image', text='Camera Mat')
