from loguru import logger

import sys
import argparse
import time
import os
import cv2
import yaml
import numpy as np
import onnxruntime as ort
import pandas as pd
from PIL import Image


def letterbox(
    im,
    new_shape=(480, 480),
    color=(114, 114, 114),
    auto=True,
    scaleup=True,
    stride=32,
):
    #logger.info("Started letterbox")
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(
        im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )  # add border
    #logger.info("Ended letterbox")
    return im, r, (dw, dh)




def preprocess_image(img_orig, img_size):
    #logger.info("Started preprocess_image")
    #   img0 = cv2.imread(img_path)
    img = letterbox(img_orig,new_shape= (img_size, img_size), auto=True)[0]
    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)
    #logger.info("Ended preprocess_image")
    return img, img_orig


def get_model_data(model_path, image_lists):
    #logger.info("Started get_model_data")
    cuda = False
    providers = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if cuda
        else ["CPUExecutionProvider"]
    )
    session = ort.InferenceSession(model_path, providers=providers)
    image_dict = {}
    p_image_list = []
    ratio_dwdh = []
    inname =[]
    for img in image_lists:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = img.copy()
        image, ratio, dwdh = letterbox(image, auto=False)
        image = image.transpose((2, 0, 1))
        image = np.expand_dims(image, 0)
        image = np.ascontiguousarray(image)
        im = image.astype(np.float32)
        im /= 255
        # im.shape
        # outname = [i.name for i in session.get_outputs()]
        inname = [i.name for i in session.get_inputs()]
        p_image_list.extend(im)
        ratio_dwdh.append([ratio, dwdh])
    image_dict = {inname[0]: np.stack(p_image_list)}
    #logger.info("Ended get_model_data")
    return image_dict, ratio_dwdh, session


def get_batch_output(outputs, img_lists):
    #logger.info("Started get_batch_output")
    batch_outputs = []
    for i in range(0, len(img_lists)):
        idx = np.where(outputs[:, 0] == i)
        arr = outputs[idx]
        batch_outputs.append(arr)
    #logger.info("Started get_batch_output")
    return batch_outputs

def post_process_output(batch_outputs, r_dwdh, img_list):
    #logger.info("Started post_process_output")
    image_coord_score = []
    for id_, output in enumerate(batch_outputs):
        inter_output = []
        for page_no, x0, y0, x1, y1, cls_id, score in output:
            # image = i_list[int(batch_id)]
            box = np.array([x0, y0, x1, y1])
            box -= np.array(r_dwdh[int(page_no)][1] * 2)
            box /= r_dwdh[int(page_no)][0]
            box = box.round().astype(np.int32).tolist()
            box = list(map(lambda x: max(0,x), box))
            cls_id = int(cls_id)
            score = round(float(score), 2)
            inter_output.append([page_no, cls_id, score, box])
        # bboxes = [box[3] for box in inter_output]
        # if bboxes:
        #     labels = get_classification_label(classification_model_path,img_list[id_],bboxes)
        # inter_output = [[row[i] if i != 1 else label for i in range(len(row))] for row,label in zip(inter_output,labels)] 
        image_coord_score.append({f"image_{id_}": inter_output})
    #logger.info("Ended post_process_output")
    return image_coord_score

def plot_image_multiple(image, bboxes, probs, labels):
    #logger.info("Started plot_image_multiple")
    for bbox, prob, label in zip(bboxes, probs, labels):
        bbox = list(map(int, bbox))
        prob = round(prob,2)
        start_p =(int(bbox[0] ), int(bbox[1] ))
        end_p = (int(bbox[2]), int(bbox[3]))
        color = (255,0,0) if label == 1 else (0,255,0)
        cv2.rectangle(image, start_p, end_p,color, 1) 
        cv2.putText(img=image, text=str(prob), org=(bbox[0], bbox[1]), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=( 255,0, 0),thickness=1)
        cv2.putText(img=image, text=str(label), org=(bbox[0] + 30, bbox[1]), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(255, 0, 0),thickness=1)
    #logger.info("Ended plot_image_multiple")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # cv2 uses BGR so changing it to RGB before saving using PIL
    return Image.fromarray(image)

def main(img_path, model_path, config_file, save_location, save_file_name, **kwargs):
  #logger.info("Started Inference")
  if not os.path.exists(save_location):
    #logger.info(f"Directory {save_location} doesn't exist, creating the directory.")
    os.makedirs(f"{save_location}", exist_ok=True)
  save_path = os.path.join(save_location, save_file_name)
  with open(config_file, 'r') as file:
    db= yaml.safe_load(file)
  label = db.get('names')
  img = cv2.imread(img_path)
  img_list = [img] 
  image_data, ratio_dwdh, model = get_model_data(model_path, img_list)
  outname = [i.name for i in model.get_outputs()]
  outputs = model.run(outname, image_data)[0]
  batch_outputs = get_batch_output(outputs, img_list)
  p_outputs = post_process_output(batch_outputs, ratio_dwdh, img_list)
  l_bboxes = p_outputs[0].get('image_0')
  bboxes = [box[3] for box in l_bboxes]
  classes = [label[box[1]] for box in l_bboxes]
  confidences = [box[2] for box in l_bboxes]
  infer_img = plot_image_multiple(img, bboxes, confidences, classes)
  infer_img.save(f"{save_path}.png")
  #logger.info("Ended Inference")
  #logger.info(f"Inferred Image saved at location {save_path}.png")
  return None

if __name__ == "__main__":
  #logger.info("Entry Point of Main")
  parser = argparse.ArgumentParser()
  parser.add_argument("--img_path", type=str, help="image path")
  parser.add_argument("--model_path", type=str, help="model path")
  parser.add_argument("--config_file", type=str, help="config path")
  parser.add_argument("--save_location", type=str, default="", help="directory name to save")
  parser.add_argument("--save_file_name", type=str, help="name of image to save")
  args = parser.parse_args()
  main(**vars(args))