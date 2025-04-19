import os
import cv2
import numpy as np
import pandas as pd
import json
import uuid
from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination

# —————————————————————————————————————
# 1) Load & extract features just as you had them
# —————————————————————————————————————
with open("labels_weed_detection.json") as f:
    data = json.load(f)

image_map   = {img['id']: img['file_name'] for img in data['images']}
annotations = data['annotations']

features      = []
bbox_by_image = {}

for ann in annotations:
    fn   = image_map.get(ann['image_id'])
    path = os.path.join("uploads", fn)
    if not fn or not os.path.isfile(path):
        continue

    img = cv2.imread(path)
    if img is None:
        continue

    x, y, w, h = map(int, ann['bbox'])
    # skip invalid or out‑of‑bounds boxes
    if w <= 0 or h <= 0 or y+h > img.shape[0] or x+w > img.shape[1]:
        continue

    crop = img[y:y+h, x:x+w]
    if crop.size == 0:
        continue

    # compute features
    avg_color = np.mean(crop, axis=(0,1))
    gray      = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    edges     = cv2.Canny(gray, 50, 150)
    # ensure denominator > 0
    denom     = crop.shape[0] * crop.shape[1]
    if denom == 0:
        continue
    edge_density = edges.sum() / denom

    features.append({
      'Image':       fn,
      'Red':         avg_color[2],
      'Green':       avg_color[1],
      'Blue':        avg_color[0],
      'EdgeDensity': edge_density,
      'IsWeed':      1
    })
    bbox_by_image.setdefault(fn, []).append((x, y, w, h))

# —————————————————————————————————————
# 2) Build DataFrame & bin into 3 categories
# —————————————————————————————————————
df = pd.DataFrame(features)
if not df.empty:
    df['Green']       = pd.cut(df['Green'], bins=3, labels=["Low","Medium","High"])
    df['EdgeDensity'] = pd.cut(df['EdgeDensity'], bins=3, labels=["Low","Medium","High"])

# —————————————————————————————————————
# 3) Train your Bayes net (only if we have data)
# —————————————————————————————————————
inference = None
_bin2idx = {'Low':0, 'Medium':1, 'High':2}

if not df.empty:
    model = BayesianNetwork([('Green','IsWeed'), ('EdgeDensity','IsWeed')])
    model.fit(df[['Green','EdgeDensity','IsWeed']], estimator=MaximumLikelihoodEstimator)
    inference = VariableElimination(model)

def run_detection(image_path):
    fn  = os.path.basename(image_path)
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image {image_path}")

    # get hand‑labeled boxes or fall back to a green mask
    if fn in bbox_by_image:
        bboxes = bbox_by_image[fn]
    else:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (35,40,40), (85,255,255))
        cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bboxes = [cv2.boundingRect(c) for c in cnts if cv2.contourArea(c) > 500]

    detected = False
    for x, y, w0, h0 in bboxes:
        # clamp to image
        x, y = max(x,0), max(y,0)
        w0, h0 = min(w0, img.shape[1]-x), min(h0, img.shape[0]-y)
        if w0 <= 0 or h0 <= 0:
            continue

        crop = img[y:y+h0, x:x+w0]
        if crop.size == 0:
            continue

        avg_color = np.mean(crop, axis=(0,1))
        gray      = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        edges     = cv2.Canny(gray, 50, 150)
        denom     = crop.shape[0] * crop.shape[1]
        if denom == 0:
            continue
        edge_density = edges.sum() / denom

        # bin into Low/Med/High
        if inference:
            green_lbl = pd.cut([avg_color[1]], bins=3, labels=["Low","Medium","High"])[0]
            edge_lbl  = pd.cut([edge_density], bins=3, labels=["Low","Medium","High"])[0]
            evidence  = {
              'Green':       _bin2idx[green_lbl],
              'EdgeDensity': _bin2idx[edge_lbl]
            }
            result = inference.map_query(variables=['IsWeed'], evidence=evidence)
            is_weed = (result.get('IsWeed', 0) == 1)
        else:
            # no trained model: simple threshold on green channel
            is_weed = avg_color[1] > 100

        if is_weed:
            cv2.rectangle(img, (x,y), (x+w0,y+h0), (0,255,0), 2)
            cv2.putText(img, "Weed", (x, y-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            detected = True

    # save & return result filename
    os.makedirs("static/results", exist_ok=True)
    out_fn = f"result_{uuid.uuid4().hex[:6]}.jpg"
    cv2.imwrite(os.path.join("static/results", out_fn), img)
    if not detected:
        print("No weeds detected.")
    return out_fn
