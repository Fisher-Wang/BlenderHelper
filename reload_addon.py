## Reference: 
# - https://github.com/JacquesLucke/blender_vscode/blob/HEAD/pythonFiles/include/blender_vscode/load_addons.py
# - https://github.com/JacquesLucke/blender_vscode/blob/HEAD/pythonFiles/include/blender_vscode/operators/addon_update.py

import bpy

import os
from os.path import join as pjoin
import sys
import zipfile

ADDON_NAME = 'addon'
cur_dir = os.path.dirname(bpy.context.space_data.text.filepath)

def zip_addon():
    # Remove old zip
    zip_path = pjoin(cur_dir, f'{ADDON_NAME}.zip')
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    # Zip all *.py files
    zf = zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_STORED)
    for root, dirs, files in os.walk('addon'):
        zf.write(root)
        for file in files:
            if file.endswith('.py'):
                zf.write(pjoin(root, file))
    zf.close()

def create_link_in_user_addon_directory(directory, link_path):
    if os.path.exists(link_path):
        os.remove(link_path)

    if sys.platform == "win32":
        import _winapi
        _winapi.CreateJunction(str(directory), str(link_path))
    else:
        os.symlink(str(directory), str(link_path), target_is_directory=True)

if __name__ == '__main__':    
    # Choice 1: Install addon (zip)
    # Sometimes it fails without any reason.
    # zip_addon()
    # bpy.ops.preferences.addon_install(filepath=pjoin(cur_dir, f'{ADDON_NAME}.zip'))
    
    # Choice 2: Install addon (soft link)
    user_addon_directory = bpy.utils.user_resource('SCRIPTS', path="addons")
    load_path = pjoin(user_addon_directory, ADDON_NAME)
    source_path = pjoin(cur_dir, 'addon')
    create_link_in_user_addon_directory(source_path, load_path)
    
    # Disable addon
    bpy.ops.preferences.addon_disable(module=ADDON_NAME)
    for name in list(sys.modules.keys()):
        if name.startswith(ADDON_NAME):
            del sys.modules[name]
    
    # Reload addon
    bpy.ops.preferences.addon_enable(module=ADDON_NAME)
    