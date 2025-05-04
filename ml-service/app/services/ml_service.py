from ultralytics import YOLO
import cv2
from typing import List, Dict, Any
from app.core.config import settings
from app.models.detection import DetectionResponse, BBox

class MLService:
    def __init__(self):
        self.model = YOLO(settings.model_path)
        self.class_names = self.model.names

    def process_image(self, image_path: str) -> List[DetectionResponse]:
        results = self.model.predict(image_path, save=True, project=settings.results_dir)
        return self._parse_results(results)

    def _parse_results(self, results) -> List[DetectionResponse]:
        detections = []
        for result in results:
            for box in result.boxes:
                detection = DetectionResponse(
                    class_name=self.class_names[int(box.cls)],
                    confidence=float(box.conf),
                    bbox=BBox(
                        x1=int(box.xyxy[0][0]),
                        y1=int(box.xyxy[0][1]),
                        x2=int(box.xyxy[0][2]),
                        y2=int(box.xyxy[0][3])
                    )
                )
                detections.append(detection)
        return detections

ml_service = MLService()