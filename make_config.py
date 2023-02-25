import os
import numpy as np
from utils import write_txt, read_yaml, make_even_stops

blender = 'blender3'
mesh_dir = 'plane'
result_dir = 'result_20230216'
conf = 'template_new.yaml'
nLight = 100
nProcess = 8

nObjs = len(read_yaml(conf)['shape_names'])

iObj = make_even_stops(nObjs, nProcess)
print(iObj)

gpus = os.environ['CUDA_VISIBLE_DEVICES'].split(',') if 'CUDA_VISIBLE_DEVICES' in os.environ else ['0']
nGPU = len(gpus)
tmp = make_even_stops(nProcess, nGPU, inverse=True)
iGPU = np.zeros(nProcess, dtype=int)
for i in range(len(tmp)-1):
    iGPU[tmp[i]:tmp[i+1]] = i
print(iGPU)

lines = [
    f'{blender} -d -b -P reload_addon.py',
]
for i in range(nProcess):
    start = iObj[i]
    end = iObj[i+1]
    gpu = gpus[iGPU[i]]
    
    lines.append(f"tmux new -d -s {i+1} \"CUDA_VISIBLE_DEVICES={gpu} {blender} -d -b -P render.py -- --mesh_dir {mesh_dir} -n {nLight} -r {result_dir} -i {i+1} -c {conf} -s {start} -e {end}\"")

write_txt('config.sh', lines)

## Config for exr2png.py
nProcess = nObjs
nObjs = len(read_yaml(conf)['shape_names'])
iObj = make_even_stops(nObjs, nProcess)

lines = []
for i in range(nProcess):
    start = iObj[i]
    end = iObj[i+1]
    
    lines.append(f"tmux new -d -s exr_{i+1:02d} \"python exr2png.py -c template_new.yaml -d {result_dir} -n {nLight} -c {conf} -s {start} -e {end}\"")

write_txt('config_exr2png.sh', lines)