import bpy
from bpy.props import *
from .utils import *

#############################
## Self-Defined Properties
#############################

class ObjectMeasurePropertyGroup(bpy.types.PropertyGroup):
    minX: FloatProperty(name='minX')
    maxX: FloatProperty(name='maxX')
    minY: FloatProperty(name='minY')
    maxY: FloatProperty(name='maxY')
    minZ: FloatProperty(name='minZ')
    maxZ: FloatProperty(name='maxZ')
    lenX: FloatProperty(name='lenX')
    lenY: FloatProperty(name='lenY')
    lenZ: FloatProperty(name='lenZ')

def declare_properies():
    bpy.types.Object.measure = PointerProperty(type=ObjectMeasurePropertyGroup)
    bpy.types.Scene.mesh_path = StringProperty(
        name='Mesh Path',
        default='',
        description='The path of mesh to be rendered',
        subtype='FILE_PATH'
    )
    bpy.types.Scene.mesh_dir = StringProperty(
        name='Mesh Dir',
        default='',
        description='The folder containing meshes to be rendered',
        subtype='DIR_PATH'
    )
    bpy.types.Scene.output_dir = StringProperty(
        name='Output Dir',
        default='',
        description='The folder where results are stored',
        subtype='DIR_PATH'
    )
    bpy.types.Scene.output_base_dir = StringProperty(
        name='Output Base Dir',
        default='',
        description='The folder where results are stored',
        subtype='DIR_PATH'
    )
    bpy.types.Scene.num_light = IntProperty(
        name='Light Number',
        default=100,
        description='The number of lights'
    )
    bpy.types.Scene.phi_min = IntProperty(
        name='Phi Min',
        default=0,
        min=0,
        max=90,
        description='The minimum \\phi'
    )
    bpy.types.Scene.phi_max = IntProperty(
        name='Phi Max',
        default=85,
        min=0,
        max=90,
        description='The maximum \\phi'
    )
    bpy.types.Scene.phi = FloatProperty(
        name='Phi',
        default=45,
        min=0,
        max=180,
        description='Angle of pitch'
    )
    bpy.types.Scene.theta = FloatProperty(
        name='Theta',
        default=0,
        min=-180,
        max=360,
        description='Azimuth'
    )

    def get_frame(self):
        return self.get('frame_custom', self.frame_current)
    def set_frame(self, value):
        frame_start, frame_end = get_frame_range_scene(self)
        if value > frame_end:
            value = frame_end
        self['frame_custom'] = value
        self.frame_current = value
    bpy.types.Scene.frame_custom = IntProperty(
        name='Current Frame',
        get=get_frame,
        set=set_frame,
        description='Current frame (DIY version)'
    )
    
    bpy.types.Scene.camera_phi = FloatProperty(
        name='Cam Phi',
        default=45,
        min=0,
        max=180,
        description='Angle of pitch'
    )
    bpy.types.Scene.camera_theta = FloatProperty(
        name='Cam Theta',
        default=0,
        min=-180,
        max=360,
        description='Azimuth'
    )
    
    bpy.types.Scene.image_path = StringProperty(
        name='Image Path',
        default='',
        description='The path of image to be imported as plane',
        subtype='FILE_PATH'
    )
    
    bpy.types.Scene.obj1 = PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.obj2 = PointerProperty(type=bpy.types.Object)
    
    ## Transformation
    bpy.types.Object.matrix_world_origin = FloatVectorProperty(
        name='Origin', 
        size=(4, 4),
        subtype='MATRIX'
    )
    bpy.types.Scene.rotation = FloatProperty(
        name='Rotation Angle',
        default=0,
        min=-180,
        max=360,
        description='Rotation angle in XY plane'
    )
    bpy.types.Scene.scale_z = FloatProperty(
        name='Z Scale',
        default=1,
        min=0,
        description='Z scale'
    )
    
    bpy.types.Scene.yaml_config_path = StringProperty(
        name='YAML Config Path',
        default='',
        subtype='FILE_PATH'
    )