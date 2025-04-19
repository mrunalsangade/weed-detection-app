# Weed Detection PGM Web App

A Flask‑based application that uses a **Bayesian network** to classify and highlight weeds in crop images.

---

## 📖 Overview

This app demonstrates a **Probabilistic Graphical Model** approach to weed detection:

1. **Training Phase**  
   - Reads COCO‑style annotation file (`labels_weed_detection.json`)  
   - Extracts two hand‑crafted features per bounding box:  
     - **Average green intensity**  
     - **Edge density**  
   - Discretizes each into Low/Medium/High and trains a Bayesian network  
     (`Green → IsWeed`, `EdgeDensity → IsWeed`) via maximum‑likelihood estimation.

2. **Inference Phase**  
   - User logs in (`admin`/`1234`) and uploads a new image.  
   - If the image matches a labeled sample, uses its boxes; else applies a green‑mask segmentation.  
   - Computes features, discretizes them, and performs Bayesian inference to label each region.  
   - Annotates “Weed” boxes in the image and displays the result.

---

## 🛠️ Tech Stack

- **Language & Framework**: Python 3.12, Flask  
- **PGM**: `pgmpy` (DiscreteBayesianNetwork, VariableElimination)  
- **Computer Vision**: OpenCV (`cv2`), NumPy, Pillow  
- **Data Handling**: Pandas  
- **Frontend**: Jinja2 templates, basic HTML/CSS  
- **Testing**: `pytest`  

---

## 🚀 Setup & Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/mrunalsangade/weed-detection-app.git
   cd weed-detection-app
