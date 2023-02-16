import os
import yaml
import numpy as np
from skimage import img_as_bool
from PIL import Image
from typing import List
from os.path import join as pjoin
from os.path import exists as pexists

def mkdir(p, exist_ok=True):
    os.makedirs(p, exist_ok=exist_ok)
    return p

def nmap_for_show(nmap):
    return ((nmap+1) / 2 * 255).astype('uint8')

def read_yaml(path):
    with open(path) as f:
        data = yaml.load(f, Loader=yaml.Loader)
    return data

def write_mask(path, mask):
    if mask.dtype != np.bool_:
        print('[WARN] Input mask is not boolean, converting...')
        mask = img_as_bool(mask)
    image = Image.fromarray(mask)
    image.save(path, bits=1, optimize=True)

def write_txt(path, l: List[str], sep='\n'):
    with open(path, 'w+') as f:
        f.write(sep.join(l))

def read_yaml(path):
    with open(path) as f:
        data = yaml.load(f, Loader=yaml.Loader)
    return data

def write_yaml(path, data):
    with open(path, 'w+') as f:
        yaml.dump(data, f, default_flow_style=False)

def list_subtract(l1, l2):
    '''
    return `l1 - l2`
    '''
    return [x for x in l1 if x not in l2]

def make_batch(l, batch_size):
    nBatch = (len(l) + batch_size - 1) // batch_size
    return [l[i*batch_size:(i+1)*batch_size] for i in range(nBatch)]

def make_even_stops(nTot, nGroup, inverse=False):
    '''
    Examples
    --------
    >>> make_even_stops(5, 2)
    [3, 2]
    >>> make_even_stops(10, 3)
    [4, 7, 10]
    '''
    k, m = divmod(nTot, nGroup)
    rst = [0] + [(i+1)*k + min(i+1, m) for i in range(nGroup)]
    if inverse:
        rst = np.array(rst)
        rst = nTot - rst
        rst = rst[::-1]
        rst = rst.tolist()
    return rst