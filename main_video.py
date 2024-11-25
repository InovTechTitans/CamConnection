import cv2
import numpy as np
from ultralytics import YOLO

from constants.paths import INPUT_PATH, INPUT_SAMPLE, OUTPUT_PATH, OUTPUT_RESULTS
from utils import create_path_if_not_exist, get_car, read_license_plate, write_csv
from video.add_missing_data import create_interpolate_date
from video.sort.sort import Sort
from video.visualize import show_vizualization

create_path_if_not_exist(INPUT_PATH)
create_path_if_not_exist(OUTPUT_PATH)

results = {}

mot_tracker = Sort()

# load models
coco_model = YOLO("input/yolov8n.pt")
license_plate_detector = YOLO("./models/license_plate_detector.pt")

# load video
cap = cv2.VideoCapture(INPUT_SAMPLE)


vehicles = [2, 3, 5, 7]

# read frames
frame_nmr = -1
ret = True

while ret:
    frame_nmr += 1
    ret, frame = cap.read()
    if ret:
        results[frame_nmr] = {}
        # detect vehicles
        detections = coco_model(frame)[0]
        detections_ = []
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) in vehicles:
                detections_.append([x1, y1, x2, y2, score])

        # track vehicles
        track_ids = mot_tracker.update(np.asarray(detections_))

        # detect license plates
        license_plates = license_plate_detector(frame)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate

            # assign license plate to car
            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

            if car_id != -1:
                # crop license plate
                license_plate_crop = frame[int(y1): int(y2), int(x1): int(x2), :]

                # process license plate
                license_plate_crop_gray = cv2.cvtColor(
                    license_plate_crop, cv2.COLOR_BGR2GRAY
                )
                _, license_plate_crop_thresh = cv2.threshold(
                    license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV
                )

                cv2.imshow("Original crop", license_plate_crop)
                cv2.imshow("Thres crop", license_plate_crop_thresh)

                # read license plate number
                license_plate_text, license_plate_text_score = read_license_plate(
                    license_plate_crop_thresh
                )

                if license_plate_text is not None:
                    results[frame_nmr][car_id] = {
                        "car": {"bbox": [xcar1, ycar1, xcar2, ycar2]},
                        "license_plate": {
                            "bbox": [x1, y1, x2, y2],
                            "text": license_plate_text,
                            "bbox_score": score,
                            "text_score": license_plate_text_score,
                        },
                    }

# write results
write_csv(results, OUTPUT_RESULTS)
create_interpolate_date()
show_vizualization()