import scipy.misc, numpy as np, os, sys
import imageio
from PIL import Image

def save_img(out_path, img):
    img = np.clip(img, 0, 255).astype(np.uint8)
    imageio.imwrite(out_path, img)

def get_img(src, img_size=None):
   img = imageio.imread(src, pilmode='RGB')
   if not (len(img.shape) == 3 and img.shape[2] == 3):
       img = np.dstack((img,img,img))
   if img_size:
       img = np.array(Image.fromarray(img).resize(img_size[:2]))
   return img

def exists(p, msg):
    assert os.path.exists(p), msg

def list_files(in_path):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(in_path):
        files.extend(filenames)
        break

    return files
