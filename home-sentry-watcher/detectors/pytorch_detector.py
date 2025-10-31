import time
from typing import List

import cv2
import numpy as np
import torch
from torchvision.models import detection

from coco_classes import COCO_CLASSES
from models.detection_result import DetectionResult
from detectors.detector import Detector
from models.person_detection import PersonDetection
from models.point import Point
from sources.videosource import VideoSource

VERBOSE = True

# ResNet50: accurate but slow
MODEL_RESNET = "frcnn-resnet"

# MobileNet v3: Fast but not as accurate
MODEL_MOBILENET = "frcnn-mobilenet"

# RetinaNet: balance between fast/accurate
MODEL_RETINANET = "retinanet"

PERSON_INDEX = COCO_CLASSES.index('person')


def log(msg):
    if VERBOSE:
        print(msg)


class PyTorchDetector(Detector):
    """
    Detector using PyTorch and a pre-trained model from the torchvision library.
    """

    def __init__(self, config=None):
        model = MODEL_MOBILENET if (config is None or 'model' not in config) else config['model']
        cuda_available = torch.cuda.is_available()
        print(
            f'Init PyTorchDetector: cuda.is_available={cuda_available}, model={model}')
        if cuda_available:
            device_name = "cuda"
        else:
            device_name = "cpu"
        print(f'Using device: {device_name}')
        self.device = torch.device(device_name)
        self.models = {
            MODEL_RESNET: detection.fasterrcnn_resnet50_fpn,
            MODEL_MOBILENET: detection.fasterrcnn_mobilenet_v3_large_fpn,
            MODEL_RETINANET: detection.retinanet_resnet50_fpn
        }
        self.model = self.models[model](pretrained=True, progress=True, num_classes=91,
                                        pretrained_backbone=True).to(self.device)
        self.model.eval()

    def convert_image(self, original_image):
        image = original_image.copy()
        # Convert the image from BGR to RGB channel ordering and change the image from channels last to channels first ordering
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.transpose((2, 0, 1))
        # Add the batch dimension, scale the raw pixel intensities to the range [0, 1], and convert the image to a floating point tensor.
        image = np.expand_dims(image, axis=0)
        image = image / 255.0
        image = torch.FloatTensor(image)
        return image

    def detect(self, original_image, video_source: VideoSource) -> DetectionResult:
        image = self.convert_image(original_image)
        image = image.to(self.device)
        height = original_image.shape[0]
        width = original_image.shape[1]
        detections = self.model(image)[0]
        person_detections: List[PersonDetection] = []
        for i in range(0, len(detections["boxes"])):
            confidence = detections["scores"][i]
            idx = int(detections["labels"][i]) - 1
            if idx == PERSON_INDEX:
                box = detections["boxes"][i].detach().cpu().numpy()
                (startX, startY, endX, endY) = box.astype("int")
                top_left_relative = Point(startX / width, startY / height)
                bottom_right_relative = Point(endX / width, endY / height)
                video_source.log.info(
                    f'Detection: conf={confidence}, TL={top_left_relative}, BR={bottom_right_relative}')
                person_detection = PersonDetection(top_left_relative, bottom_right_relative, confidence,
                                                   time.time())
                person_detections.append(person_detection)
        return DetectionResult(person_detections, original_image)
