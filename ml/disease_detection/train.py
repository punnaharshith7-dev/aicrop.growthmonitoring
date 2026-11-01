"""
AI Crop Disease Detection — Model Training Pipeline.
Supports TensorFlow/Keras and PyTorch backends, data augmentation,
learning rate scheduling, model checkpointing, evaluation, and ONNX export.
"""

import os
import sys
import argparse
import json
import numpy as np

# Reconfigure stdout/stderr for UTF-8 on Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is accessible
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.disease_detection.model import (
    MODEL_CLASSES, build_keras_cnn, build_mobilenet_v2_model,
    build_pytorch_cnn, save_class_indices
)


def train_keras(data_dir, output_path, epochs=25, batch_size=32, img_size=(224, 224),
                learning_rate=1e-3, architecture='custom_cnn'):
    """
    Train a CNN using TensorFlow/Keras with ImageDataGenerator data augmentation.
    """
    import tensorflow as tf
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

    print(f"\n==================================================")
    print(f"Starting Keras Training Pipeline")
    print(f"Architecture: {architecture} | Epochs: {epochs} | Batch: {batch_size}")
    print(f"Dataset: {data_dir}")
    print(f"Target Output: {output_path}")
    print(f"==================================================\n")

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        fill_mode='nearest',
        validation_split=0.2
    )

    print("Loading training dataset...")
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )

    print("Loading validation dataset...")
    val_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )

    num_classes = train_generator.num_classes
    class_indices = train_generator.class_indices
    # Invert mapping: {index: class_name}
    index_to_class = {v: k for k, v in class_indices.items()}
    mapping_path = os.path.join(os.path.dirname(output_path), 'class_indices.json')
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(index_to_class, f, indent=2)
    print(f"Saved class index mapping ({num_classes} classes) to {mapping_path}")

    # Build model
    if architecture == 'mobilenet':
        model = build_mobilenet_v2_model(num_classes=num_classes, input_shape=(img_size[0], img_size[1], 3))
    else:
        model = build_keras_cnn(num_classes=num_classes, input_shape=(img_size[0], img_size[1], 3))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    callbacks = [
        ModelCheckpoint(
            output_path,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=7,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.3,
            patience=3,
            min_lr=1e-6,
            verbose=1
        )
    ]

    history = model.fit(
        train_generator,
        epochs=epochs,
        validation_data=val_generator,
        callbacks=callbacks
    )

    print(f"\n[SUCCESS] Model training complete. Best model saved to: {output_path}")
    return model, history


def train_pytorch(data_dir, output_path, epochs=15, batch_size=32, img_size=(224, 224),
                  learning_rate=1e-3):
    """
    Train a CNN using PyTorch with standard DataLoader and transforms.
    Runs in Python 3.13 where PyTorch is installed.
    """
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, random_split
    from torchvision import datasets, transforms

    print(f"\n==================================================")
    print(f"Starting PyTorch Training Pipeline")
    print(f"Epochs: {epochs} | Batch: {batch_size} | LR: {learning_rate}")
    print(f"Dataset: {data_dir}")
    print(f"Output: {output_path}")
    print(f"==================================================\n")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using compute device: {device}")

    transform_train = transforms.Compose([
        transforms.Resize(img_size),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    transform_val = transforms.Compose([
        transforms.Resize(img_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    full_dataset = datasets.ImageFolder(root=data_dir, transform=transform_train)
    num_classes = len(full_dataset.classes)
    class_names = full_dataset.classes

    mapping_path = os.path.join(os.path.dirname(output_path), 'class_indices.json')
    save_class_indices(mapping_path, class_names)
    print(f"Saved class index mapping ({num_classes} classes) to {mapping_path}")

    # 80/20 train/val split
    val_size = int(0.2 * len(full_dataset))
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, num_workers=0)

    model = build_pytorch_cnn(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)

    best_val_acc = 0.0
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        train_loss = running_loss / total
        train_acc  = 100.0 * correct / total

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                val_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                val_total += targets.size(0)
                val_correct += predicted.eq(targets).sum().item()

        val_loss = val_loss / val_total
        val_acc  = 100.0 * val_correct / val_total
        scheduler.step(val_loss)

        print(f"Epoch [{epoch:02d}/{epochs:02d}] "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), output_path)
            print(f"  -> Saved new best checkpoint (Val Acc: {val_acc:.2f}%) to {output_path}")

    # Export to ONNX for universal lightweight deployment
    onnx_path = os.path.splitext(output_path)[0] + '.onnx'
    try:
        dummy_input = torch.randn(1, 3, img_size[0], img_size[1], device=device)
        torch.onnx.export(
            model,
            dummy_input,
            onnx_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=['input_image'],
            output_names=['class_probabilities'],
            dynamic_axes={'input_image': {0: 'batch_size'}, 'class_probabilities': {0: 'batch_size'}}
        )
        print(f"[ONNX Export] Successfully exported OpenCV DNN-compatible model: {onnx_path}")
    except Exception as e:
        print(f"[Note] ONNX export skipped: {e}")

    print(f"\n[SUCCESS] PyTorch training complete. Best Val Accuracy: {best_val_acc:.2f}%")
    return model


def main():
    parser = argparse.ArgumentParser(description="Train AI Crop Disease Detection CNN Model")
    parser.add_argument('--data_dir', type=str, default='ml/datasets/crop_disease',
                        help='Path to dataset directory organized into class subfolders')
    parser.add_argument('--output', type=str,
                        default=os.path.join(CURRENT_DIR, 'disease_model.h5'),
                        help='Path to save the trained model file')
    parser.add_argument('--framework', type=str, choices=['keras', 'pytorch'], default='auto',
                        help='Deep learning framework (keras, pytorch, or auto-detect)')
    parser.add_argument('--architecture', type=str, choices=['custom_cnn', 'mobilenet'], default='custom_cnn',
                        help='CNN Architecture type')
    parser.add_argument('--epochs', type=int, default=15, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Mini-batch size')
    parser.add_argument('--lr', type=float, default=1e-3, help='Initial learning rate')
    parser.add_argument('--create_sample_data', action='store_true',
                        help='Generate synthetic leaf samples for pipeline verification if dataset is unavailable')
    args = parser.parse_args()

    # Verify dataset existence
    if not os.path.exists(args.data_dir) or not os.listdir(args.data_dir):
        if args.create_sample_data:
            from ml.disease_detection.dataset import create_sample_dataset
            print(f"Dataset directory '{args.data_dir}' not found. Generating sample training data...")
            create_sample_dataset(args.data_dir)
        else:
            print("\n" + "="*70)
            print("⚠ DATASET NOT FOUND")
            print("="*70)
            print(f"No image dataset was found in: '{args.data_dir}'")
            print("\nTo train the AI Crop Disease Vision Model, follow these steps:")
            print("1. Download the PlantVillage or Kaggle Crop Disease dataset.")
            print("2. Extract the dataset folder into 'ml/datasets/crop_disease/'")
            print("   Expected directory structure:")
            print("     ml/datasets/crop_disease/")
            print("       ├── Tomato_Early_Blight/")
            print("       │     ├── leaf_001.jpg")
            print("       ├── Tomato_Healthy/")
            print("       │     ├── leaf_002.jpg")
            print("       └── ...")
            print("\n3. Or quickly run the training pipeline with sample benchmark images:")
            print("   python ml/disease_detection/train.py --create_sample_data --epochs 3")
            print("="*70 + "\n")
            sys.exit(0)

    # Framework selection
    framework = args.framework
    if framework == 'auto':
        try:
            import tensorflow
            framework = 'keras'
        except ImportError:
            try:
                import torch
                framework = 'pytorch'
            except ImportError:
                print("Error: Neither TensorFlow nor PyTorch is installed in this Python environment.")
                sys.exit(1)

    print(f"Selected Framework: {framework}")

    if framework == 'keras':
        train_keras(
            data_dir=args.data_dir,
            output_path=args.output,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
            architecture=args.architecture
        )
    else:
        pytorch_output = os.path.splitext(args.output)[0] + '.pth'
        train_pytorch(
            data_dir=args.data_dir,
            output_path=pytorch_output,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr
        )


if __name__ == '__main__':
    main()
