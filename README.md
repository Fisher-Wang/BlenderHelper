# Render Helper

### How to install

#### Step 1: Locate your blender python
On windows, it is usualy somewhere like `C:\Program Files\Blender Foundation\Blender 3.3\3.3\python\bin\python.exe`

#### Step 2: Install the pre-required packages
On windows, make sure you are doing the following commands with Administrative Permission. 

Using the blender python, run 
```
<blender python> -m pip install <packages>
```

The packages are:
- numpy
- PyYAML
- scipy
- matplotlib
- OpenEXR
- scikit-image
- opencv-python

If the pip is not installed, run
```
<blender python> -m ensurepip
```
and try again. 

One may encounter the case that the packages are succesfully installed, and can be found in `pip list`, but still got `No module named xxx` error in Blender python. That is probably because the installation path is wrong. All the packages should be installed somewhere like `python -m ensurepip
python -m pip install --upgrade pip` so as to be found by Blender. To solve this problem simply add the following flag and try again.
```
--target "C:\Program Files\Blender Foundation\Blender 3.3\3.3\python\lib\site-packages"
```

#### Step 3: Locate your blender addon folder
On windows, it is usually somewhere like `C:\Users\<user name>\AppData\Roaming\Blender Foundation\Blender\3.3\scripts\addons`

Or you can run `bpy.utils.user_resource('SCRIPTS', path="addons")` to get the location. 

#### Step 4: Add this addon
Open up the folder you found in Step 3, then copy the `addon` directory to that folder. Launch blender, and you will see the addon panel, in Layout - Side bar - MVPSRenderHelper, like this. 
![success](imgs\addon_UI_success.png)