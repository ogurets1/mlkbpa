from fastapi import APIRouter, UploadFile, File
from app.services import file_service, ml_service
from app.models.detection import ProcessResponse, DetectionResponse
from app.core.config import settings

router = APIRouter()

@router.post("/process", response_model=ProcessResponse)
async def process_file(file: UploadFile = File(...)):
    file_path = await file_service.save_upload_file(file)
    results = ml_service.process_image(file_path)
    
    detections = []
    for r in results:
        for box in r.boxes:
            detections.append(DetectionResponse(
                class_name=ml_service.model.names[int(box.cls)],
                confidence=float(box.conf),
                bbox=BBox(
                    x1=int(box.xyxy[0][0]),
                    y1=int(box.xyxy[0][1]),
                    x2=int(box.xyxy[0][2]),
                    y2=int(box.xyxy[0][3])
                )
            ))
    
    return {
        "result_url": f"{settings.results_dir}/{file_path.split('/')[-1]}",
        "detections": detections
    }