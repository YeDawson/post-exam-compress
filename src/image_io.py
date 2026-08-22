from PIL import Image
import numpy as np

def load_grayscale(path):
    # replace with Image.open(path).conver("RGB")
    image = Image.open(path).convert("L")
    return np.array

def save_grayscale(matrix, path):
    matrix = np.clip(matrix, 0, 255)
    matrix = matrix.astype(np.uint8)
