"""
CNN Model Architectures for AI Crop Disease Detection.
Provides deep convolutional neural network implementations in TensorFlow/Keras
and PyTorch, supporting both custom CNNs and transfer learning backbones.
"""

import json
import os

# Standard 23 agronomic classes matching PlantVillage & Crop Disease Benchmarks
MODEL_CLASSES = [
    'Tomato_Early_Blight',
    'Tomato_Late_Blight',
    'Tomato_Leaf_Mold',
    'Tomato_Septoria_Leaf_Spot',
    'Tomato_Spider_Mites',
    'Tomato_Target_Spot',
    'Tomato_Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato_Tomato_Mosaic_Virus',
    'Tomato_Healthy',
    'Potato_Early_Blight',
    'Potato_Late_Blight',
    'Potato_Healthy',
    'Corn_Common_Rust',
    'Corn_Gray_Leaf_Spot',
    'Corn_Northern_Leaf_Blight',
    'Corn_Healthy',
    'Rice_Bacterial_Leaf_Blight',
    'Rice_Blast',
    'Rice_Brown_Spot',
    'Rice_Healthy',
    'Wheat_Yellow_Rust',
    'Wheat_Leaf_Rust',
    'Wheat_Healthy',
]


def save_class_indices(output_path, class_list=None):
    """Save class name mapping to a JSON file."""
    if class_list is None:
        class_list = MODEL_CLASSES
    mapping = {idx: name for idx, name in enumerate(class_list)}
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    return mapping


def load_class_indices(json_path):
    """Load class name mapping from JSON file."""
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
            # Ensure keys are integers
            return {int(k): v for k, v in raw.items()}
    return {idx: name for idx, name in enumerate(MODEL_CLASSES)}


# ──────────────────────────────────────────────────────────────────────────────
# TensorFlow / Keras Architecture
# ──────────────────────────────────────────────────────────────────────────────
def build_keras_cnn(num_classes=len(MODEL_CLASSES), input_shape=(224, 224, 3)):
    """
    Build a deep CNN model using TensorFlow/Keras with batch normalization,
    dropout regularization, and global average pooling to minimize overfitting.
    """
    import tensorflow as tf
    from tensorflow.keras import layers, models

    model = models.Sequential([
        # Block 1
        layers.Input(shape=input_shape),
        layers.Conv2D(32, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.Conv2D(32, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2),

        # Block 2
        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        # Block 3
        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.3),

        # Block 4
        layers.Conv2D(256, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.35),

        # Dense Classifier Head
        layers.GlobalAveragePooling2D(),
        layers.Dense(256),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax', name='disease_prediction')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def build_mobilenet_v2_model(num_classes=len(MODEL_CLASSES), input_shape=(224, 224, 3)):
    """
    Build a lightweight Transfer Learning CNN using MobileNetV2 pre-trained on ImageNet.
    Ideal for real-time mobile and edge agricultural telemetry.
    """
    import tensorflow as tf
    from tensorflow.keras import layers, models
    from tensorflow.keras.applications import MobileNetV2

    base_model = MobileNetV2(input_shape=input_shape, include_top=False, weights='imagenet')
    base_model.trainable = False  # Freeze base weights initially

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


# ──────────────────────────────────────────────────────────────────────────────
# PyTorch Architecture (Native Python 3.13 Compatible)
# ──────────────────────────────────────────────────────────────────────────────
def build_pytorch_cnn(num_classes=len(MODEL_CLASSES)):
    """
    Build a PyTorch CNN model for crop leaf disease detection.
    Compatible with Python 3.13 environments where PyTorch is installed.
    """
    import torch
    import torch.nn as nn

    class CropDiseasePyTorchCNN(nn.Module):
        def __init__(self, num_classes):
            super().__init__()
            self.features = nn.Sequential(
                # Block 1: 3 -> 32
                nn.Conv2d(3, 32, kernel_size=3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(inplace=True),
                nn.Conv2d(32, 32, kernel_size=3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2, 2),
                nn.Dropout(0.2),

                # Block 2: 32 -> 64
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(inplace=True),
                nn.Conv2d(64, 64, kernel_size=3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2, 2),
                nn.Dropout(0.25),

                # Block 3: 64 -> 128
                nn.Conv2d(64, 128, kernel_size=3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.Conv2d(128, 128, kernel_size=3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2, 2),
                nn.Dropout(0.3),

                # Block 4: 128 -> 256
                nn.Conv2d(128, 256, kernel_size=3, padding=1),
                nn.BatchNorm2d(256),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2, 2),
                nn.Dropout(0.35),
            )
            self.pool = nn.AdaptiveAvgPool2d((1, 1))
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(256, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(inplace=True),
                nn.Dropout(0.5),
                nn.Linear(256, num_classes)
            )

        def forward(self, x):
            x = self.features(x)
            x = self.pool(x)
            x = self.classifier(x)
            return x

    return CropDiseasePyTorchCNN(num_classes)

