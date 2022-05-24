from mss import mss
from PIL import Image
import numpy as np
import pyautogui

sct = mss()
def screenshot(left, top, width, height):
    if width * height < 1286000:
        mon = {'left': left, 'top': top, 'width': width, 'height': height}
        screenShot = sct.grab(mon)
        img = np.array(Image.frombytes(
            'RGB', 
            (screenShot.width, screenShot.height), 
            screenShot.rgb, 
        ))
    else:
        img = np.array(pyautogui.screenshot())[left:left+width, top:top+height]

    return img