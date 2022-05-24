from mss import mss
from PIL import Image
import numpy as np

sct = mss()
def screenshot(left, top, width, height):
    mon = {'left': left, 'top': top, 'width': width, 'height': height}
    screenShot = sct.grab(mon)
    img = np.array(Image.frombytes(
        'RGB', 
        (screenShot.width, screenShot.height), 
        screenShot.rgb, 
    ))

    return img