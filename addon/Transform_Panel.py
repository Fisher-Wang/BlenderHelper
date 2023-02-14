import bpy
from bpy.types import Panel

class HELPER_PT_TRANSFORM(Panel):
    bl_label = 'Transform'
    bl_idname = 'HELPER_PT_TRANSFORM'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MVPSRenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('object.trans_set_origin')
        row = layout.row()
        row.operator('object.trans_reset')
        row = layout.row()
        row.prop(context.scene, 'rotation')
        row = layout.row()
        row.prop(context.scene, 'scale_z')
        row = layout.row()
        row.operator('object.trans_set')