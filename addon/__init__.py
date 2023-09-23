# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "DynamicMVPSRenderer",
    "author" : "Fisher Wang",
    "description" : "",
    "blender" : (3, 3, 1),
    "version" : (0, 1, 0),
    "location" : "View3d",
    "warning" : "",
    "category" : "Generic"
}

import bpy

from .ImportMesh_Op import *
from .ImportMesh_Panel import *
# from .MeshMeasure_Op import *
from .Camera_Op import *
from .Camera_Panel import *
# from .AnimationControl_Panel import *
from .Output_Op import *
from .Output_Panel import *
# from .Light_Op import *
# from .Light_Panel import *
from .CircularLight_Op import *
from .CircularLight_Panel import *
from .Pipeline_Op import *
from .Pipeline_Panel import *
from .Setting_Panel import *
# from .ImagePlane_Op import *
# from .ImagePlane_Panel import *
# from .Transform_Op import *
# from .Transform_Panel import *
from .property import *

classes = (
    IMPORT_MESH_OT_ANY, 
    # MESH_OT_RESCALE,
    # MESH_OT_MEASURE,
    HELPER_PT_IMPORT_MESH,
    
    # MESH_OT_SET_ORIGIN,
    # MESH_OT_RESET,
    # MESH_OT_SET,
    # HELPER_PT_TRANSFORM,
    
    # SCENE_OT_IMPORT_IMAGE_PLANE,
    # SCENE_OT_SWITCH_VISIBILITY,
    # HELPER_PT_IMPORT_PLANE_IMAGE,
    
    CAMERA_OT_ADD_ORTHOGRAPHIC,
    CAMERA_OT_SET_POSITION,
    CAMERA_OT_SET_POSITION_FROM_MATRIX,
    HELPER_PT_CAMERA,
    HELPER_PT_CAMERA_POSE,
    
    # HELPER_PT_ANIMATION_CONTROL,
    
    # RENDER_OT_SET_LIGHT_DIRECTION,
    # RENDER_OT_MULTI_LIGHT,
    # HELPER_PT_LIGHT,
    
    HELPER_PT_CIRCULAR_LIGHT,
    RENDER_OT_CIRCULAR_LIGHT,
    RENDER_OT_PIPELINE_CIRCULAR_LIGHT,
    RENDER_OT_PIPELINE_CIRCULAR_LIGHT_2,
    
    # RENDER_OT_HIDE_OTHERS,
    # SCENE_OT_EXPORT_NORMAL,
    SCENE_OT_EXPORT_IMAGE,
    # SCENE_OT_EXPORT_ALBEDO,
    HELPER_PT_OUTPUT,
    
    RENDER_OT_PIPELINE,
    HELPER_PT_PIPELINE,
    # RENDER_OT_PIPELINE_COLORPSNERF,
    
    HELPER_PT_RENDER_SETTING,

    ObjectMeasurePropertyGroup,
    OutputRenderPassPropertyGroup,
)

def register():
    for c in classes:
        print(c)
        bpy.utils.register_class(c)
    
    from .property import declare_properies
    declare_properies()

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
