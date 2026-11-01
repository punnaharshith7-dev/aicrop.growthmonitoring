"""
OpenCV & NumPy Image Preprocessing Pipeline for Crop Disease Detection.
Handles image loading, color-space transformations, aspect-preserving resizing,
pixel normalization, and agronomic vegetation diagnostics.
"""

import os
import cv2
import numpy as np
from PIL import Image


def load_image_cv2(image_path_or_bytes):
    """
    Load an image into an OpenCV BGR numpy array from either a file path
    or in-memory bytes/bytearray.
    Safely handles Unicode / non-ASCII file paths on Windows using np.fromfile.
    """
    if isinstance(image_path_or_bytes, (bytes, bytearray)):
        nparr = np.frombuffer(image_path_or_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif isinstance(image_path_or_bytes, str):
        if not os.path.exists(image_path_or_bytes):
            raise FileNotFoundError(f"Image file does not exist: {image_path_or_bytes}")
        # np.fromfile handles non-ASCII / Unicode paths on Windows where cv2.imread fails
        nparr = np.fromfile(image_path_or_bytes, dtype=np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        raise TypeError(f"Unsupported image input type: {type(image_path_or_bytes)}")

    if img is None:
        raise ValueError("Failed to decode image with OpenCV. File may be corrupted or unsupported format.")
    return img


def preprocess_image_cv2(image_path_or_bytes, target_size=(224, 224)):
    """
    Preprocess image for CNN model inference using OpenCV.

    Steps:
      1. Load BGR image with OpenCV.
      2. Convert BGR color space to RGB.
      3. Resize to target dimension (default 224x224) using high-quality interpolation.
      4. Normalize float32 values to range [0.0, 1.0].
      5. Expand dimensions to create 4D tensor (1, 224, 224, 3).

    Returns:
      tensor: np.ndarray of shape (1, target_size[0], target_size[1], 3), dtype float32
      diagnostics: dict containing resolution, channel count, brightness, and vegetation index.
    """
    img_bgr = load_image_cv2(image_path_or_bytes)
    orig_h, orig_w = img_bgr.shape[:2]

    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Calculate Agronomic Quality Diagnostics
    diagnostics = extract_leaf_diagnostics(img_rgb, orig_w, orig_h)

    # High-quality interpolation: cv2.INTER_AREA for downsampling, cv2.INTER_LINEAR for upsampling
    interp = cv2.INTER_AREA if (orig_h > target_size[0] or orig_w > target_size[1]) else cv2.INTER_LINEAR
    resized_rgb = cv2.resize(img_rgb, target_size, interpolation=interp)

    # Normalize to [0.0, 1.0]
    normalized = resized_rgb.astype(np.float32) / 255.0

    # Expand dims for batch: (1, 224, 224, 3)
    tensor = np.expand_dims(normalized, axis=0)

    return tensor, diagnostics


def extract_leaf_diagnostics(img_rgb, orig_w, orig_h):
    """
    Extract computer vision image statistics:
    - Width, Height, Channels
    - Mean Brightness & Contrast
    - Excess Green Index (ExG = 2*G - R - B) to measure vegetation presence
    """
    r = img_rgb[:, :, 0].astype(np.float32)
    g = img_rgb[:, :, 1].astype(np.float32)
    b = img_rgb[:, :, 2].astype(np.float32)

    mean_brightness = float(np.mean(img_rgb))
    contrast_std    = float(np.std(img_rgb))

    # Excess Green Index (ExG)
    exg = 2.0 * g - r - b
    mean_exg = float(np.mean(exg))
    is_vegetation = mean_exg > -10.0  # general threshold indicating plant matter

    return {
        'original_width': orig_w,
        'original_height': orig_h,
        'channels': 3,
        'mean_brightness': round(mean_brightness, 2),
        'contrast_std': round(contrast_std, 2),
        'excess_green_index': round(mean_exg, 2),
        'is_vegetation_detected': is_vegetation
    }


def preprocess_for_pytorch(image_path_or_bytes, target_size=(224, 224)):
    """
    Preprocess image for PyTorch model inference:
    Converts (1, H, W, C) to PyTorch channel-first format (1, C, H, W)
    with standard ImageNet mean and standard deviation normalization.
    """
    tensor, diag = preprocess_image_cv2(image_path_or_bytes, target_size)
    # Convert (1, H, W, C) -> (1, C, H, W)
    ch_first = np.transpose(tensor, (0, 3, 1, 2))

    # Standard ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
    std  = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)
    normalized_torch = (ch_first - mean) / std

    return normalized_torch.astype(np.float32), diag
