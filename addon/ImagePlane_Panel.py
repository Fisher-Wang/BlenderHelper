import bpy
from bpy.types import Panel

class HELPER_PT_IMPORT_PLANE_IMAGE(bpy.types.Panel):
    bl_label = 'Import Image'
    bl_idname = 'HELPER_PT_IMPORT_PLANE_IMAGE'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MVPSRenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'image_path')
        row = layout.row()
        row.operator('scene.import_image_plane', icon='IMPORT')
        row = layout.row()
        row.prop(context.scene, 'obj1', text='Obj1')
        row = layout.row()
        row.prop(context.scene, 'obj2', text='Obj2')
        row = layout.row()
        row.operator('scene.switch_visibility', icon='ARROW_LEFTRIGHT')