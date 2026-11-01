"""
Dataset Utilities for AI Crop Disease Detection.
Handles dataset preparation, download guidelines for PlantVillage/Kaggle,
and synthetic foliage image generation for training pipeline testing.
"""

import os
import sys
import argparse
import numpy as np
import cv2

# Reconfigure stdout/stderr for UTF-8 on Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from ml.disease_detection.model import MODEL_CLASSES


def create_sample_leaf_image(class_name, width=224, height=224):
    """
    Generate a synthetic leaf pattern using OpenCV and NumPy for pipeline testing.
    Simulates leaf base color, veining, and specific pathology patterns.
    """
    # Base background (soil/dark canvas)
    img = np.full((height, width, 3), (35, 45, 30), dtype=np.uint8)

    # Leaf contour points (elliptical leaf shape)
    center = (width // 2, height // 2)
    axes = (int(width * 0.42), int(height * 0.45))
    angle = 15

    # Healthy leaf base color: vibrant green in BGR
    is_healthy = 'healthy' in class_name.lower()
    base_color = (45, 160, 40) if is_healthy else (35, 125, 45)

    # Draw leaf body
    cv2.ellipse(img, center, axes, angle, 0, 360, base_color, -1)

    # Draw central midrib vein
    pt1 = (width // 2 - 40, height - 20)
    pt2 = (width // 2 + 35, 20)
    cv2.line(img, pt1, pt2, (60, 180, 55), 2)

    # Draw side veins
    for offset in range(-60, 70, 25):
        v1 = (width // 2 + offset // 2, height // 2 + offset)
        v2 = (width // 2 + offset, height // 2 + offset - 20)
        cv2.line(img, v1, v2, (55, 170, 50), 1)

    # Inject specific pathology signatures if diseased
    if not is_healthy:
        np.random.seed(abs(hash(class_name)) % (2**31))

        if 'blight' in class_name.lower():
            # Concentric dark necrotic spots (Early/Late Blight)
            for _ in range(np.random.randint(4, 9)):
                cx = np.random.randint(int(width * 0.25), int(width * 0.75))
                cy = np.random.randint(int(height * 0.25), int(height * 0.75))
                radius = np.random.randint(12, 28)
                # Outer yellow halo
                cv2.circle(img, (cx, cy), radius + 6, (30, 200, 210), -1)
                # Middle brown ring
                cv2.circle(img, (cx, cy), radius, (20, 50, 110), -1)
                # Inner dark center
                cv2.circle(img, (cx, cy), radius // 2, (10, 25, 45), -1)

        elif 'rust' in class_name.lower():
            # Powdery orange/yellow rust pustules
            for _ in range(np.random.randint(15, 30)):
                rx = np.random.randint(int(width * 0.2), int(width * 0.8))
                ry = np.random.randint(int(height * 0.2), int(height * 0.8))
                # Orange/yellow pustule dots in BGR
                cv2.circle(img, (rx, ry), np.random.randint(2, 6), (15, 140, 230), -1)

        elif 'spot' in class_name.lower():
            # Brown leaf spots
            for _ in range(np.random.randint(8, 16)):
                sx = np.random.randint(int(width * 0.25), int(width * 0.75))
                sy = np.random.randint(int(height * 0.25), int(height * 0.75))
                cv2.circle(img, (sx, sy), np.random.randint(4, 10), (25, 60, 90), -1)

        elif 'virus' in class_name.lower() or 'mosaic' in class_name.lower():
            # Chlorotic yellow mottled mosaic patches
            for _ in range(np.random.randint(6, 12)):
                mx = np.random.randint(int(width * 0.3), int(width * 0.7))
                my = np.random.randint(int(height * 0.3), int(height * 0.7))
                cv2.ellipse(img, (mx, my), (20, 12), np.random.randint(0, 180), 0, 360, (50, 220, 210), -1)

    # Slight Gaussian blur to simulate camera focus
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return img


def create_sample_dataset(output_dir='ml/datasets/crop_disease', samples_per_class=12):
    """
    Generate synthetic sample images for every supported crop disease and healthy class.
    Enables testing and verifying the entire CNN training pipeline locally.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating sample dataset in: {output_dir}")
    print(f"Classes: {len(MODEL_CLASSES)} | Samples per class: {samples_per_class}")

    total_images = 0
    for cls_name in MODEL_CLASSES:
        class_folder = os.path.join(output_dir, cls_name)
        os.makedirs(class_folder, exist_ok=True)

        for idx in range(1, samples_per_class + 1):
            img = create_sample_leaf_image(cls_name)
            filename = f"sample_{cls_name.lower()}_{idx:03d}.jpg"
            filepath = os.path.join(class_folder, filename)
            cv2.imwrite(filepath, img)
            total_images += 1

    print(f"[SUCCESS] Generated {total_images} sample leaf images across {len(MODEL_CLASSES)} classes.")
    return output_dir


def print_dataset_instructions():
    """Print agronomic dataset acquisition and structure guidelines."""
    print("""
================================================================================
AI CROP DISEASE DETECTION — DATASET GUIDE
================================================================================
The AI Crop Disease Vision Model classifies foliar diseases and healthy leaves.

1. RECOMMENDED PUBLIC DATASETS:
   - PlantVillage Dataset (54,306 images across 38 crop disease classes)
     Source: https://www.kaggle.com/datasets/emmarex/plantdisease
     GitHub: https://github.com/spMohanty/PlantVillage-Dataset

   - Rice Leaf Disease Dataset
     Source: https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases

   - Wheat Rust & Fungal Pathology Dataset
     Source: Global Rust Reference Center (GRRC) / CGIAR Agronomy

2. DIRECTORY STRUCTURE:
   Extract and organize your images under:
     ml/datasets/crop_disease/
       ├── Tomato_Early_Blight/
       │     ├── leaf_001.jpg
       │     └── leaf_002.jpg
       ├── Tomato_Late_Blight/
       ├── Tomato_Healthy/
       ├── Corn_Common_Rust/
       ├── Corn_Healthy/
       └── ... (matching class names in MODEL_CLASSES)

3. FAST PIPELINE VERIFICATION:
   To test the complete CNN training pipeline without downloading large datasets:
     python ml/disease_detection/dataset.py --create_samples
     python ml/disease_detection/train.py --epochs 3
================================================================================
""")


def main():
    parser = argparse.ArgumentParser(description="AI Crop Disease Dataset Utility")
    parser.add_argument('--create_samples', action='store_true',
                        help='Generate synthetic leaf imagery for pipeline testing')
    parser.add_argument('--samples_per_class', type=int, default=12,
                        help='Number of synthetic samples per class')
    parser.add_argument('--output_dir', type=str, default='ml/datasets/crop_disease',
                        help='Output directory for dataset')
    args = parser.parse_args()

    if args.create_samples:
        create_sample_dataset(args.output_dir, args.samples_per_class)
    else:
        print_dataset_instructions()


if __name__ == '__main__':
    main()
