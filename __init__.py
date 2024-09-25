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
    "version" : (0, 0, 1),
    "location" : "View3d",
    "warning" : "",
    "category" : "Generic"
}

import bpy

from .ImportMesh_Op import *
from .ImportMesh_Panel import *
from .Camera_Op import *
from .Camera_Panel import *
from .property import ObjectMeasurePropertyGroup

classes = (
    IMPORT_MESH_OT_ANY, 
    HELPER_PT_IMPORT_MESH,
    CAMERA_OT_ADD_ORTHOGRAPHIC,
    HELPER_PT_CAMERA,
    
    ObjectMeasurePropertyGroup,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    from .property import declare_properies
    declare_properies()

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
