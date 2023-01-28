import bpy
from .utils import *

#############################
## Self-Defined Properties
#############################

class ObjectMeasurePropertyGroup(bpy.types.PropertyGroup):
    minX: bpy.props.FloatProperty(name='minX')
    maxX: bpy.props.FloatProperty(name='maxX')
    minY: bpy.props.FloatProperty(name='minY')
    maxY: bpy.props.FloatProperty(name='maxY')
    minZ: bpy.props.FloatProperty(name='minZ')
    maxZ: bpy.props.FloatProperty(name='maxZ')
    lenX: bpy.props.FloatProperty(name='lenX')
    lenY: bpy.props.FloatProperty(name='lenY')
    lenZ: bpy.props.FloatProperty(name='lenZ')

def declare_properies():
    bpy.types.Object.measure = bpy.props.PointerProperty(type=ObjectMeasurePropertyGroup)
    bpy.types.Scene.mesh_path = bpy.props.StringProperty(
        name='Mesh Path',
        default='',
        description='The path of mesh to be rendered',
        subtype='FILE_PATH'
    )
    bpy.types.Scene.mesh_dir = bpy.props.StringProperty(
        name='Mesh Dir',
        default='',
        description='The folder containing meshes to be rendered',
        subtype='DIR_PATH'
    )
    bpy.types.Scene.output_dir = bpy.props.StringProperty(
        name='Output Dir',
        default='',
        description='The folder where results are stored',
        subtype='DIR_PATH'
    )
    bpy.types.Scene.output_base_dir = bpy.props.StringProperty(
        name='Output Base Dir',
        default='',
        description='The folder where results are stored',
        subtype='DIR_PATH'
    )
    bpy.types.Scene.num_light = bpy.props.IntProperty(
        name='Light Number',
        default=100,
        description='The number of lights'
    )
    bpy.types.Scene.phi_min = bpy.props.IntProperty(
        name='Phi Min',
        default=0,
        min=0,
        max=90,
        description='The minimum \\phi'
    )
    bpy.types.Scene.phi_max = bpy.props.IntProperty(
        name='Phi Max',
        default=85,
        min=0,
        max=90,
        description='The maximum \\phi'
    )
    bpy.types.Scene.phi = bpy.props.FloatProperty(
        name='Phi',
        default=45,
        min=0,
        max=180,
        description='Angle of pitch'
    )
    bpy.types.Scene.theta = bpy.props.FloatProperty(
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
    bpy.types.Scene.frame_custom = bpy.props.IntProperty(
        name='Current Frame',
        get=get_frame,
        set=set_frame,
        description='Current frame (DIY version)'
    )
    
    bpy.types.Scene.camera_phi = bpy.props.FloatProperty(
        name='Cam Phi',
        default=45,
        min=0,
        max=180,
        description='Angle of pitch'
    )
    bpy.types.Scene.camera_theta = bpy.props.FloatProperty(
        name='Cam Theta',
        default=0,
        min=-180,
        max=360,
        description='Azimuth'
    )