# AI Crop Disease Detection Module

Deep Learning computer vision system for identifying foliar plant pathologies and classifying healthy leaf tissue using **Python**, **OpenCV**, and **TensorFlow / Keras / PyTorch**.

---

## 📌 Architecture & Modules

```
ml/disease_detection/
├── disease_db.py          # Agronomic knowledge base (symptoms, precautions, organic & chemical treatments)
├── preprocess.py          # OpenCV image loading, color-space conversion, resizing, normalization
├── model.py               # CNN classification architectures (Deep Custom CNN, MobileNetV2, PyTorch CNN)
├── train.py               # Complete training pipeline with augmentation, callbacks, and evaluation
├── dataset.py             # Dataset downloader and synthetic leaf image generator for pipeline tests
├── class_indices.json     # Class-to-index mapping for model inference
└── README.md              # Pipeline documentation
```

---

## 🌿 Supported Diagnostic Classes (23 Classes)

### **Tomato**
- Early Blight (*Alternaria solani*)
- Late Blight (*Phytophthora infestans*)
- Leaf Mold (*Passalora fulva*)
- Septoria Leaf Spot (*Septoria lycopersici*)
- Spider Mites (*Tetranychus urticae*)
- Target Spot (*Corynespora cassiicola*)
- Yellow Leaf Curl Virus (*TYLCV*)
- Mosaic Virus (*ToMV*)
- **Tomato Healthy Foliage**

### **Potato**
- Early Blight (*Alternaria solani*)
- Late Blight (*Phytophthora infestans*)
- **Potato Healthy Foliage**

### **Corn (Maize)**
- Common Rust (*Puccinia sorghi*)
- Northern Leaf Blight (*Exserohilum turcicum*)
- Gray Leaf Spot (*Cercospora zeae-maydis*)
- **Corn Healthy Foliage**

### **Rice**
- Bacterial Leaf Blight (*Xanthomonas oryzae*)
- Blast (*Magnaporthe oryzae*)
- Brown Spot (*Bipolaris oryzae*)
- **Rice Healthy Foliage**

### **Wheat**
- Stripe / Yellow Rust (*Puccinia striiformis*)
- Brown / Leaf Rust (*Puccinia triticina*)
- **Wheat Healthy Foliage**

---

## 🚀 Quick Start: Training the CNN Model

### 1. Download or Generate Dataset
To quickly test the training pipeline with synthetic agronomic samples:
```bash
python ml/disease_detection/dataset.py --create_samples
```
Or place your real PlantVillage / Kaggle images in `ml/datasets/crop_disease/<class_name>/`.

### 2. Run Training Pipeline
```bash
python ml/disease_detection/train.py --epochs 15 --batch_size 32
```
The pipeline automatically:
1. Applies data augmentation (rotations, flips, zooming, color adjustments).
2. Splits into 80% training / 20% validation.
3. Saves the best model checkpoint to `ml/disease_detection/disease_model.h5` (or `.pth` / `.onnx`).
4. Exports `class_indices.json`.

---

## 🔍 Image Preprocessing Pipeline with OpenCV

1. **File Decoding**: Loaded with `cv2.imread` or decoded from raw upload byte buffers.
2. **Color Space**: Converted from OpenCV's native BGR to standard RGB (`cv2.cvtColor`).
3. **Resizing**: Scaled to `(224, 224)` via area-averaging (`cv2.INTER_AREA`) or linear interpolation.
4. **Normalization**: Floating-point scaled to $[0.0, 1.0]$.
5. **Quality Diagnostics**: Evaluates Excess Green Index (ExG), brightness, and contrast.

---

## 🛡 Strict Inference Policy: No Random Predictions
In accordance with precision agriculture safety standards, this module **strictly refuses to fabricate random predictions** if an authentic trained model is unavailable. If the model file is not present, the system informs the farmer clearly and provides the training instructions.

