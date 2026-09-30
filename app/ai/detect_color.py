from PIL import Image
import numpy as np


def detect_color(image_path):

    image = Image.open(image_path)

    image = image.convert("RGB")

    image = image.resize((100,100))

    pixels = np.array(image)

    avg = pixels.mean(axis=(0,1))

    r,g,b = avg

    if r > 180 and g > 140 and b < 120:
        color = "Gold"

    elif r < 60 and g < 60 and b < 60:
        color = "Black"

    elif r > 180 and g > 180 and b > 180:
        color = "White"

    elif b > r and b > g:
        color = "Blue"

    elif g > r and g > b:
        color = "Green"

    elif r > g and r > b:
        color = "Red"

    else:
        color = "Grey"

    return {
        "detected_color": color
    }