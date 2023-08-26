import bpy
from bpy.types import Panel

class HELPER_PT_OUTPUT(Panel):
    bl_label = 'Output'
    bl_idname = 'HELPER_PT_OUTPUT'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MVPSRenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('render.hide_others', icon='PROP_CON')
        row = layout.row()
        row.operator('scene.export_normal')
        row = layout.row()
        row.operator('scene.export_image', text='Image')
        # row = layout.row()
        # row.operator('scene.export_image', text='Image w/o Shadow')
        row = layout.row()
        row.operator('scene.export_albedo')
        # row = layout.row()
        # row.operator('scene.export_image', text='Camera Mat')
        
        # output_pass = context.scene.output_pass
        # layout.prop(output_pass, 'combined')
        # layout.prop(output_pass, 'normal')
        # layout.prop(output_pass, 'albedo')
        # layout.prop(output_pass, 'depth')
        # layout.prop(output_pass, 'shadow')