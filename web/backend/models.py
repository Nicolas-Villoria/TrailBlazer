from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PointModel(BaseModel):
    lat: float
    lon: float

class BoxModel(BaseModel):
    bottom_left: PointModel
    top_right: PointModel

class MonumentModel(BaseModel):
    name: str
    location: PointModel

class RouteRequest(BaseModel):
    start_point: PointModel
    monument_type: str
    search_box: BoxModel
    settings: Optional[Dict[str, Any]] = None

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: float
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Response Models for API endpoints
class MonumentResponse(BaseModel):
    name: str
    location: PointModel

class MonumentListResponse(BaseModel):
    monuments: List[MonumentResponse]
    count: int

class SegmentResponse(BaseModel):
    start: PointModel
    end: PointModel

class SegmentPreviewResponse(BaseModel):
    segments: List[SegmentResponse]
    total_count: int
    preview_count: int

class MonumentTypeResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str

class MonumentTypesResponse(BaseModel):
    types: List[MonumentTypeResponse]

class JobStartResponse(BaseModel):
    job_id: str
    status: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str

class ApiInfoResponse(BaseModel):
    message: str
    version: str
    status: str