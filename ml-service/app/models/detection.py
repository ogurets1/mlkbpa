from pydantic import BaseModel

class BBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class DetectionResponse(BaseModel):
    class_name: str
    confidence: float
    bbox: BBox

class ProcessResponse(BaseModel):
    result_url: str
    detections: list[DetectionResponse]